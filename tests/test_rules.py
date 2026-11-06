"""Tests for minimum pitch sample validation."""

import pytest

from app.agent import Claim
from app.rules import filter_unsupported_claims, validate_minimum_sample


def test_minimum_sample_accepts_150_pitches() -> None:
    validate_minimum_sample(150)


def test_minimum_sample_rejects_149_pitches() -> None:
    with pytest.raises(ValueError, match="Insufficient sample"):
        validate_minimum_sample(149)


def test_filter_keeps_claim_when_all_numbers_match_metrics() -> None:
    claim = Claim(
        claim_text="Slider usage rose from 0.2 to 0.25.",
        metric_name="slider_usage",
        early_value="0.2",
        recent_value="0.25",
        evidence_rows=[],
        confidence="low",
    )

    result = filter_unsupported_claims(
        [claim], {"early_slider_usage": 0.2, "recent_slider_usage": 0.25}
    )

    assert result == [claim]


def test_filter_drops_claim_with_number_not_in_metrics() -> None:
    claim = Claim(
        claim_text="Slider usage rose from 0.2 to 0.3.",
        metric_name="slider_usage",
        early_value="0.2",
        recent_value="0.25",
        evidence_rows=[],
        confidence="low",
    )

    result = filter_unsupported_claims(
        [claim], {"early_slider_usage": 0.2, "recent_slider_usage": 0.25}
    )

    assert result == []


def test_filter_compares_decimal_values_as_numbers() -> None:
    claim = Claim(
        claim_text="The rate is 0.25, not 2.5.",
        metric_name="slider_usage",
        early_value="0.2",
        recent_value="0.25",
        evidence_rows=[],
        confidence="low",
    )

    result = filter_unsupported_claims(
        [claim], {"early_slider_usage": 0.2, "recent_slider_usage": 0.25}
    )

    assert result == []
