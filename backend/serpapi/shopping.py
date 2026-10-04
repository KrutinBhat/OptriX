"""Google Shopping collector."""

from typing import Any

from .client import SerpApiClient


def collect_google_shopping(topic: str, location: str, query: str) -> dict[str, Any]:
    payload = SerpApiClient().search({"engine": "google_shopping", "q": query, "location": location})
    results = [
        {
            "product_title": item.get("title"), "price": item.get("price"),
            "source": item.get("source"), "product_link": item.get("link"),
            "rating": item.get("rating"), "reviews": item.get("reviews"),
            "position": item.get("position", index),
        }
        for index, item in enumerate(payload.get("shopping_results", []), start=1)
        if isinstance(item, dict)
    ]
    return {"source": "google_shopping", "query": query, "results": results}
