"""Smoke tests for the initial FastAPI skeleton."""

from fastapi.testclient import TestClient

from app.agent import BriefResponse
from app.main import app

client = TestClient(app)


def test_home_page_loads_with_main_heading() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "<h1" in response.text


def test_generate_endpoint_returns_declared_top_level_fields() -> None:
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
