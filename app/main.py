"""FastAPI routes and the project page."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.agent import BriefRequest, BriefResponse, Claim

app = FastAPI(title="Pitcher Scouting Brief Assistant")


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
      <section aria-labelledby="claims-heading"><h2 id="claims-heading">3. Draft claims to review</h2><div id="response">No brief generated yet.</div></section>
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
        const response = await fetch('/generate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const brief = await response.json();
        document.querySelector('#response').textContent = JSON.stringify(brief, null, 2);
      });
    </script>
  </body>
</html>"""


@app.post("/generate", response_model=BriefResponse)
async def generate_brief(request: BriefRequest) -> BriefResponse:
    """Return a fixed example response without processing the request."""
    del request
    return BriefResponse(
        claims=[
            Claim(
                claim_text="Example placeholder claim for review.",
                metric_name="example_metric",
                early_value="0",
                recent_value="0",
                evidence_rows=[],
                confidence="low",
            )
        ],
        note_matches_data="partly",
    )
