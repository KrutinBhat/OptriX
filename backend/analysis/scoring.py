from typing import Any, Dict, Iterable


class OpportunityScorer:
    """
    Calculates transparent, opportunity-specific scores.

    The scorer can evaluate either:
        1. a specific set of supporting signals for an opportunity
        2. all signals for backward compatibility

    Scores are normalized to 0-100.
    """

    # Default weights used when no specific signal set is provided.
    DEFAULT_WEIGHTS = {
        "demand": 0.25,
        "supply_gap": 0.25,
        "momentum": 0.15,
        "technology": 0.15,
        "geographic_gap": 0.10,
        "competition": 0.10,
    }

    # Pattern-specific weights.
    #
    # Positive signals contribute positively.
    # Competition acts as a negative factor.
    PATTERN_WEIGHTS = {
        "high_demand_supply_gap": {
            "demand": 0.40,
            "supply_gap": 0.40,
            "competition": 0.20,
        },
        "emerging_technology": {
            "momentum": 0.45,
            "technology": 0.40,
            "competition": 0.15,
        },
        "geographic_market": {
            "demand": 0.40,
            "geographic_gap": 0.40,
            "competition": 0.20,
        },
        "market_momentum": {
            "momentum": 0.50,
            "demand": 0.35,
            "competition": 0.15,
        },
    }

    def calculate(
        self,
        signals: Dict[str, Any],
        supporting_signals: Iterable[str] | None = None,
        counter_evidence_count: int = 0,
        pattern: str | None = None,
    ) -> Dict[str, Any]:
        """
        Calculate an opportunity score.

        Parameters
        ----------
        signals:
            Complete signal dictionary produced by SignalEngine.

        supporting_signals:
            Signals directly relevant to this opportunity.

        counter_evidence_count:
            Number of counter-evidence findings affecting the opportunity.

        pattern:
            Optional pattern name used to select predefined weights.
        """

        if not isinstance(signals, dict):
            raise TypeError("signals must be a dictionary.")

        # Select the weight system.
        weights = self._resolve_weights(
            supporting_signals=supporting_signals,
            pattern=pattern,
        )

        scores: Dict[str, float] = {}

        for signal_name in weights:
            scores[signal_name] = self._get_score(
                signals,
                signal_name,
            )

        # Separate positive and negative signals.
        positive_score = 0.0
        negative_score = 0.0

        for signal_name, weight in weights.items():
            score = scores.get(signal_name, 0.0)

            if signal_name == "competition":
                negative_score += score * weight
            else:
                positive_score += score * weight

        # Counter evidence penalty.
        counter_penalty = min(
            max(counter_evidence_count, 0) * 3,
            15,
        )

        final_score = (
            positive_score
            - negative_score
            - counter_penalty
        )

        final_score = max(
            0.0,
            min(100.0, final_score),
        )

        breakdown = self._build_breakdown(
            signals=signals,
            weights=weights,
            scores=scores,
            counter_evidence_count=counter_evidence_count,
            counter_penalty=counter_penalty,
        )

        return {
            "score": round(final_score),
            "breakdown": breakdown,
        }

    def _resolve_weights(
        self,
        supporting_signals: Iterable[str] | None,
        pattern: str | None,
    ) -> Dict[str, float]:
        """
        Resolve the weights used for this particular opportunity.
        """

        if pattern:
            pattern_weights = self.PATTERN_WEIGHTS.get(pattern)

            if pattern_weights:
                return dict(pattern_weights)

        if supporting_signals is None:
            return dict(self.DEFAULT_WEIGHTS)

        requested = [
            name
            for name in supporting_signals
            if name in self.DEFAULT_WEIGHTS
        ]

        if not requested:
            return dict(self.DEFAULT_WEIGHTS)

        # Keep only the relevant signals and normalize
        # their weights so the total equals 1.
        selected = {
            name: self.DEFAULT_WEIGHTS[name]
            for name in requested
        }

        total = sum(selected.values())

        if total <= 0:
            return dict(self.DEFAULT_WEIGHTS)

        return {
            name: weight / total
            for name, weight in selected.items()
        }

    def _build_breakdown(
        self,
        signals: Dict[str, Any],
        weights: Dict[str, float],
        scores: Dict[str, float],
        counter_evidence_count: int,
        counter_penalty: float,
    ) -> Dict[str, Any]:
        """
        Build an explanation-friendly scoring breakdown.

        All known signals are retained so the frontend can display
        a consistent structure. Signals not used by this opportunity
        are marked inactive.
        """

        breakdown: Dict[str, Any] = {}

        for signal_name in self.DEFAULT_WEIGHTS:
            active = signal_name in weights
            score = scores.get(
                signal_name,
                self._get_score(signals, signal_name),
            )

            weight = weights.get(
                signal_name,
                0.0,
            )

            if not active:
                breakdown[signal_name] = {
                    "score": round(score),
                    "weight": 0.0,
                    "effect": "not_used",
                    "active": False,
                }
                continue

            effect = (
                "negative"
                if signal_name == "competition"
                else "positive"
            )

            breakdown[signal_name] = {
                "score": round(score),
                "weight": round(weight, 3),
                "effect": effect,
                "active": True,
            }

        breakdown["counter_evidence"] = {
            "count": counter_evidence_count,
            "penalty": counter_penalty,
            "effect": "negative",
            "active": counter_evidence_count > 0,
        }

        return breakdown

    @staticmethod
    def _get_score(
        signals: Dict[str, Any],
        name: str,
    ) -> float:
        """
        Safely extract a 0-100 signal score.
        """

        value = signals.get(name, {})

        if not isinstance(value, dict):
            return 0.0

        score = value.get("score", 0)

        if not isinstance(score, (int, float)):
            return 0.0

        return max(
            0.0,
            min(100.0, float(score)),
        )