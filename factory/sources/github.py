"""GitHub source adapter — searches repos via GitHub API."""

from __future__ import annotations

import os
import httpx

from factory.sources import SearchResult, SourceUnavailable

_GITHUB_API = "https://api.github.com/search/repositories"


def search_github(
    query: str,
    *,
    token: str | None = None,
    max_results: int = 10,
) -> SearchResult:
    """Search GitHub repositories.

    Returns SearchResult(ok=True, items=[...]) on success.
    Raises SourceUnavailable on network/auth errors.
    Returns SearchResult(ok=False, ...) for non-transient HTTP errors.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = httpx.get(
            _GITHUB_API,
            params={"q": query, "per_page": max_results},
            headers=headers,
            timeout=15.0,
        )
    except httpx.TransportError as exc:
        raise SourceUnavailable(f"github transport error: {exc}") from exc

    if resp.status_code == 403:
        return SearchResult(ok=False, error="rate_limited", source="github")
    if resp.status_code >= 500:
        return SearchResult(ok=False, error=f"server_{resp.status_code}", source="github")
    if resp.status_code != 200:
        return SearchResult(ok=False, error=f"http_{resp.status_code}", source="github")

    data = resp.json()
    items = []
    for repo in data.get("items", [])[:max_results]:
        items.append({
            "name": repo.get("full_name", ""),
            "description": repo.get("description", ""),
            "stars": repo.get("stargazers_count", 0),
            "url": repo.get("html_url", ""),
            "language": repo.get("language", ""),
            "updated_at": repo.get("updated_at", ""),
        })

    return SearchResult(ok=True, items=items, source="github")
