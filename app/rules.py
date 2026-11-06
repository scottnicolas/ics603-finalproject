"""Plain Python rules for pitcher scouting briefs."""

import re
from decimal import Decimal, InvalidOperation
from typing import Protocol


class ClaimWithNumericText(Protocol):
    """Text fields inspected when checking numbers in a proposed claim."""

    claim_text: str
    early_value: str
    recent_value: str


_NUMBER_PATTERN = re.compile(
    r"(?<![\w.])[+-]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][+-]?\d+)?(?!\w|\.(?=\d))"
)


def validate_minimum_sample(pitch_count: int) -> None:
    """Reject a date range with fewer than 150 pitches."""
    if pitch_count < 150:
        raise ValueError("Insufficient sample")


def filter_unsupported_claims[ClaimType: ClaimWithNumericText](
    claims: list[ClaimType], metrics: dict[str, float]
) -> list[ClaimType]:
    """Keep claims whose numeric text is present among the supplied metrics."""
    supported_numbers = {
        number
        for value in metrics.values()
        if (number := Decimal(str(value))).is_finite()
    }
    return [
        claim
        for claim in claims
        if all(
            _number_is_supported(match.group(), supported_numbers)
            for field in (claim.claim_text, claim.early_value, claim.recent_value)
            for match in _NUMBER_PATTERN.finditer(field)
        )
    ]


def _number_is_supported(number_text: str, supported_numbers: set[Decimal]) -> bool:
    try:
        number = Decimal(number_text)
    except InvalidOperation:
        return False
    return number.is_finite() and number in supported_numbers
