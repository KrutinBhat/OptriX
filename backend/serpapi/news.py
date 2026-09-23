"""Google News collector."""

from typing import Any

from .client import SerpApiClient


def collect_google_news(topic: str, location: str, query: str) -> dict[str, Any]:
    payload = SerpApiClient().search({"engine": "google_news", "q": query, "location": location})
    results = [
        {
            "title": item.get("title"), "link": item.get("link"),
            "source": item.get("source"), "date": item.get("date"),
            "snippet": item.get("snippet"), "position": index,
        }
        for index, item in enumerate(payload.get("news_results", []), start=1)
        if isinstance(item, dict)
    ]
    return {"source": "google_news", "query": query, "results": results}
