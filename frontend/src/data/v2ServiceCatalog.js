export const V2_SERVICE_CATALOG = [
  {
    key: "transcription",
    title: "Transcription",
    description: "Live speech-to-text with automatic cleanup and diarization hooks.",
    accent: "emerald",
    kpi: [
      { label: "Characters", compute: (payload = {}) => (payload.transcript ? `${payload.transcript.length} chars` : "—") },
      { label: "Source", compute: (payload = {}) => (payload.auto_generated ? "Auto" : payload.transcript ? "Provided" : "Pending" ) }
    ]
  },
  {
    key: "audio_analysis",
    title: "Audio Quality",
    description: "Signal-to-noise, loudness, and channel level diagnostics.",
    accent: "cyan",
    kpi: [
      { label: "Quality", compute: (payload = {}) => payload.local?.overall_quality ?? "—" },
      { label: "Score", compute: (payload = {}) => (payload.local?.quality_score ?? "—") }
    ]
  },
  {
    key: "quantitative_metrics",
    title: "Interaction Metrics",
    description: "Word counts, speech rate, and engagement signals from the transcript.",
    accent: "violet",
    kpi: [
      { label: "Words", compute: (payload = {}) => payload.local?.numerical_linguistic_metrics?.word_count ?? "—" },
      { label: "Speech Rate", compute: (payload = {}) => {
        const wpm = payload.local?.numerical_linguistic_metrics?.speech_rate_wpm;
        return wpm ? `${wpm} wpm` : "—";
      } }
    ]
  },
  {
    key: "manipulation",
    title: "Manipulation & Influence",
    description: "LLM review for coercion, gaslighting, or anchoring attempts.",
    accent: "rose",
    kpi: [
      { label: "Score", compute: (payload = {}) => payload.gemini?.manipulation_score ?? payload.local?.manipulation_score ?? "—" },
      { label: "Tactics", compute: (payload = {}) => {
        const tactics = payload.gemini?.manipulation_tactics || payload.local?.manipulation_tactics;
        return Array.isArray(tactics) ? tactics.length : 0;
      } }
    ]
  },
  {
    key: "argument",
    title: "Argument Structure",
    description: "Checks coherence, supporting evidence, and logical consistency.",
    accent: "amber",
    kpi: [
      { label: "Coherence", compute: (payload = {}) => payload.gemini?.overall_argument_coherence_score ?? payload.local?.overall_argument_coherence_score ?? "—" },
      { label: "Weaknesses", compute: (payload = {}) => {
        const weaknesses = payload.gemini?.argument_weaknesses || payload.local?.argument_weaknesses;
        return Array.isArray(weaknesses) ? weaknesses.length : 0;
      } }
    ]
  },
  {
    key: "linguistic_analysis",
    title: "Linguistic Forensics",
    description: "Legacy NLP heuristics for hedging, distancing, and filler words.",
    accent: "indigo",
    planned: true
  },
  {
    key: "emotion_analysis",
    title: "Emotion Pulse",
    description: "Tracks swings in affect, tension, and empathy cues.",
    accent: "fuchsia",
    planned: true
  },
  {
    key: "psychological_profile",
    title: "Psychological Signals",
    description: "Maps cognitive load indicators and stress markers.",
    accent: "blue",
    planned: true
  },
  {
    key: "conversation_flow",
    title: "Conversation Flow",
    description: "Detects derailment, evasiveness, and cadence anomalies.",
    accent: "sky",
    planned: true
  },
  {
    key: "behavioral_patterns",
    title: "Behavioral Patterns",
    description: "Cross-turn behavioral consistency checks.",
    accent: "lime",
    planned: true
  },
  {
    key: "verification_suggestions",
    title: "Verification",
    description: "Suggests follow-up actions to validate claims.",
    accent: "teal",
    planned: true
  },
  {
    key: "session_insights",
    title: "Session Insights",
    description: "Summaries, trust shifts, and longitudinal notes.",
    accent: "slate",
    planned: true
  },
  {
    key: "recommendations",
    title: "Recommendations",
    description: "Actionable coaching and escalation suggestions.",
    accent: "orange",
    planned: true
  }
];

export const getServiceMetaByKey = (key) => V2_SERVICE_CATALOG.find((service) => service.key === key);
