from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

# --- Pydantic Models for API Documentation ---
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message describing what went wrong.")
    # Optional error code for more specific error handling
    code: Optional[int] = Field(None, description="Optional error code for specific error identification.")
    # Timestamp of when the error occurred
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the error occurred.")
    # Additional details for debugging (optional)
    details: Optional[Dict[str, Any]] = Field(None, description="Optional additional details for debugging purposes.")
    # Suggestion for resolution (optional)
    suggestion: Optional[str] = Field(None, description="Optional suggestion for resolving the error.")
    # Documentation link for more info (optional)
    documentation_link: Optional[str] = Field(None, description="Optional URL to documentation for more information.")
    # User-friendly message (optional)
    user_friendly_message: Optional[str] = Field(None, description="Optional user-friendly message for end-users.")
    # Severity level (optional)
    severity: Optional[str] = Field(None, description="Optional severity level of the error (e.g., low, medium, high).")
    # path or location of the error (optional)
    location: Optional[str] = Field(None, description="Optional path or location where the error occurred.")
    
    
class AudioQualityMetrics(BaseModel):
    duration: float = Field(default=0.0, description="Duration of the audio in seconds.")
    sample_rate: int = Field(default=0, description="Sample rate of the audio in Hz.")
    channels: int = Field(default=0, description="Number of audio channels.")
    loudness: float = Field(default=0.0, description="Loudness of the audio in dBFS.")
    quality_score: int = Field(default=0, description="Overall quality score (0-100).")
    overall_quality: str = Field(default="Good", description="Overall quality assessment (e.g., 'Good', 'Fair', 'Poor').")
    signal_to_noise_ratio: float = Field(default=0.0, description="Signal to noise ratio.")
    clarity_score: float = Field(default=50.0, description="Audio clarity score (0-100).")
    volume_consistency: float = Field(default=50.0, description="Volume consistency score (0-100).")
    background_noise_level: float = Field(default=0.0, description="Background noise level assessment.")

class EmotionScore(BaseModel):
    label: str = Field(default="", description="Emotion label (e.g., 'anger', 'joy').")
    score: float = Field(default=0.0, description="Confidence score for the emotion (0.0-1.0).")

class NumericalLinguisticMetrics(BaseModel):
    word_count: int = Field(default=0, description="Total number of words in the transcript.")
    unique_word_count: int = Field(default=0, description="Total number of unique words in the transcript.")
    hesitation_marker_count: int = Field(default=0, description="Number of common hesitation markers (e.g., um, uh, er, ah).")
    filler_word_count: int = Field(default=0, description="Number of common filler words (e.g., like, you know, basically).")  # Differentiated from hesitation markers
    qualifier_count: int = Field(default=0, description="Number of uncertainty qualifiers (e.g., maybe, perhaps, might, sort of, kind of).")
    certainty_indicator_count: int = Field(default=0, description="Number of certainty indicators (e.g., definitely, absolutely, sure, clearly).")
    repetition_count: int = Field(default=0, description="Number of significant word or phrase repetitions detected.")
    sentence_count: int = Field(default=0, description="Total number of sentences.")
    avg_word_length_chars: float = Field(default=0.0, description="Average word length in characters.")
    avg_sentence_length_words: float = Field(default=0.0, description="Average number of words per sentence.")
    speech_rate_wpm: Optional[float] = Field(default=None, description="Speech rate in words per minute (calculated if audio duration is known or can be estimated).")
    hesitation_rate_hpm: Optional[float] = Field(default=None, description="Hesitation markers per minute (calculated if audio duration is known or can be estimated).")
    vocabulary_richness_ttr: float = Field(default=0.0, description="Type-Token Ratio (unique words / total words) as a measure of vocabulary richness.")
    confidence_metric_ratio: Optional[float] = Field(default=None, description="Ratio of certainty indicators to the sum of certainty and uncertainty indicators. Ranges from 0 (all uncertainty) to 1 (all certainty), or None if no indicators found.")
    formality_score_calculated: float = Field(default=0.0, description="Calculated formality score (0-100) based on specific linguistic cues, not LLM opinion.")
    complexity_score_calculated: float = Field(default=0.0, description="Calculated linguistic complexity score (0-100) based on metrics like sentence length, word length, etc.")

class LinguisticAnalysis(BaseModel):
    # Descriptive analysis (for backwards compatibility or direct LLM assessment)
    speech_patterns_description: str = Field(default="Speech patterns analysis not available.", description="LLM analysis of speech rhythm, pace, pauses not covered by specific counts.")
    word_choice_description: str = Field(default="Word choice analysis not available.", description="LLM analysis of vocabulary and phrasing choices, beyond simple counts.")
    emotional_consistency_description: str = Field(default="Emotional consistency analysis not available.", description="LLM assessment of consistency between claimed emotions and linguistic expression.")
    detail_level_description: str = Field(default="Detail level analysis not available.", description="LLM assessment of whether the level of detail is appropriate versus vague or overly granular.")

    # LLM-generated analysis of numerical linguistic data (referencing NumericalLinguisticMetrics)
    word_count_analysis: str = Field(default="Word count analysis not available.", description="LLM interpretation of the significance of the word count in context.")
    hesitation_marker_analysis: str = Field(default="Hesitation marker analysis not available.", description="LLM interpretation of the impact of hesitation markers on communication.")
    filler_word_analysis: str = Field(default="Filler word analysis not available.", description="LLM interpretation of the impact of filler words on communication.")
    qualifier_analysis: str = Field(default="Qualifier analysis not available.", description="LLM interpretation of the impact of uncertainty qualifiers.")
    certainty_indicator_analysis: str = Field(default="Certainty indicator analysis not available.", description="LLM interpretation of the impact of certainty indicators.")
    repetition_analysis: str = Field(default="Repetition analysis not available.", description="LLM interpretation of word/phrase repetitions and their implications.")
    sentence_count_analysis: str = Field(default="Sentence count analysis not available.", description="LLM interpretation of the sentence count in context.")
    avg_word_length_analysis: str = Field(default="Average word length analysis not available.", description="LLM interpretation of average word length and its implications.")
    avg_sentence_length_analysis: str = Field(default="Average sentence length analysis not available.", description="LLM interpretation of average sentence length and its implications.")
    speech_rate_analysis: str = Field(default="Speech rate analysis not available.", description="LLM interpretation of speech rate (WPM) and its impact, if WPM is available.")
    hesitation_rate_analysis: str = Field(default="Hesitation rate analysis not available.", description="LLM interpretation of hesitation rate (HPM) and its impact, if HPM is available.")
    vocabulary_richness_analysis: str = Field(default="Vocabulary richness analysis not available.", description="LLM interpretation of vocabulary richness (TTR) and its implications.")
    confidence_metric_analysis: str = Field(default="Confidence metric analysis not available.", description="LLM interpretation of the calculated confidence metric ratio.")
    formality_score_analysis: str = Field(default="Formality score analysis not available.", description="LLM interpretation of the calculated formality score.")
    complexity_score_analysis: str = Field(default="Complexity score analysis not available.", description="LLM interpretation of the calculated complexity score.")
    pause_occurrence_analysis: str = Field(default="Pause analysis not available.", description="LLM analysis of pauses (based on transcript markers or audio silence detection) and their significance.")  # Renamed from pause_analysis
    overall_linguistic_style_summary: str = Field(default="Overall linguistic style summary not available.", description="LLM's comprehensive summary of linguistic patterns and their implications.")  # Renamed from overall_linguistic_analysis

class RiskAssessment(BaseModel):
    overall_risk: str = Field(default="Risk assessment not available.", description="Overall risk level (low/medium/high).")
    risk_factors: List[str] = Field(default_factory=list, description="Specific risk factors identified.")
    mitigation_suggestions: List[str] = Field(default_factory=list, description="Suggestions to mitigate identified risks.")
    # New fields for risk assessment
    risk_factors_analysis: str = Field(default="Risk factors analysis not available.", description="Analysis of each risk factor and its implications.")
    mitigation_suggestions_analysis: str = Field(default="Mitigation suggestions analysis not available.", description="Analysis of each mitigation suggestion and its potential impact.")
    overall_risk_analysis: str = Field(default="Overall risk analysis not available.", description="Overall analysis of the risk assessment and its implications.")
    confidence_in_risk_assessment: float = Field(default=0.0, description="Confidence level in the risk assessment (0-1).")

class SessionStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    PENDING = "pending"

# New Models for Enhanced Analysis Dimensions
class NewSessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    status: SessionStatus = Field(default=SessionStatus.CREATED, description="Current status of the session.")
    message: Optional[str] = Field(None, description="Optional message regarding session creation.")
    

class AnalysisInput(BaseModel):
    session_id: Optional[str] = None
    audio_file_path: Optional[str] = None
    transcript_file_path: Optional[str] = None
    text_input: Optional[str] = None
    language: str = "en"
    user_id: Optional[str] = None
    enable_detailed_analysis: bool = True

class EmotionDetail(BaseModel):
    emotion: str
    score: float
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None

class PatternDetail(BaseModel):
    pattern_type: str  # e.g., "RepetitivePhrasing", "HesitationCluster"
    description: str
    occurrences: int
    examples: List[str] = Field(default_factory=list)
    significance_score: Optional[float] = None  # 0-1 scale

class DialogueAct(BaseModel):
    speaker: str
    act_type: str  # e.g., "Question", "Statement", "Agreement", "Disagreement"
    text_segment: str
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None

class SpeakerSegment(BaseModel):
    speaker_label: str = "Unknown"
    start_time: float
    end_time: float
    transcript_segment: Optional[str] = None

# New Detailed Analysis Models
class ManipulationAssessment(BaseModel):
    is_manipulative: bool = False
    manipulation_score: float = Field(default=0.0, description="Score from 0.0 to 1.0 indicating likelihood of manipulation.")
    manipulation_techniques: List[str] = Field(default_factory=list, description="List of identified manipulation techniques.")
    manipulation_confidence: float = Field(default=0.0, description="Confidence in the manipulation assessment.")
    manipulation_explanation: str = Field(default="Analysis not available.", description="Explanation of the manipulation assessment.")
    manipulation_score_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the manipulation score.")

class ArgumentAnalysis(BaseModel):
    arguments_present: bool = False
    key_arguments: List[Dict[str, str]] = Field(default_factory=list, description="List of key arguments, e.g., {'claim': '...', 'evidence': '...'}."
    )
    argument_strength: float = Field(default=0.0, description="Overall strength of arguments presented (0.0 to 1.0).")
    fallacies_detected: List[str] = Field(default_factory=list, description="List of logical fallacies detected.")
    argument_summary: str = Field(default="Analysis not available.", description="Summary of the arguments.")
    argument_structure_rating: float = Field(default=0.0, description="Rating of the argument structure (0.0 to 1.0).")
    argument_structure_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the argument structure.")

class SpeakerAttitude(BaseModel):
    dominant_attitude: str = Field(default="Neutral", description="Dominant attitude of the speaker.")
    attitude_scores: Dict[str, float] = Field(default_factory=dict, description="Scores for various attitudes, e.g., {'respectful': 0.8}."
    )
    respect_level: str = Field(default="Neutral", description="Assessed level of respect.")
    respect_level_score: float = Field(default=0.0, description="Numerical score for respect level (0.0 to 1.0).")
    respect_level_score_analysis: str = Field(default="Analysis not available.", description="Analysis of the respect level score.")
    formality_score: float = Field(default=0.0, description="Formality score (0.0 informal to 1.0 formal).")
    formality_assessment: str = Field(default="Analysis not available.", description="Qualitative assessment of formality.")
    politeness_score: float = Field(default=0.0, description="Politeness score (0.0 to 1.0).")
    politeness_assessment: str = Field(default="Analysis not available.", description="Qualitative assessment of politeness.")

class EnhancedUnderstanding(BaseModel):
    key_topics: List[str] = Field(default_factory=list, description="Key topics discussed.")
    action_items: List[str] = Field(default_factory=list, description="Identified action items.")
    unresolved_questions: List[str] = Field(default_factory=list, description="Unresolved questions from the conversation.")
    summary_of_understanding: str = Field(default="Analysis not available.", description="Summary of the core understanding derived.")
    contextual_insights: List[str] = Field(default_factory=list, description="Insights based on context.")
    nuances_detected: List[str] = Field(default_factory=list, description="Subtle nuances detected in communication.")
    key_inconsistencies: List[str] = Field(default_factory=list, description="List of key contradictions or inconsistencies in statements.")
    areas_of_evasiveness: List[str] = Field(default_factory=list, description="Topics or questions the speaker seemed to avoid.")
    suggested_follow_up_questions: List[str] = Field(default_factory=list, description="Suggested questions to ask for clarity or further probing.")
    unverified_claims: List[str] = Field(default_factory=list, description="Claims made by the speaker that may require fact-checking.")
    # new fields for enhanced understanding
    key_inconsistencies_analysis: str = Field(default="Key inconsistencies analysis not available.", description="Analysis of each key inconsistency and its implications.")
    areas_of_evasiveness_analysis: str = Field(default="Areas of evasiveness analysis not available.", description="Analysis of each area of evasiveness and its implications.")
    suggested_follow_up_questions_analysis: str = Field(default="Suggested follow-up questions analysis not available.", description="Analysis of each suggested follow-up question and its potential impact.")
    fact_checking_analysis: str = Field(default="Fact checking analysis not available.", description="Analysis of each unverified claim and its implications.")
    deep_dive_analysis: str = Field(default="Deep dive enhanced understanding analysis not available.", description="Deep dive analysis of the enhanced understanding.")


class PsychologicalAnalysis(BaseModel):
    emotional_state: str = Field(default="Neutral", description="Overall emotional state inferred.")
    emotional_state_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred emotional state.")  # Added
    cognitive_load: str = Field(default="Normal", description="Inferred cognitive load (e.g., Low, Normal, High).")
    cognitive_load_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred cognitive load.")  # Added
    stress_level: float = Field(default=0.0, description="Inferred stress level (0.0 to 1.0).")
    stress_level_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred stress level.")
    confidence_level: float = Field(default=0.0, description="Inferred confidence level (0.0 to 1.0).")
    confidence_level_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred confidence level.")  # Added
    psychological_summary: str = Field(default="Analysis not available.", description="Summary of the psychological state analysis.")
    potential_biases: List[str] = Field(default_factory=list, description="Identified potential cognitive biases.")
    potential_biases_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the identified potential cognitive biases and their possible impact.")  # Added

class SessionInsights(BaseModel):
    consistency_analysis: str = Field(default="Consistency analysis not available.", description="Analysis of consistency patterns across session interactions.")
    behavioral_evolution: str = Field(default="Behavioral evolution analysis not available.", description="How speaker behavior has evolved throughout the session.")
    risk_trajectory: str = Field(default="Risk trajectory analysis not available.", description="Trend analysis of risk levels across the session.")
    conversation_dynamics: str = Field(default="Conversation dynamics analysis not available.", description="Analysis of conversation flow and interaction patterns.")
    # new fields for session insights
    consistency_analysis_analysis: str = Field(default="Consistency analysis details not available.", description="Analysis of the consistency analysis and its implications.")
    behavioral_evolution_analysis: str = Field(default="Behavioral evolution details not available.", description="Analysis of the behavioral evolution and its implications.")
    risk_trajectory_analysis: str = Field(default="Risk trajectory details not available.", description="Analysis of the risk trajectory and its implications.")
    conversation_dynamics_analysis: str = Field(default="Conversation dynamics details not available.", description="Analysis of the conversation dynamics and its implications.")
    deep_dive_analysis: str = Field(default="Deep dive session insights analysis not available.", description="Deep dive analysis of the session insights.")
    overall_session_analysis: str = Field(default="Overall session analysis not available.", description="Overall analysis of the session insights.")
    trust_building_indicators: str = Field(default="Trust building indicators analysis not available.", description="Analysis of trust-building indicators in the conversation.")
    concern_escalation: str = Field(default="Concern escalation analysis not available.", description="Analysis of concern escalation patterns in the conversation.")


class AudioAnalysis(BaseModel):
    # Existing fields, some refined for clarity and with added analysis fields
    speech_clarity_score: float = Field(default=0.0, description="Clarity of speech (0.0 to 1.0).")
    speech_clarity_analysis: Optional[str] = Field(default="Analysis not available.", description="Explanation of the speech clarity assessment.")

    background_noise_assessment: str = Field(default="Low", description="Qualitative level of background noise (e.g., Low, Medium, High).")
    background_noise_analysis: Optional[str] = Field(default="Analysis not available.", description="Details about the background noise characteristics and impact.")

    average_speech_rate_wpm: int = Field(default=0, description="Average speech rate in words per minute, derived from audio timing and transcript word count.")
    speech_rate_variability_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of speech rate consistency and significant variations observed in the audio.")

    intonation_patterns_analysis: str = Field(default="Analysis not available.", description="Description of intonation patterns (e.g., monotonous, expressive, questioning) and their perceived implications from the audio.")

    overall_audio_quality_assessment: str = Field(default="Analysis not available.", description="Overall qualitative assessment of the audio recording's technical quality.")

    # New fields for deeper audio analysis
    audio_duration_seconds: Optional[float] = Field(default=None, description="Duration of the analyzed audio segment in seconds.")

    loudness_dbfs: Optional[float] = Field(default=None, description="Average loudness of the audio in dBFS.")
    loudness_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of audio volume levels (e.g., too quiet, too loud, appropriate, dynamic range).")

    signal_to_noise_ratio_db: Optional[float] = Field(default=None, description="Estimated signal-to-noise ratio in dB.")
    signal_to_noise_ratio_analysis: Optional[str] = Field(default="Analysis not available.", description="Explanation of SNR and its impact on intelligibility.")

    pitch_profile_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of pitch characteristics from the audio (e.g., average, range, variability, common contours) and perceived meaning.")

    voice_timbre_description: Optional[str] = Field(default="Analysis not available.", description="Description of voice timbre/quality observed in the audio (e.g., resonant, thin, hoarse, nasal, breathy).")

    vocal_effort_assessment: Optional[str] = Field(default="Analysis not available.", description="Assessment of vocal effort apparent in the audio (e.g., strained, relaxed, projected, whispered).")

    acoustic_event_detection: List[str] = Field(default_factory=list, description="Notable non-speech acoustic events detected from the audio (e.g., cough, door slam, laughter).")
    acoustic_event_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of detected acoustic events and their potential relevance or impact.")

    pause_characteristics_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of pause frequency, duration, and placement from an acoustic perspective (silence detection).")

    vocal_stress_indicators_acoustic: List[str] = Field(default_factory=list, description="Acoustically identified vocal stress indicators from the audio (e.g., pitch breaks, voice tremors, strained phonation).")
    vocal_stress_indicators_acoustic_analysis: Optional[str] = Field(default="Analysis not available.", description="Explanation of the acoustically identified vocal stress indicators.")


class InteractionMetrics(BaseModel):  # Renamed from QuantitativeMetrics
    talk_to_listen_ratio: Optional[float] = Field(default=None, description="Ratio of talking time for a primary speaker to total speaking time or to other speakers' time. Context-dependent.")
    speaker_turn_duration_avg_seconds: Optional[float] = Field(default=None, description="Average duration of speaker turns in seconds, if speaker diarization is available.")
    interruptions_count: Optional[int] = Field(default=None, description="Number of interruptions detected, typically requiring diarization or explicit markers.")
    sentiment_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Trend of sentiment over time or segments, e.g., [{'segment': 'opening', 'sentiment_score': 0.7, 'sentiment_label': 'positive'}].")
    overall_sentiment_label: Optional[str] = Field(default=None, description="Dominant sentiment classification inferred from the interaction (e.g., positive, neutral, negative).")
    overall_sentiment_score: Optional[float] = Field(default=None, description="Normalized sentiment score between 0 and 1 where 0 is negative and 1 is positive.")
    sentiment_confidence: Optional[float] = Field(default=None, description="Confidence score for the dominant sentiment between 0 and 1.")
    emotion_distribution: List[Dict[str, Any]] = Field(default_factory=list, description="Distribution of notable emotions with optional scores or weights.")
    engagement_level: Optional[str] = Field(default=None, description="Qualitative engagement assessment such as Low, Medium, or High.")
    question_to_statement_ratio: Optional[float] = Field(default=None, description="Ratio of interrogative sentences to declarative statements.")
    conversation_energy_score: Optional[float] = Field(default=None, description="Relative measure (0-1) of conversational energy inferred from pacing, punctuation, and emphasis cues.")
    notable_interaction_events: List[str] = Field(default_factory=list, description="List of notable behaviors observed (e.g., 'frequent interruptions', 'high filler usage').")
    # Removed word_count and vocabulary_richness_score as they are in NumericalLinguisticMetrics

class ConversationFlow(BaseModel):
    engagement_level: str = Field(default="Medium", description="Overall engagement level (e.g., Low, Medium, High).")
    topic_coherence_score: float = Field(default=0.0, description="Coherence of topics discussed (0.0 to 1.0).")
    conversation_dominance: Dict[str, float] = Field(default_factory=dict, description="Speaker dominance, e.g., {'speaker_A': 0.6, 'speaker_B': 0.4}."
    )
    turn_taking_efficiency: str = Field(default="Analysis not available.", description="Assessment of turn-taking efficiency.")
    conversation_phase: str = Field(default="Analysis not available.", description="Current phase of conversation (e.g., Opening, Development, Closing).")
    flow_disruptions: List[str] = Field(default_factory=list, description="Identified disruptions in conversation flow.")

# Main Analysis Response Model
class AnalyzeResponse(BaseModel):
    session_id: str = ""
    transcript: str = ""
    enhanced_transcript: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    overall_sentiment: str = "Neutral"
    overall_sentiment_score: float = 0.0
    emotions_detected: List[str] = Field(default_factory=list)
    emotion_details: List[EmotionDetail] = Field(default_factory=list)
    communication_effectiveness_score: float = 0.0
    key_phrases: List[str] = Field(default_factory=list)
    summary: str = "Analysis not available."
    alerts: List[str] = Field(default_factory=list)
    patterns_identified: List[PatternDetail] = Field(default_factory=list)
    numerical_linguistic_metrics: Optional[NumericalLinguisticMetrics] = None  # Added
    dialogue_acts: List[DialogueAct] = Field(default_factory=list)
    speaker_diarization: List[SpeakerSegment] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, description="Overall confidence in the analysis results.")
    version: str = "2.1.0"  # Updated version due to significant model changes

    # Modularized analysis components
    manipulation_assessment: Optional[ManipulationAssessment] = None
    argument_analysis: Optional[ArgumentAnalysis] = None
    speaker_attitude: Optional[SpeakerAttitude] = None
    enhanced_understanding: Optional[EnhancedUnderstanding] = None
    psychological_analysis: Optional[PsychologicalAnalysis] = None
    audio_analysis: Optional[AudioAnalysis] = None
    interaction_metrics: Optional[InteractionMetrics] = None  # Updated from quantitative_metrics
    linguistic_analysis: Optional[LinguisticAnalysis] = None  # Ensure this is added if it wasn't explicitly part of AnalyzeResponse before
    conversation_flow: Optional[ConversationFlow] = None

class ProgressUpdate(BaseModel):
    stage: str
    percentage: float
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AnalyzeStreamResponse(BaseModel):
    event_type: str  # e.g., "full_response", "interim_transcript", "analysis_update", "error", "progress_update"
    data: Optional[Any] = None  # Can be AnalyzeResponse, str (for transcript), or specific analysis model
    session_id: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[ProgressUpdate] = None  # For granular progress updates

class StreamInput(BaseModel):
    session_id: str
    # Potentially other parameters like what to stream

# Session Management Models
class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    initial_audio_path: Optional[str] = None  # Path to pre-existing audio
    initial_transcript_path: Optional[str] = None  # Path to pre-existing transcript
    configuration: Optional[Dict[str, Any]] = None  # e.g., specific analyses to run

class SessionCreateResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str
    created_at: str  # ISO format timestamp

class SessionUpdateRequest(BaseModel):
    status: Optional[SessionStatus] = None
    # Potentially other fields to update, e.g., add new data

class SessionUpdateResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str
    updated_at: str  # ISO format timestamp

class SessionResponse(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    status: SessionStatus
    created_at: str
    updated_at: Optional[str] = None
    # Potentially links to results or full analysis data if small
    analysis_summary: Optional[Dict[str, Any]] = None  # A brief overview

class SessionListItem(BaseModel):
    session_id: str
    session_name: Optional[str] = None
    status: SessionStatus
    created_at: str


# Models for session history and deletion responses
class SessionHistoryItem(BaseModel):
    item_id: str
    timestamp: datetime
    title: Optional[str] = Field(None, description="Short title for the history entry")
    summary: Optional[str] = Field(None, description="Brief summary of this history entry")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional extended details for the history item")


class SessionHistoryResponse(BaseModel):
    session_id: str
    history: List[SessionHistoryItem] = Field(default_factory=list, description="Ordered list of history items for the session")


class DeleteSessionResponse(BaseModel):
    session_id: str
    message: str

class SessionInsightsInput(BaseModel):  # This is for multi-session analysis
    session_ids: List[str]
    insight_types: Optional[List[str]] = None  # e.g., ["sentiment_trend", "topic_comparison"]

class SessionInsight(BaseModel):  # This is for multi-session analysis
    insight_type: str
    data: Any  # Could be charts, tables, text summaries
    description: Optional[str] = None

class SessionInsightsResponse(BaseModel):  # This is for multi-session analysis
    requested_session_ids: List[str]
    insights: List[SessionInsight] = Field(default_factory=list)
    summary_across_sessions: Optional[str] = None

class GeminiSummary(BaseModel):
    tone: str = Field(default="Analysis not available", description="Description of the speaker's tone.")
    motivation: str = Field(default="Analysis not available", description="Analysis of the speaker's potential motivation.")
    credibility: str = Field(default="Analysis not available", description="Assessment of the speaker's credibility based on content and delivery.")
    emotional_state: str = Field(default="Analysis not available", description="Description of the speaker's emotional state.")
    communication_style: str = Field(default="Analysis not available", description="Analysis of the speaker's communication style.")
    key_concerns: str = Field(default="Analysis not available", description="Key concerns raised by the analysis.")
    strengths: str = Field(default="Analysis not available", description="Strengths of the speaker's communication.")


# Enhanced Acoustic Metrics Models
class EnhancedAcousticMetrics(BaseModel):
    """Comprehensive acoustic features for advanced voice analysis."""
    # Pitch-related metrics
    pitch_jitter: float = Field(default=0.0, description="F0 cycle deviation - variation in fundamental frequency period.")
    pitch_shimmer: float = Field(default=0.0, description="Amplitude instability between consecutive periods.")
    pitch_mean: float = Field(default=0.0, description="Mean fundamental frequency (F0) in Hz.")
    pitch_std: float = Field(default=0.0, description="Standard deviation of fundamental frequency.")
    pitch_range: float = Field(default=0.0, description="Range of pitch values (max - min) in Hz.")
    
    # Vocal tremor
    vocal_tremor_rate: Optional[float] = Field(default=None, description="Rate of vocal tremor in Hz (if detected).")
    vocal_tremor_intensity: Optional[float] = Field(default=None, description="Intensity of vocal tremor (0.0-1.0).")
    
    # Formant dispersion (F1/F2/F3)
    formant_f1_mean: float = Field(default=0.0, description="Mean first formant frequency in Hz.")
    formant_f2_mean: float = Field(default=0.0, description="Mean second formant frequency in Hz.")
    formant_f3_mean: float = Field(default=0.0, description="Mean third formant frequency in Hz.")
    formant_dispersion: float = Field(default=0.0, description="Dispersion across formants (measure of vowel space).")
    formant_std: float = Field(default=0.0, description="Standard deviation of formant values.")
    formant_range: float = Field(default=0.0, description="Range of formant values.")
    
    # Intensity and loudness
    intensity_mean: float = Field(default=0.0, description="Mean intensity in dB.")
    intensity_std: float = Field(default=0.0, description="Standard deviation of intensity.")
    intensity_range: float = Field(default=0.0, description="Range of intensity values.")
    intensity_slope: Optional[float] = Field(default=None, description="Slope of intensity curve over time.")
    loudness_mean: float = Field(default=0.0, description="Mean loudness in sones.")
    loudness_std: float = Field(default=0.0, description="Standard deviation of loudness.")
    loudness_range: float = Field(default=0.0, description="Range of loudness values.")
    loudness_slope: Optional[float] = Field(default=None, description="Slope of loudness curve over time.")
    
    # Pause characteristics
    pause_duration_total: float = Field(default=0.0, description="Total duration of unfilled pauses in seconds.")
    pause_count: int = Field(default=0, description="Number of detected pauses.")
    pause_duration_mean: float = Field(default=0.0, description="Mean pause duration in seconds.")
    pause_duration_std: float = Field(default=0.0, description="Standard deviation of pause durations.")
    pause_rate: float = Field(default=0.0, description="Pauses per minute.")
    
    # Speech rate
    speech_rate_wpm: float = Field(default=0.0, description="Speech rate in words per minute.")
    speech_rate_sps: float = Field(default=0.0, description="Speech rate in syllables per second.")
    articulation_rate: float = Field(default=0.0, description="Articulation rate (syllables/sec excluding pauses).")
    
    # Harmonics-to-Noise Ratio (HNR)
    hnr_mean: float = Field(default=0.0, description="Mean harmonics-to-noise ratio in dB.")
    hnr_std: float = Field(default=0.0, description="Standard deviation of HNR.")
    hnr_range: float = Field(default=0.0, description="Range of HNR values.")
    
    # Energy metrics
    energy_mean: float = Field(default=0.0, description="Mean energy.")
    energy_std: float = Field(default=0.0, description="Standard deviation of energy.")
    energy_range: float = Field(default=0.0, description="Range of energy values.")
    
    # Point process metrics
    point_process_mean: float = Field(default=0.0, description="Mean point process value.")
    point_process_std: float = Field(default=0.0, description="Standard deviation of point process.")
    point_process_range: float = Field(default=0.0, description="Range of point process values.")
    
    # Quality indicators
    voice_quality_score: float = Field(default=0.0, description="Overall voice quality score (0.0-1.0).")
    signal_to_noise_ratio: float = Field(default=0.0, description="Signal-to-noise ratio in dB.")


# Linguistic Enhancement Metrics
class LinguisticEnhancementMetrics(BaseModel):
    """Enhanced linguistic features for detailed text analysis."""
    # Pronoun analysis
    pronoun_ratio_first_person: float = Field(default=0.0, description="Ratio of first-person pronouns (I/me/my) to total words.")
    pronoun_count_first_person: int = Field(default=0, description="Count of first-person pronouns.")
    pronoun_ratio_second_person: float = Field(default=0.0, description="Ratio of second-person pronouns (you/your) to total words.")
    pronoun_ratio_third_person: float = Field(default=0.0, description="Ratio of third-person pronouns (he/she/they) to total words.")
    
    # Article usage
    article_usage_ratio: float = Field(default=0.0, description="Ratio of articles (a/an/the) to total words.")
    article_count: int = Field(default=0, description="Count of articles.")
    definite_article_ratio: float = Field(default=0.0, description="Ratio of definite articles (the) to total articles.")
    
    # Sentence complexity
    sentence_complexity_score: float = Field(default=0.0, description="Sentence complexity score (0.0-1.0).")
    avg_clause_per_sentence: float = Field(default=0.0, description="Average number of clauses per sentence.")
    subordinate_clause_ratio: float = Field(default=0.0, description="Ratio of subordinate clauses to total sentences.")
    
    # Emotional leakage
    emotional_leakage_words: List[str] = Field(default_factory=list, description="Detected emotional leakage words.")
    emotional_leakage_count: int = Field(default=0, description="Count of emotional leakage words.")
    emotional_leakage_ratio: float = Field(default=0.0, description="Ratio of emotional leakage words to total words.")
    
    # Response latency (requires timestamp tracking)
    response_latency_mean: Optional[float] = Field(default=None, description="Mean response latency in seconds.")
    response_latency_std: Optional[float] = Field(default=None, description="Standard deviation of response latency.")
    
    # Prosodic congruence (acoustic-linguistic mismatch)
    prosodic_congruence_score: Optional[float] = Field(default=None, description="Prosodic congruence score (0.0-1.0).")
    prosodic_mismatches: List[str] = Field(default_factory=list, description="Detected prosodic-linguistic mismatches.")


# Baseline Profile for User Calibration
class BaselineProfile(BaseModel):
    """User baseline profile for normalization and calibration."""
    user_id: Optional[str] = Field(default=None, description="User identifier.")
    session_id: Optional[str] = Field(default=None, description="Calibration session identifier.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Profile creation timestamp.")
    
    # Acoustic baselines
    baseline_pitch_mean: float = Field(default=0.0, description="Baseline mean pitch.")
    baseline_pitch_std: float = Field(default=0.0, description="Baseline pitch standard deviation.")
    baseline_intensity_mean: float = Field(default=0.0, description="Baseline mean intensity.")
    baseline_speech_rate: float = Field(default=0.0, description="Baseline speech rate (WPM).")
    baseline_pause_rate: float = Field(default=0.0, description="Baseline pause rate.")
    baseline_hnr_mean: float = Field(default=0.0, description="Baseline HNR mean.")
    
    # Linguistic baselines
    baseline_hesitation_rate: float = Field(default=0.0, description="Baseline hesitation rate.")
    baseline_filler_rate: float = Field(default=0.0, description="Baseline filler word rate.")
    baseline_pronoun_ratio: float = Field(default=0.0, description="Baseline first-person pronoun ratio.")
    baseline_complexity_score: float = Field(default=0.0, description="Baseline sentence complexity.")
    
    # Statistical measures for normalization
    calibration_samples: int = Field(default=0, description="Number of samples used for calibration.")
    confidence_level: float = Field(default=0.0, description="Confidence in baseline profile (0.0-1.0).")


# Credibility Score with Confidence Intervals
class CredibilityScore(BaseModel):
    """Comprehensive credibility assessment with statistical confidence."""
    # Overall credibility
    credibility_score: float = Field(default=0.0, description="Overall credibility score (0.0-1.0).")
    credibility_level: str = Field(default="Unknown", description="Credibility level (Low/Medium/High/Inconclusive).")
    
    # Confidence intervals
    confidence_interval_lower: float = Field(default=0.0, description="Lower bound of 95% confidence interval.")
    confidence_interval_upper: float = Field(default=1.0, description="Upper bound of 95% confidence interval.")
    confidence_level: float = Field(default=0.0, description="Confidence in the assessment (0.0-1.0).")
    
    # Component scores (weighted)
    acoustic_score: float = Field(default=0.0, description="Acoustic analysis component score.")
    linguistic_score: float = Field(default=0.0, description="Linguistic analysis component score.")
    behavioral_score: float = Field(default=0.0, description="Behavioral patterns component score.")
    consistency_score: float = Field(default=0.0, description="Internal consistency component score.")
    
    # Statistical measures
    z_score: float = Field(default=0.0, description="Z-score relative to baseline.")
    mad_score: float = Field(default=0.0, description="Median Absolute Deviation score.")
    outlier_flags: List[str] = Field(default_factory=list, description="Detected outlier metrics.")
    
    # Inconclusive detection
    is_inconclusive: bool = Field(default=False, description="Whether the assessment is inconclusive.")
    inconclusive_reasons: List[str] = Field(default_factory=list, description="Reasons for inconclusive assessment.")
    
    # Explanation
    explanation: str = Field(default="", description="Detailed explanation of the credibility assessment.")
    contributing_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Factors contributing to the score.")
    risk_indicators: List[str] = Field(default_factory=list, description="Identified risk indicators.")
    
    # EMA smoothing (for real-time updates)
    ema_smoothed_score: Optional[float] = Field(default=None, description="EMA smoothed credibility score.")
    ema_alpha: Optional[float] = Field(default=None, description="EMA smoothing parameter used.")


