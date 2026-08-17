"""app/client.py — OpenAI-compatible LLM client with retries + usage capture.

Talks to any OpenAI-compatible /chat/completions endpoint (e.g. the VentureLab
provider at OPENCODE_GO_BASE_URL). Every call records:

  - usage (prompt/completion/reasoning/total tokens) straight from the API
  - provider-reported cost when the API returns a nonzero numeric `cost` field
  - duration_ms, retry count, error text

Retries happen only on transient failures (429/5xx/connection); a 4xx like 400
is a hard error. Tools use the standard OpenAI `tools`/`tool_calls` shape when
the endpoint supports them; callers may always fall back to text extraction.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

DEFAULT_TIMEOUT = 90.0
DEFAULT_MAX_RETRIES = 2


class ModelClient(Protocol):
    """The duck-typed client contract the runner requires (LLMClient and
    FakeClient both satisfy it)."""
    model: str

    def chat(
        self,
        messages: list[dict],
        *,
        tools: list[dict] | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        seed: int | None = None,
    ) -> "ChatResult": ...

    def close(self) -> None: ...


@dataclass
class ChatResult:
    content: str = ""
    reasoning: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0
    provider_cost: float | None = None
    duration_ms: int = 0
    status: str = "ok"  # ok | error
    retries: int = 0
    error: str = ""
    raw: dict = field(default_factory=dict)


def _read_usage(data: dict) -> dict:
    usage = data.get("usage") or {}
    return {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
        "reasoning_tokens": int(usage.get("completion_tokens_details", {}).get("reasoning_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
    }


def _parse_cost(data: dict) -> float | None:
    """Provider-reported cost if present and numeric and nonzero."""
    cost = data.get("cost")
    if cost is None:
        return None
    try:
        value = float(cost)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(timeout=timeout)

    def chat(
        self,
        messages: list[dict],
        *,
        tools: list[dict] | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        seed: int | None = None,
    ) -> ChatResult:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if seed is not None:
            payload["seed"] = seed

        started = time.monotonic()
        retries = 0
        last_error = ""
        while True:
            try:
                resp = self._client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            except httpx.HTTPError as exc:
                last_error = f"connection: {exc.__class__.__name__}"
                if retries < self.max_retries:
                    retries += 1
                    time.sleep(0.5 * (2 ** retries))
                    continue
                return ChatResult(status="error", error=last_error, retries=retries,
                                  duration_ms=int((time.monotonic() - started) * 1000))

            if resp.status_code in (429, 500, 502, 503, 504, 529):
                last_error = f"http_{resp.status_code}"
                if retries < self.max_retries:
                    retries += 1
                    time.sleep(0.5 * (2 ** retries))
                    continue
            if resp.status_code != 200:
                return ChatResult(
                    status="error",
                    error=f"http_{resp.status_code}: {resp.text[:300]}",
                    retries=retries,
                    duration_ms=int((time.monotonic() - started) * 1000),
                )

            data = resp.json()
            usage = _read_usage(data)
            choice = (data.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            tool_calls = message.get("tool_calls") or []
            return ChatResult(
                content=message.get("content") or "",
                reasoning=message.get("reasoning") or "",
                tool_calls=[
                    {
                        "id": tc.get("id") or f"call_{i}",
                        "type": tc.get("type") or "function",
                        "function": tc.get("function") or {},
                    }
                    for i, tc in enumerate(tool_calls)
                ],
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                reasoning_tokens=usage["reasoning_tokens"],
                total_tokens=usage["total_tokens"],
                provider_cost=_parse_cost(data),
                duration_ms=int((time.monotonic() - started) * 1000),
                status="ok",
                retries=retries,
                raw=data,
            )

    def close(self) -> None:
        self._client.close()