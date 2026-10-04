from typing import Any, Dict, List, Sequence

from .scoring import OpportunityScorer


class OpportunityEngine:
    """
    Converts market signals into opportunity candidates.

    Pipeline:

        market data
            ↓
        signals
            ↓
        opportunity pattern
            ↓
        pattern-specific scoring
            ↓
        source-level evidence

    This keeps opportunity generation explainable and traceable.
    """

    def __init__(
        self,
        research_data: Dict[str, Any],
        evidence: Sequence[Any] | None = None,
    ):
        self.data = research_data
        self.evidence = list(evidence or [])
        self.scorer = OpportunityScorer()

    def generate(
        self,
        signals: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate opportunity candidates from market signals.
        """

        opportunities: List[Dict[str, Any]] = []

        patterns = [
            {
                "title": "High-Demand Supply Gap",
                "description": (
                    "Demand signals combined with relatively limited "
                    "supply indicate a potential market gap."
                ),
                "signals": ["demand", "supply_gap"],
                "pattern": "high_demand_supply_gap",
            },
            {
                "title": "Emerging Technology Opportunity",
                "description": (
                    "Strong market momentum combined with technology "
                    "activity indicates an emerging opportunity area."
                ),
                "signals": ["momentum", "technology"],
                "pattern": "emerging_technology",
            },
            {
                "title": "Geographic Market Opportunity",
                "description": (
                    "Demand activity combined with a geographic "
                    "difference between demand and supply indicates "
                    "a possible regional opportunity."
                ),
                "signals": ["demand", "geographic_gap"],
                "pattern": "geographic_market",
            },
            {
                "title": "Market Momentum Opportunity",
                "description": (
                    "Strong momentum combined with commercial demand "
                    "indicates a market area worth investigating."
                ),
                "signals": ["momentum", "demand"],
                "pattern": "market_momentum",
            },
        ]

        for pattern in patterns:
            supporting = pattern["signals"]

            # Only generate an opportunity when its supporting
            # signals contain enough activity.
            if not self._pattern_has_evidence(
                signals,
                supporting,
            ):
                continue

            # Use the scoring model specifically designed for
            # this opportunity pattern.
            score_result = self.scorer.calculate(
                signals,
                supporting_signals=supporting,
                pattern=pattern["pattern"],
            )

            opportunities.append(
                self._create_opportunity(
                    title=pattern["title"],
                    description=pattern["description"],
                    signals=signals,
                    score_result=score_result,
                    supporting=supporting,
                    pattern=pattern["pattern"],
                )
            )

        # Remove duplicate opportunity types.
        unique: Dict[str, Dict[str, Any]] = {}

        for opportunity in opportunities:
            unique[opportunity["title"]] = opportunity

        return list(unique.values())

    @staticmethod
    def _pattern_has_evidence(
        signals: Dict[str, Any],
        signal_names: List[str],
    ) -> bool:
        """
        Determine whether the signals supporting an opportunity
        have enough activity to justify generating it.
        """

        scores: List[float] = []

        for name in signal_names:
            value = signals.get(name, {})

            if not isinstance(value, dict):
                continue

            score = value.get("score", 0)

            if isinstance(score, (int, float)):
                scores.append(float(score))

        if not scores:
            return False

        average = sum(scores) / len(scores)

        return average >= 40

    def _create_opportunity(
        self,
        title: str,
        description: str,
        signals: Dict[str, Any],
        score_result: Dict[str, Any],
        supporting: List[str],
        pattern: str,
    ) -> Dict[str, Any]:
        """
        Construct the final opportunity object.
        """

        signal_evidence = self._collect_signal_evidence(
            signals,
            supporting,
        )

        source_evidence = self._collect_source_evidence(
            supporting,
        )

        return {
            "title": title,
            "description": description,
            "score": score_result["score"],
            "score_breakdown": score_result["breakdown"],
            "pattern": pattern,
            "supporting_signals": supporting,

            # Explains how SignalEngine produced the signals.
            "signal_evidence": signal_evidence,

            # Actual source-level evidence from EvidenceEngine.
            "supporting_evidence": source_evidence,

            # Counter-evidence will be attached by the
            # higher-level analysis pipeline when applicable.
            "counter_evidence": [],
        }

    @staticmethod
    def _collect_signal_evidence(
        signals: Dict[str, Any],
        supporting: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Preserve signal-level evidence generated by SignalEngine.

        Example:

            News results = 78
            Search results = 9

        This explains how the numerical signal was constructed.
        """

        evidence: List[Dict[str, Any]] = []

        for signal_name in supporting:
            signal = signals.get(signal_name, {})

            if not isinstance(signal, dict):
                continue

            signal_items = signal.get("evidence", [])

            if not isinstance(signal_items, list):
                continue

            for item in signal_items:
                if not isinstance(item, dict):
                    continue

                evidence.append(
                    {
                        **item,
                        "signal": signal_name,
                    }
                )

        return evidence

    def _collect_source_evidence(
        self,
        supporting: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Collect actual EvidenceEngine records relevant to the
        opportunity's supporting signal families.
        """

        signal_categories = {
            "demand": {
                "professional_demand",
                "market_interest",
                "commercial_activity",
            },
            "supply_gap": {
                "local_supply",
                "commercial_activity",
                "market_interest",
            },
            "momentum": {
                "market_momentum",
                "market_interest",
            },
            "technology": {
                "technology_activity",
                "market_momentum",
            },
            "geographic_gap": {
                "local_supply",
                "professional_demand",
            },
            "competition": {
                "local_supply",
                "commercial_activity",
            },
        }

        allowed_categories = set()

        for signal_name in supporting:
            allowed_categories.update(
                signal_categories.get(
                    signal_name,
                    set(),
                )
            )

        source_evidence: List[Dict[str, Any]] = []
        seen_ids: set[str] = set()

        for record in self.evidence:
            record_dict = self._record_to_dict(record)

            if not record_dict:
                continue

            evidence_id = record_dict.get("evidence_id")

            if not isinstance(evidence_id, str):
                continue

            # Prevent duplicate source evidence.
            if evidence_id in seen_ids:
                continue

            category = record_dict.get("category")

            if category not in allowed_categories:
                continue

            seen_ids.add(evidence_id)

            matching_signals = [
                signal_name
                for signal_name in supporting
                if category
                in signal_categories.get(
                    signal_name,
                    set(),
                )
            ]

            source_evidence.append(
                {
                    **record_dict,
                    "signals": matching_signals,
                }
            )

        return source_evidence

    @staticmethod
    def _record_to_dict(
        record: Any,
    ) -> Dict[str, Any] | None:
        """
        Convert an EvidenceRecord or mapping into a dictionary.
        """

        if isinstance(record, dict):
            return record

        to_dict = getattr(
            record,
            "to_dict",
            None,
        )

        if callable(to_dict):
            result = to_dict()

            if isinstance(result, dict):
                return result

        return None