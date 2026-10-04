
"""
OptriX AI Intelligence Layer
Module: extractor.py

Purpose:
    Transform heterogeneous SerpApi records into normalized,
    traceable market evidence.

Responsibilities:
    - Normalize source records.
    - Extract claims and descriptive text.
    - Preserve URLs and source attribution.
    - Extract explicit numeric prices and counts where present.
    - Assign evidence categories and quality indicators.
    - Reject malformed records safely.

This module is a deterministic extraction component.
It does not generate unsupported facts or financial forecasts.
"""

from __future__ import annotations

import hashlib
import logging
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

SUPPORTED_SOURCES = {
    "search",
    "news",
    "jobs",
    "maps",
    "shopping",
    "scholar",
}

SOURCE_CATEGORIES = {
    "search": "market_interest",
    "news": "market_momentum",
    "jobs": "professional_demand",
    "maps": "local_supply",
    "shopping": "commercial_activity",
    "scholar": "technology_activity",
}

MAX_TEXT_LENGTH = 10_000
MAX_RECORDS_PER_SOURCE = 10_000


class ExtractionError(ValueError):
    """Raised when evidence extraction receives invalid input."""


@dataclass(slots=True)
class ExtractedEvidence:
    """Standardized evidence extracted from one source record."""

    evidence_id: str
    source: str
    category: str
    claim: str
    title: str
    snippet: str
    url: str | None
    domain: str | None
    observed_at: str
    publication_date: str | None
    entity_name: str | None
    location: str | None
    numeric_values: dict[str, float]
    source_position: int | None
    quality_score: int
    quality_reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvidenceExtractor:
    """
    Extract normalized evidence from SerpApi research responses.

    Parameters
    ----------
    max_records_per_source:
        Maximum number of records processed per source.
    """

    def __init__(
        self,
        max_records_per_source: int = MAX_RECORDS_PER_SOURCE,
    ) -> None:
        if (
            isinstance(max_records_per_source, bool)
            or not isinstance(max_records_per_source, int)
            or not 1 <= max_records_per_source <= 100_000
        ):
            raise ExtractionError(
                "max_records_per_source must be between "
                "1 and 100000."
            )

        self.max_records_per_source = (
            max_records_per_source
        )

    def extract(
        self,
        research_data: Mapping[str, Any],
    ) -> list[ExtractedEvidence]:
        """
        Extract evidence across all supported research sources.

        Input:
            {
                "search": {"results": [...]},
                "news": {"results": [...]},
                ...
            }

        Output:
            List of ExtractedEvidence objects.
        """

        if not isinstance(research_data, Mapping):
            raise ExtractionError(
                "research_data must be a mapping."
            )

        extracted: list[ExtractedEvidence] = []

        for source, source_data in research_data.items():
            normalized_source = str(source).strip().lower()

            if normalized_source not in SUPPORTED_SOURCES:
                logger.debug(
                    "Ignoring unsupported source: %s",
                    normalized_source,
                )
                continue

            if not isinstance(source_data, Mapping):
                logger.warning(
                    "Ignoring malformed source container: %s",
                    normalized_source,
                )
                continue

            records = source_data.get("results", [])

            if not isinstance(records, Sequence) or isinstance(
                records,
                (str, bytes, bytearray),
            ):
                logger.warning(
                    "Source '%s' has an invalid results collection.",
                    normalized_source,
                )
                continue

            if len(records) > self.max_records_per_source:
                logger.warning(
                    "Source '%s' exceeded extraction limit.",
                    normalized_source,
                )

            for record in records[
                :self.max_records_per_source
            ]:
                if not isinstance(record, Mapping):
                    continue

                evidence = self.extract_record(
                    source=normalized_source,
                    record=record,
                )

                if evidence is not None:
                    extracted.append(evidence)

        logger.info(
            "Extracted %d evidence records.",
            len(extracted),
        )

        return extracted

    def extract_record(
        self,
        source: str,
        record: Mapping[str, Any],
    ) -> ExtractedEvidence | None:
        """
        Extract one record into a standardized evidence object.
        """

        source = str(source).strip().lower()

        if source not in SUPPORTED_SOURCES:
            raise ExtractionError(
                f"Unsupported source: {source}"
            )

        if not isinstance(record, Mapping):
            return None

        title = self._first_text(
            record,
            ("title", "name", "product_name", "company_name"),
        )

        snippet = self._first_text(
            record,
            (
                "snippet",
                "description",
                "summary",
                "content",
                "details",
            ),
        )

        if not title and not snippet:
            return None

        title = title or "Untitled source record"
        snippet = snippet or ""

        claim = self._build_claim(
            title=title,
            snippet=snippet,
        )

        url = self._first_text(
            record,
            ("link", "url", "website", "website_url"),
        )

        domain = self._extract_domain(url)

        entity_name = self._first_text(
            record,
            (
                "company",
                "company_name",
                "business_name",
                "brand",
                "product_name",
            ),
        )

        location = self._first_text(
            record,
            (
                "address",
                "location",
                "city",
                "region",
            ),
        )

        publication_date = self._extract_publication_date(
            record
        )

        numeric_values = self._extract_numeric_values(
            record
        )

        position = self._safe_integer(
            record.get("position")
        )

        quality_score, quality_reasons = (
            self._calculate_quality(
                title=title,
                snippet=snippet,
                url=url,
                source=source,
            )
        )

        evidence_id = self._make_evidence_id(
            source=source,
            title=title,
            url=url,
            snippet=snippet,
        )

        return ExtractedEvidence(
            evidence_id=evidence_id,
            source=source,
            category=SOURCE_CATEGORIES[source],
            claim=claim,
            title=title,
            snippet=snippet,
            url=url,
            domain=domain,
            observed_at=datetime.now(
                timezone.utc
            ).isoformat(),
            publication_date=publication_date,
            entity_name=entity_name,
            location=location,
            numeric_values=numeric_values,
            source_position=position,
            quality_score=quality_score,
            quality_reasons=quality_reasons,
        )

    # ---------------------------------------------------------------
    # TEXT NORMALIZATION
    # ---------------------------------------------------------------

    @staticmethod
    def _first_text(
        record: Mapping[str, Any],
        fields: tuple[str, ...],
    ) -> str | None:
        """Extract the first valid textual field."""

        for field_name in fields:
            value = record.get(field_name)

            if not isinstance(value, str):
                continue

            cleaned = re.sub(
                r"\s+",
                " ",
                value,
            ).strip()

            if cleaned:
                return cleaned[:MAX_TEXT_LENGTH]

        return None

    @staticmethod
    def _build_claim(
        title: str,
        snippet: str,
    ) -> str:
        """
        Build a concise source-derived claim.

        This preserves the original wording rather than turning
        it into an unsupported factual assertion.
        """

        if not snippet:
            return title

        if title.casefold() in snippet.casefold():
            return snippet[:MAX_TEXT_LENGTH]

        return f"{title}. {snippet}"[:MAX_TEXT_LENGTH]

    @staticmethod
    def _extract_domain(
        url: str | None,
    ) -> str | None:
        """Extract the hostname from a source URL."""

        if not isinstance(url, str) or not url.strip():
            return None

        candidate = url.strip()

        if "://" not in candidate:
            candidate = "https://" + candidate

        try:
            hostname = urlparse(candidate).hostname
        except ValueError:
            return None

        if not hostname:
            return None

        hostname = hostname.casefold()

        hostname = hostname.removeprefix("www.")

        return hostname

    # ---------------------------------------------------------------
    # NUMERIC AND DATE EXTRACTION
    # ---------------------------------------------------------------

    @staticmethod
    def _safe_integer(
        value: Any,
    ) -> int | None:
        if isinstance(value, bool):
            return None

        if isinstance(value, int) and value >= 0:
            return value

        if isinstance(value, str) and value.isdigit():
            return int(value)

        return None

    @staticmethod
    def _extract_publication_date(
        record: Mapping[str, Any],
    ) -> str | None:
        """
        Extract an explicitly provided date.

        This method does not infer publication dates from the
        current date or from search-result position.
        """

        fields = (
            "date",
            "published_date",
            "publication_date",
            "date_published",
            "iso_date",
        )

        for field_name in fields:
            value = record.get(field_name)

            if not isinstance(value, str):
                continue

            value = value.strip()

            if not value:
                continue

            # Preserve the source date text. Parsing may be
            # source-specific, so no unverified conversion occurs.
            return value[:100]

        return None

    @staticmethod
    def _extract_numeric_values(
        record: Mapping[str, Any],
    ) -> dict[str, float]:
        """
        Extract explicit numeric values from common fields.

        Values are preserved under their original field names.
        No currency conversion or unit conversion is performed.
        """

        numeric_fields = {
            "price",
            "rating",
            "reviews",
            "review_count",
            "quantity",
            "position",
            "salary",
            "jobs_count",
            "number_of_employees",
        }

        numeric_values: dict[str, float] = {}

        for field_name in numeric_fields:
            value = record.get(field_name)

            if isinstance(value, bool):
                continue

            if isinstance(value, (int, float)):
                number = float(value)

                if number == number and abs(number) != float("inf"):  # noqa: PLR0124
                    numeric_values[field_name] = number

                continue

            if isinstance(value, str):
                # Only parse an explicit numeric token. For
                # currency strings, this records the number
                # without assuming a currency conversion.
                match = re.search(
                    r"[-+]?\d[\d,]*(?:\.\d+)?",
                    value,
                )

                if not match:
                    continue

                try:
                    number = float(
                        match.group(0).replace(",", "")
                    )
                except ValueError:
                    continue

                if number == number and abs(number) != float("inf"):  # noqa: PLR0124
                    numeric_values[field_name] = number

        return numeric_values

    # ---------------------------------------------------------------
    # EVIDENCE QUALITY
    # ---------------------------------------------------------------

    @staticmethod
    def _calculate_quality(
        title: str,
        snippet: str,
        url: str | None,
        source: str,
    ) -> tuple[int, list[str]]:
        """
        Calculate a transparent extraction completeness score.

        This is a data-quality indicator, not a probability that
        a claim is true.
        """

        score = 0
        reasons: list[str] = []

        if title and title != "Untitled source record":
            score += 30
            reasons.append("title_present")

        if snippet:
            score += 30
            reasons.append("descriptive_text_present")

        if url:
            score += 25
            reasons.append("source_url_present")

        if source in SUPPORTED_SOURCES:
            score += 15
            reasons.append("recognized_source")

        return min(100, score), reasons

    # ---------------------------------------------------------------
    # IDENTIFIERS AND SERIALIZATION
    # ---------------------------------------------------------------

    @staticmethod
    def _make_evidence_id(
        source: str,
        title: str,
        url: str | None,
        snippet: str,
    ) -> str:
        """Create a deterministic evidence identifier."""

        identity = "|".join(
            (
                source.casefold(),
                (url or "").casefold(),
                title.casefold().strip(),
                snippet.casefold().strip(),
            )
        )

        digest = hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:20]

        return f"ev_{digest}"


def extract_evidence(
    research_data: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Convenience function returning serializable evidence."""

    extractor = EvidenceExtractor()

    return [
        item.to_dict()
        for item in extractor.extract(research_data)
    ]