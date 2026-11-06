"""Offline tests for structured brief generation."""

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from app.agent import BriefRequest, BriefResponse, generate_brief


def make_test_agent(output: dict[str, object]) -> tuple[Agent, TestModel]:
    test_model = TestModel(custom_output_args=output)
    return Agent(output_type=BriefResponse), test_model


def make_request(metrics: dict[str, float]) -> BriefRequest:
    return BriefRequest(
        pitcher_hand="R",
        date_range="2026-08-01 to 2026-09-30",
        metrics=metrics,
        analyst_note="Slider usage may have increased.",
    )


@pytest.mark.anyio
async def test_generate_brief_uses_structured_response_and_clears_evidence() -> None:
    output = {
        "claims": [
            {
                "claim_text": "Slider usage rose from 0.2 to 0.25.",
                "metric_name": "slider_usage",
                "early_value": "0.2",
                "recent_value": "0.25",
                "evidence_rows": ["invented row"],
                "confidence": "low",
            }
        ],
        "note_matches_data": "yes",
    }
    agent, test_model = make_test_agent(output)

    with agent.override(model=test_model):
        result = await generate_brief(
            make_request({"early_slider_usage": 0.2, "recent_slider_usage": 0.25}),
            agent,
        )

    assert result.note_matches_data == "yes"
    assert len(result.claims) == 1
    assert result.claims[0].evidence_rows == []
    assert test_model.last_model_request_parameters is not None


@pytest.mark.anyio
async def test_generate_brief_drops_unsupported_numeric_claim() -> None:
    output = {
        "claims": [
            {
                "claim_text": "Slider usage rose from 0.2 to 0.3.",
                "metric_name": "slider_usage",
                "early_value": "0.2",
                "recent_value": "0.3",
                "evidence_rows": [],
                "confidence": "low",
            }
        ],
        "note_matches_data": "partly",
    }
    agent, test_model = make_test_agent(output)

    with agent.override(model=test_model):
        result = await generate_brief(
            make_request({"early_slider_usage": 0.2, "recent_slider_usage": 0.25}),
            agent,
        )

    assert result.claims == []
    assert test_model.last_model_request_parameters is not None
