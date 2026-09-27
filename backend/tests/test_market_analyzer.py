"""
Tests for OptriX MarketAnalyzer.

These tests verify:

1. Evidence extraction is integrated.
2. Entity resolution is integrated.
3. Evidence ledger is generated.
4. Existing SignalEngine contract is preserved.
5. Existing OpportunityEngine contract is preserved.
6. Counter-evidence is returned.
7. Empty research data does not crash the AI layer.
8. Invalid input is rejected.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from backend.analysis.market_analyzer import (
    MarketAnalyzer,
    MarketAnalyzerError,
    analyze_market,
)

# ================================================================
# SAMPLE RESEARCH DATA
# ================================================================


@pytest.fixture
def research_data():
    return {
        "search": {
            "results": [
                {
                    "title": "ABC Technologies",
                    "link": "https://www.abctech.com",
                    "snippet": (
                        "ABC Technologies provides "
                        "industrial automation solutions."
                    ),
                    "position": 1,
                },
                {
                    "title": "Industrial Automation Market",
                    "link": "https://example.com/market",
                    "snippet": (
                        "Industrial automation demand is "
                        "increasing across manufacturing."
                    ),
                    "position": 2,
                },
            ]
        },
        "news": {
            "results": [
                {
                    "title": (
                        "Industrial automation "
                        "investment increases"
                    ),
                    "link": "https://example.com/news",
                    "snippet": (
                        "Manufacturers are investing "
                        "in automation technologies."
                    ),
                    "date": "2026-09-20",
                }
            ]
        },
        "jobs": {
            "results": [
                {
                    "title": "Automation Engineer",
                    "company": "ABC Technologies",
                    "link": (
                        "https://jobs.example.com/automation"
                    ),
                    "snippet": (
                        "Engineering role involving "
                        "industrial automation."
                    ),
                }
            ]
        },
        "maps": {
            "results": [
                {
                    "name": (
                        "ABC Technologies Pvt Ltd"
                    ),
                    "website": (
                        "https://www.abctech.com"
                    ),
                    "address": (
                        "Bengaluru, India"
                    ),
                }
            ]
        },
        "shopping": {
            "results": [
                {
                    "title": (
                        "Industrial Automation Controller"
                    ),
                    "link": (
                        "https://example.com/product"
                    ),
                    "price": "25000",
                    "snippet": (
                        "Industrial automation "
                        "controller."
                    ),
                }
            ]
        },
        "scholar": {
            "results": [
                {
                    "title": (
                        "Advances in Industrial Automation"
                    ),
                    "link": (
                        "https://scholar.example.com/paper"
                    ),
                    "snippet": (
                        "Research on industrial "
                        "automation technologies."
                    ),
                }
            ]
        },
    }


# ================================================================
# BASIC ANALYZER TESTS
# ================================================================


def test_market_analyzer_returns_expected_structure(
    research_data,
):
    """
    Verify that the complete analyzer returns all expected
    top-level sections.
    """

    result = analyze_market(
        research_data
    )

    assert isinstance(
        result,
        dict,
    )

    assert "signals" in result
    assert "opportunities" in result
    assert "evidence" in result
    assert "entities" in result
    assert "counter_evidence" in result


def test_market_analyzer_returns_signals(
    research_data,
):
    """Existing SignalEngine output should remain available."""

    result = analyze_market(
        research_data
    )

    assert isinstance(
        result["signals"],
        dict,
    )


def test_market_analyzer_returns_opportunities(
    research_data,
):
    """Existing OpportunityEngine output should remain available."""

    result = analyze_market(
        research_data
    )

    assert isinstance(
        result["opportunities"],
        list,
    )


# ================================================================
# EVIDENCE INTEGRATION
# ================================================================


def test_market_analyzer_extracts_evidence(
    research_data,
):
    """Verify that evidence extraction is connected."""

    result = analyze_market(
        research_data
    )

    evidence = result["evidence"]

    assert isinstance(
        evidence,
        dict,
    )

    assert "records" in evidence
    assert "summary" in evidence

    assert isinstance(
        evidence["records"],
        list,
    )

    assert len(
        evidence["records"]
    ) > 0


def test_market_analyzer_evidence_summary(
    research_data,
):
    """Verify evidence summary fields."""

    result = analyze_market(
        research_data
    )

    summary = result[
        "evidence"
    ]["summary"]

    assert "total_records" in summary
    assert "unique_claims" in summary
    assert "source_count" in summary
    assert "category_count" in summary
    assert "average_quality_score" in summary
    assert "coverage_score" in summary

    assert (
        summary["total_records"] > 0
    )

    assert (
        0 <= summary["coverage_score"] <= 100
    )


# ================================================================
# ENTITY RESOLUTION
# ================================================================


def test_market_analyzer_resolves_entities(
    research_data,
):
    """Verify that entity resolution is connected."""

    result = analyze_market(
        research_data
    )

    entities = result[
        "entities"
    ]

    assert isinstance(
        entities,
        list,
    )

    assert len(
        entities
    ) > 0


def test_company_mentions_are_resolved(
    research_data,
):
    """
    The search/jobs/maps records contain variations of
    ABC Technologies and should produce a resolved entity.
    """

    result = analyze_market(
        research_data
    )

    entities = result[
        "entities"
    ]

    names = [
        entity.get(
            "canonical_name",
            "",
        ).casefold()
        for entity in entities
    ]

    assert any(
        "abc technologies" in name
        for name in names
    )


# ================================================================
# COUNTER-EVIDENCE
# ================================================================


def test_market_analyzer_returns_counter_evidence(
    research_data,
):
    """Verify that counter-evidence analysis is connected."""

    result = analyze_market(
        research_data
    )

    counter_evidence = result[
        "counter_evidence"
    ]

    assert isinstance(
        counter_evidence,
        list,
    )


def test_opportunities_preserve_counter_evidence_field(
    research_data,
):
    """
    Existing OpportunityEngine opportunities should continue
    to expose their counter_evidence field.
    """

    result = analyze_market(
        research_data
    )

    for opportunity in result[
        "opportunities"
    ]:
        assert isinstance(
            opportunity,
            dict,
        )

        assert "counter_evidence" in opportunity


# ================================================================
# INVALID INPUT
# ================================================================


def test_market_analyzer_rejects_invalid_input():
    """Invalid research input should fail clearly."""

    with pytest.raises(
        MarketAnalyzerError
    ):
        MarketAnalyzer(
            None
        )


def test_analyze_market_rejects_invalid_input():
    """Functional API should also reject invalid input."""

    with pytest.raises(
        MarketAnalyzerError
    ):
        analyze_market(
            None
        )


# ================================================================
# EMPTY RESEARCH
# ================================================================


def test_empty_research_does_not_break_evidence_layer():
    """
    The AI evidence layer should safely handle empty research.

    Existing analysis engines may return empty signals or
    opportunities depending on their implementation.
    """

    empty_research = {
        "search": {
            "results": []
        },
        "news": {
            "results": []
        },
        "jobs": {
            "results": []
        },
        "maps": {
            "results": []
        },
        "shopping": {
            "results": []
        },
        "scholar": {
            "results": []
        },
    }

    result = analyze_market(
        empty_research
    )

    assert isinstance(
        result,
        dict,
    )

    assert "evidence" in result
    assert "entities" in result
    assert "counter_evidence" in result

    assert (
        result["evidence"]["records"]
        == []
    )

    assert (
        result["entities"]
        == []
    )


# ================================================================
# EXISTING ENGINE CONTRACTS
# ================================================================


def test_signal_engine_contract_is_preserved(
    research_data,
):
    """
    Verify that MarketAnalyzer still calls the existing
    SignalEngine(research_data).analyze() contract.
    """

    fake_signals = {
        "demand": {
            "score": 70,
            "evidence": [],
        },
        "supply_gap": {
            "score": 60,
            "evidence": [],
        },
        "momentum": {
            "score": 50,
            "evidence": [],
        },
        "technology": {
            "score": 50,
            "evidence": [],
        },
        "geographic_gap": {
            "score": 40,
            "evidence": [],
        },
        "competition": {
            "score": 30,
            "evidence": [],
        },
    }

    with patch(
        "backend.analysis.market_analyzer.SignalEngine"
    ) as mock_signal_engine:

        mock_instance = (
            mock_signal_engine.return_value
        )

        mock_instance.analyze.return_value = (
            fake_signals
        )

        with patch(
            "backend.analysis.market_analyzer.OpportunityEngine"
        ) as mock_opportunity_engine:

            opportunity_instance = (
                mock_opportunity_engine.return_value
            )

            opportunity_instance.generate.return_value = []

            result = analyze_market(
                research_data
            )

    mock_signal_engine.assert_called_once_with(
        research_data
    )

    mock_instance.analyze.assert_called_once()

    mock_opportunity_engine.assert_called_once_with(
        research_data
    )

    opportunity_instance.generate.assert_called_once_with(
        fake_signals
    )

    assert (
        result["signals"]
        == fake_signals
    )


def test_market_analyzer_preserves_opportunity_output(
    research_data,
):
    """Existing opportunity data should not be rewritten."""

    fake_signals = {
        "demand": {
            "score": 80,
            "evidence": [],
        }
    }

    fake_opportunities = [
        {
            "title": "Test Opportunity",
            "description": "Test description",
            "score": 75,
            "score_breakdown": {},
            "supporting_signals": [
                "demand"
            ],
            "supporting_evidence": [],
            "counter_evidence": [],
        }
    ]

    with patch(
        "backend.analysis.market_analyzer.SignalEngine"
    ) as mock_signal_engine:

        mock_signal_engine.return_value.analyze.return_value = (
            fake_signals
        )

        with patch(
            "backend.analysis.market_analyzer.OpportunityEngine"
        ) as mock_opportunity_engine:

            mock_opportunity_engine.return_value.generate.return_value = (
                fake_opportunities
            )

            result = analyze_market(
                research_data
            )

    assert (
        result["opportunities"][0]["title"]
        == "Test Opportunity"
    )

    assert (
        result["opportunities"][0]["score"]
        == 75
    )