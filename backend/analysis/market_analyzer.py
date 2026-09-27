"""
OptriX Market Analyzer
=======================

Coordinates the existing market-analysis engines with the new
AI evidence layer.

Pipeline:

    Research Data
        |
        +--> EvidenceExtractor
        |
        +--> EntityResolver
        |
        +--> EvidenceEngine
        |
        +--> SignalEngine
        |
        +--> OpportunityEngine
        |
        +--> CounterEvidenceEngine
        |
        v
    Structured Market Analysis
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from backend.ai.counter_evidence import CounterEvidenceEngine
from backend.ai.entity_resolution import EntityResolver
from backend.ai.evidence_engine import EvidenceEngine
from backend.ai.extractor import EvidenceExtractor

from .opportunity_engine import OpportunityEngine
from .signal_engine import SignalEngine

logger = logging.getLogger(__name__)


class MarketAnalyzerError(Exception):
    """Raised when market analysis cannot be completed."""


class MarketAnalyzer:
    """
    Main orchestration layer for OptriX market analysis.

    This class deliberately preserves the existing contracts of:

        SignalEngine(research_data).analyze()

        OpportunityEngine(research_data).generate(signals)

    The new AI modules enrich the existing pipeline rather than
    replacing its scoring logic.
    """

    def __init__(
        self,
        research_data: Mapping[str, Any],
    ) -> None:
        if not isinstance(research_data, Mapping):
            raise MarketAnalyzerError(
                "research_data must be a mapping."
            )

        self.research_data = research_data

    def analyze(self) -> dict[str, Any]:
        """
        Run the complete OptriX market-analysis pipeline.

        Returns
        -------
        dict
            {
                "signals": ...,
                "opportunities": ...,
                "evidence": {
                    "records": [...],
                    "summary": {...}
                },
                "entities": [...],
                "counter_evidence": [...]
            }
        """

        logger.info(
            "Starting OptriX market analysis."
        )

        try:
            # -----------------------------------------------------
            # STEP 1 — Extract evidence
            # -----------------------------------------------------

            extracted_evidence = self._extract_evidence()

            logger.info(
                "Extracted %d evidence records.",
                len(extracted_evidence),
            )

            # -----------------------------------------------------
            # STEP 2 — Resolve entities
            # -----------------------------------------------------

            resolved_entities = self._resolve_entities()

            logger.info(
                "Resolved %d entities.",
                len(resolved_entities),
            )

            # -----------------------------------------------------
            # STEP 3 — Build evidence ledger
            # -----------------------------------------------------

            evidence_ledger, evidence_summary = (
                self._build_evidence_ledger(
                    extracted_evidence,
                    resolved_entities,
                )
            )

            logger.info(
                "Built evidence ledger with %d records.",
                len(evidence_ledger),
            )

            # -----------------------------------------------------
            # STEP 4 — Existing SignalEngine
            # -----------------------------------------------------
            #
            # IMPORTANT:
            # Preserve your existing constructor and method
            # contract.
            #
            # SignalEngine(research_data).analyze()
            # -----------------------------------------------------

            signal_engine = SignalEngine(
                self.research_data
            )

            signals = signal_engine.analyze()

            if not isinstance(signals, Mapping):
                raise MarketAnalyzerError(
                    "SignalEngine.analyze() must return a mapping."
                )

            signals = dict(signals)

            logger.info(
                "Generated %d market signals.",
                len(signals),
            )

            # -----------------------------------------------------
            # STEP 5 — Existing OpportunityEngine
            # -----------------------------------------------------
            #
            # Existing contract:
            #
            # OpportunityEngine(research_data)
            #     .generate(signals)
            # -----------------------------------------------------

            opportunity_engine = OpportunityEngine(
                self.research_data
            )

            opportunities = opportunity_engine.generate(
                signals
            )

            if not isinstance(opportunities, list):
                raise MarketAnalyzerError(
                    "OpportunityEngine.generate() must return a list."
                )

            logger.info(
                "Generated %d opportunities.",
                len(opportunities),
            )

            # -----------------------------------------------------
            # STEP 6 — Counter-evidence
            # -----------------------------------------------------

            counter_evidence = self._analyze_counter_evidence(
                evidence_ledger=evidence_ledger,
                signals=signals,
                opportunities=opportunities,
            )

            # -----------------------------------------------------
            # STEP 7 — Attach counter-evidence to opportunities
            # -----------------------------------------------------

            opportunities = (
                self._attach_counter_evidence(
                    opportunities=opportunities,
                    counter_evidence=counter_evidence,
                )
            )

            # -----------------------------------------------------
            # STEP 8 — Final response
            # -----------------------------------------------------

            result = {
                "signals": signals,

                "opportunities": opportunities,

                "evidence": {
                    "records": [
                        record.to_dict()
                        for record in evidence_ledger
                    ],
                    "summary": evidence_summary.to_dict(),
                },

                "entities": [
                    entity.to_dict()
                    for entity in resolved_entities
                ],

                "counter_evidence": [
                    finding.to_dict()
                    for finding in counter_evidence
                ],
            }

            logger.info(
                "OptriX market analysis completed successfully."
            )

            return result

        except MarketAnalyzerError:
            raise

        except Exception as exc:
            logger.exception(
                "Market analysis failed."
            )

            raise MarketAnalyzerError(
                f"Market analysis failed: {exc}"
            ) from exc

    # =============================================================
    # EVIDENCE EXTRACTION
    # =============================================================

    def _extract_evidence(
        self,
    ) -> list[Any]:
        """Extract normalized evidence from research data."""

        extractor = EvidenceExtractor()

        return extractor.extract(
            self.research_data
        )

    # =============================================================
    # ENTITY RESOLUTION
    # =============================================================

    def _resolve_entities(
        self,
    ) -> list[Any]:
        """Resolve duplicate entities across research sources."""

        resolver = EntityResolver()

        return resolver.resolve_sources(
            self.research_data
        )

    # =============================================================
    # EVIDENCE LEDGER
    # =============================================================

    @staticmethod
    def _build_evidence_ledger(
        extracted_evidence: list[Any],
        resolved_entities: list[Any],
    ) -> tuple[list[Any], Any]:
        """
        Build the normalized evidence ledger and summary.
        """

        evidence_engine = EvidenceEngine()

        evidence_ledger = (
            evidence_engine.build_ledger(
                extracted_evidence=[
                    evidence.to_dict()
                    for evidence in extracted_evidence
                ],
                resolved_entities=[
                    entity.to_dict()
                    for entity in resolved_entities
                ],
            )
        )

        evidence_summary = (
            evidence_engine.summarize(
                evidence_ledger
            )
        )

        return (
            evidence_ledger,
            evidence_summary,
        )

    # =============================================================
    # COUNTER-EVIDENCE
    # =============================================================

    @staticmethod
    def _analyze_counter_evidence(
        evidence_ledger: list[Any],
        signals: Mapping[str, Any],
        opportunities: list[dict[str, Any]],
    ) -> list[Any]:
        """Analyze limitations and contradictory market signals."""

        counter_engine = CounterEvidenceEngine()

        return counter_engine.analyze(
            evidence=[
                record.to_dict()
                for record in evidence_ledger
            ],
            signals=signals,
            opportunities=opportunities,
        )

    # =============================================================
    # OPPORTUNITY ENRICHMENT
    # =============================================================

    @staticmethod
    def _attach_counter_evidence(
        opportunities: list[dict[str, Any]],
        counter_evidence: list[Any],
    ) -> list[dict[str, Any]]:
        """
        Attach relevant counter-evidence to opportunities.

        Existing OpportunityEngine output is preserved.

        Findings that specifically mention an opportunity are
        attached to that opportunity. General market findings
        remain at the top-level counter_evidence collection.
        """

        if not opportunities:
            return opportunities

        enriched: list[dict[str, Any]] = []

        for index, opportunity in enumerate(
            opportunities
        ):
            if not isinstance(opportunity, dict):
                enriched.append(opportunity)
                continue

            updated = dict(opportunity)

            relevant_findings: list[dict[str, Any]] = []

            opportunity_title = str(
                opportunity.get(
                    "title",
                    f"Opportunity {index + 1}",
                )
            ).casefold()

            for finding in counter_evidence:
                finding_dict = finding.to_dict()

                finding_title = str(
                    finding_dict.get(
                        "title",
                        "",
                    )
                ).casefold()

                if opportunity_title in finding_title:
                    relevant_findings.append(
                        finding_dict
                    )

            # Preserve existing counter_evidence if the
            # OpportunityEngine already supplied it.
            existing_counter = opportunity.get(
                "counter_evidence",
                [],
            )

            if isinstance(existing_counter, list):
                combined = list(existing_counter)

                for finding in relevant_findings:
                    if finding not in combined:
                        combined.append(finding)

                updated[
                    "counter_evidence"
                ] = combined

            else:
                updated[
                    "counter_evidence"
                ] = relevant_findings

            enriched.append(updated)

        return enriched


# =================================================================
# FUNCTIONAL API
# =================================================================

def analyze_market(
    research_data: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Public functional API used by routes/research.py.

    This keeps compatibility with the existing route:

        analysis = analyze_market(research_data)
    """

    analyzer = MarketAnalyzer(
        research_data
    )

    return analyzer.analyze()


__all__ = [
    "MarketAnalyzer",
    "MarketAnalyzerError",
    "analyze_market",
]