"""Probe interface (spec section 'Probe interface'):

    class Probe:
        id: str
        version: str
        async def run(endpoint, credentials) -> ProbeResult

ProbeResult:
    {
        "status": "SUCCESS",
        "measurements": [Observation, ...],
        "raw_artifacts": [dict, ...],
        "errors": []
    }
"""

from __future__ import annotations

import abc
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from ..schema import Endpoint, ProbeResult


@dataclass
class Credentials:
    api_key: Optional[str] = None
    base_url: str = ""
    headers: dict = field(default_factory=dict)
    # extra non-secret context the probe may record (e.g. model family)
    meta: dict = field(default_factory=dict)

    @property
    def usable(self) -> bool:
        return bool(self.base_url) and self.api_key is not None

    def auth_headers(self) -> dict:
        h = dict(self.headers)
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h


def load_credentials(endpoint: Endpoint, env: Optional[dict] = None) -> Credentials:
    """Resolve credentials from env var names. base_url_env overrides base_url;
    api_key_env must be set for inference probes unless it equals "NONE"
    (no-auth local endpoint). Never emits secrets."""
    env = env if env is not None else os.environ
    base_url = endpoint.base_url
    if endpoint.base_url_env and env.get(endpoint.base_url_env):
        base_url = env[endpoint.base_url_env].rstrip("/")
    api_key = None
    if endpoint.api_key_env and endpoint.api_key_env != "NONE":
        api_key = env.get(endpoint.api_key_env)
    elif endpoint.api_key_env == "NONE":
        api_key = ""  # present but empty: no Authorization header sent
    return Credentials(base_url=base_url, api_key=api_key,
                       meta={"provider": endpoint.provider_id})


class Probe(abc.ABC):
    id: str = "base"
    version: str = "0.0.0"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self._client = client

    @abc.abstractmethod
    async def run(self, endpoint: Endpoint, creds: Credentials) -> ProbeResult:
        ...

    async def _http(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0))


def classify_http_error(status_code: int) -> str:
    """Map HTTP status to the state enum. Distinguishes rate limit (429) from
    outage/absence, per required scenarios:
      - 404 / 400 model-not-found -> ABSENT (provider says model exists but inference 404s)
      - 429 -> RATE_LIMITED
      - 5xx / network / timeout -> UNAVAILABLE
    """
    if status_code == 429:
        return "RATE_LIMITED"
    if status_code in (404, 400):
        # 400 can be a bad request; classify as ABSENT only when message says
        # the model is unknown; otherwise UNAVAILABLE. Conservative default.
        return "ABSENT"
    if 500 <= status_code < 600:
        return "UNAVAILABLE"
    return "UNAVAILABLE"


def make_chat_request(endpoint: Endpoint, messages: list[dict],
                      max_tokens: int = 16, temperature: float = 0.0,
                      stream: bool = False, response_format: Optional[dict] = None,
                      tools: Optional[list] = None,
                      extra: Optional[dict] = None) -> dict:
    body: dict[str, Any] = {
        "model": endpoint.provider_model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }
    if response_format is not None:
        body["response_format"] = response_format
    if tools is not None:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    if extra:
        body.update(extra)
    return body


def parse_stream_line(line: str) -> Optional[dict]:
    """Parse one SSE line. Returns None for non-data lines. Raises ValueError
    on malformed data payload (required scenario: HTTP 200 but malformed stream)."""
    line = line.strip()
    if not line:
        return None
    if line.startswith("data:"):
        payload = line[5:].strip()
        if payload == "[DONE]":
            return {"_done": True}
        try:
            import json
            obj = json.loads(payload)
        except Exception as e:
            raise ValueError(f"malformed stream chunk: {payload[:200]!r} ({e})")
        if not isinstance(obj, dict):
            raise ValueError(f"malformed stream chunk (non-object): {payload[:200]!r}")
        return obj
    return None


def measure_elapsed_ms(t0: float) -> float:
    return round((time.monotonic() - t0) * 1000.0, 2)


def http_error_kind(exc: Exception) -> str:
    if isinstance(exc, httpx.TimeoutException):
        return "timeout"
    if isinstance(exc, httpx.ConnectError):
        return "connect_error"
    if isinstance(exc, httpx.HTTPStatusError):
        return f"http_{exc.response.status_code}"
    return type(exc).__name__.lower()