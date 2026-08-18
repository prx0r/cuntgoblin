from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class SourceHit:
    uri: str
    title: str
    source_type: str
    source_family: str
    snippet: str | None = None
    published_at: str | None = None

@dataclass(frozen=True)
class SearchResult:
    ok: bool
    hits: tuple[SourceHit, ...] = ()
    error_class: str | None = None
    error_message: str | None = None

class SourceAdapter(Protocol):
    name: str
    def search(self, query: str, limit: int = 10) -> SearchResult: ...

def require_success(result: SearchResult) -> tuple[SourceHit, ...]:
    if not result.ok:
        raise RuntimeError(
            f"source failed: {result.error_class}: {result.error_message}"
        )
    return result.hits
