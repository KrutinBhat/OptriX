"""
OptriX Market Analysis Package.

This package coordinates the existing signal and opportunity
engines with the AI evidence layer.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from ai.counter_evidence import CounterEvidenceEngine
from ai.entity_resolution import EntityResolver
from ai.evidence_engine import EvidenceEngine
from ai.extractor import EvidenceExtractor

from .opportunity_engine import OpportunityEngine
from .signal_engine import SignalEngine

logger = logging.getLogger(__name__)


def analyze_market(
    research_data: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Analyze collected research data.

    Pipeline:

        SerpApi data
            ↓
        Evidence extraction
            ↓
        Entity resolution
            ↓
        Evidence ledger
            ↓
        Existing SignalEngine
            ↓
        Existing OpportunityEngine
            ↓
        Counter-evidence analysis

    Parameters
    ----------
    research_data:
        Dictionary containing results from the research collectors.

    Returns
    -------
    dict
        Structured market analysis response.
    """

    if not isinstance(research_data, Mapping):
        raise TypeError(
            "research_data must be a mapping."
        )

    logger.info(
        "Starting OptriX market analysis."
    )

    # ---------------------------------------------------------
    # 1. EXTRACT EVIDENCE
    # ---------------------------------------------------------

    extractor = EvidenceExtractor()

    extracted_evidence = extractor.extract(
        research_data
    )

    extracted_dicts = [
        evidence.to_dict()
        for evidence in extracted_evidence
    ]

    logger.info(
        "Extracted %d evidence records.",
        len(extracted_evidence),
    )

    # ---------------------------------------------------------
    # 2. RESOLVE ENTITIES
    # ---------------------------------------------------------

    resolver = EntityResolver()

    resolved_entities = resolver.resolve_sources(
        research_data
    )

    resolved_entity_dicts = [
        entity.to_dict()
        for entity in resolved_entities
    ]

    logger.info(
        "Resolved %d entities.",
        len(resolved_entities),
    )

    # ---------------------------------------------------------
    # 3. BUILD EVIDENCE LEDGER
    # ---------------------------------------------------------

    evidence_engine = EvidenceEngine()

    evidence_ledger = evidence_engine.build_ledger(
        extracted_evidence=extracted_dicts,
        resolved_entities=resolved_entity_dicts,
    )

    evidence_summary = evidence_engine.summarize(
        evidence_ledger
    )

    logger.info(
        "Evidence ledger contains %d records.",
        len(evidence_ledger),
    )

    # ---------------------------------------------------------
    # 4. EXISTING SIGNAL ENGINE
    # ---------------------------------------------------------

    signal_engine = SignalEngine(research_data) 

    signals = signal_engine.analyze()
    

    # ---------------------------------------------------------
    # 5. EXISTING OPPORTUNITY ENGINE
    # ---------------------------------------------------------

    opportunity_engine = OpportunityEngine(
    research_data,
    evidence=evidence_ledger,
)

    opportunities = opportunity_engine.generate(signals)

    # ---------------------------------------------------------
    # 6. COUNTER-EVIDENCE
    # ---------------------------------------------------------

    counter_evidence_engine = CounterEvidenceEngine()

    counter_evidence = counter_evidence_engine.analyze(
        evidence=[
            evidence.to_dict()
            for evidence in evidence_ledger
        ],
        signals=signals,
        opportunities=opportunities,
    )

    # ---------------------------------------------------------
    # 7. FINAL RESPONSE
    # ---------------------------------------------------------

    result = {
        "signals": signals,
        "opportunities": opportunities,

        "evidence": {
            "records": [
                evidence.to_dict()
                for evidence in evidence_ledger
            ],
            "summary": evidence_summary.to_dict(),
        },

        "entities": resolved_entity_dicts,

        "counter_evidence": [
            finding.to_dict()
            for finding in counter_evidence
        ],
    }

    logger.info(
        "OptriX market analysis completed successfully."
    )

    return result


__all__ = [
    "analyze_market",
]