"""arXiv source adapter — searches papers via arXiv API (Atom feed)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from factory.sources import SearchResult, SourceUnavailable

_ARXIV_API = "http://export.arxiv.org/api/query"


def search_arxiv(
    query: str,
    *,
    max_results: int = 10,
) -> SearchResult:
    """Search arXiv papers.

    Returns SearchResult(ok=True, items=[...]) on success.
    Raises SourceUnavailable on network errors.
    Returns SearchResult(ok=False, ...) for non-transient errors.
    """
    try:
        resp = httpx.get(
            _ARXIV_API,
            params={
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
            },
            timeout=15.0,
        )
    except httpx.TransportError as exc:
        raise SourceUnavailable(f"arxiv transport error: {exc}") from exc

    if resp.status_code != 200:
        return SearchResult(ok=False, error=f"http_{resp.status_code}", source="arxiv")

    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    items = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)
        link_el = entry.find("atom:id", ns)
        authors = [
            a.find("atom:name", ns).text or ""
            for a in entry.findall("atom:author", ns)
        ]

        items.append({
            "title": (title_el.text or "").strip().replace("\n", " ") if title_el is not None else "",
            "summary": (summary_el.text or "").strip().replace("\n", " ") if summary_el is not None else "",
            "published": published_el.text.strip() if published_el is not None else "",
            "url": link_el.text.strip() if link_el is not None else "",
            "authors": authors[:5],
        })

    return SearchResult(ok=True, items=items, source="arxiv")
