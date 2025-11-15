"""
Linguistic Analysis Service
Provides quantitative linguistic analysis and LLM-based interpretation.
"""
import re
import logging
import json
from typing import Dict, Any, Optional, Tuple

from backend.models import NumericalLinguisticMetrics, LinguisticAnalysis
from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# Define patterns for hesitation markers and other filler/hesitation words
# Regex patterns are defined as regular strings; backslashes are escaped for Python, then for regex.
# So \\b becomes \b for regex engine.
HESITATION_MARKER_PATTERN = '\\b(um|uh|er|ah)\\b'

# Broader hesitation/filler words, EXCLUDING the markers above which are counted separately
# what's -> what\'s in the string literal
FILLER_WORD_PATTERNS_LIST = [
    '\\b(like|you know|well|so|actually|basically|literally|totally|really|just|i mean|you see)\\b',
    '\\b(let me think|how do i say|what\'s the word|you understand|if you will|sort of speak)\\b'
]
COMBINED_FILLER_PATTERN = '(' + '|'.join(FILLER_WORD_PATTERNS_LIST) + ')'

QUALIFIER_PATTERN = '\\b(maybe|perhaps|might|could|possibly|probably|sort of|kind of|i think|i guess|i believe|i suppose|somewhat|rather|fairly|quite|seems like|appears to|tends to|usually|sometimes|often|occasionally|potentially|presumably|allegedly|supposedly|apparently)\\b'
CERTAINTY_PATTERN = '\\b(definitely|certainly|absolutely|sure|confident|know|always|never|exactly|clearly|obviously|undoubtedly|unquestionably|positively|guaranteed|without doubt|for certain|no doubt|100 percent|completely|totally|entirely|perfectly)\\b'
IMMEDIATE_REPETITION_PATTERN = '\\b(\\w+)\\s+\\1\\b'

# Formality patterns
FORMAL_TRANSITIONS_PATTERN = '\\b(furthermore|however|nevertheless|therefore|consequently|moreover|additionally|subsequently|accordingly|thus|hence|whereas|albeit|notwithstanding|indeed|inasmuch as|insofar as|heretofore|henceforth|notwithstanding)\\b'
FORMAL_COURTESY_PATTERN = '\\b(sir|madam|please|thank you|kindly|respectfully|sincerely|cordially|graciously|humbly|your honor|your excellency|distinguished|esteemed)\\b'
FORMAL_LEGAL_PATTERN = '\\b(pursuant to|in accordance with|with regard to|concerning|regarding|herein|thereof|whereby|wherein|whereof|heretofore|aforementioned|subsequent to|prior to|in lieu of|notwithstanding)\\b'
FORMAL_ACADEMIC_PATTERN = '\\b(substantially|significantly|predominantly|fundamentally|essentially|particularly|specifically|generally|typically|consistently|primarily|principally|ultimately|comprehensively)\\b'
FORMAL_EXPRESSIONS_PATTERN = '\\b(allow me to|permit me to|if I may|with your permission|I would like to express|I wish to convey|it is my understanding|it has come to my attention|I am compelled to|I feel obligated to)\\b'

# Informality patterns
INFORMAL_CASUAL_PATTERN = '\\b(yeah|yep|nah|yup|uh-huh|mm-hmm|nope|yep|sure thing|no way|for real|totally|whatever|awesome|cool|sweet|nice|dude|buddy|man|bro|sis)\\b'
INFORMAL_CONTRACTIONS_PATTERN = '\\b(gonna|wanna|gotta|kinda|sorta|dunno|shoulda|woulda|coulda|lemme|gimme|betcha|whatcha|lookin|doin|nothin|somethin|anythin|everythin)\\b'
STANDARD_CONTRACTIONS_PATTERN = '\\b(ain\'t|can\'t|won\'t|shouldn\'t|wouldn\'t|couldn\'t|isn\'t|aren\'t|wasn\'t|weren\'t|haven\'t|hasn\'t|hadn\'t|don\'t|doesn\'t|didn\'t|I\'m|you\'re|he\'s|she\'s|it\'s|we\'re|they\'re|I\'ve|you\'ve|we\'ve|they\'ve|I\'ll|you\'ll|he\'ll|she\'ll|we\'ll|they\'ll|I\'d|you\'d|he\'d|she\'d|we\'d|they\'d)\\b'
INFORMAL_SLANG_PATTERN = '\\b(ok|okay|alright|right on|no biggie|no prob|my bad|oh well|so what|big deal|kinda like|sorta like|you know what I mean|if you know what I mean)\\b'

CHARS_TO_STRIP_FROM_WORDS = ".,!?\'"

def analyze_numerical_linguistic_metrics(transcript: str, duration: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyze linguistic patterns in the transcript to provide quantitative metrics.
    This function performs direct calculations and does not call any LLM.

    Args:
        transcript (str): The transcribed text to analyze.
        duration (float, optional): Audio duration in seconds for rate calculations.

    Returns:
        Dict containing numerical linguistic metrics.
    """
    if not transcript or not transcript.strip():
        return NumericalLinguisticMetrics().model_dump()

    try:
        words = transcript.split()
        word_count = len(words)
        if word_count == 0:
            return NumericalLinguisticMetrics().model_dump()

        hesitation_markers = re.findall(HESITATION_MARKER_PATTERN, transcript, re.IGNORECASE)
        hesitation_marker_count = len(hesitation_markers)

        other_filler_words_match = re.findall(COMBINED_FILLER_PATTERN, transcript, re.IGNORECASE)
        filler_word_count = 0
        if other_filler_words_match:
            # Flatten list of tuples if regex groups are used from the OR construct
            if isinstance(other_filler_words_match[0], tuple):
                filler_word_count = len([item for tpl in other_filler_words_match for item in tpl if item])
            else:
                filler_word_count = len(other_filler_words_match)
        
        qualifiers = re.findall(QUALIFIER_PATTERN, transcript, re.IGNORECASE)
        qualifier_count = len(qualifiers)

        certainty_words = re.findall(CERTAINTY_PATTERN, transcript, re.IGNORECASE)
        certainty_indicator_count = len(certainty_words)

        immediate_repetitions = re.findall(IMMEDIATE_REPETITION_PATTERN, transcript, re.IGNORECASE)
        
        phrase_repetitions_list = []
        words_clean = [word.strip(CHARS_TO_STRIP_FROM_WORDS) for word in words]
        for i in range(len(words_clean) - 1):
            for phrase_len in range(2, min(5, len(words_clean) - i + 1)):
                phrase = ' '.join(words_clean[i:i+phrase_len]).lower()
                if len(phrase.split()) < 2: continue
                rest_text_for_phrase_search = ' '.join(words_clean[i+phrase_len:]).lower()
                if phrase in rest_text_for_phrase_search:
                    is_new_repetition = True
                    for existing_rep in phrase_repetitions_list:
                        if phrase in existing_rep or existing_rep in phrase:
                            is_new_repetition = False
                            break
                    if is_new_repetition:
                        phrase_repetitions_list.append(phrase)
        repetition_count = len(immediate_repetitions) + len(phrase_repetitions_list)

        avg_word_length_chars = sum(len(word.strip(CHARS_TO_STRIP_FROM_WORDS)) for word in words) / word_count
        
        sentences = re.split(r'[.!?]+', transcript)
        valid_sentences = [s for s in sentences if s.strip()]
        sentence_count = len(valid_sentences) if len(valid_sentences) > 0 else 1
        avg_sentence_length_words = word_count / sentence_count

        speech_rate_wpm = None
        hesitation_rate_hpm = None
        if duration and duration > 0:
            speech_rate_wpm = (word_count / duration) * 60
            hesitation_rate_hpm = (hesitation_marker_count / duration) * 60

        unique_word_list = set(word.lower().strip(CHARS_TO_STRIP_FROM_WORDS) for word in words)
        unique_word_count = len(unique_word_list)
        vocabulary_richness_ttr = unique_word_count / word_count if word_count > 0 else 0.0
        
        confidence_metric_ratio = None
        if qualifier_count + certainty_indicator_count > 0:
            confidence_metric_ratio = certainty_indicator_count / (qualifier_count + certainty_indicator_count)

        formal_transitions_c = len(re.findall(FORMAL_TRANSITIONS_PATTERN, transcript, re.IGNORECASE))
        formal_courtesy_c = len(re.findall(FORMAL_COURTESY_PATTERN, transcript, re.IGNORECASE))
        formal_legal_c = len(re.findall(FORMAL_LEGAL_PATTERN, transcript, re.IGNORECASE))
        formal_academic_c = len(re.findall(FORMAL_ACADEMIC_PATTERN, transcript, re.IGNORECASE))
        formal_expressions_c = len(re.findall(FORMAL_EXPRESSIONS_PATTERN, transcript, re.IGNORECASE))
        formal_words_count = formal_transitions_c + formal_courtesy_c + formal_legal_c + formal_academic_c + formal_expressions_c
        
        informal_casual_c = len(re.findall(INFORMAL_CASUAL_PATTERN, transcript, re.IGNORECASE))
        informal_contractions_c = len(re.findall(INFORMAL_CONTRACTIONS_PATTERN, transcript, re.IGNORECASE))
        standard_contractions_c = len(re.findall(STANDARD_CONTRACTIONS_PATTERN, transcript, re.IGNORECASE))
        informal_slang_c = len(re.findall(INFORMAL_SLANG_PATTERN, transcript, re.IGNORECASE))
        
        formal_ratio = formal_words_count / word_count if word_count > 0 else 0
        casual_penalty_val = (informal_casual_c + informal_contractions_c + informal_slang_c) / word_count if word_count > 0 else 0
        standard_penalty_val = standard_contractions_c / word_count if word_count > 0 else 0
        
        baseline = 50
        formal_boost = formal_ratio * 500
        casual_reduction = casual_penalty_val * 250
        standard_reduction = standard_penalty_val * 100
        formality_score_calculated = max(0, min(100, baseline + formal_boost - casual_reduction - standard_reduction))

        word_length_factor = min(100, avg_word_length_chars * 15)
        sentence_length_factor = min(100, avg_sentence_length_words * 3)
        vocabulary_diversity_factor = vocabulary_richness_ttr * 100
        
        total_hesitations_fillers = hesitation_marker_count + filler_word_count
        hesitation_filler_penalty_for_complexity = min(50, (total_hesitations_fillers / word_count) * 1000 if word_count > 0 else 0)
        
        certainty_balance_factor = min(25, abs(certainty_indicator_count - qualifier_count) * 5)
        
        complexity_factors_sum = word_length_factor + sentence_length_factor + vocabulary_diversity_factor + certainty_balance_factor
        complexity_base = complexity_factors_sum / 4
        complexity_score_calculated = max(0, min(100, complexity_base - hesitation_filler_penalty_for_complexity))

        return {
            "word_count": word_count,
            "unique_word_count": unique_word_count,
            "hesitation_marker_count": hesitation_marker_count,
            "filler_word_count": filler_word_count,
            "qualifier_count": qualifier_count,
            "certainty_indicator_count": certainty_indicator_count,
            "repetition_count": repetition_count,
            "sentence_count": sentence_count,
            "avg_word_length_chars": round(avg_word_length_chars, 1),
            "avg_sentence_length_words": round(avg_sentence_length_words, 1),
            "speech_rate_wpm": round(speech_rate_wpm, 1) if speech_rate_wpm is not None else None,
            "hesitation_rate_hpm": round(hesitation_rate_hpm, 1) if hesitation_rate_hpm is not None else None,
            "vocabulary_richness_ttr": round(vocabulary_richness_ttr, 2),
            "confidence_metric_ratio": round(confidence_metric_ratio, 2) if confidence_metric_ratio is not None else None,
            "formality_score_calculated": round(formality_score_calculated, 1),
            "complexity_score_calculated": round(complexity_score_calculated, 1),
        }

    except Exception as e:
        logger.error(f"Error in numerical linguistic metrics calculation: {e}", exc_info=True)
        return NumericalLinguisticMetrics().model_dump()

def get_default_numerical_linguistic_metrics() -> NumericalLinguisticMetrics:
    """Return default NumericalLinguisticMetrics model."""
    return NumericalLinguisticMetrics()

def get_default_linguistic_analysis_interpretation() -> LinguisticAnalysis:
    """Return default LinguisticAnalysis model."""
    return LinguisticAnalysis()

async def interpret_linguistic_metrics_with_gemini(
    numerical_metrics: NumericalLinguisticMetrics,
    transcript: str,
    gemini_service: GeminiService,
    session_context: Optional[Dict[str, Any]] = None
) -> LinguisticAnalysis:
    """
    Uses Gemini to interpret the calculated numerical linguistic metrics and provide
    a qualitative linguistic analysis.

    Args:
        numerical_metrics: Calculated numerical metrics.
        transcript: The full transcript for context.
        gemini_service: Instance of GeminiService.
        session_context: Optional session context for GeminiService.

    Returns:
        LinguisticAnalysis model populated by Gemini.
    """
    if not transcript.strip():
        return get_default_linguistic_analysis_interpretation()

    numerical_metrics_dict = numerical_metrics.model_dump(exclude_none=True)
    numerical_metrics_json_string = json.dumps(numerical_metrics_dict, indent=2)

    # Note: ''' in the prompt string below are escaped as \'\'\' for the tool argument
    prompt = f"""You are an expert linguistic analyst. Your task is to interpret a set of pre-calculated numerical linguistic metrics
derived from a text transcript. Based on these metrics AND the full transcript, provide a comprehensive linguistic analysis.

The full transcript is:
\'\'\'
{transcript}
\'\'\'

The pre-calculated Numerical Linguistic Metrics are:
```json
{numerical_metrics_json_string}
```

Please generate a JSON object that strictly adheres to the Pydantic model structure for 'LinguisticAnalysis' provided below.
For each field in the 'LinguisticAnalysis' model, provide a thoughtful interpretation.
- For fields ending with '_analysis' (e.g., 'word_count_analysis'), explain the significance of the corresponding numerical metric in the context of the provided transcript and general communication principles.
- For descriptive fields (e.g., 'speech_patterns_description'), synthesize information from relevant metrics and the overall transcript to provide a qualitative assessment.
- For 'pause_occurrence_analysis', consider pause indicators in the transcript (e.g., '...', long silences if identifiable) and discuss their potential impact.
- The 'overall_linguistic_style_summary' should be a comprehensive summary of the speaker's linguistic style and its implications, drawing from all available data.

If a specific aspect cannot be reliably analyzed from the provided data, use a default message like "Sufficient data not available for a detailed analysis of [aspect name]." for that field, but try to provide insights where possible.

Pydantic Model for 'LinguisticAnalysis':
{{
    "speech_patterns_description": "LLM analysis of speech rhythm, pace, pauses not covered by specific counts. Consider overall flow, rhythm, and use of pauses evident in the transcript.",
    "word_choice_description": "LLM analysis of vocabulary (e.g., sophistication, specificity, jargon) and phrasing choices, beyond simple counts. Consider if word choice is appropriate for context.",
    "emotional_consistency_description": "LLM assessment of consistency between language used and potential emotional undertones. Does the language align with a consistent emotional expression, or are there mixed signals?",
    "detail_level_description": "LLM assessment of whether the level of detail in the transcript is appropriate (e.g., for answering a question, explaining a topic) versus being overly vague or excessively granular.",
    "word_count_analysis": "Interpret the significance of the word_count ({numerical_metrics_dict.get('word_count', 'N/A')}) in the context of the communication's purpose or length.",
    "hesitation_marker_analysis": "Interpret the impact of hesitation markers (e.g., um, uh; count: {numerical_metrics_dict.get('hesitation_marker_count', 'N/A')}) on fluency and perceived confidence.",
    "filler_word_analysis": "Interpret the impact of other filler words (e.g., like, you know; count: {numerical_metrics_dict.get('filler_word_count', 'N/A')}) on clarity and formality.",
    "qualifier_analysis": "Interpret the impact of uncertainty qualifiers (count: {numerical_metrics_dict.get('qualifier_count', 'N/A')}) on the speaker\\'s assertiveness and the message\\'s perceived certainty.",
    "certainty_indicator_analysis": "Interpret the impact of certainty indicators (count: {numerical_metrics_dict.get('certainty_indicator_count', 'N/A')}) on the speaker\\'s conviction and the message\\'s forcefulness.",
    "repetition_analysis": "Interpret word/phrase repetitions (count: {numerical_metrics_dict.get('repetition_count', 'N/A')}). Do they emphasize points, indicate uncertainty, or suggest a lack of preparation?",
    "sentence_count_analysis": "Interpret the significance of the sentence count ({numerical_metrics_dict.get('sentence_count', 'N/A')}) relative to the word count and overall message length.",
    "avg_word_length_analysis": "Interpret the average word length ({numerical_metrics_dict.get('avg_word_length_chars', 'N/A')} chars). Does it suggest simple or complex vocabulary?",
    "avg_sentence_length_analysis": "Interpret the average sentence length ({numerical_metrics_dict.get('avg_sentence_length_words', 'N/A')} words). Does it suggest simple or complex sentence structures? What is its impact on readability?",
    "speech_rate_analysis": "If speech rate (WPM: {numerical_metrics_dict.get('speech_rate_wpm', 'N/A')}) is available, interpret its impact on clarity, engagement, and perceived speaker energy. If N/A, state that.",
    "hesitation_rate_analysis": "If hesitation rate (HPM: {numerical_metrics_dict.get('hesitation_rate_hpm', 'N/A')}) is available, interpret its impact on fluency and listener perception. If N/A, state that.",
    "vocabulary_richness_analysis": "Interpret vocabulary richness (TTR: {numerical_metrics_dict.get('vocabulary_richness_ttr', 'N/A')}). Does it indicate a broad or limited vocabulary for the context?",
    "confidence_metric_analysis": "Interpret the calculated confidence metric ratio ({numerical_metrics_dict.get('confidence_metric_ratio', 'N/A')}). What does this suggest about the speaker\\'s overall assertiveness vs. caution?",
    "formality_score_analysis": "Interpret the calculated formality score ({numerical_metrics_dict.get('formality_score_calculated', 'N/A')}/100). Is the language appropriate for a formal/informal setting?",
    "complexity_score_analysis": "Interpret the calculated linguistic complexity score ({numerical_metrics_dict.get('complexity_score_calculated', 'N/A')}/100). What does this suggest about the cognitive demand or sophistication of the language?",
    "pause_occurrence_analysis": "Analyze the presence and potential impact of pauses. Look for explicit markers like '...' or infer from context. Discuss their effect on rhythm, emphasis, or potential hesitation.",
    "overall_linguistic_style_summary": "Provide a comprehensive summary of the speaker\\'s linguistic style, integrating various observations. Describe the overall impression the language conveys (e.g., articulate, hesitant, concise, verbose, formal, casual)."
}}

Return ONLY the JSON object adhering to the 'LinguisticAnalysis' model structure. Do not add any explanatory text before or after the JSON object.
"""
    try:
        raw_json_output = await gemini_service.query_gemini_for_raw_json(prompt, session_context)
        if raw_json_output:
            try:
                if isinstance(raw_json_output, str):
                    # Clean potential markdown code block fences
                    cleaned_json_string = raw_json_output.strip()
                    if cleaned_json_string.startswith("```json"):
                        cleaned_json_string = cleaned_json_string[7:]
                    if cleaned_json_string.endswith("```"):
                        cleaned_json_string = cleaned_json_string[:-3]
                    data = json.loads(cleaned_json_string)
                elif isinstance(raw_json_output, dict):
                    data = raw_json_output
                else:
                    logger.error(f"Unexpected type from Gemini for LinguisticAnalysis: {type(raw_json_output)}")
                    return get_default_linguistic_analysis_interpretation()
                return LinguisticAnalysis(**data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to parse LinguisticAnalysis JSON from Gemini: {e}. Raw output: {raw_json_output}")
                return get_default_linguistic_analysis_interpretation()
        else:
            logger.warning("Received no output from Gemini for linguistic interpretation.")
            return get_default_linguistic_analysis_interpretation()
    except Exception as e:
        logger.error(f"Error during Gemini call for linguistic interpretation: {e}", exc_info=True)
        return get_default_linguistic_analysis_interpretation()

async def linguistic_analysis_pipeline(
    transcript: str,
    gemini_service: GeminiService,
    duration: Optional[float] = None,
    session_context: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[NumericalLinguisticMetrics], Optional[LinguisticAnalysis]]:
    """
    Main linguistic analysis pipeline.
    1. Calculates numerical linguistic metrics from the transcript.
    2. Uses Gemini to interpret these metrics and provide qualitative analysis.

    Args:
        transcript (str): The transcribed text.
        gemini_service: Instance of GeminiService.
        duration (float, optional): Audio duration in seconds.
        session_context: Optional session context for GeminiService.

    Returns:
        A tuple containing (NumericalLinguisticMetrics, LinguisticAnalysis).
        Returns (None, None) or default models if analysis cannot be performed.
    """
    if not transcript or not transcript.strip():
        logger.warning("Linguistic analysis pipeline: Empty transcript provided.")
        return get_default_numerical_linguistic_metrics(), get_default_linguistic_analysis_interpretation()

    try:
        numerical_metrics_dict = analyze_numerical_linguistic_metrics(transcript, duration)
        numerical_metrics = NumericalLinguisticMetrics(**numerical_metrics_dict)
        
        linguistic_interpretation = get_default_linguistic_analysis_interpretation() # Default first
        if numerical_metrics.word_count > 0:
            linguistic_interpretation = await interpret_linguistic_metrics_with_gemini(
                numerical_metrics, transcript, gemini_service, session_context
            )
            
        return numerical_metrics, linguistic_interpretation

    except Exception as e:
        logger.error(f"Exception in linguistic_analysis_pipeline: {e}", exc_info=True)
        return get_default_numerical_linguistic_metrics(), get_default_linguistic_analysis_interpretation()

# Constant for descriptive field placeholder messages
_SYNC_MODE_NOT_AVAILABLE = "analysis not available in synchronous mode."

def analyze_linguistic_patterns(transcript: str, duration: Optional[float] = None) -> Dict[str, Any]:
    """
    Legacy synchronous function for linguistic pattern analysis.
    Returns a flat dictionary with both numerical metrics and default descriptive fields.
    This function is provided for backward compatibility with existing tests and code.
    
    For new code, prefer using:
    - analyze_numerical_linguistic_metrics() for just the numerical data
    - linguistic_analysis_pipeline() for full analysis with LLM interpretation
    
    Args:
        transcript (str): The transcribed text to analyze.
        duration (float, optional): Audio duration in seconds for rate calculations.
    
    Returns:
        Dict containing numerical linguistic metrics and default descriptive fields.
    """
    # Get numerical metrics
    numerical_metrics = analyze_numerical_linguistic_metrics(transcript, duration)
    
    # In the legacy implementation, "hesitation_count" included both hesitation markers
    # (um, uh, er, ah) AND filler words (like, you know, well, etc.)
    # This maintains backward compatibility with existing tests
    hesitation_marker_count = numerical_metrics.get("hesitation_marker_count", 0)
    filler_word_count = numerical_metrics.get("filler_word_count", 0)
    combined_hesitation_count = hesitation_marker_count + filler_word_count
    
    # Map keys for backward compatibility
    result = {
        # Map new keys to old expected keys
        "word_count": numerical_metrics.get("word_count", 0),
        "hesitation_count": combined_hesitation_count,  # Combined for backward compatibility
        "qualifier_count": numerical_metrics.get("qualifier_count", 0),
        "certainty_count": numerical_metrics.get("certainty_indicator_count", 0),
        "filler_count": numerical_metrics.get("filler_word_count", 0),
        "repetition_count": numerical_metrics.get("repetition_count", 0),
        "formality_score": numerical_metrics.get("formality_score_calculated", 0.0),
        "complexity_score": numerical_metrics.get("complexity_score_calculated", 0.0),
        "avg_word_length": numerical_metrics.get("avg_word_length_chars", 0.0),
        "avg_words_per_sentence": numerical_metrics.get("avg_sentence_length_words", 0.0),
        "speech_rate_wpm": numerical_metrics.get("speech_rate_wpm"),
        "confidence_ratio": numerical_metrics.get("confidence_metric_ratio"),
        
        # Add default descriptive fields (these would normally come from LLM interpretation)
        "speech_patterns": f"Speech patterns {_SYNC_MODE_NOT_AVAILABLE}",
        "word_choice": f"Word choice {_SYNC_MODE_NOT_AVAILABLE}",
        "emotional_consistency": f"Emotional consistency {_SYNC_MODE_NOT_AVAILABLE}",
        "detail_level": f"Detail level {_SYNC_MODE_NOT_AVAILABLE}",
    }
    
    return result
