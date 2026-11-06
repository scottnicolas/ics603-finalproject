# Model-Backed Brief Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect the existing brief form and `POST /generate` route to a configured Pydantic AI model, returning a draft `BriefResponse` checked against supplied metrics.

**Architecture:** Keep FastAPI routing and page behavior in `app/main.py`, the model and its structured output in `app/agent.py`, and deterministic numeric validation in `app/rules.py`. Inject the agent at the route boundary so API tests use `TestModel` with live model requests disabled.

**Tech Stack:** Python 3.13+, FastAPI, Pydantic AI OpenAI-compatible provider, Pydantic models, pytest `TestClient` and `TestModel`.

**Spec:** `docs/superpowers/specs/2026-11-05-model-backed-generation-design.md`; proposal context in `docs/proposal.md`.

## Global Constraints

- `app/main.py` contains routes and the page; it has no business rules.
- `app/agent.py` contains the Pydantic AI agent and output model.
- `app/rules.py` contains plain Python rules, with no FastAPI or LLM client.
- Read `LLM_API_TOKEN` and `LLM_API_GATEWAY` from the environment; never write a key outside `.env`.
- Tests never call a real model. Use `TestModel` with `override_allow_model_requests(False)`.
- No RAG, database, accounts, CSV loading, pitch-row retrieval, metric computation, or saved-work behavior.
- Keep `BriefRequest` and `BriefResponse` field names and types unchanged.
- Claims are drafts; because no pitch rows are provided, every returned claim has empty `evidence_rows`, and the page says pitch-row evidence is not loaded.
- Run `uv run pytest`, `uv run ruff check`, and `uv run mypy` after each change; do not weaken checks.

## Review Focus

- A claim contains an unsupported number: the output rule drops the entire claim. Test in Task 1.
- A metric value is represented as an integer, decimal, or negative number: compare normalized numeric values without treating `25` as `2.5`. Test in Task 1.
- Configuration is absent: the request returns a clear service error and reveals no credential or provider details. Test in Task 3.
- The model returns non-empty evidence rows despite having no pitch rows: the application clears them. Test in Task 2.
- Browser response text contains model-provided markup: render it as text, not executable HTML. Test in Task 3 through a small extracted rendering helper or verify the page uses `textContent`.

---

## File Structure

- `app/rules.py`: retain the 150-pitch rule and add pure numeric claim filtering.
- `app/agent.py`: retain the request/response models; add prompt construction, provider configuration, and the structured model call.
- `app/main.py`: inject the generation agent, call it asynchronously, map configuration/model failures to a generic response, and render success/error states in the existing form page.
- `tests/test_rules.py`: pin numeric filtering behavior.
- `tests/test_agent.py`: exercise prompt/model output contract using Pydantic AI `TestModel` without network access.
- `tests/test_skeleton.py`: preserve existing route assertions while overriding the agent with `TestModel`.

### Task 1: Filter claims against supplied metric numbers

**Files:**
- Modify: `app/rules.py`
- Test: `tests/test_rules.py`

**Interfaces:**
- Consumes: `Claim` from `app.agent` and `dict[str, float]` from `BriefRequest.metrics`.
- Produces: `filter_unsupported_claims(claims: list[Claim], metrics: dict[str, float]) -> list[Claim]`.

- [ ] **Step 1: Write failing tests**

Add `test_filter_keeps_claim_when_all_numbers_match_metrics`, `test_filter_drops_claim_with_number_not_in_metrics`, and `test_filter_compares_decimal_values_as_numbers`. Assert the matching claim remains unchanged, the unsupported claim is absent, and `0.25` matches a supplied `0.25` without substring matching.

- [ ] **Step 2: Run the focused tests and confirm the expected failure**

Run: `uv run pytest tests/test_rules.py -q`
Expected: FAIL because `filter_unsupported_claims` is not defined.

- [ ] **Step 3: Implement the pure rule**

In `app/rules.py`, extract signed integer/decimal numeric tokens from `claim_text`, `early_value`, and `recent_value`; normalize tokens and supplied metric values with `Decimal`; keep a claim only when every number equals one of the supplied metric values. Do not inspect or change `metric_name` labels.

- [ ] **Step 4: Verify focused tests and project checks**

Run: `uv run pytest tests/test_rules.py -q`, `uv run ruff check`, and `uv run mypy`.
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add app/rules.py tests/test_rules.py
git commit -m "feat: filter unsupported claim numbers"
```

### Task 2: Add the configured structured-output agent

**Files:**
- Modify: `app/agent.py`
- Create: `tests/test_agent.py`

**Interfaces:**
- Consumes: `BriefRequest`, `BriefResponse`, and `filter_unsupported_claims` from Task 1.
- Produces: `create_agent() -> Agent[None, BriefResponse]` and `async generate_brief(request: BriefRequest, agent: Agent[None, BriefResponse]) -> BriefResponse`.

- [ ] **Step 1: Write failing offline tests**

Add `test_generate_brief_uses_structured_response_and_clears_evidence` using `TestModel` configured with one complete `BriefResponse` output. Override the agent with `agent.override(model=TestModel(...))` and wrap execution in `override_allow_model_requests(False)`; assert the response fields, empty `evidence_rows`, and that the model was called. Add `test_generate_brief_drops_unsupported_numeric_claim` where the test model returns a number absent from the input metrics and assert that claim is removed.

- [ ] **Step 2: Run the focused tests and confirm the expected failure**

Run: `uv run pytest tests/test_agent.py -q`
Expected: FAIL because the agent factory and generation function are not defined.

- [ ] **Step 3: Implement provider construction and prompt**

Implement `create_agent()` using the OpenAI-compatible provider configured with `LLM_API_GATEWAY` and `LLM_API_TOKEN`. Keep the model identifier in one configuration constant, selected as a gateway-supported model; do not add a credential. Configure the existing `BriefResponse` as structured output. The prompt must pass all four request fields, request exact quotation of supplied metric values with no arithmetic or unit conversion, and prohibit fabricated pitch-row evidence. Implement `generate_brief` to run the agent asynchronously, clear every claim's `evidence_rows`, then apply `filter_unsupported_claims` before returning.

- [ ] **Step 4: Verify agent tests and project checks**

Run: `uv run pytest tests/test_agent.py -q`, `uv run ruff check`, and `uv run mypy`.
Expected: all pass with model requests disabled.

- [ ] **Step 5: Commit**

```bash
git add app/agent.py tests/test_agent.py
git commit -m "feat: add structured brief generation agent"
```

### Task 3: Wire the form to generation and display draft output

**Files:**
- Modify: `app/main.py`
- Modify: `tests/test_skeleton.py`

**Interfaces:**
- Consumes: `create_agent()` and `generate_brief()` from Task 2; current `/generate` request and response models remain unchanged.
- Produces: `POST /generate` that returns `BriefResponse` on success and a generic HTTP 503 response when configuration or model generation fails.

- [ ] **Step 1: Update route tests to use `TestModel`**

Update `test_generate_endpoint_returns_declared_top_level_fields` to override the route's agent dependency with an agent backed by `TestModel`, and wrap the test in `override_allow_model_requests(False)`. Add `test_generate_endpoint_returns_generic_error_when_agent_fails` by monkeypatching the generation adapter to raise a provider-like exception; assert HTTP 503 and that the response does not contain a token, gateway URL, or exception detail. Add `test_home_page_renders_generation_response_as_text` to ensure the response area is populated with `textContent` rather than HTML insertion.

- [ ] **Step 2: Run route tests to confirm expected failures**

Run: `uv run pytest tests/test_skeleton.py -q`
Expected: the existing success test fails because the route still returns the placeholder rather than using the dependency; the generic failure and rendering tests fail because safe error mapping and the text-based response display are not implemented.

- [ ] **Step 3: Connect route and form**

Add a FastAPI dependency that lazily constructs the configured agent, then have `generate_brief` await the agent adapter. Map configuration and model exceptions to HTTP 503 with a short generic detail, without logging or returning secrets/provider details. Keep the existing form fields and `/generate` path. On success, render the structured draft and note-match result in the response area and retain a visible message that pitch-row evidence is not loaded. Display errors in the same area using `textContent`.

- [ ] **Step 4: Verify route and full project checks**

Run: `uv run pytest`, `uv run ruff check`, and `uv run mypy`.
Expected: all pass; all model tests use `TestModel` with real model requests disabled.

- [ ] **Step 5: Commit**

```bash
git add app/main.py tests/test_skeleton.py
git commit -m "feat: connect brief form to model generation"
```

## Self-Review

- **Spec coverage:** model call, provider configuration, structured response, exact supplied numbers, dropping unsupported claims, empty evidence, draft disclosure, generic failure behavior, and offline model tests are assigned to Tasks 1–3. Proposal-only data loading, retrieval, persistence, and review workflows remain out of scope.
- **Step scan:** each task has named tests, a focused expected failure, exact function interfaces, implementation direction, verification commands, and a commit.
- **Type consistency:** `BriefRequest` and `BriefResponse` stay unchanged; the same `Agent[None, BriefResponse]` type flows from the factory through the route and adapter.
- **Review Focus:** each of the five failure/input classes maps to its owning task's named tests, including `test_home_page_renders_generation_response_as_text`.
- **Proportion:** this plan keeps changes to the existing app boundaries and only adds one focused agent test module.
