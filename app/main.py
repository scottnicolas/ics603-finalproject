"""FastAPI routes and the project page."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic_ai import Agent
from pydantic_ai.exceptions import AgentRunError

from app.agent import (
    BriefRequest,
    BriefResponse,
    create_agent,
)
from app.agent import generate_brief as run_generation

app = FastAPI(title="Pitcher Scouting Brief Assistant")


def get_agent() -> Agent[None, BriefResponse] | None:
    """Create the configured model agent without exposing configuration errors."""
    try:
        return create_agent()
    except ValueError:
        return None


@app.get("/", response_class=HTMLResponse)
async def home() -> str:
    """Render the four main areas from the project sketch."""
    return """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Pitcher Scouting Brief Assistant</title></head>
  <body>
    <main>
      <h1>Pitcher Scouting Brief Assistant</h1>
      <section aria-labelledby="input-heading">
        <h2 id="input-heading">1. Input</h2>
        <form id="brief-form">
          <label>Pitcher hand
            <select name="pitcher_hand"><option value="R">Right</option><option value="L">Left</option></select>
          </label>
          <label>Date range <input name="date_range" required></label>
          <label>Metrics (JSON object) <textarea name="metrics">{}</textarea></label>
          <label>Analyst note <textarea name="analyst_note"></textarea></label>
          <button type="submit">Generate brief</button>
        </form>
      </section>
      <section aria-labelledby="evidence-heading"><h2 id="evidence-heading">2. Evidence</h2><p>Evidence chart and pitch rows will appear here.</p></section>
      <section aria-labelledby="claims-heading"><h2 id="claims-heading">3. Draft claims to review</h2><p>This draft is unverified; pitch-row evidence is not loaded.</p><div id="response">No brief generated yet.</div></section>
      <section aria-labelledby="saved-heading"><h2 id="saved-heading">4. Saved work</h2><p>Saved briefs will appear here.</p></section>
    </main>
    <script>
      const form = document.querySelector('#brief-form');
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const values = new FormData(form);
        const payload = {
          pitcher_hand: values.get('pitcher_hand'),
          date_range: values.get('date_range'),
          metrics: JSON.parse(values.get('metrics')),
          analyst_note: values.get('analyst_note')
        };
        const output = document.querySelector('#response');
        try {
          const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
          });
          const result = await response.json();
          if (!response.ok) {
            output.textContent = result.detail || 'Brief generation is unavailable.';
            return;
          }
          output.textContent = JSON.stringify(result, null, 2);
        } catch {
          output.textContent = 'Brief generation is unavailable.';
        }
      });
    </script>
  </body>
</html>"""


@app.post("/generate", response_model=BriefResponse)
async def generate_brief(
    request: BriefRequest,
    agent: Annotated[Agent[None, BriefResponse] | None, Depends(get_agent)],
) -> BriefResponse:
    """Generate a checked draft using the configured model agent."""
    if agent is None:
        raise HTTPException(
            status_code=503, detail="Brief generation is unavailable."
        )
    try:
        return await run_generation(request, agent)
    except AgentRunError:
        raise HTTPException(
            status_code=503, detail="Brief generation is unavailable."
        ) from None
