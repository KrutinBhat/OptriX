from typing import Any, Dict

from .signal_engine import SignalEngine
from .opportunity_engine import OpportunityEngine


def analyze_market(research_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete OpportunityOS market intelligence pipeline.
    """

    signal_engine = SignalEngine(research_data)
    signals = signal_engine.analyze()

    opportunity_engine = OpportunityEngine(research_data)
    opportunities = opportunity_engine.generate(signals)

    return {
        "signals": signals,
        "opportunities": opportunities,
    }