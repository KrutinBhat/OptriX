
"""
OptriX AI Intelligence Package
==============================

Public interface for the OptriX AI research and evidence layer.

Modules:
    query_planner
    entity_resolution
    extractor
    evidence_engine
    counter_evidence

The package provides deterministic, explainable research
intelligence components with no mandatory external LLM dependency.
"""

from .counter_evidence import (
    CounterEvidenceEngine,
    CounterEvidenceError,
    CounterEvidenceFinding,
    analyze_counter_evidence,
)
from .entity_resolution import (
    EntityMention,
    EntityResolutionError,
    EntityResolver,
    ResolvedEntity,
    resolve_entities,
)
from .evidence_engine import (
    EvidenceEngine,
    EvidenceEngineError,
    EvidenceRecord,
    EvidenceSummary,
    build_evidence,
)
from .extractor import (
    EvidenceExtractor,
    ExtractedEvidence,
    ExtractionError,
    extract_evidence,
)
from .query_planner import (
    QueryPlan,
    QueryPlanItem,
    QueryPlanner,
    QueryPlanningError,
    plan_research,
)

__all__ = [
    # Counter-evidence
    "CounterEvidenceEngine",
    "CounterEvidenceError",
    "CounterEvidenceFinding",
    # Entity resolution
    "EntityMention",
    "EntityResolutionError",
    "EntityResolver",
    # Evidence engine
    "EvidenceEngine",
    "EvidenceEngineError",
    # Evidence extraction
    "EvidenceExtractor",
    "EvidenceRecord",
    "EvidenceSummary",
    "ExtractedEvidence",
    "ExtractionError",
    # Query planning
    "QueryPlan",
    "QueryPlanItem",
    "QueryPlanner",
    "QueryPlanningError",
    "ResolvedEntity",
    "analyze_counter_evidence",
    "build_evidence",
    "extract_evidence",
    "plan_research",
    "resolve_entities",
]