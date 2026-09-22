"""Research API: executes the initial fixed set of collection queries."""

import asyncio
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter

from schemas.models import ResearchRequest
from serpapi.client import SerpApiError
from serpapi.jobs import collect_google_jobs
from serpapi.maps import collect_google_maps
from serpapi.news import collect_google_news
from serpapi.scholar import collect_google_scholar
from serpapi.search import collect_google_search
from serpapi.shopping import collect_google_shopping

router = APIRouter(tags=["research"])


@router.post("/research")
async def research(request: ResearchRequest) -> dict[str, Any]:
    """Collect raw results. A failed source remains isolated in the response."""
    topic = request.topic.strip()
    location = request.location.strip()
    plans: list[tuple[str, Callable[[str, str, str], dict[str, Any]], list[str]]] = [
        ("google_search", collect_google_search, [
            f"{topic} manufacturers {location}",
            f"{topic} suppliers {location}",
        ]),
        ("google_news", collect_google_news, [f"{topic} industry {location}"]),
        ("google_jobs", collect_google_jobs, [f"{topic} engineer {location}"]),
        ("google_maps", collect_google_maps, [f"{topic} suppliers"]),
        ("google_shopping", collect_google_shopping, [topic]),
        ("google_scholar", collect_google_scholar, [f"{topic} thermal management"]),
    ]

    collected = await asyncio.gather(
        *(
            _collect_source(source, collector, queries, topic, location)
            for source, collector, queries in plans
        )
    )
    sources = dict(collected)
    total_results = sum(len(source_data.get("results", [])) for source_data in sources.values())

    return {
        "topic": topic,
        "location": location,
        **sources,
        "research_stats": {"total_queries": 7, "total_results": total_results},
    }


async def _collect_source(
    source: str,
    collector: Callable[[str, str, str], dict[str, Any]],
    queries: list[str],
    topic: str,
    location: str,
) -> tuple[str, dict[str, Any]]:
    """Run a source's queries in worker threads and merge their raw results."""
    responses = await asyncio.gather(
        *(asyncio.to_thread(_safe_collect, source, collector, topic, location, query) for query in queries)
    )
    successful = [response for response in responses if "error" not in response]
    errors = [response["error"] for response in responses if "error" in response]
    merged_results = [result for response in successful for result in response["results"]]
    data: dict[str, Any] = {
        "source": source,
        "queries_executed": len(queries),
        "results": merged_results,
    }
    # Preserve per-query failures without removing valid data from other queries.
    if errors:
        data["error"] = "; ".join(errors)
    return source, data


def _safe_collect(
    source: str,
    collector: Callable[[str, str, str], dict[str, Any]],
    topic: str,
    location: str,
    query: str,
) -> dict[str, Any]:
    try:
        return collector(topic, location, query)
    except SerpApiError as exc:
        return {"source": source, "query": query, "results": [], "error": str(exc)}
    except Exception:
        # Deliberately do not expose internal exception details through the public API.
        return {"source": source, "query": query, "results": [], "error": f"Unable to retrieve {source} results"}
