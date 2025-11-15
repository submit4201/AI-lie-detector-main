from backend.models import ConversationFlow
from typing import List, Dict, Optional, Any, TYPE_CHECKING
import json

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

class ConversationFlowService:
    def __init__(self, gemini_service: Optional["GeminiService"] = None):
        if gemini_service is None:
            # Import here to avoid circular import at module level
            from backend.services.gemini_service import GeminiService
            gemini_service = GeminiService()
        self.gemini_service = gemini_service

    async def analyze(self, text: str, dialogue_acts: Optional[List[Dict[str, Any]]] = None, speaker_diarization: Optional[List[Dict[str, Any]]] = None) -> ConversationFlow:
        if not text:
            return ConversationFlow() # Return default if no text

        dialogue_acts_summary = "Dialogue acts not available."
        if dialogue_acts:
            try:
                # Summarize to keep prompt shorter if many acts
                if len(dialogue_acts) > 10:
                    summary_acts = [f"{act.get('speaker', 'S')}: {act.get('act_type', 'Unknown')[:20]}..." for act in dialogue_acts[:5]] # first 5
                    summary_acts.append("...")
                    summary_acts.extend([f"{act.get('speaker', 'S')}: {act.get('act_type', 'Unknown')[:20]}..." for act in dialogue_acts[-2:]]) # last 2
                    dialogue_acts_summary = f"Dialogue acts summary: {json.dumps(summary_acts)}"
                else:
                    dialogue_acts_summary = f"Dialogue acts: {json.dumps(dialogue_acts)}"
            except TypeError:
                dialogue_acts_summary = "Dialogue acts data is not JSON serializable."

        diarization_summary = "Speaker diarization not available."
        if speaker_diarization:
            try:
                diarization_summary = f"Speaker diarization data: {json.dumps(speaker_diarization)}"
            except TypeError:
                diarization_summary = "Speaker diarization data is not JSON serializable."

        prompt = f"""Analyze the following transcript and associated data to assess conversation flow.
Transcript:
"{text}"

{dialogue_acts_summary}
{diarization_summary}

Based on the provided information, evaluate the following aspects of conversation flow:
1.  Engagement Level (Low, Medium, High): Overall engagement level of participants. Consider turn-taking frequency, response latency (if inferable), and emotional tone from text.
2.  Topic Coherence Score (0.0 to 1.0): How well do speakers stick to topics, and how smoothly do topic shifts occur? Consider dialogue acts for topic continuity.
3.  Conversation Dominance (Dict[str, float]): Estimate the proportion of talk time or contribution for each speaker if multiple speakers are identified (e.g., {{"speaker_A": 0.6, "speaker_B": 0.4}}). Use diarization if available, otherwise infer from text cues.
4.  Turn-Taking Efficiency: Describe the efficiency of turn-taking (e.g., "Smooth", "Frequent Overlaps", "Long Pauses Between Turns"). Infer from diarization or textual cues like interruptions or trailing sentences.
5.  Conversation Phase: Identify the current phase (e.g., "Opening", "Topic Development", "Problem Solving", "Closing", "Off-topic").
6.  Flow Disruptions (List[str]): List any identified disruptions to the flow (e.g., "Frequent interruptions by Speaker A", "Abrupt topic change", "Unresponsive participant").

Provide your analysis as a JSON object matching the structure of the ConversationFlow model:
{{
  "engagement_level": str ("Low", "Medium", "High"),
  "topic_coherence_score": float (0.0-1.0),
  "conversation_dominance": {{ "speaker_label": float }},
  "turn_taking_efficiency": str,
  "conversation_phase": str,
  "flow_disruptions": []
}}
If specific details cannot be reliably inferred, use appropriate defaults like "Analysis not available", 0.0, or empty lists/dictionaries.
"""

        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt)
            
            if raw_analysis:
                analysis_data = json.loads(raw_analysis)
                return ConversationFlow(
                    engagement_level=analysis_data.get("engagement_level", "Analysis not available"),
                    topic_coherence_score=analysis_data.get("topic_coherence_score", 0.0),
                    conversation_dominance=analysis_data.get("conversation_dominance", {}),
                    turn_taking_efficiency=analysis_data.get("turn_taking_efficiency", "Analysis not available"),
                    conversation_phase=analysis_data.get("conversation_phase", "Analysis not available"),
                    flow_disruptions=analysis_data.get("flow_disruptions", [])
                )
            else:
                return self._fallback_text_analysis(text, dialogue_acts, speaker_diarization)
        except Exception as e:
            print(f"Error during LLM conversation flow analysis: {e}")
            return self._fallback_text_analysis(text, dialogue_acts, speaker_diarization)

    def _fallback_text_analysis(self, text: str, dialogue_acts: Optional[List[Dict[str, Any]]] = None, speaker_diarization: Optional[List[Dict[str, Any]]] = None) -> ConversationFlow:
        engagement = "Medium"
        coherence = 0.0
        dominance: Dict[str, float] = {}
        turn_taking = "Analysis not available (fallback)."
        phase = "Analysis not available (fallback)."
        disruptions = []

        if text:
            word_count = len(text.split())
            if word_count > 200:
                engagement = "High"
                coherence = 0.75
                phase = "Development"
            elif word_count > 50:
                engagement = "Medium"
                coherence = 0.5
                phase = "Opening"
            else:
                engagement = "Low"
                coherence = 0.25
                phase = "Initial"

        if speaker_diarization and len(speaker_diarization) > 0:
            speaker_times: Dict[str, float] = {}
            total_speech_time = 0.0
            for segment in speaker_diarization:
                duration = (segment.get('end_time', 0.0) - segment.get('start_time', 0.0))
                speaker = segment.get('speaker_label', 'Unknown')
                speaker_times[speaker] = speaker_times.get(speaker, 0.0) + duration
                total_speech_time += duration
            
            if total_speech_time > 0:
                for speaker_label, time in speaker_times.items():
                    dominance[speaker_label] = round(time / total_speech_time, 2)
            
            if len(speaker_diarization) > 10: # Arbitrary
                 turn_taking = "Seemingly fluid (fallback)"
            elif len(speaker_diarization) > 1:
                 turn_taking = "Potentially stilted (fallback)"
            else:
                 turn_taking = "Single speaker or minimal turns (fallback)"

        if dialogue_acts and len(dialogue_acts) > 1: # Need at least two acts for some coherence/disruption logic
            act_types = {act.get('act_type') for act in dialogue_acts if act.get('act_type')}
            if len(act_types) > 3: 
                coherence = min(1.0, coherence + 0.1)
            
            # Basic disruption: look for many disagreements or questions without answers (harder)
            disagreement_count = sum(1 for act in dialogue_acts if act.get('act_type') == "Disagreement")
            if disagreement_count > len(dialogue_acts) * 0.3 and len(dialogue_acts) > 3: # If >30% are disagreements
                disruptions.append("Frequent disagreements noted.")
                coherence = max(0.0, coherence - 0.2) # Penalize coherence
        elif not dialogue_acts and not speaker_diarization and len(text.split()) < 20:
             turn_taking = "Very short input, likely single turn (fallback)."
             phase = "Brief Utterance (fallback)"

        return ConversationFlow(
            engagement_level=engagement,
            topic_coherence_score=round(coherence,2),
            conversation_dominance=dominance,
            turn_taking_efficiency=turn_taking,
            conversation_phase=phase,
            flow_disruptions=disruptions
        )

    async def analyze_conversation_flow(self, transcript: str, session_context: str = None) -> ConversationFlow:
        prompt = f"""
Analyze the conversation flow based on the following transcript.
Consider turn-taking, topic shifts, conversation depth, engagement, balance, clarity, and coherence.
Identify any disruptions or enhancers to the flow.
Provide a summary of the conversation flow.

Transcript:
{transcript}

Session Context (if any):
{session_context if session_context else "No specific session context provided."}

Please return your analysis in a JSON format with the following fields:
- turn_taking_frequency (e.g., "High", "Medium", "Low", or specific metrics if inferable)
- topic_shifts (e.g., "Frequent and abrupt", "Smooth and logical", "Few")
- conversation_depth (e.g., "Superficial", "Moderate", "Deep")
- engagement_levels (e.g., "High for all participants", "Mixed", "Low")
- conversation_balance (e.g., "Balanced", "Dominated by one speaker")
- clarity_and_coherence (e.g., "Clear and coherent", "Sometimes unclear", "Fragmented")
- summary_of_flow (A brief narrative summary)
- flow_disruptions (List of observed disruptions, e.g., ["Frequent interruptions", "Long silences"])
- flow_enhancers (List of observed enhancers, e.g., ["Active listening cues", "Clear topic transitions"])
- turn_taking_frequency_analysis (Your reasoning for the turn_taking_frequency assessment)
- topic_shifts_analysis (Your reasoning for the topic_shifts assessment)
- conversation_depth_analysis (Your reasoning for the conversation_depth assessment)
- engagement_levels_analysis (Your reasoning for the engagement_levels assessment)
- conversation_balance_analysis (Your reasoning for the conversation_balance assessment)
- clarity_and_coherence_analysis (Your reasoning for the clarity_and_coherence assessment)
- summary_of_flow_analysis (Your reasoning for the summary_of_flow)
- flow_disruptions_analysis (Your reasoning for identifying these flow_disruptions)
- flow_enhancers_analysis (Your reasoning for identifying these flow_enhancers)

If specific data is unavailable or analysis is not possible for a field, use appropriate default values like "N/A", "Could not determine", empty lists for list types, or a neutral assessment.
Ensure all fields are present in your JSON response.
IMPORTANT: Your entire response must be only the JSON object, with no surrounding text, explanations, or markdown formatting.
"""
        try:
            response_json_str = await self.gemini_service.query_gemini_for_raw_json(prompt)
            response_data = json.loads(response_json_str)
            
            # Ensure all expected fields are present in the response
            expected_fields = [
                "turn_taking_frequency", "topic_shifts", "conversation_depth",
                "engagement_levels", "conversation_balance", "clarity_and_coherence",
                "summary_of_flow", "flow_disruptions", "flow_enhancers",
                "turn_taking_frequency_analysis", "topic_shifts_analysis",
                "conversation_depth_analysis", "engagement_levels_analysis",
                "conversation_balance_analysis", "clarity_and_coherence_analysis",
                "summary_of_flow_analysis", "flow_disruptions_analysis", "flow_enhancers_analysis"
            ]
            
            # Fill missing fields with default values
            for field in expected_fields:
                if field not in response_data:
                    if "analysis" in field or field in ["summary_of_flow", "turn_taking_frequency", "topic_shifts", "conversation_depth", "engagement_levels", "conversation_balance", "clarity_and_coherence"]:
                        response_data[field] = "N/A"  # Default for analysis and summary fields
                    elif field in ["flow_disruptions", "flow_enhancers"]:
                        response_data[field] = []  # Default to empty list
                    else:
                        response_data[field] = "Could not determine"  # Generic default

            return ConversationFlow(
                engagement_level=response_data.get("engagement_levels", "Analysis not available"),
                topic_coherence_score=response_data.get("topic_coherence_score", 0.0),
                conversation_dominance=response_data.get("conversation_dominance", {}),
                turn_taking_efficiency=response_data.get("turn_taking_frequency", "Analysis not available"),
                conversation_phase=response_data.get("conversation_phase", "Analysis not available"),
                flow_disruptions=response_data.get("flow_disruptions", [])
            )
        except Exception as e:
            print(f"Error during enhanced conversation flow analysis: {e}")
            return self._fallback_text_analysis(transcript, None, None)
