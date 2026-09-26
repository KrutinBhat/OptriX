from typing import Any, Dict


class SignalEngine:
    """
    Converts collected SerpApi research data into structured
    market signals for OpportunityOS.

    Signals:
    - demand
    - supply_gap
    - momentum
    - technology
    - competition
    - geographic_gap

    Important:
    The normalization thresholds used here are transparent
    engineering baselines. They are not statistical market
    benchmarks and should be calibrated with real research
    runs later.
    """

    def __init__(self, research_data: Dict[str, Any]):
        self.data = research_data

    def analyze(self) -> Dict[str, Any]:
        """
        Run all market signal analyses.
        """

        return {
            "demand": self._analyze_demand(),
            "supply_gap": self._analyze_supply_gap(),
            "momentum": self._analyze_momentum(),
            "technology": self._analyze_technology(),
            "competition": self._analyze_competition(),
            "geographic_gap": self._analyze_geographic_gap(),
        }

    # ============================================================
    # DATA HELPERS
    # ============================================================

    def _get_results(self, source: str) -> list:
        """
        Safely retrieve normalized results for a SerpApi source.
        """

        source_data = self.data.get(source, {})

        if isinstance(source_data, dict):
            results = source_data.get("results", [])

            if isinstance(results, list):
                return results

        return []

    def _count_results(self, source: str) -> int:
        """
        Count results returned by a source.
        """

        return len(self._get_results(source))

    @staticmethod
    def _normalize(value: float, baseline: float) -> int:
        """
        Convert a raw activity value into a 0-100 score.

        Values above the baseline are capped at 100.
        """

        if baseline <= 0:
            return 0

        return min(100, round((value / baseline) * 100))

    # ============================================================
    # DEMAND
    # ============================================================

    def _analyze_demand(self) -> Dict[str, Any]:
        """
        Estimate market demand using:

        - Jobs       → professional demand
        - Search     → market interest
        - Shopping   → commercial activity
        """

        jobs = self._count_results("jobs")
        search = self._count_results("search")
        shopping = self._count_results("shopping")

        jobs_score = self._normalize(jobs, 50)
        search_score = self._normalize(search, 100)
        shopping_score = self._normalize(shopping, 30)

        score = round(
            jobs_score * 0.45
            + search_score * 0.30
            + shopping_score * 0.25
        )

        evidence = []

        if jobs:
            evidence.append({
                "source": "jobs",
                "metric": "job_results",
                "value": jobs,
                "score": jobs_score,
                "interpretation": (
                    "Job listings provide evidence of professional "
                    "demand related to the researched topic."
                ),
            })

        if search:
            evidence.append({
                "source": "search",
                "metric": "search_results",
                "value": search,
                "score": search_score,
                "interpretation": (
                    "Search results provide evidence of market "
                    "interest around the researched topic."
                ),
            })

        if shopping:
            evidence.append({
                "source": "shopping",
                "metric": "shopping_results",
                "value": shopping,
                "score": shopping_score,
                "interpretation": (
                    "Shopping results provide evidence of "
                    "commercial product activity."
                ),
            })

        return {
            "score": score,
            "evidence": evidence,
            "metrics": {
                "jobs": jobs,
                "jobs_score": jobs_score,
                "search": search,
                "search_score": search_score,
                "shopping": shopping,
                "shopping_score": shopping_score,
            },
        }

    # ============================================================
    # SUPPLY GAP
    # ============================================================

    def _analyze_supply_gap(self) -> Dict[str, Any]:
        """
        Estimate potential supply gap.

        More existing supply → smaller gap.
        Less existing supply → larger gap.

        Sources:
        - Maps       → local supplier presence
        - Shopping   → commercial product presence
        - Search     → broader supply evidence
        """

        maps_count = self._count_results("maps")
        shopping_count = self._count_results("shopping")
        search_count = self._count_results("search")

        maps_supply_score = self._normalize(maps_count, 30)
        shopping_supply_score = self._normalize(shopping_count, 30)
        search_supply_score = self._normalize(search_count, 100)

        supply_presence = round(
            maps_supply_score * 0.50
            + shopping_supply_score * 0.30
            + search_supply_score * 0.20
        )

        score = max(0, min(100, 100 - supply_presence))

        evidence = []

        if maps_count:
            evidence.append({
                "source": "maps",
                "metric": "supplier_results",
                "value": maps_count,
                "score": maps_supply_score,
                "interpretation": (
                    "Local business results provide evidence "
                    "of existing supplier presence."
                ),
            })

        if shopping_count:
            evidence.append({
                "source": "shopping",
                "metric": "product_results",
                "value": shopping_count,
                "score": shopping_supply_score,
                "interpretation": (
                    "Product listings provide evidence of "
                    "existing commercial supply."
                ),
            })

        if search_count:
            evidence.append({
                "source": "search",
                "metric": "search_results",
                "value": search_count,
                "score": search_supply_score,
                "interpretation": (
                    "General search results provide additional "
                    "evidence of market supply."
                ),
            })

        return {
            "score": score,
            "evidence": evidence,
            "metrics": {
                "maps": maps_count,
                "maps_supply_score": maps_supply_score,
                "shopping": shopping_count,
                "shopping_supply_score": shopping_supply_score,
                "search": search_count,
                "search_supply_score": search_supply_score,
                "supply_presence": supply_presence,
            },
        }

    # ============================================================
    # MOMENTUM
    # ============================================================

    def _analyze_momentum(self) -> Dict[str, Any]:
        """
        Estimate market momentum using news and search activity.

        News receives higher weight because it provides
        time-sensitive market activity.
        """

        news = self._count_results("news")
        search = self._count_results("search")

        news_score = self._normalize(news, 50)
        search_score = self._normalize(search, 100)

        score = round(
            news_score * 0.65
            + search_score * 0.35
        )

        evidence = []

        if news:
            evidence.append({
                "source": "news",
                "metric": "news_results",
                "value": news,
                "score": news_score,
                "interpretation": (
                    "Recent news activity provides evidence "
                    "of market attention and momentum."
                ),
            })

        if search:
            evidence.append({
                "source": "search",
                "metric": "search_results",
                "value": search,
                "score": search_score,
                "interpretation": (
                    "Search activity provides additional "
                    "evidence of market interest."
                ),
            })

        return {
            "score": score,
            "evidence": evidence,
            "metrics": {
                "news": news,
                "news_score": news_score,
                "search": search,
                "search_score": search_score,
            },
        }

    # ============================================================
    # TECHNOLOGY
    # ============================================================

    def _analyze_technology(self) -> Dict[str, Any]:
        """
        Estimate technology activity using research and news.

        Scholar results receive higher weight because they provide
        direct evidence of research activity.
        """

        scholar = self._count_results("scholar")
        news = self._count_results("news")

        scholar_score = self._normalize(scholar, 50)
        news_score = self._normalize(news, 50)

        score = round(
            scholar_score * 0.70
            + news_score * 0.30
        )

        evidence = []

        if scholar:
            evidence.append({
                "source": "scholar",
                "metric": "research_results",
                "value": scholar,
                "score": scholar_score,
                "interpretation": (
                    "Research publications provide evidence "
                    "of technological development and activity."
                ),
            })

        if news:
            evidence.append({
                "source": "news",
                "metric": "news_results",
                "value": news,
                "score": news_score,
                "interpretation": (
                    "News activity provides additional evidence "
                    "of technology-related market activity."
                ),
            })

        return {
            "score": score,
            "evidence": evidence,
            "metrics": {
                "scholar": scholar,
                "scholar_score": scholar_score,
                "news": news,
                "news_score": news_score,
            },
        }

    # ============================================================
    # COMPETITION
    # ============================================================

    def _analyze_competition(self) -> Dict[str, Any]:
        """
        Estimate competitive presence using local businesses
        and commercial products.

        Higher score = stronger visible competition.
        """

        maps = self._count_results("maps")
        shopping = self._count_results("shopping")

        maps_score = self._normalize(maps, 30)
        shopping_score = self._normalize(shopping, 30)

        score = round(
            maps_score * 0.60
            + shopping_score * 0.40
        )

        evidence = []

        if maps:
            evidence.append({
                "source": "maps",
                "metric": "competitor_results",
                "value": maps,
                "score": maps_score,
                "interpretation": (
                    "Local business results provide evidence "
                    "of competitive presence."
                ),
            })

        if shopping:
            evidence.append({
                "source": "shopping",
                "metric": "product_results",
                "value": shopping,
                "score": shopping_score,
                "interpretation": (
                    "Product listings provide evidence of "
                    "commercial competition."
                ),
            })

        return {
            "score": score,
            "evidence": evidence,
            "metrics": {
                "maps": maps,
                "maps_score": maps_score,
                "shopping": shopping,
                "shopping_score": shopping_score,
            },
        }

    # ============================================================
    # GEOGRAPHIC GAP
    # ============================================================

    def _analyze_geographic_gap(self) -> Dict[str, Any]:
        """
        Estimate potential geographic gap.

        Jobs represent geographic demand.
        Maps represents geographic supply.

        Higher score = potentially larger geographic mismatch.

        This remains a baseline until entity-level geographic
        clustering is implemented.
        """

        maps = self._count_results("maps")
        jobs = self._count_results("jobs")

        maps_supply_score = self._normalize(maps, 30)
        jobs_demand_score = self._normalize(jobs, 50)

        # Geographic gap becomes larger when demand evidence
        # is stronger than visible local supply.
        gap_raw = jobs_demand_score - maps_supply_score

        # Convert the difference into a 0-100 gap score.
        # 50 represents a roughly balanced baseline.
        score = max(
            0,
            min(
                100,
                round(50 + (gap_raw / 2))
            )
        )

        evidence = []

        if maps:
            evidence.append({
                "source": "maps",
                "metric": "location_results",
                "value": maps,
                "score": maps_supply_score,
                "interpretation": (
                    "Local business results provide evidence "
                    "of geographic supply."
                ),
            })

        if jobs:
            evidence.append({
                "source": "jobs",
                "metric": "job_results",
                "value": jobs,
                "score": jobs_demand_score,
                "interpretation": (
                    "Job locations provide evidence of "
                    "geographic professional demand."
                ),
            })

        return {
            "score": score,
            "evidence": evidence,
            "metrics": {
                "maps": maps,
                "maps_supply_score": maps_supply_score,
                "jobs": jobs,
                "jobs_demand_score": jobs_demand_score,
                "gap_raw": gap_raw,
            },
        }