# Aggressive Refactor Plan

I'll create a concrete aggressive-refactor plan and add tracked TODOs for each implementation step.

Thanks — aggressive refactor confirmed. Below is a concise but detailed design, expectations, API signatures, streaming behavior, error handling, testing and rollout plan you can use as a spec (I can start implementing these steps when you say “Go”).

## Proposal

- Replace the current tangled gemini_service.py with a small set of focused components:

- Replace the current tangled gemini_service.py with a small set of focused components:
  - `backend/services/analysis_protocol.py` — abstract protocol/ABC that every analysis service implements.
- Update existing analysis services to implement the protocol and to call `GeminiClient` for their domain-specific LLM calls.

## High-level data flow

- HTTP API receives audio file (or text + audio optional).

- HTTP API receives audio file (or text + audio optional).
- API reads file into bytes and builds initial `meta` (session_id, filename, sample_rate, duration, speaker hints).
- API calls `ServiceRunner.run(audio_bytes, transcript=None, meta)` (or `run_stream(...)` for SSE).
- Runner:
  - Optionally transcribes first using `GeminiClient.transcribe(audio_bytes)`.
  - Instantiates each registered `AnalysisService` and calls their `analyze(transcript, audio_bytes, meta)` concurrently.
- API forwards aggregated result to the frontend. Streaming SSE sends incremental JSON events.

## Protocol / ABC (file: `backend/services/analysis_protocol.py`)

- Purpose: enforce a single shape for services so runner can call them generically.

- Purpose: enforce a single shape for services so runner can call them generically.

Proposed Python sketch:

- from typing import Protocol, AsyncGenerator, Optional, Dict, Any
- class AnalysisService(Protocol):
  - name: str  # e.g., "manipulation"
- Notes:
  - `analyze` returns a dict that MUST include keys: `service_name`, `gemini` (dict or None), `local` (dict).
  - `stream_analyze` yields partial dicts (same shape) and ends with the final one.

## Gemini client (file: `backend/services/gemini_client.py`)

- Responsibilities:

- Responsibilities:
  - Async `httpx` client reused for all calls.
  - Central `_choose_model(task_hint)` reading config.py per-task preferred models and fallback list.
  - Methods:
    - async def transcribe(self, audio_bytes: bytes, *, model_hint=None) -> str
    - async def analyze_audio(self, audio_bytes: bytes, transcript: str, prompt: str, *, model_hint=None, max_tokens=4096) -> Dict
    - async def query_json(self, prompt: str, *, model_hint=None, max_tokens=2048) -> Dict
  - Implementation details:
    - Send inline audio using `"inline_data": {"mime_type":..., "data": base64}` in the `contents.parts` as current code does.
    - Request `response_mime_type: "application/json"` where possible and robustly parse `candidates`/`content` or extract JSON text using centralized parsing helper `parse_gemini_response`.
    - On 404 or model unavailable errors, automatically fall back to next model in `GEMINI_FALLBACK_MODELS` and retry once per fallback (bounded retries).
    - Metrics: expose hooks/counters for request counts, latencies, and fallback events.

## Runner / Orchestrator (file: `backend/services/full_audio_analysis_runner.py`)

- API:

- API:
  - class AnalysisRunner:
    - async def run(self, audio_bytes: bytes, transcript: Optional[str], meta: Dict) -> Dict
    - async def stream_run(self, audio_bytes: bytes, transcript: Optional[str], meta: Dict) -> AsyncGenerator[Dict, None]
- Behavior:
  - If transcript is None: call `GeminiClient.transcribe` (respect per-task transcription model).
  - Create instances of all registered services (or accept a list of service instances).
  - Launch service `analyze` or `stream_analyze` concurrently.
  - Merge results into final aggregated payload: keys by service (e.g., `"manipulation_assessment": {...}`), plus `transcript`, `audio_quality`, `timings`, `errors`.
  - Provide error handling so a single service failure does not fail the whole run — include service-level error info in final output.

## Service design / expectations

- Each service implements `AnalysisService`:

- Each service implements `AnalysisService`:
  - Receives `transcript`, `audio_bytes`, `meta`.
  - Is free to call `GeminiClient` for its specific prompt; but must not call external LLMs directly — use the client so model selection and retries are centralized.
  - Returns:
    - `service_name` (string),
    - `local` (dict) — local metrics/heuristics produced without LLM,
    - `gemini` (dict) — Gemini-provided structured JSON for that service's domain,
- This keeps responsibilities clear:
  - Services own domain prompts and can combine local heuristics with LLM responses.
  - Runner only aggregates and streams.

## Streaming behavior

- SSE event shape:

- SSE event shape:
  - Event name: `analysis.update` or `analysis.done`.
- UX note:
  - Frontend should merge service results as they arrive and display loading states per panel.
  - Runner should send a small initial event with `transcript` (if available) quickly so UI can render text-first.

## Return / JSON contract

- Final aggregated response (one-shot) structure:

- Final aggregated response (one-shot) structure:
  - {
    "session_id": "...",
    "transcript": "...",
    "audio_quality": {...},
    "services": {
       "manipulation": { "local": {...}, "gemini": {...}, "errors": null, "timings": {...} },
       "argument": {...},
       ...
    },
    "timings": {"transcribe_ms": 1234, "total_ms": 4521},
- Each `gemini` object should be valid JSON parsed by `parse_gemini_response`. If Gemini returned a raw string, services should place that in `gemini_raw` and set `gemini=None` or `parsed=false`.

## Error handling

- Per-service errors must be captured and surfaced in `services.<name>.errors` without failing other services.

- Rate-limit and backoff: implement exponential backoff for temporary 5xx errors, with jitter and a limit of 2 retries.

## Testing

- Unit tests:

- Unit tests:
  - `tests/test_analysis_protocol.py` ensures services implement the ABC correctly.
  - `tests/test_gemini_client.py` use httpx mocking to simulate responses, failures and fallback ordering.
  - `tests/test_runner_integration.py` mocks `GeminiClient` and runs runner in-memory verifying concurrency and streaming order.
- Add CI steps (pytest) to run these tests.

## Migration plan

- Implement new client and runner behind a feature flag or new endpoints (`/v2/analyze`, `/v2/analyze/stream`).

- Implement new client and runner behind a feature flag or new endpoints (`/v2/analyze`, `/v2/analyze/stream`).
- Keep SDK-compatible helpers for a short time (adapter layer) to avoid large code churn at once.

## Performance & infra

- Long audio + LLM analysis is expensive — plan for:

- Long audio + LLM analysis is expensive — plan for:
  - Concurrency limits (max concurrent runs).
- Observability: log model selection, request durations, fallback counts, errors.

## Security & privacy

- Avoid logging full audio or transcripts. Log sizes, model ids, durations.

- Keep API keys in env and never print them.

## Deliverables I can implement for you now

- Create the `AnalysisService` ABC and the `GeminiClient` core.

- Create the `AnalysisService` ABC and the `GeminiClient` core.
- Implement the `AnalysisRunner` with a minimal set of services adapter (e.g., ManipulationService refactored to implement the ABC).
- Add SSE streaming endpoint and update `run_audio_test.py` to test it.
- Add unit tests for the new components and run the audio smoke test.

Next step (what I need from you)

- Confirm: proceed with the aggressive refactor now.
- Optional: confirm which services you want migrated immediately (all at once or in phases); I suggest migrating Manipulation, AudioAnalysis, QuantitativeMetrics first (they produce critical outputs).
- Any constraints about model selection (you previously specified `gemini-2.5-flash-lite` for transcription and `gemini-2.5-pro` for analysis — I’ll honor those in the client by default).

If you confirm, I’ll start by creating `analysis_protocol.py` and `gemini_client.py`, mark the TODO progress, and implement `ManipulationService` as an example, then wire the runner and a streaming endpoint and run the end-to-end audio test. Which services should I migrate first (or do you want all migrated in this pass)?
