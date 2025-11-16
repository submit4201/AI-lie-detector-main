Here’s a tightened final edit of the plan, with infra/metrics and a completion rubric baked in and aligned to how this repo already works and what you’ve been asking for.

---

## Plan: Deep, All‑In v2 Streaming (Backend + UI, No v1 Reliance)

**Goal:** A v2‑only, fully streaming, audio‑aware analysis pipeline (all services) plus a v2‑only UI, with observability and quality gates that reach ≥90% “production‑ready” by this project’s own standards.

---

### 1. Core Contracts, Context, and Non‑Negotiables

1. **v2 API as the only path**
   - Frontend uses **only**:
     - `POST /v2/analyze` (snapshot)
     - `POST /v2/analyze/stream` (SSE)
   - v1 routes remain only as temporary compatibility; no v1 usage in the UI, tests, or docs.

2. **`AnalysisContext` in `runner.py` (central brain, no globals)**
   - Internal dataclass:
     - `transcript_partial: str`
     - `transcript_final: str | None`
     - `audio_bytes: bytes | None`
     - `audio_summary: dict`
     - `quantitative_metrics: dict`
     - `service_results: dict[str, dict]`
     - `speaker_segments: list[dict]` (start, end, speaker, text)
     - `session_summary: dict | None` (compact, privacy‑safe)
     - `config: dict` (e.g., `{"aggressive_streaming": True, "model_hint": "...", ...}`)
   - Injected into `meta["analysis_context"]` for all v2 services.
   - **Non‑negotiable:** No per‑request state anywhere else (no global mutable state).

3. **`AnalysisService` protocol: streaming‑first**
   - In analysis_protocol.py:
     - `stream_analyze(transcript, audio, meta)` is the primary path.
     - Default `analyze` consumes all `stream_analyze` chunks and returns the final one.
   - Every v2 service:
     - Implements `stream_analyze` (real streaming or pseudo‑stream).
     - Always returns the standard v2 result shape (plus streaming metadata):
       ```python
       {
         "service_name": str,
         "service_version": str,
         "local": dict,
         "gemini": dict,
         "errors": list,
         "partial": bool,
         "phase": str,          # e.g. "coarse", "refine", "final"
         "chunk_index": int | None,
       }
       ```

---

### 2. GeminiClientV2 Streaming, Providers, and Prompt Layer

4. **`GeminiClientV2.json_stream` (structured streaming)**  
   In gemini_client.py:
   - Signature:
     ```python
     async def json_stream(
         self,
         prompt: str,
         *,
         schema: dict | None = None,
         audio_bytes: bytes | None = None,
         context: dict | None = None,
         model_hint: str | None = None,
     ) -> AsyncIterator[dict]:
     ```
   - Behavior:
     - If Live JSON streaming is available:
       - Open Live session, send prompt (+audio if provided).
       - Parse **strict** JSON chunks according to `schema` when present.
       - Yield small dicts: `{"data": partial_json, "chunk_index": i, "done": bool}`.
     - Else (no Live):
       - Use `query_json` / `generate_content` once.
       - Chunk the result into 3–10 JSON fragments.
       - Yield them with small, configurable delays to simulate streaming.

5. **Provider abstraction (Live vs Simulated vs future providers)**
   - Internal strategy object used by `transcribe_stream` and `json_stream`:
     - `LiveProvider`: wraps `client.aio.live.chat.connect` or similar.
     - `SimulatedProvider`: uses batch + chunking.
   - Chosen per‑instance based on SDK capabilities; no global flag.
   - **Future‑proofing:** Provider abstraction allows adding other LLM backends later without touching service code.

6. **`transcribe_stream` around the provider**
   - Emits only transcript and speaker‑related JSON (no analysis):
     - Partial chunks:
       ```python
       {"partial_transcript": "...", "chunk_index": i, "segments": [...?]}
       ```
     - Final:
       ```python
       {"transcript": full, "transcript_segments": [...], "final": True}
       ```
   - Updates `AnalysisContext.transcript_partial/final` and `speaker_segments` at service level, not inside the client.

7. **Prompt/context injection layer**
   - A small helper module (e.g., `backend/services/v2_services/context_prompts.py`) with:
     - `build_context_report(ctx: AnalysisContext) -> dict`
     - `build_manipulation_prompt(ctx: AnalysisContext, phase: str) -> tuple[str, dict]`
     - `build_argument_prompt(ctx: AnalysisContext, phase: str) -> tuple[str, dict]`
   - These functions:
     - Use transcript summary, audio summary, quantitative metrics, speaker info, and session summary.
     - Enforce **strict JSON schemas** for `json_stream` / `query_json`.
   - **Non‑negotiable:** Services do not directly embed free‑form prompt walls everywhere; they go through these helpers.

---

### 3. Service‑Level Streaming Details (All v2 Services)

8. **TranscriptionService (text + diarization)**
   - `stream_analyze`:
     - Calls `gemini_client.transcribe_stream`.
     - For each chunk:
       - Update context: `ctx.transcript_partial` and optionally `ctx.speaker_segments`.
       - Yield v2 result:
         - `local["transcript"]` = partial or final.
         - `local["segments"]` = speaker segments if available.
         - `partial=True` until final; final chunk has `partial=False`, `phase="final"`.

9. **AudioAnalysisService (audio‑first)**
   - `stream_analyze`:
     - Immediately run a fast local analysis:
       - Duration, RMS, silence ratio, clipping heuristics.
       - Update `ctx.audio_summary` (coarse).
       - Yield result: `phase="coarse"`, `partial=True`.
     - Optionally (if configured):
       - Use `json_stream` with an audio‑focused prompt to get richer Gemini insights.
       - Merge each JSON chunk into `local["prosody"]`/`gemini` and yield updates.
     - Final:
       - Refined metrics, `partial=False`, `phase="final"`, store in `ctx.audio_summary`.

10. **QuantitativeMetricsService (transcript‑driven pseudo‑stream)**
    - `stream_analyze`:
      - While `ctx.transcript_final` is `None`:
        - Use `ctx.transcript_partial` to compute approximate:
          - Words/min, pauses, interruptions, turn‑taking patterns.
        - Yield `phase="coarse"`, `partial=True`.
      - Once `ctx.transcript_final` is set:
        - Run full existing quantitative logic.
        - Yield final metrics: `partial=False`, `phase="final"`.
        - Save in `ctx.quantitative_metrics`.

11. **ManipulationService (audio + transcript + metrics, true streaming)**
    - Inputs:
      - `meta["analysis_context"]` for text, audio, metrics, speakers, history.
    - `stream_analyze`:
      - Wait until:
        - `ctx.transcript_partial` ≥ N tokens AND `ctx.audio_summary` present (and optionally coarse metrics).
      - Build prompt via `build_manipulation_prompt(ctx, phase="coarse")`; get JSON schema.
      - Call `json_stream`:
        - For each chunk:
          - Merge into `gemini` (e.g., scores, rationales, flags).
          - Keep safe fallbacks in `local` (defaults when fields missing).
          - Yield v2 result with `partial=True`, `phase="coarse"`.
      - After `ctx.transcript_final` and full metrics available:
        - Option 1: send a new `json_stream` call with `phase="final"`.
        - Option 2: finalize within the same stream if schema supports it.
        - Yield last result with `partial=False`, `phase="final"`.
        - Store in `ctx.service_results["manipulation"]`.

12. **ArgumentService (mirrors ManipulationService, argument‑structure focus)**
    - Similar pattern to ManipulationService, but:
      - Prompt asks for claim structure, support, contradictions, logical fallacies, hesitations.
      - Streaming:
        - Early chunks: basic outline of claims and confidence per claim.
        - Final: full structured argument graph or list, with speaker attribution.
    - Uses `build_argument_prompt` + `json_stream` + the same `partial`/`phase` semantics.

13. **Other v2 services (if present)**
    - Must implement at least pseudo‑stream:
      - Internally call `analyze` then split result into 2–3 chunks.
      - Yield `partial=True` for early summary, `partial=False` for final.

---

### 4. Runner & SSE Orchestration

14. **`V2AnalysisRunner.stream_run` as canonical**
    - Phased orchestration:
      - Phase A (input prep):
        - Build `AnalysisContext` from request body (audio bytes, optional preset transcript), session metadata, config flags.
      - Phase B (foundational services):
        - Start `TranscriptionService.stream_analyze` and `AudioAnalysisService.stream_analyze` immediately, in parallel tasks.
        - As they yield:
          - Update `ctx` and emit SSE `analysis.update` events.
      - Phase C (metrics):
        - When transcript and audio_summary cross thresholds:
          - Start `QuantitativeMetricsService.stream_analyze`.
      - Phase D (higher‑level analysis):
        - When transcript/audio/metrics are “good enough”:
          - Start `ManipulationService.stream_analyze` and `ArgumentService.stream_analyze`.
    - Event wrapping:
      - Each yielded chunk from any service:
        ```json
        {
          "event": "analysis.update",
          "service": "<service_name>",
          "payload": {
            "service_name": "...",
            "service_version": "...",
            "local": {...},
            "gemini": {...},
            "errors": [...],
            "partial": true/false,
            "phase": "coarse|refine|final",
            "chunk_index": 0
          }
        }
        ```
      - Optionally, keep a simple `analysis.progress` based on completed phases/services.
    - `run` (batch mode):
      - Internally consumes `stream_run` into memory and returns:
        - Final `ctx.service_results` mapping and relevant `ctx` snapshots.

15. **SSE contract (v2‑only)**
    - `/v2/analyze/stream` always sends:
      - `analysis.update` for any chunk from any service.
      - `analysis.done` with:
        ```json
        {
          "results": { "<service>": final_result, ... },
          "meta": { "transcript_final": "...", "speaker_segments": [...], ... }
        }
        ```
    - Backward compatibility: v2 is allowed to evolve, but once this contract is in place, it is treated as stable for the v2 UI.

---

### 5. Frontend: v2‑Only UI Overhaul

16. **Drop v1 usage**
    - In src:
      - Remove any calls to `/analyze` or `/analyze/stream`.
      - Wire everything to `/v2/analyze/stream` and `/v2/analyze`.

17. **Streaming UI model**
    - Per‑service state:
      - `currentResult`, `chunks[]`, `isPartial`, `phase`.
    - Rendering:
      - Transcription:
        - Live transcript area with speaker labels.
      - Audio:
        - Simple meter for noise/clarity, maybe basic waveform bar.
      - Quantitative:
        - Early numeric hints (e.g., “speech rate: ~x words/min”) with “updating…” label.
      - Manipulation/Argument:
        - Early “preview” cards with low‑confidence labels, then refined final cards.
    - Handle SSE:
      - On `analysis.update`, merge into per‑service state by `service`.
      - When `partial=false`, mark final and optionally archive previous chunks.

18. **UI quality standards**
    - Responsive layout for desktop + tablet.
    - Error UX:
      - Display `errors` from service payloads cleanly; keep UI interactive even if some services fail.
    - Accessible color and contrast for risk scores and flags.

---

### 6. Observability, Metrics, and Infra (Non‑Negotiables)

19. **Structured logging & privacy**
    - For each request:
      - Log high‑level, **sanitized** metadata:
        - `session_id`, `request_id`, services invoked, durations, error counts.
      - Never log raw audio or full transcripts.
      - If necessary, log hashes or character counts for correlation only.

20. **Metrics**
    - At minimum (backend):
      - Per‑service:
        - `service_duration_ms`
        - `service_chunks_count`
        - `service_error_count`
        - `service_partial_to_final_latency_ms`
      - For runner:
        - `analysis_total_duration_ms`
        - `analysis_stream_started_to_first_token_ms`
    - Wire them through a simple metrics abstraction (can be plain Python counters/histograms now, easily swapped to Prometheus or another backend later).

21. **Testing & CI expectations**
    - Backend:
      - `pytest` default (unit) green.
      - v2 streaming tests in v2_tests green:
        - Runner streaming
        - Service `stream_analyze` behaviors with mocked `GeminiClientV2`.
    - Frontend:
      - Vitest suite passing.
      - At least basic tests for SSE consumer and per‑service components.
    - Coverage:
      - Maintain or improve current backend coverage, especially around v2.

---

### 7. Completion Rubric (90%+ Production‑Ready)

Use this rubric to sign off each area. A section is “green” when it hits **90%+** of these criteria.

**A. `AnalysisContext` & Protocol**
- [ ] `AnalysisContext` implemented with fields above, passed in `meta`.
- [ ] `AnalysisService` clearly documented; `stream_analyze` is primary, `analyze` wraps it.
- [ ] All v2 services implement `stream_analyze` and return the standard result shape.
- [ ] No global state; services are stateless apart from constructor configs.

**B. GeminiClientV2 & Providers**
- [ ] `json_stream` implemented and used for streaming JSON.
- [ ] Provider abstraction (Live vs Simulated) implemented and tested.
- [ ] `transcribe_stream` uses provider, yields only transcript‑level JSON.
- [ ] No direct SDK calls outside `GeminiClientV2` (services only use client methods).

**C. Services (Transcription, Audio, Quantitative, Manipulation, Argument, others)**
- [ ] Each service supports `stream_analyze` (real or pseudo).
- [ ] TranscriptionService updates context and yields diarized partials + final.
- [ ] AudioAnalysisService yields early coarse + final, updates `audio_summary`.
- [ ] QuantitativeMetricsService uses partial/final transcript for coarse + final metrics.
- [ ] ManipulationService and ArgumentService:
  - Use `AnalysisContext` (text + audio + metrics + speakers).
  - Use prompt helpers and `json_stream`.
  - Emit coarse and final JSON with clear `phase` transitions.
- [ ] Each service handles errors gracefully and populates `errors`.

**D. Runner & SSE**
- [ ] `V2AnalysisRunner.stream_run` orchestrates phases correctly (A/B/C/D).
- [ ] `run` delegates to streaming logic for consistency.
- [ ] SSE events follow the v2 contract: `analysis.update`, optional `analysis.progress`, `analysis.done`.
- [ ] Event payloads include `partial`, `phase`, and optional `chunk_index`.
- [ ] Tests cover:
  - Orchestration order.
  - Non‑blocking behavior (slow service doesn’t block others).
  - Final aggregate consistency.

**E. Frontend v2‑Only UI**
- [ ] No v1 endpoints used anywhere.
- [ ] `/v2/analyze/stream` wired up; SSE events mapped to per‑service state.
- [ ] UI renders partial vs final states clearly for each service.
- [ ] Error messages from `errors` are visible but not catastrophic.
- [ ] Basic responsiveness and accessibility checks pass.

**F. Observability & Metrics**
- [ ] Structured logs for each request (sanitized).
- [ ] Basic per‑service and per‑analysis timing metrics in place.
- [ ] Errors counted and surfaced (backend logs + optional UI).
- [ ] No raw audio or full transcripts written to logs.

**G. Documentation & Developer Experience**
- [ ] AGENTS.md / NEW_V2_API_SERVICE_STRUUCTURE_AND_PLAN.md updated to describe this v2 design and streaming behavior.
- [ ] A short `STREAMING_EVENTS_V2.md` explaining SSE events and per‑service payloads exists.
- [ ] README / UI help hints updated to describe v2‑only behavior and expectations.

If each section above is ≥90% satisfied and tests are green, v2 is effectively production‑ready by this project’s standards, with “100%” reserved for further polish (e.g., richer UI, observability backends, additional providers) rather than structural gaps.