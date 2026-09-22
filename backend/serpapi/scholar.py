"""Google Scholar collector."""

from typing import Any, Optional

from .client import SerpApiClient


def collect_google_scholar(topic: str, location: str, query: str) -> dict[str, Any]:
    payload = SerpApiClient().search({"engine": "google_scholar", "q": query})
    results = [
        {
            "paper_title": item.get("title"),
            "authors": (item.get("publication_info") or {}).get("authors"),
            "publication": (item.get("publication_info") or {}).get("summary"),
            "year": _extract_year((item.get("publication_info") or {}).get("summary")),
            "link": item.get("link"), "snippet": item.get("snippet"),
            "position": item.get("position", index),
        }
        for index, item in enumerate(payload.get("organic_results", []), start=1)
        if isinstance(item, dict)
    ]
    return {"source": "google_scholar", "query": query, "results": results}


def _extract_year(publication: Optional[str]) -> Optional[str]:
    if not publication:
        return None
    import re
    match = re.search(r"\b(?:19|20)\d{2}\b", publication)
    return match.group(0) if match else None
