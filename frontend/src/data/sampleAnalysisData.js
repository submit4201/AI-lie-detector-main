// Sample analysis data for testing the enhanced frontend
export const sampleAnalysisResult = {
  session_id: "test-session-123",
  timestamp: "2024-06-07T10:30:00Z",
  transcript: "Well, I was at the office yesterday, you know, working on the quarterly report. I definitely didn't leave early or anything like that. I mean, why would I? There's so much work to do, and I'm really committed to getting everything done on time.",
  speaker_transcripts: {
    "Speaker 1": "Well, I was at the office yesterday, you know, working on the quarterly report.",
    "Speaker 2": "I definitely didn't leave early or anything like that. I mean, why would I?"
  },
  credibility_score: 65,
  confidence_level: "medium",
  
  // Risk Assessment
  risk_assessment: {
    overall_risk: "medium",
    risk_factors: [
      "Presence of hedge words (well, you know)",
      "Defensive language patterns",
      "Unsolicited denials"
    ],
    mitigation_suggestions: [
      "Ask follow-up questions about specific times",
      "Request verification of office attendance",
      "Probe deeper into the defensive responses"
    ]
  },

  // Red flags per speaker
  red_flags_per_speaker: {
    "Speaker 1": [
      "Use of hedge words 'well', 'you know'",
      "Vague time references"
    ],
    "Speaker 2": [
      "Unprompted denial 'didn't leave early'",
      "Defensive questioning 'why would I?'"
    ]
  },

  // Emotion Analysis
  emotion_analysis: [
    {
      emotion: "anxiety",
      intensity: 0.7,
      time_segment: "0:00-0:15",
      context: "Beginning of statement shows elevated stress"
    },
    {
      emotion: "defensiveness", 
      intensity: 0.8,
      time_segment: "0:15-0:30",
      context: "Strong defensive response to unasked question"
    }
  ],

  // Gemini Summary
  gemini_summary: {
    credibility: "Moderate credibility with concerning patterns of defensive language and hedge words indicating potential deception",
    key_concerns: "Unprompted denials and defensive questioning suggest speaker may be concealing information about their whereabouts",
    tone: "Initially casual but becomes increasingly defensive",
    motivation: "Appears motivated to convince listener of their story while avoiding direct scrutiny",
    emotional_state: "Anxious and defensive, particularly when discussing office attendance",
    communication_style: "Conversational with defensive interruptions and qualifying language"
  },

  // Linguistic Analysis
  linguistic_analysis: {
    formality_score: 0.3,
    speech_rate_wpm: 145,
    avg_sentence_length: 12.5,
    filler_word_frequency: 8.2,
    word_count: 85,
    unique_words: 62,
    complexity_score: 0.4,
    pause_patterns: "Longer pauses before potentially deceptive statements"
  },

  // Advanced Analysis Features
  manipulation_assessment: {
    manipulation_score: 72,
    tactics_identified: [
      "Deflection through questioning",
      "Unsolicited information provision",
      "Emotional manipulation through commitment statements"
    ],
    examples: [
      {
        tactic: "Deflection",
        phrase: "I mean, why would I?",
        explanation: "Redirects attention away from the original question"
      }
    ]
  },

  argument_analysis: {
    overall_argument_coherence_score: 58,
    strengths: ["Clear timeline reference", "Specific work context"],
    weaknesses: ["Defensive tone undermines credibility", "Unprompted denials raise suspicion"],
    logical_flow: "Statement starts coherently but becomes defensive without prompting"
  },

  speaker_attitude: {
    respect_level_score: 45,
    sarcasm_detected: true,
    sarcasm_confidence: 0.6,
    tone_indicators: ["defensive", "slightly sarcastic", "anxious"]
  },

  enhanced_understanding: {
    key_inconsistencies: [
      "Claims commitment while showing defensive body language",
      "Provides unsolicited denials about leaving early"
    ],
    areas_of_evasiveness: [
      "Specific timing of office departure",
      "Details about what 'working on report' actually involved"
    ],
    suggested_follow_up_questions: [
      "What specific time did you arrive at and leave the office?",
      "Who else was working on the quarterly report with you?",
      "Can you provide more details about what you accomplished on the report?"
    ],
    unverified_claims: [
      "Working on quarterly report",
      "Staying late at office",
      "High level of work commitment"
    ]
  },

  // Audio Analysis
  audio_analysis: {
    vocal_stress_indicators: ["pitch variations", "speaking rate changes"],
    pitch_analysis: "Elevated pitch during denial statements",
    pause_patterns: "Unusual pauses before key claims",
    vocal_confidence_level: 0.6,
    speaking_pace_consistency: 0.4
  },

  // Session Insights
  session_insights: {
    behavioral_evolution: "Initial confidence declining to defensive posture",
    consistency_across_topics: 0.5,
    stress_progression: "Increasing stress levels throughout statement",
    credibility_trend: "downward",
    interaction_patterns: ["becoming more defensive", "increasing hedge word usage"]
  },

  // Recommendations
  recommendations: [
    "Focus follow-up questions on specific timeline verification",
    "Request corroborating evidence for office attendance",
    "Address the defensive tone directly to understand its cause",
    "Probe deeper into the unprompted denial about leaving early"
  ]
};

export const sampleSessionHistory = [
  {
    id: "analysis-1",
    timestamp: "2024-06-07T09:00:00Z",
    credibility_score: 78,
    overall_risk: "low",
    summary: "Initial statement about project status - high credibility",
    duration: 45
  },
  {
    id: "analysis-2", 
    timestamp: "2024-06-07T09:30:00Z",
    credibility_score: 52,
    overall_risk: "medium",
    summary: "Questions about budget allocation - some inconsistencies",
    duration: 120
  },
  {
    id: "analysis-3",
    timestamp: "2024-06-07T10:30:00Z", 
    credibility_score: 65,
    overall_risk: "medium",
    summary: "Office attendance verification - defensive responses",
    duration: 30
  }
];
