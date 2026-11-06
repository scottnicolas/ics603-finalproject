# Model-Backed Brief Generation

## Intent

Connect the existing brief form to a language model so a hitting analyst can see a structured draft based on supplied metrics and an analyst note. This is the next slice of the proposal's LLM feature; it does not load or retrieve data.

## Current state

`GET /` renders the four proposal areas. Its form submits `pitcher_hand`, `date_range`, `metrics`, and `analyst_note` to `POST /generate`. `app/agent.py` defines `BriefRequest`, `Claim`, and `BriefResponse`; the route currently returns a fixed response. Pydantic AI's OpenAI extra is already a dependency, and the environment has `LLM_API_TOKEN` and `LLM_API_GATEWAY` keys.

## Goals

- Have `/generate` call a Pydantic AI agent using the configured gateway and credentials.
- Give the model the request fields and require the existing `BriefResponse` shape: claims with text, metric name, early and recent values, evidence rows, and confidence, plus the note-match answer.
- Instruct the model not to calculate or transform numbers. Code remains responsible for all numeric values and rejects any claim whose numbers are not present in the supplied metrics.
- Render the returned draft as claims and a note-match result on the page.
- Keep tests offline by using Pydantic AI's `TestModel` with model requests disabled.

## Non-goals

- No RAG, database, accounts, search, or saved work.
- No CSV loading, pitch-row retrieval, or metric computation.
- No claim confirmation, editing, or rejection workflow.
- No claim of verified pitch-row evidence: the current request contains metrics but no pitch rows. The model must not invent evidence rows; the page should identify this as a draft until the evidence slice is built.

## Approaches considered

1. **Model-backed draft (chosen):** connect the current endpoint to the model with the existing request and response models. It provides the requested model connection now, but operates only on supplied metrics and cannot provide pitch-row evidence.
2. **Evidence and metric pipeline first:** load saved CSVs, compute a metric, enforce the sample limit, and show its source rows. This builds trustworthy inputs but postpones the requested model connection.
3. **Saved review workflow first:** let users confirm, edit, reject, and revisit claims. This addresses human review but depends on generated claims and persistent storage, so it adds breadth before the draft exists.

## Design

- Keep the existing `POST /generate` contract and page sections. Replace the placeholder response with one Pydantic AI call.
- Configure the OpenAI-compatible provider from `LLM_API_GATEWAY` and `LLM_API_TOKEN`; keep the model identifier in one configuration location and choose one supported by the configured gateway during implementation. Do not add a new credential or require a database.
- Pass the four request fields as context. Require structured output using `BriefResponse` and tell the model to quote metric values exactly, without arithmetic or unit conversion.
- Add a plain-Python output check that compares numbers in each proposed claim with the supplied metric values. Drop claims containing unsupported numbers. Do not let the model create pitch-row evidence; keep `evidence_rows` empty until real rows are supplied.
- Display claims as drafts and show the note-match answer. Make clear that pitch-row evidence is not loaded yet.
- If model configuration or a request fails, return a clear error without exposing credentials or provider details.

## Constraints and follow-up

- `docs/proposal.md` is now the editable working spec, based on the submitted PDF, which remains unchanged. The initial scope is recorded in the LLM role section.
- The proposal's requirement that no claim ships without a source is not satisfied by this first slice. These outputs remain drafts until the CSV/evidence slice can attach pitch rows.
