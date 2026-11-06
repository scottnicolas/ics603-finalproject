"""Smoke tests for the initial FastAPI skeleton."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.test import TestModel

from app.agent import BriefResponse
from app.main import app, get_agent

client = TestClient(app)
TEST_OUTPUT = {
    "claims": [
        {
            "claim_text": "Slider usage rose from 0.2 to 0.25.",
            "metric_name": "slider_usage",
            "early_value": "0.2",
            "recent_value": "0.25",
            "evidence_rows": [],
            "confidence": "low",
        }
    ],
    "note_matches_data": "partly",
}


@pytest.fixture
def offline_agent_override() -> Generator[None]:
    test_model = TestModel(custom_output_args=TEST_OUTPUT)
    agent = Agent(model=test_model, output_type=BriefResponse)
    app.dependency_overrides[get_agent] = lambda: agent
    yield
    app.dependency_overrides.pop(get_agent, None)


def test_home_page_loads_with_main_heading() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "<h1" in response.text


def test_generate_endpoint_returns_declared_top_level_fields(
    offline_agent_override: None,
) -> None:
    del offline_agent_override
    response = client.post(
        "/generate",
        json={
            "pitcher_hand": "R",
            "date_range": "2026-08-01 to 2026-09-30",
            "metrics": {"slider_usage": 0.25},
            "analyst_note": "Slider usage may have increased.",
        },
    )

    assert response.status_code == 200
    assert set(response.json()) == set(BriefResponse.model_fields)


def test_generate_endpoint_returns_generic_error_when_agent_fails(
    offline_agent_override: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    del offline_agent_override

    async def fail_generation(request: object, agent: object) -> BriefResponse:
        del request, agent
        raise UnexpectedModelBehavior(
            "token=secret gateway=https://gateway.example/provider failed"
        )

    monkeypatch.setattr("app.main.run_generation", fail_generation)
    response = client.post(
        "/generate",
        json={
            "pitcher_hand": "R",
            "date_range": "2026-08-01 to 2026-09-30",
            "metrics": {"slider_usage": 0.25},
            "analyst_note": "Slider usage may have increased.",
        },
    )

    assert response.status_code == 503
    assert "secret" not in response.text
    assert "gateway.example" not in response.text
    assert "provider failed" not in response.text


def test_generate_endpoint_returns_unavailable_without_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LLM_API_GATEWAY", raising=False)
    monkeypatch.delenv("LLM_API_TOKEN", raising=False)
    response = client.post(
        "/generate",
        json={
            "pitcher_hand": "R",
            "date_range": "2026-08-01 to 2026-09-30",
            "metrics": {"slider_usage": 0.25},
            "analyst_note": "Slider usage may have increased.",
        },
    )

    assert response.status_code == 503
    assert "not configured" not in response.text


def test_home_page_discloses_unloaded_evidence_and_uses_text_rendering() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "pitch-row evidence is not loaded" in response.text
    assert "output.textContent = JSON.stringify(result, null, 2)" in response.text
