"""Google Jobs collector."""

from typing import Any

from .client import SerpApiClient


def collect_google_jobs(topic: str, location: str, query: str) -> dict[str, Any]:
    payload = SerpApiClient().search({"engine": "google_jobs", "q": query, "location": location})
    results = [
        {
            "job_title": item.get("title"), "company": item.get("company_name"),
            "location": item.get("location"), "description": item.get("description"),
            "link": _job_link(item),
            "detected_query": query, "position": index,
        }
        for index, item in enumerate(payload.get("jobs_results", []), start=1)
        if isinstance(item, dict)
    ]
    return {"source": "google_jobs", "query": query, "results": results}


def _job_link(item: dict[str, Any]) -> Any:
    """Use a direct share link first, then the first related link when present."""
    if item.get("share_link"):
        return item["share_link"]
    related_links = item.get("related_links") or []
    if isinstance(related_links, list) and related_links and isinstance(related_links[0], dict):
        return related_links[0].get("link")
    return None
