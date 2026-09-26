from typing import Any, Dict


class OpportunityScorer:
    """
    Calculates a transparent opportunity score.

    Positive signals increase opportunity potential.
    Competition and counter-evidence reduce it.
    """

    WEIGHTS = {
        "demand": 0.25,
        "supply_gap": 0.25,
        "momentum": 0.15,
        "technology": 0.15,
        "geographic_gap": 0.10,
        "competition": 0.10,
    }

    def calculate(
        self,
        signals: Dict[str, Any],
        counter_evidence_count: int = 0,
    ) -> Dict[str, Any]:

        scores = {
            name: self._get_score(signals, name)
            for name in self.WEIGHTS
        }

        # Competition is a negative factor.
        positive_score = (
            scores["demand"] * 0.25
            + scores["supply_gap"] * 0.25
            + scores["momentum"] * 0.15
            + scores["technology"] * 0.15
            + scores["geographic_gap"] * 0.10
        )

        competition_penalty = scores["competition"] * 0.10

        counter_penalty = min(counter_evidence_count * 3, 15)

        final_score = max(
            0,
            min(
                100,
                positive_score
                - competition_penalty
                - counter_penalty,
            ),
        )

        return {
            "score": round(final_score),
            "breakdown": {
                "demand": {
                    "score": scores["demand"],
                    "weight": 0.25,
                    "effect": "positive",
                },
                "supply_gap": {
                    "score": scores["supply_gap"],
                    "weight": 0.25,
                    "effect": "positive",
                },
                "momentum": {
                    "score": scores["momentum"],
                    "weight": 0.15,
                    "effect": "positive",
                },
                "technology": {
                    "score": scores["technology"],
                    "weight": 0.15,
                    "effect": "positive",
                },
                "geographic_gap": {
                    "score": scores["geographic_gap"],
                    "weight": 0.10,
                    "effect": "positive",
                },
                "competition": {
                    "score": scores["competition"],
                    "weight": 0.10,
                    "effect": "negative",
                },
                "counter_evidence": {
                    "count": counter_evidence_count,
                    "penalty": counter_penalty,
                    "effect": "negative",
                },
            },
        }

    @staticmethod
    def _get_score(
        signals: Dict[str, Any],
        name: str,
    ) -> float:

        value = signals.get(name, {})

        if isinstance(value, dict):
            score = value.get("score", 0)

            if isinstance(score, (int, float)):
                return max(0, min(100, float(score)))

        return 0