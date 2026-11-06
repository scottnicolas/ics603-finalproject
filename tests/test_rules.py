"""Tests for minimum pitch sample validation."""

import pytest

from app.rules import validate_minimum_sample


def test_minimum_sample_accepts_150_pitches() -> None:
    validate_minimum_sample(150)


def test_minimum_sample_rejects_149_pitches() -> None:
    with pytest.raises(ValueError, match="Insufficient sample"):
        validate_minimum_sample(149)
