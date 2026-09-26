from typing import Any, Dict, List

from .scoring import OpportunityScorer


class OpportunityEngine:
    """
    Converts market signals into opportunity candidates.

    The engine looks for different combinations of market signals
    instead of requiring every signal to cross a fixed threshold.
    """

    def __init__(self, research_data: Dict[str, Any]):
        self.data = research_data
        self.scorer = OpportunityScorer()

    def generate(
        self,
        signals: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        opportunities: List[Dict[str, Any]] = []

        patterns = [
            {
                "title": "High-Demand Supply Gap",
                "description": (
                    "Demand signals combined with relatively limited "
                    "supply indicate a potential market gap."
                ),
                "signals": ["demand", "supply_gap"],
            },
            {
                "title": "Emerging Technology Opportunity",
                "description": (
                    "Strong market momentum combined with technology "
                    "activity indicates an emerging opportunity area."
                ),
                "signals": ["momentum", "technology"],
            },
            {
                "title": "Geographic Market Opportunity",
                "description": (
                    "Demand activity combined with a geographic "
                    "difference between demand and supply indicates "
                    "a possible regional opportunity."
                ),
                "signals": ["demand", "geographic_gap"],
            },
            {
                "title": "Market Momentum Opportunity",
                "description": (
                    "Strong momentum combined with commercial demand "
                    "indicates a market area worth investigating."
                ),
                "signals": ["momentum", "demand"],
            },
        ]

        for pattern in patterns:

            supporting = pattern["signals"]

            if not self._pattern_has_evidence(
                signals,
                supporting,
            ):
                continue

            score_result = self.scorer.calculate(signals)

            opportunities.append(
                self._create_opportunity(
                    title=pattern["title"],
                    description=pattern["description"],
                    signals=signals,
                    score_result=score_result,
                    supporting=supporting,
                )
            )

        # Remove duplicate opportunity types if necessary.
        unique = {}
        for opportunity in opportunities:
            unique[opportunity["title"]] = opportunity

        return list(unique.values())

    @staticmethod
    def _pattern_has_evidence(
        signals: Dict[str, Any],
        signal_names: List[str],
    ) -> bool:

        scores = []

        for name in signal_names:
            value = signals.get(name, {})
            score = value.get("score", 0)

            if isinstance(score, (int, float)):
                scores.append(score)

        if not scores:
            return False

        # Average evidence threshold.
        average = sum(scores) / len(scores)

        return average >= 40

    @staticmethod
    def _create_opportunity(
        title: str,
        description: str,
        signals: Dict[str, Any],
        score_result: Dict[str, Any],
        supporting: List[str],
    ) -> Dict[str, Any]:

        supporting_evidence = []

        for signal_name in supporting:

            signal = signals.get(signal_name, {})

            for evidence in signal.get("evidence", []):

                supporting_evidence.append(
                    {
                        **evidence,
                        "signal": signal_name,
                    }
                )

        return {
            "title": title,
            "description": description,
            "score": score_result["score"],
            "score_breakdown": score_result["breakdown"],
            "supporting_signals": supporting,
            "supporting_evidence": supporting_evidence,
            "counter_evidence": [],
        }