"""Request and response schemas for the future brief assistant."""

from typing import Literal

from pydantic import BaseModel


class BriefRequest(BaseModel):
    """Fields the proposal names as input to the brief assistant."""

    pitcher_hand: str
    date_range: str
    metrics: dict[str, float]
    analyst_note: str


class Claim(BaseModel):
    """A draft claim and its evidence details."""

    claim_text: str
    metric_name: str
    early_value: str
    recent_value: str
    evidence_rows: list[str]
    confidence: str


class BriefResponse(BaseModel):
    """Output shape named in the proposal."""

    claims: list[Claim]
    note_matches_data: Literal["yes", "partly", "no"]
