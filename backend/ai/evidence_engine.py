"""
OptriX AI Intelligence Layer
Module: evidence_engine.py

Purpose:
    Build a traceable evidence ledger from normalized market
    research records.

Responsibilities:
    - Validate and normalize evidence records.
    - Deduplicate evidence.
    - Group evidence by source and category.
    - Track source diversity and evidence coverage.
    - Link evidence to resolved entities.
    - Produce explainable evidence summaries.

Important:
    This module measures evidence coverage and data quality.
    It does not determine whether a source claim is objectively true.
"""

from __future__ import annotations

import hashlib
import logging
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .entity_resolution import EntityResolver

logger = logging.getLogger(__name__)

SUPPORTED_SOURCES = {
    "search",
    "news",
    "jobs",
    "maps",
    "shopping",
    "scholar",
}


class EvidenceEngineError(ValueError):
    """Raised when evidence processing receives invalid data."""


@dataclass(slots=True)
class EvidenceRecord:
    """Canonical evidence record stored in the evidence ledger."""

    evidence_id: str
    source: str
    category: str
    claim: str
    title: str
    url: str | None
    domain: str | None
    entity_id: str | None
    entity_name: str | None
    quality_score: int
    observed_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(slots=True)
class EvidenceSummary:
    """Summary statistics for an evidence ledger."""

    total_records: int
    unique_claims: int
    source_count: int
    category_count: int
    source_counts: dict[str, int]
    category_counts: dict[str, int]
    average_quality_score: float
    coverage_score: int
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


class EvidenceEngine:
    """
    Build and analyze a traceable evidence ledger.

    Parameters
    ----------
    minimum_quality_score:
        Minimum completeness score accepted into the ledger.
        0 means all valid records are retained.
    """

    def __init__(
        self,
        minimum_quality_score: int = 0,
    ) -> None:
        if (
            isinstance(minimum_quality_score, bool)
            or not isinstance(minimum_quality_score, int)
            or not 0 <= minimum_quality_score <= 100
        ):
            raise EvidenceEngineError(
                "minimum_quality_score must be an integer "
                "between 0 and 100."
            )

        self.minimum_quality_score = minimum_quality_score

    # ==============================================================
    # PUBLIC API
    # ==============================================================

    def build_ledger(
        self,
        extracted_evidence: Sequence[Mapping[str, Any]],
        resolved_entities: Sequence[Mapping[str, Any]] | None = None,
    ) -> list[EvidenceRecord]:
        """
        Build a validated and deduplicated evidence ledger.

        Parameters
        ----------
        extracted_evidence:
            Evidence records produced by EvidenceExtractor.

        resolved_entities:
            Entities produced by EntityResolver.

        Returns
        -------
        list[EvidenceRecord]
            Normalized evidence records with entity IDs attached
            whenever a reliable entity match exists.
        """

        if isinstance(
            extracted_evidence,
            (str, bytes, bytearray),
        ):
            raise EvidenceEngineError(
                "extracted_evidence must be a sequence of mappings."
            )

        if not isinstance(extracted_evidence, Sequence):
            raise EvidenceEngineError(
                "extracted_evidence must be a sequence."
            )

        entity_index = self._build_entity_index(
            resolved_entities or []
        )

        ledger: list[EvidenceRecord] = []
        seen_ids: set[str] = set()

        for item in extracted_evidence:
            if not isinstance(item, Mapping):
                logger.warning(
                    "Skipping non-mapping evidence record."
                )
                continue

            record = self._normalize_record(item)

            if record is None:
                continue

            if record.quality_score < self.minimum_quality_score:
                continue

            # Protect against duplicate records.
            if record.evidence_id in seen_ids:
                continue

            seen_ids.add(record.evidence_id)

            # Attach resolved entity if possible.
            record.entity_id = self._match_entity(
                record,
                entity_index,
            )

            ledger.append(record)

        logger.info(
            "Evidence ledger built: %d records.",
            len(ledger),
        )

        return ledger

    def summarize(
        self,
        ledger: Sequence[EvidenceRecord],
    ) -> EvidenceSummary:
        """
        Generate evidence coverage statistics.

        coverage_score is a research-coverage heuristic.
        It is NOT a probability that the underlying claims are true.
        """

        if isinstance(
            ledger,
            (str, bytes, bytearray),
        ):
            raise EvidenceEngineError(
                "ledger must be a sequence of EvidenceRecord objects."
            )

        if not isinstance(ledger, Sequence):
            raise EvidenceEngineError(
                "ledger must be a sequence."
            )

        valid_records = [
            record
            for record in ledger
            if isinstance(record, EvidenceRecord)
        ]

        source_counts = Counter(
            record.source
            for record in valid_records
        )

        category_counts = Counter(
            record.category
            for record in valid_records
        )

        unique_claims = {
            self._normalize_claim(record.claim)
            for record in valid_records
            if record.claim.strip()
        }

        if valid_records:
            average_quality = (
                sum(
                    record.quality_score
                    for record in valid_records
                )
                / len(valid_records)
            )
        else:
            average_quality = 0.0

        supported_source_count = len(
            set(source_counts.keys()).intersection(
                SUPPORTED_SOURCES
            )
        )

        source_coverage = (
            supported_source_count
            / len(SUPPORTED_SOURCES)
            * 100
        )

        # Coverage score combines:
        #
        #   60% source diversity
        #   40% evidence completeness
        #
        # This measures research coverage, not truth probability.
        coverage_score = round(
            (source_coverage * 0.60)
            + (average_quality * 0.40)
        )

        coverage_score = max(
            0,
            min(100, coverage_score),
        )

        return EvidenceSummary(
            total_records=len(valid_records),
            unique_claims=len(unique_claims),
            source_count=len(source_counts),
            category_count=len(category_counts),
            source_counts=dict(source_counts),
            category_counts=dict(category_counts),
            average_quality_score=round(
                average_quality,
                2,
            ),
            coverage_score=coverage_score,
            generated_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    def group_by_category(
        self,
        ledger: Sequence[EvidenceRecord],
    ) -> dict[str, list[dict[str, Any]]]:
        """Group evidence records by evidence category."""

        grouped: dict[
            str,
            list[dict[str, Any]],
        ] = defaultdict(list)

        for record in ledger:
            if not isinstance(record, EvidenceRecord):
                continue

            grouped[record.category].append(
                record.to_dict()
            )

        return dict(grouped)

    def group_by_source(
        self,
        ledger: Sequence[EvidenceRecord],
    ) -> dict[str, list[dict[str, Any]]]:
        """Group evidence records by original research source."""

        grouped: dict[
            str,
            list[dict[str, Any]],
        ] = defaultdict(list)

        for record in ledger:
            if not isinstance(record, EvidenceRecord):
                continue

            grouped[record.source].append(
                record.to_dict()
            )

        return dict(grouped)

    def find_entity_evidence(
        self,
        ledger: Sequence[EvidenceRecord],
        entity_id: str,
    ) -> list[EvidenceRecord]:
        """Return all evidence linked to a specific entity."""

        if (
            not isinstance(entity_id, str)
            or not entity_id.strip()
        ):
            raise EvidenceEngineError(
                "entity_id must be a non-empty string."
            )

        return [
            record
            for record in ledger
            if (
                isinstance(record, EvidenceRecord)
                and record.entity_id == entity_id
            )
        ]

    # ==============================================================
    # RECORD NORMALIZATION
    # ==============================================================

    @staticmethod
    def _normalize_record(
        item: Mapping[str, Any],
    ) -> EvidenceRecord | None:
        """Validate and normalize one evidence record."""

        source = item.get("source")
        claim = item.get("claim")

        if not isinstance(source, str):
            logger.warning(
                "Skipping evidence record without valid source."
            )
            return None

        source = source.strip().lower()

        if source not in SUPPORTED_SOURCES:
            logger.warning(
                "Skipping unsupported evidence source: %s",
                source,
            )
            return None

        if not isinstance(claim, str) or not claim.strip():
            logger.warning(
                "Skipping evidence record without claim."
            )
            return None

        evidence_id = item.get("evidence_id")

        if (
            not isinstance(evidence_id, str)
            or not evidence_id.strip()
        ):
            evidence_id = EvidenceEngine._make_id(
                source=source,
                claim=claim,
                url=item.get("url"),
            )

        category = item.get(
            "category",
            "uncategorized",
        )

        if not isinstance(category, str):
            category = "uncategorized"

        title = item.get("title", "")

        if not isinstance(title, str):
            title = ""

        url = item.get("url")

        if not isinstance(url, str):
            url = None

        domain = item.get("domain")

        if not isinstance(domain, str):
            domain = None

        entity_name = item.get("entity_name")

        if not isinstance(entity_name, str):
            entity_name = None

        quality_score = item.get(
            "quality_score",
            0,
        )

        if (
            isinstance(quality_score, bool)
            or not isinstance(
                quality_score,
                (int, float),
            )
        ):
            quality_score = 0

        quality_score = max(
            0,
            min(
                100,
                round(float(quality_score)),
            ),
        )

        observed_at = item.get(
            "observed_at"
        )

        if not isinstance(observed_at, str):
            observed_at = datetime.now(
                timezone.utc
            ).isoformat()

        # Preserve all fields that are not explicitly represented
        # by EvidenceRecord.
        known_fields = {
            "evidence_id",
            "source",
            "category",
            "claim",
            "title",
            "url",
            "domain",
            "entity_id",
            "entity_name",
            "quality_score",
            "observed_at",
        }

        metadata = {
            key: value
            for key, value in item.items()
            if key not in known_fields
        }

        return EvidenceRecord(
            evidence_id=evidence_id.strip(),
            source=source,
            category=category.strip(),
            claim=claim.strip(),
            title=title.strip(),
            url=url.strip() if url else None,
            domain=domain.strip().lower()
            if domain
            else None,
            entity_id=None,
            entity_name=(
                entity_name.strip()
                if entity_name
                else None
            ),
            quality_score=quality_score,
            observed_at=observed_at,
            metadata=metadata,
        )

    # ==============================================================
    # ENTITY LINKING
    # ==============================================================

    @staticmethod
    def _build_entity_index(
        entities: Sequence[Mapping[str, Any]],
    ) -> dict[str, str]:
        """
        Build a normalized entity-name -> entity-ID index.

        The exact same EntityResolver normalization is used here
        and when matching evidence. This prevents mismatches such as:

            "ABC Technologies Pvt Ltd"
                vs
            "ABC Technologies"
        """

        index: dict[str, str] = {}

        if isinstance(
            entities,
            (str, bytes, bytearray),
        ):
            return index

        for entity in entities:
            if not isinstance(entity, Mapping):
                continue

            entity_id = entity.get(
                "entity_id"
            )

            if not isinstance(entity_id, str):
                continue

            # Prefer the already-normalized field generated by
            # EntityResolver.
            normalized_name = entity.get(
                "normalized_name"
            )

            if not isinstance(
                normalized_name,
                str,
            ):
                # Fall back to canonical display name.
                normalized_name = entity.get(
                    "canonical_name",
                    "",
                )

            if not isinstance(
                normalized_name,
                str,
            ):
                continue

            if not normalized_name.strip():
                continue

            canonical_name = (
                EntityResolver.normalize_name(
                    normalized_name
                )
            )

            if not canonical_name:
                continue

            index[
                canonical_name.casefold()
            ] = entity_id

        return index

    @staticmethod
    def _match_entity(
        record: EvidenceRecord,
        entity_index: Mapping[str, str],
    ) -> str | None:
        """
        Link evidence to a resolved entity.

        Uses EntityResolver's normalization rules so entity names
        are compared consistently across the entire AI pipeline.
        """

        if not record.entity_name:
            return None

        normalized_name = (
            EntityResolver.normalize_name(
                record.entity_name
            )
        )

        if not normalized_name:
            return None

        return entity_index.get(
            normalized_name.casefold()
        )

    # ==============================================================
    # UTILITIES
    # ==============================================================

    @staticmethod
    def _normalize_claim(
        claim: str,
    ) -> str:
        """Normalize claim text for duplicate detection."""

        return " ".join(
            claim.casefold().split()
        )

    @staticmethod
    def _make_id(
        source: str,
        claim: str,
        url: Any,
    ) -> str:
        """
        Generate a deterministic evidence ID.

        The ID contains no source text and is only a hash-derived
        internal identifier.
        """

        identity = "|".join(
            (
                source.casefold().strip(),
                claim.casefold().strip(),
                str(url or "").strip().casefold(),
            )
        )

        digest = hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:20]

        return f"ev_{digest}"


def build_evidence(
    extracted_evidence: Sequence[Mapping[str, Any]],
    resolved_entities: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Convenience function for building an evidence response.

    Returns
    -------
    dict
        {
            "evidence": [...],
            "summary": {...}
        }
    """

    engine = EvidenceEngine()

    ledger = engine.build_ledger(
        extracted_evidence=extracted_evidence,
        resolved_entities=resolved_entities,
    )

    summary = engine.summarize(
        ledger
    )

    return {
        "evidence": [
            record.to_dict()
            for record in ledger
        ],
        "summary": summary.to_dict(),
    }


__all__ = [
    "EvidenceEngine",
    "EvidenceEngineError",
    "EvidenceRecord",
    "EvidenceSummary",
    "build_evidence",
]