"""Plain Python rules for pitcher scouting briefs."""


def validate_minimum_sample(pitch_count: int) -> None:
    """Reject a date range with fewer than 150 pitches."""
    if pitch_count < 150:
        raise ValueError("Insufficient sample")
