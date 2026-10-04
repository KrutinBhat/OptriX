
"""
OptriX AI Intelligence Layer
Module: query_planner.py

Purpose:
    Build structured, source-specific research query plans for
    market opportunity intelligence.

Supported research sources:
    Google Search, News, Jobs, Maps, Shopping, Scholar.

Responsibilities:
    - Validate research inputs.
    - Normalize topic and location.
    - Generate targeted search queries.
    - Remove duplicate queries.
    - Apply configurable per-source limits.
    - Return a serializable query plan.

This module does not call external APIs.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass
from typing import Final, Literal

logger = logging.getLogger(__name__)

ResearchSource = Literal[
    "search",
    "news",
    "jobs",
    "maps",
    "shopping",
    "scholar",
]

SUPPORTED_SOURCES: Final[tuple[ResearchSource, ...]] = (
    "search",
    "news",
    "jobs",
    "maps",
    "shopping",
    "scholar",
)

DEFAULT_MAX_QUERIES: Final[int] = 3
MAX_QUERY_LENGTH: Final[int] = 300
MAX_TOPIC_LENGTH: Final[int] = 200
MAX_LOCATION_LENGTH: Final[int] = 120


class QueryPlanningError(ValueError):
    """Raised when a valid research plan cannot be constructed."""


@dataclass(frozen=True, slots=True)
class QueryPlanItem:
    """A single source-specific query."""

    source: ResearchSource
    query: str
    purpose: str
    priority: int

    def to_dict(self) -> dict[str, str | int]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QueryPlan:
    """Complete research plan for a topic and location."""

    topic: str
    location: str
    objective: str
    queries: tuple[QueryPlanItem, ...]

    @property
    def total_queries(self) -> int:
        return len(self.queries)

    def queries_for(
        self,
        source: ResearchSource,
    ) -> list[str]:
        """Return all queries assigned to one source."""
        return [
            item.query
            for item in self.queries
            if item.source == source
        ]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible plan."""
        return {
            "topic": self.topic,
            "location": self.location,
            "objective": self.objective,
            "total_queries": self.total_queries,
            "queries": [
                item.to_dict()
                for item in self.queries
            ],
        }


class QueryPlanner:
    """
    Generate deterministic research queries for OptriX.

    Parameters
    ----------
    max_queries_per_source:
        Maximum number of queries generated for each source.

    include_global_queries:
        Whether to generate selected queries without a geographic
        qualifier. This is useful when a location-specific search
        needs broader market context.
    """

    def __init__(
        self,
        max_queries_per_source: int = DEFAULT_MAX_QUERIES,
        include_global_queries: bool = True,
    ) -> None:
        if (
            isinstance(max_queries_per_source, bool)
            or not isinstance(max_queries_per_source, int)
            or not 1 <= max_queries_per_source <= 10
        ):
            raise QueryPlanningError(
                "max_queries_per_source must be an integer "
                "between 1 and 10."
            )

        self.max_queries_per_source = max_queries_per_source
        self.include_global_queries = bool(
            include_global_queries
        )

    def plan(
        self,
        topic: str,
        location: str,
        objective: str = "market_opportunity",
    ) -> QueryPlan:
        """
        Generate a complete research plan.

        Parameters
        ----------
        topic:
            Product, industry, technology, or market being studied.

        location:
            Target geography, such as India or Bengaluru, India.

        objective:
            One of:
                market_opportunity
                demand_analysis
                competitor_analysis
                supplier_discovery
                technology_trends

        Returns
        -------
        QueryPlan
            Structured, serializable research plan.
        """

        normalized_topic = self._validate_text(
            topic,
            field_name="topic",
            max_length=MAX_TOPIC_LENGTH,
        )

        normalized_location = self._validate_text(
            location,
            field_name="location",
            max_length=MAX_LOCATION_LENGTH,
        )

        normalized_objective = self._normalize_objective(
            objective
        )

        logger.info(
            "Planning research queries for topic=%r, location=%r",
            normalized_topic,
            normalized_location,
        )

        templates = self._build_templates(
            topic=normalized_topic,
            location=normalized_location,
            objective=normalized_objective,
        )

        plan_items: list[QueryPlanItem] = []

        for source in SUPPORTED_SOURCES:
            candidates = templates[source]

            unique_queries = self._deduplicate(
                candidates
            )

            for priority, (query, purpose) in enumerate(
                unique_queries[
                    :self.max_queries_per_source
                ],
                start=1,
            ):
                plan_items.append(
                    QueryPlanItem(
                        source=source,
                        query=query,
                        purpose=purpose,
                        priority=priority,
                    )
                )

        if not plan_items:
            raise QueryPlanningError(
                "The planner generated no research queries."
            )

        logger.info(
            "Generated %d research queries across %d sources.",
            len(plan_items),
            len(SUPPORTED_SOURCES),
        )

        return QueryPlan(
            topic=normalized_topic,
            location=normalized_location,
            objective=normalized_objective,
            queries=tuple(plan_items),
        )

    def _build_templates(
        self,
        topic: str,
        location: str,
        objective: str,
    ) -> dict[ResearchSource, list[tuple[str, str]]]:
        """
        Create candidate queries for each supported source.

        Query wording is adapted to the requested research objective.
        """

        geo = location
        global_context = ""

        if self.include_global_queries:
            global_context = " global market"

        objective_terms: dict[str, list[str]] = {
            "market_opportunity": [
                "market opportunities",
                "industry trends",
                "unmet needs",
            ],
            "demand_analysis": [
                "market demand",
                "customer requirements",
                "industry adoption",
            ],
            "competitor_analysis": [
                "competitors",
                "market leaders",
                "competitive landscape",
            ],
            "supplier_discovery": [
                "manufacturers and suppliers",
                "distributors",
                "component vendors",
            ],
            "technology_trends": [
                "technology trends",
                "research developments",
                "emerging technologies",
            ],
        }

        terms = objective_terms[objective]

        queries: dict[
            ResearchSource,
            list[tuple[str, str]],
        ] = {
            "search": [
                (
                    f"{topic} {terms[0]} {geo}",
                    "Identify broad market evidence.",
                ),
                (
                    f"{topic} manufacturers suppliers {geo}",
                    "Identify existing suppliers and market participants.",
                ),
                (
                    f"{topic} {terms[2]}{global_context}",
                    "Identify unmet needs and broader market context.",
                ),
            ],
            "news": [
                (
                    f"{topic} industry developments {geo}",
                    "Find recent industry developments.",
                ),
                (
                    f"{topic} market investment expansion",
                    "Identify investment and expansion activity.",
                ),
                (
                    f"{topic} industry challenges regulations",
                    "Identify risks and industry challenges.",
                ),
            ],
            "jobs": [
                (
                    f"{topic} jobs engineers {geo}",
                    "Identify professional hiring activity.",
                ),
                (
                    f"{topic} skills hiring demand {geo}",
                    "Identify skill and workforce requirements.",
                ),
                (
                    f"{topic} careers industry",
                    "Identify broader industry workforce activity.",
                ),
            ],
            "maps": [
                (
                    f"{topic} suppliers {geo}",
                    "Identify local suppliers and businesses.",
                ),
                (
                    f"{topic} manufacturers {geo}",
                    "Identify local manufacturing presence.",
                ),
                (
                    f"{topic} distributors service providers {geo}",
                    "Identify regional distribution and service providers.",
                ),
            ],
            "shopping": [
                (
                    f"{topic} products",
                    "Identify commercial product listings.",
                ),
                (
                    f"{topic} price comparison",
                    "Identify visible pricing and product alternatives.",
                ),
                (
                    f"{topic} alternatives brands",
                    "Identify competing products and brands.",
                ),
            ],
            "scholar": [
                (
                    f"{topic} research publications",
                    "Identify relevant academic research.",
                ),
                (
                    f"{topic} emerging technologies",
                    "Identify research on emerging technology.",
                ),
                (
                    f"{topic} review survey challenges",
                    "Identify research reviews and documented challenges.",
                ),
            ],
        }

        # Ensure the objective's primary term is included in each
        # source's initial query when appropriate.
        if objective == "competitor_analysis":
            queries["search"][0] = (
                f"{topic} competitors {geo}",
                "Identify competitors and market participants.",
            )

        elif objective == "supplier_discovery":
            queries["search"][0] = (
                f"{topic} suppliers manufacturers {geo}",
                "Identify potential suppliers.",
            )

        elif objective == "technology_trends":
            queries["scholar"][0] = (
                f"{topic} technology research trends",
                "Identify technology research trends.",
            )

        return queries

    @staticmethod
    def _validate_text(
        value: str,
        field_name: str,
        max_length: int,
    ) -> str:
        """Validate and normalize a required string."""

        if not isinstance(value, str):
            raise QueryPlanningError(
                f"{field_name} must be a string."
            )

        normalized = re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

        if not normalized:
            raise QueryPlanningError(
                f"{field_name} cannot be empty."
            )

        if len(normalized) > max_length:
            raise QueryPlanningError(
                f"{field_name} cannot exceed "
                f"{max_length} characters."
            )

        if any(ord(char) < 32 for char in normalized):
            raise QueryPlanningError(
                f"{field_name} contains invalid control characters."
            )

        return normalized

    @staticmethod
    def _normalize_objective(
        objective: str,
    ) -> str:
        """Validate supported research objectives."""

        allowed = {
            "market_opportunity",
            "demand_analysis",
            "competitor_analysis",
            "supplier_discovery",
            "technology_trends",
        }

        if not isinstance(objective, str):
            raise QueryPlanningError(
                "objective must be a string."
            )

        normalized = objective.strip().lower()

        if normalized not in allowed:
            raise QueryPlanningError(
                "Unsupported research objective. "
                f"Choose one of: {', '.join(sorted(allowed))}."
            )

        return normalized

    @staticmethod
    def _deduplicate(
        candidates: list[tuple[str, str]],
    ) -> list[tuple[str, str]]:
        """Remove duplicate queries while preserving their order."""

        seen: set[str] = set()
        unique: list[tuple[str, str]] = []

        for query, purpose in candidates:
            cleaned_query = re.sub(
                r"\s+",
                " ",
                query,
            ).strip()

            if not cleaned_query:
                continue

            if len(cleaned_query) > MAX_QUERY_LENGTH:
                cleaned_query = cleaned_query[
                    :MAX_QUERY_LENGTH
                ].rstrip()

            key = cleaned_query.casefold()

            if key in seen:
                continue

            seen.add(key)
            unique.append(
                (cleaned_query, purpose)
            )

        return unique


def plan_research(
    topic: str,
    location: str,
    objective: str = "market_opportunity",
    max_queries_per_source: int = DEFAULT_MAX_QUERIES,
) -> dict[str, object]:
    """
    Convenience function for other OptriX modules.

    Returns a JSON-compatible dictionary.
    """

    planner = QueryPlanner(
        max_queries_per_source=max_queries_per_source,
    )

    return planner.plan(
        topic=topic,
        location=location,
        objective=objective,
    ).to_dict()