Nice idea. Let’s do a quick brand kit pass focused on identity you can refine later.

**1. Brand Core**

- **Product role:** “AI‑assisted lie and manipulation radar for spoken conversations.”  
- **Primary promise:** Turn messy, emotional audio into clear, structured insight: “What was really said, how, and why it felt off.”
- **Tone of voice (copywriting):**
  - Calm, analytical, non‑judgmental.
  - Plain language, zero hype; emphasizes *patterns* and *signals* not absolute truth.
  - Speaks in terms like “indicators”, “signals”, “confidence”, not “you’re lying”.

**2. Name & Tagline Options**

- **Working name:** `VerityScope` (you can keep “AI Lie Detector” as a technical/project name).
- **Tagline options:**
  - “Listen deeper to every word.”
  - “Signals behind the story.”
  - “From voice to verified signals.”
- Choose one that feels closest to your project’s heart; we can tune later.

**3. Personality & Principles**

- **Personality:**
  - Analyst, not judge.
  - Forensic but empathetic: cares about accuracy and fairness.
  - Transparent: explains *why* it flags something.
- **Design principles:**
  - Clarity over drama (no red sirens or “LIAR” stamps).
  - Signal, not noise: only show what the model knows and how sure it is.
  - Safety first: highlight uncertainty and limitations prominently.

**4. Visual Direction (light MD3‑inspired)**

- **Color palette (example):**
  - Primary: Deep teal `#11697A` (analytic, trustworthy).
  - Secondary: Indigo `#3F51B5` for emphasis and actions.
  - Accent (risk): Amber `#FFC107` → Red `#D32F2F` gradient for risk states (always with clear labels).
  - Neutral surfaces: `#121212` (dark), `#1E1E1E`, `#F5F5F5` for light mode.
- **Shapes & components:**
  - Cards with soft corners and subtle elevation for each service.
  - Chips/pills for flags (e.g., “High pressure”, “Evasion cue”).
  - Simple iconography (waveforms, quotation marks, “radar” style pulse).

**5. Brand Language for Services**

Map each v2 service to a branded concept:

- `Transcription` → “Conversation Transcript”
- `AudioAnalysis` → “Voice & Tone Signals”
- `QuantitativeMetrics` → “Conversation Metrics”
- `ManipulationService` → “Influence Signals”
- `ArgumentService` → “Argument Structure”

Use these names in UI labels rather than raw service names.

**6. Ethics & Disclaimers**

- Always present:
  - “These are *indicators*, not proof.”
  - Confidence meter with short explanation (“High confidence means multiple patterns aligned; still not a definitive verdict.”).
- Include an “Ethics & Limitations” link in the main UI (footer or panel).

**7. Minimal Brand Kit Checklist**

You can drop this into ui-overhual-expoectiuions.md:

- [ ] Chosen brand/product name and tagline.
- [ ] Defined tone of voice in 3–5 bullets.
- [ ] Locked color tokens (primary, secondary, risk, surface, text).
- [ ] Friendly service names mapped from backend services.
- [ ] Ethics/limitations copy drafted and placed in UI.
- [ ] Example screenshots or mockups reflect “analyst, not judge” identity.

V2 Frontend UI Rubric (Target ≥90% Before “Done”)

For each category, score 0–10. Anything <8 in any category means “iterate again”.

Architecture & API Usage
0–3: v1 endpoints still referenced; v2 SSE handling mixed into components; no central API/stream client.
4–7: v1 mostly removed but some ad‑hoc fetches; SSE logic partially centralized; unclear separation of state vs view.
8–10: Only /v2/analyze + /v2/analyze/stream used; clean api + streaming modules; useV2AnalysisSession (or equivalent) owns streaming state; components are dumb, data‑in/view‑out.
Streaming UX & Service Panels
0–3: UI treats everything as batch; partial vs final states not visible; user can’t tell if analysis is in progress.
4–7: Some live updates but inconsistent; some services don’t show “coarse” vs “final” clearly; chunk ordering can feel jittery.
8–10: Each service panel clearly shows “live/coarse” vs “final” (badges, subtle motion); transcript updates feel continuous; user always knows what’s happening, what’s coming next, and when it’s done.
Modern Design & Visual Language (MD3‑inspired)
0–3: Inconsistent spacing, typography, and colors; no clear hierarchy; hard to scan.
4–7: Some structure but mixed styles; inconsistent use of elevation, surfaces, and color roles; risk levels not clearly encoded.
8–10: Consistent MD3‑like tokens (primary/secondary/tertiary, surfaces, elevation); clear visual hierarchy; cards/chips/lists used appropriately; manipulation/argument risk states encoded with clear, accessible color and iconography.
Responsiveness & Layout
0–3: Layout breaks or becomes unusable on smaller screens; panels overlap or scroll badly.
4–7: Works on desktop; acceptable but cramped on tablet; some horizontal scroll or overflow issues.
8–10: Responsive grid or layout that degrades gracefully down to ~768px width; panels stack politely; key actions remain visible; no awkward scroll traps.
Accessibility & Clarity
0–3: Poor color contrast; no semantic headings; screen reader experience is unclear; ambiguous text labels.
4–7: Adequate contrast and some ARIA roles; still missing clear labels or announcements for streaming states.
8–10: WCAG‑respecting color contrast; semantic HTML; streaming state changes (loading, partial, final, errors) exposed via text and, where relevant, ARIA live regions; clear labels and tooltips for all key metrics.
Error Handling & Empty States
0–3: Errors crash the page or leave it blank; user gets no guidance.
4–7: Toasts or banners exist but are generic; per‑service failures are not obviously localized.
8–10: Per‑service error messaging; global failure handling that leaves existing data visible; thoughtful empty states (no audio, no transcript yet, short recording) that explain what to do next.
Performance & Perceived Latency
0–3: Heavy re‑renders on each SSE message; animations or loading elements feel janky.
4–7: Mostly fine, but some panels re‑render unnecessarily; long analyses feel sluggish or “stuck”.
8–10: SSE reducer is efficient; only affected panels re‑render; skeleton/loading states and transitions hide small delays; UI remains responsive even during long analyses.
Code Quality & Test Coverage (UI)
0–3: No tests; complex logic in components; hard to reason about.
4–7: Some tests for hooks or critical components; still brittle or incomplete; repeated logic not abstracted.
8–10: useV2AnalysisSession fully covered with event sequences; core panels covered with snapshot or behavior tests; clear separation of concerns; minimal duplication; easy to add new service panels.
Acceptance Rule

Compute per‑category scores (0–10).
If any category <8, the agent must iterate: rewrite/refine components, styling, or state management before considering the UI “ready”.
Only when overall average ≥9 and no category <8 can the v2 UI be marked “production‑ready” and v1 fully retired.

Here’s a focused frontend overhaul plan tailored to the new v2 streaming model.

**Goals**

- Use only `/v2/analyze` and `/v2/analyze/stream` from the UI.
- Treat streaming as first‑class: partial + phase‑aware updates per service.
- Make it easy to plug in new services and event fields without rewiring the UI.
- Keep things clean, responsive, and testable.

---

**1. API & Data Layer**

- **HTTP client**
  - Centralize API calls in `frontend/src/lib/api/analysisV2.js` (or similar).
  - Expose:
    - `startStreamingAnalysis(formData | payload)` → returns an EventSource wrapper.
    - `runSnapshotAnalysis(formData | payload)` → calls `/v2/analyze` once.

- **SSE handler**
  - Create `frontend/src/lib/streaming/v2SseClient.js`:
    - Connects to `/v2/analyze/stream`.
    - Normalizes messages into:
      ```js
      {
        event: "analysis.update" | "analysis.done",
        service: "transcription" | "audio" | "quantitative" | "manipulation" | "argument" | ...,
        payload: { local, gemini, errors, partial, phase, chunkIndex }
      }
      ```
    - Handles reconnect/cleanup on unmount or stop.

---

**2. State Model & Hooks**

- **Global analysis state**
  - Add a hook `useV2AnalysisSession` in `frontend/src/hooks/useV2AnalysisSession.js`:
    - Manages:
      ```js
      {
        status: "idle" | "streaming" | "completed" | "error",
        transcript: { text, segments, partial },
        services: {
          [serviceName]: {
            current: { local, gemini, errors, partial, phase },
            chunks: [ ...history ],
          }
        },
        meta: {
          sessionId,
          startedAt,
          finishedAt,
          config,
        },
        error: null | { message, details }
      }
      ```
    - Provides actions:
      - `startStreaming(payload)`
      - `stopStreaming()`
      - `reset()`

- **Event → state reducer**
  - Implement a reducer that:
    - On `analysis.update`:
      - Merges per‑service state by `service`.
      - Updates transcript & speaker segments from the transcription service.
    - On `analysis.done`:
      - Finalizes `services` map and sets `status="completed"`.

---

**3. Page Layout & Flows**

- **Main analysis page**
  - In `frontend/src/pages/AnalyzeV2.jsx` (or similar):
    - Left column:
      - Input controls: mic recording, file upload, text notes, config toggles.
      - Start/Stop buttons bound to `useV2AnalysisSession`.
    - Right column:
      - Tabs or stacked panels:
        - Transcript (live)
        - Audio Quality
        - Quantitative Metrics
        - Manipulation
        - Argument / Reasoning
      - Each backed by a dedicated component and fed via `services` state.

- **Snapshot mode**
  - Secondary button to call `/v2/analyze` once:
    - Reuses the same components but skips streaming path and just injects final results into state.

---

**4. Per‑Service Components**

Design each component to handle partial + final states:

- `TranscriptPanel`
  - Shows:
    - Live transcript with typing effect and speaker labels (from `transcription` service).
  - UI states:
    - `partial`: show animated “Live” badge and subtle shimmer.
    - `final`: remove shimmer, mark as “Final transcript”.

- `AudioQualityPanel`
  - Displays:
    - Noise/clarity meter, basic waveform or simple bar chart.
  - Uses `audio_analysis` service `local.audio_summary` and `gemini.prosody` (if present).

- `QuantitativeMetricsPanel`
  - Shows:
    - Words/min, pauses, talk ratio, etc.
  - For `phase="coarse"`:
    - Render hints with “updating…” label.
  - For `phase="final"`:
    - Replace with stable numeric cards.

- `ManipulationPanel`
  - Displays:
    - Overall manipulation score (0–1), confidence, key flags, rationales.
  - Partial:
    - Show a “draft” bar with lower opacity, maybe “early estimate”.
  - Final:
    - Solid styling, with a clear label (e.g., “Final assessment”).

- `ArgumentStructurePanel`
  - Displays:
    - Claim list or simple graph: who said what, support vs challenge.
  - Partial:
    - Basic outline with “refining…” label.
  - Final:
    - Full structure with tooltips and speaker colors.

Each component only depends on its slice: `services[serviceName].current`, `phase`, `partial`, `errors`.

---

**5. Controls, Errors, and UX Polishing**

- **Controls**
  - Record button:
    - Uses existing audio capture logic but now always posts to v2 endpoints.
  - Stop button:
    - Closes EventSource and finalizes state; UI stops “live” indicators.

- **Errors**
  - Per‑service:
    - Show a small error banner in the relevant panel when `errors.length > 0`.
  - Global:
    - If the stream fails entirely, show a top‑level error but keep already received results visible.

- **Guidance**
  - Small inline text:
    - Explain that early results are coarse and may change until final.

---

**6. De‑risking and Tests**

- **Remove v1 references**
  - Search for `/analyze` or `v1` in src and:
    - Replace with v2 or delete dead code.
  - Update any hardcoded response assumptions to use v2 payload shape.

- **Unit tests (Vitest)**
  - For `useV2AnalysisSession`:
    - Simulate sequences of SSE events and assert state transitions.
  - For key components:
    - Render with partial vs final data and snapshot the DOM output.

- **Smoke test flow**
  - Manual:
    - Start server, run frontend, record a short sample:
      - Check live transcript, audio, metrics, manipulation, argument panels update over time.
      - Confirm no v1 calls in the network tab.

---
