"""Google Maps/local-business collector."""

from typing import Any

from .client import SerpApiClient


def collect_google_maps(topic: str, location: str, query: str) -> dict[str, Any]:
    payload = SerpApiClient().search({"engine": "google_maps", "q": query, "location": location})
    results = [
        {
            "business_name": item.get("title"), "address": item.get("address"),
            "rating": item.get("rating"), "reviews": item.get("reviews"),
            "category": item.get("type") or item.get("category"),
            "website": item.get("website"), "position": item.get("position", index),
        }
        for index, item in enumerate(payload.get("local_results", []), start=1)
        if isinstance(item, dict)
    ]
    return {"source": "google_maps", "query": query, "results": results}
