"""Google web-search collector."""

from typing import Any

from .client import SerpApiClient


def collect_google_search(topic: str, location: str, query: str) -> dict[str, Any]:
    payload = SerpApiClient().search({"engine": "google", "q": query, "location": location})
    results = [
        {
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
            "source": item.get("source") or item.get("displayed_link"),
            "position": item.get("position"),
        }
        for item in payload.get("organic_results", [])
        if isinstance(item, dict)
    ]
    return {"source": "google_search", "query": query, "results": results}
