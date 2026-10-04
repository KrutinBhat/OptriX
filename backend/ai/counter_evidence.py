
"""
OptriX AI Intelligence Layer
Module: counter_evidence.py

Purpose:
    Identify evidence limitations, contradictory market indicators,
    and potential risks that should qualify opportunity analysis.

Responsibilities:
    - Evaluate evidence coverage.
    - Detect source concentration.
    - Identify weak evidence support.
    - Compare market signal directions.
    - Flag stale or undated evidence.
    - Produce explainable counter-evidence findings.

Counter-evidence findings are analytical caveats.
They are not proof that an opportunity will fail.
"""

from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

SUPPORTED_SOURCES = {
    "search",
    "news",
    "jobs",
    "maps",
    "shopping",
    "scholar",
}

DEFAULT_STALE_AFTER_DAYS = 365


class CounterEvidenceError(ValueError):
    """Raised for invalid counter-evidence inputs."""


@dataclass(slots=True)
class CounterEvidenceFinding:
    """One explainable limitation or contradictory finding."""

    finding_id: str
    category: str
    severity: str
    title: str
    description: str
    affected_signals: list[str]
    evidence_ids: list[str]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CounterEvidenceEngine:
    """
    Identify counter-evidence and research limitations.

    Parameters
    ----------
    stale_after_days:
        Evidence older than this number of days may be flagged.

    minimum_independent_sources:
        Minimum number of distinct source categories expected
        before considering an evidence base broadly supported.
    """

    def __init__(
        self,
        stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
        minimum_independent_sources: int = 3,
    ) -> None:
        if (
            isinstance(stale_after_days, bool)
            or not isinstance(stale_after_days, int)
            or stale_after_days < 1
        ):
            raise CounterEvidenceError(
                "stale_after_days must be a positive integer."
            )

        if (
            isinstance(minimum_independent_sources, bool)
            or not isinstance(minimum_independent_sources, int)
            or minimum_independent_sources < 1
        ):
            raise CounterEvidenceError(
                "minimum_independent_sources must be "
                "a positive integer."
            )

        self.stale_after_days = stale_after_days
        self.minimum_independent_sources = (
            minimum_independent_sources
        )

    def analyze(
        self,
        evidence: Sequence[Mapping[str, Any]],
        signals: Mapping[str, Any] | None = None,
        opportunities: Sequence[Mapping[str, Any]] | None = None,
    ) -> list[CounterEvidenceFinding]:
        """
        Analyze an evidence ledger and optional market signals.

        Parameters
        ----------
        evidence:
            Extracted evidence or evidence-engine ledger records.

        signals:
            SignalEngine output, such as demand, supply_gap,
            competition, and momentum.

        opportunities:
            Optional opportunity candidates.

        Returns
        -------
        list[CounterEvidenceFinding]
            Explainable findings sorted by severity.
        """

        if isinstance(evidence, (str, bytes, bytearray)):
            raise CounterEvidenceError(
                "evidence must be a sequence of mappings."
            )

        if not isinstance(evidence, Sequence):
            raise CounterEvidenceError(
                "evidence must be a sequence."
            )

        valid_evidence = [
            item
            for item in evidence
            if isinstance(item, Mapping)
        ]

        normalized_signals = (
            signals
            if isinstance(signals, Mapping)
            else {}
        )

        valid_opportunities = (
            [
                item
                for item in opportunities
                if isinstance(item, Mapping)
            ]
            if isinstance(opportunities, Sequence)
            and not isinstance(
                opportunities,
                (str, bytes, bytearray),
            )
            else []
        )

        findings: list[CounterEvidenceFinding] = []

        findings.extend(
            self._check_evidence_volume(
                valid_evidence
            )
        )

        findings.extend(
            self._check_source_diversity(
                valid_evidence
            )
        )

        findings.extend(
            self._check_source_concentration(
                valid_evidence
            )
        )

        findings.extend(
            self._check_evidence_quality(
                valid_evidence
            )
        )

        findings.extend(
            self._check_stale_evidence(
                valid_evidence
            )
        )

        findings.extend(
            self._check_signal_conflicts(
                normalized_signals
            )
        )

        findings.extend(
            self._check_opportunity_support(
                valid_opportunities
            )
        )

        # Deterministic ordering: severity first, then finding ID.
        severity_order = {
            "high": 0,
            "medium": 1,
            "low": 2,
            "informational": 3,
        }

        findings.sort(
            key=lambda item: (
                severity_order.get(
                    item.severity,
                    4,
                ),
                item.finding_id,
            )
        )

        logger.info(
            "Counter-evidence analysis completed: %d findings.",
            len(findings),
        )

        return findings

    # ---------------------------------------------------------------
    # EVIDENCE VOLUME
    # ---------------------------------------------------------------

    def _check_evidence_volume(
        self,
        evidence: Sequence[Mapping[str, Any]],
    ) -> list[CounterEvidenceFinding]:
        if evidence:
            return []

        return [
            CounterEvidenceFinding(
                finding_id="ce_no_evidence",
                category="evidence_gap",
                severity="high",
                title="No supporting evidence collected",
                description=(
                    "The research run contains no usable evidence "
                    "records. Market conclusions cannot be supported "
                    "by the current dataset."
                ),
                affected_signals=[],
                evidence_ids=[],
                recommendation=(
                    "Retry research collection, verify the source "
                    "configuration, and obtain relevant evidence "
                    "before evaluating opportunities."
                ),
            )
        ]

    # ---------------------------------------------------------------
    # SOURCE DIVERSITY AND CONCENTRATION
    # ---------------------------------------------------------------

    def _check_source_diversity(
        self,
        evidence: Sequence[Mapping[str, Any]],
    ) -> list[CounterEvidenceFinding]:
        source_names = {
            str(item.get("source", "")).strip().lower()
            for item in evidence
            if item.get("source")
        }

        source_names.intersection_update(
            SUPPORTED_SOURCES
        )

        if (
            len(source_names)
            >= self.minimum_independent_sources
        ):
            return []

        return [
            CounterEvidenceFinding(
                finding_id="ce_low_source_diversity",
                category="source_coverage",
                severity="medium",
                title="Limited source diversity",
                description=(
                    f"Evidence is available from "
                    f"{len(source_names)} supported source "
                    f"category or categories. The configured "
                    f"minimum is "
                    f"{self.minimum_independent_sources}. "
                    "This limits cross-source corroboration."
                ),
                affected_signals=[],
                evidence_ids=[
                    str(item.get("evidence_id"))
                    for item in evidence
                    if item.get("evidence_id")
                ],
                recommendation=(
                    "Collect additional evidence from independent "
                    "research channels before treating the findings "
                    "as broadly corroborated."
                ),
            )
        ]

    def _check_source_concentration(
        self,
        evidence: Sequence[Mapping[str, Any]],
    ) -> list[CounterEvidenceFinding]:
        if len(evidence) < 2:
            return []

        counts = Counter(
            str(item.get("source", "unknown")).lower()
            for item in evidence
        )

        total = sum(counts.values())

        if total == 0:
            return []

        dominant_source, dominant_count = counts.most_common(1)[0]

        concentration = dominant_count / total

        if concentration < 0.80:
            return []

        return [
            CounterEvidenceFinding(
                finding_id="ce_source_concentration",
                category="source_concentration",
                severity="medium",
                title="Evidence concentrated in one source",
                description=(
                    f"{concentration:.0%} of evidence records "
                    f"come from '{dominant_source}'. The findings "
                    "may reflect the coverage or ranking behavior "
                    "of that source rather than the complete market."
                ),
                affected_signals=[],
                evidence_ids=[
                    str(item.get("evidence_id"))
                    for item in evidence
                    if (
                        str(item.get("source", "")).lower()
                        == dominant_source
                        and item.get("evidence_id")
                    )
                ],
                recommendation=(
                    "Seek independent evidence from other source "
                    "categories and avoid interpreting repeated "
                    "listings as independent market confirmation."
                ),
            )
        ]

    # ---------------------------------------------------------------
    # EVIDENCE QUALITY
    # ---------------------------------------------------------------

    def _check_evidence_quality(
        self,
        evidence: Sequence[Mapping[str, Any]],
    ) -> list[CounterEvidenceFinding]:
        if not evidence:
            return []

        scores: list[float] = []

        for item in evidence:
            score = item.get("quality_score", 0)

            if (
                isinstance(score, bool)
                or not isinstance(score, (int, float))
            ):
                continue

            scores.append(
                max(0.0, min(100.0, float(score)))
            )

        if not scores:
            return []

        average = sum(scores) / len(scores)

        if average >= 40:
            return []

        return [
            CounterEvidenceFinding(
                finding_id="ce_low_quality",
                category="evidence_quality",
                severity="medium",
                title="Low evidence completeness",
                description=(
                    f"The average evidence completeness score "
                    f"is {average:.1f}/100. Records may lack "
                    "descriptive text, source links, or other "
                    "useful attribution fields."
                ),
                affected_signals=[],
                evidence_ids=[
                    str(item.get("evidence_id"))
                    for item in evidence
                    if item.get("evidence_id")
                ],
                recommendation=(
                    "Improve source collection and retain original "
                    "URLs, titles, descriptive text, and publication "
                    "dates wherever available."
                ),
            )
        ]

    # ---------------------------------------------------------------
    # TEMPORAL EVIDENCE
    # ---------------------------------------------------------------

    def _check_stale_evidence(
        self,
        evidence: Sequence[Mapping[str, Any]],
    ) -> list[CounterEvidenceFinding]:
        now = datetime.now(timezone.utc)

        stale_ids: list[str] = []
        undated_count = 0

        for item in evidence:
            raw_date = (
                item.get("publication_date")
                or item.get("date")
            )

            if not isinstance(raw_date, str) or not raw_date.strip():
                undated_count += 1
                continue

            parsed_date = self._parse_date(raw_date)

            # An unparseable date is treated as undated, not
            # automatically stale.
            if parsed_date is None:
                undated_count += 1
                continue

            age_days = (now - parsed_date).days

            if age_days > self.stale_after_days:
                evidence_id = item.get("evidence_id")

                if isinstance(evidence_id, str):
                    stale_ids.append(evidence_id)

        findings: list[CounterEvidenceFinding] = []

        if stale_ids:
            findings.append(
                CounterEvidenceFinding(
                    finding_id="ce_stale_evidence",
                    category="temporal_relevance",
                    severity="medium",
                    title="Some evidence may be outdated",
                    description=(
                        f"{len(stale_ids)} evidence record(s) "
                        f"are older than the configured "
                        f"{self.stale_after_days}-day threshold."
                    ),
                    affected_signals=[
                        "momentum",
                        "demand",
                        "competition",
                    ],
                    evidence_ids=stale_ids,
                    recommendation=(
                        "Refresh time-sensitive evidence and "
                        "distinguish current activity from "
                        "historical market context."
                    ),
                )
            )

        if evidence and undated_count / len(evidence) >= 0.50:
            findings.append(
                CounterEvidenceFinding(
                    finding_id="ce_undated_evidence",
                    category="temporal_relevance",
                    severity="low",
                    title="Publication dates are missing",
                    description=(
                        f"{undated_count} of {len(evidence)} "
                        "evidence records do not have a usable "
                        "publication date. Recency cannot be "
                        "established for these records."
                    ),
                    affected_signals=["momentum"],
                    evidence_ids=[
                        str(item.get("evidence_id"))
                        for item in evidence
                        if (
                            not item.get("publication_date")
                            and item.get("evidence_id")
                        )
                    ],
                    recommendation=(
                        "Retain publication timestamps from source "
                        "providers wherever available. Do not treat "
                        "collection time as publication time."
                    ),
                )
            )

        return findings

    @staticmethod
    def _parse_date(
        value: str,
    ) -> datetime | None:
        """Parse common ISO date formats without guessing."""

        normalized = value.strip()

        try:
            parsed = datetime.fromisoformat(
                normalized.replace("Z", "+00:00")
            )
        except ValueError:
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(timezone.utc)

    # ---------------------------------------------------------------
    # SIGNAL CONFLICTS
    # ---------------------------------------------------------------

    def _check_signal_conflicts(
        self,
        signals: Mapping[str, Any],
    ) -> list[CounterEvidenceFinding]:
        """
        Identify combinations of signals that warrant caution.

        Signal scores are heuristic indicators. These rules flag
        tensions for human review; they do not establish causation.
        """

        demand = self._signal_score(
            signals,
            "demand",
        )

        competition = self._signal_score(
            signals,
            "competition",
        )

        supply_gap = self._signal_score(
            signals,
            "supply_gap",
        )

        momentum = self._signal_score(
            signals,
            "momentum",
        )

        findings: list[CounterEvidenceFinding] = []

        if demand >= 70 and competition >= 70:
            findings.append(
                CounterEvidenceFinding(
                    finding_id="ce_high_demand_competition",
                    category="market_tension",
                    severity="medium",
                    title=(
                        "Demand signals coincide with "
                        "strong visible competition"
                    ),
                    description=(
                        "The demand indicator is high, but the "
                        "competition indicator is also high. "
                        "Demand alone does not establish that a "
                        "new entrant can acquire customers "
                        "profitably."
                    ),
                    affected_signals=[
                        "demand",
                        "competition",
                    ],
                    evidence_ids=[],
                    recommendation=(
                        "Investigate differentiation, customer "
                        "switching costs, pricing, margins, and "
                        "incumbent market positions."
                    ),
                )
            )

        if supply_gap >= 70 and demand < 40:
            findings.append(
                CounterEvidenceFinding(
                    finding_id="ce_supply_without_demand",
                    category="market_tension",
                    severity="medium",
                    title=(
                        "Potential supply gap has limited "
                        "demand support"
                    ),
                    description=(
                        "The supply-gap indicator is high while "
                        "the demand indicator is low. Limited "
                        "visible supply may reflect limited demand, "
                        "incomplete collection, or an actual gap."
                    ),
                    affected_signals=[
                        "supply_gap",
                        "demand",
                    ],
                    evidence_ids=[],
                    recommendation=(
                        "Validate customer needs, willingness to "
                        "pay, and unmet demand before interpreting "
                        "limited supply as a commercial opportunity."
                    ),
                )
            )

        if momentum >= 70 and demand < 40:
            findings.append(
                CounterEvidenceFinding(
                    finding_id="ce_momentum_without_demand",
                    category="market_tension",
                    severity="low",
                    title=(
                        "Market attention is not matched "
                        "by strong demand evidence"
                    ),
                    description=(
                        "News or other momentum indicators are "
                        "high, while the demand indicator is low. "
                        "Media attention does not necessarily "
                        "translate into customer purchases."
                    ),
                    affected_signals=[
                        "momentum",
                        "demand",
                    ],
                    evidence_ids=[],
                    recommendation=(
                        "Seek customer, purchasing, adoption, "
                        "and commercial evidence to validate "
                        "whether market attention corresponds "
                        "to real demand."
                    ),
                )
            )

        return findings

    # ---------------------------------------------------------------
    # OPPORTUNITY SUPPORT
    # ---------------------------------------------------------------

    def _check_opportunity_support(
        self,
        opportunities: Sequence[Mapping[str, Any]],
    ) -> list[CounterEvidenceFinding]:
        findings: list[CounterEvidenceFinding] = []

        for index, opportunity in enumerate(opportunities):
            title = opportunity.get(
                "title",
                f"Opportunity {index + 1}",
            )

            if not isinstance(title, str):
                title = f"Opportunity {index + 1}"

            evidence = opportunity.get(
                "supporting_evidence",
                [],
            )

            if not isinstance(evidence, list):
                evidence = []

            source_names = {
                str(item.get("source", "")).lower()
                for item in evidence
                if isinstance(item, Mapping)
                and item.get("source")
            }

            if len(source_names) >= 2:
                continue

            evidence_ids = [
                str(item.get("evidence_id"))
                for item in evidence
                if (
                    isinstance(item, Mapping)
                    and item.get("evidence_id")
                )
            ]

            findings.append(
                CounterEvidenceFinding(
                    finding_id=(
                        f"ce_opportunity_support_{index + 1}"
                    ),
                    category="opportunity_support",
                    severity="medium",
                    title=(
                        f"Limited independent support: {title}"
                    ),
                    description=(
                        "The opportunity has fewer than two "
                        "distinct source categories represented "
                        "in its supporting evidence. Its "
                        "supporting research may be incomplete."
                    ),
                    affected_signals=[],
                    evidence_ids=evidence_ids,
                    recommendation=(
                        "Collect additional independent evidence "
                        "before treating this opportunity as "
                        "well-corroborated."
                    ),
                )
            )

        return findings

    # ---------------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------------

    @staticmethod
    def _signal_score(
        signals: Mapping[str, Any],
        name: str,
    ) -> float:
        """Safely retrieve a 0-100 signal score."""

        signal = signals.get(name)

        if not isinstance(signal, Mapping):
            return 0.0

        score = signal.get("score", 0)

        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
        ):
            return 0.0

        return max(
            0.0,
            min(100.0, float(score)),
        )


def analyze_counter_evidence(
    evidence: Sequence[Mapping[str, Any]],
    signals: Mapping[str, Any] | None = None,
    opportunities: Sequence[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Convenience function returning serializable findings."""

    engine = CounterEvidenceEngine()

    findings = engine.analyze(
        evidence=evidence,
        signals=signals,
        opportunities=opportunities,
    )

    return [
        finding.to_dict()
        for finding in findings
    ]