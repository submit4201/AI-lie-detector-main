# Session Insights Service
# Provides intelligent session analysis based on conversation history and patterns

from typing import Dict, List, Any, Optional
import statistics
from datetime import datetime

class SessionInsightsGenerator:
    def __init__(self):
        pass
    
    def generate_session_insights(self, 
                                  session_context: Dict[str, Any], 
                                  current_analysis: Dict[str, Any], 
                                  session_history: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate intelligent session insights based on conversation history and current analysis
        """
        
        if session_context.get("previous_analyses", 0) == 0:
            return {}  # No insights for first analysis
            
        insights = {}
        
        # Generate consistency analysis
        insights["consistency_analysis"] = self._analyze_consistency(session_context, current_analysis, session_history)
        
        # Generate behavioral evolution analysis
        insights["behavioral_evolution"] = self._analyze_behavioral_evolution(session_context, current_analysis, session_history)
        
        # Generate risk trajectory analysis
        insights["risk_trajectory"] = self._analyze_risk_trajectory(session_context, current_analysis, session_history)
        
        # Generate conversation dynamics analysis
        insights["conversation_dynamics"] = self._analyze_conversation_dynamics(session_context, current_analysis, session_history)
        
        return insights
    
    def _analyze_consistency(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """Analyze consistency patterns across the session"""
        
        # Get credibility scores from history
        credibility_scores = []
        for entry in session_history:
            score = entry.get("analysis", {}).get("credibility_score")
            if score is not None:
                credibility_scores.append(score)
        
        current_score = current_analysis.get("credibility_score", 0)
        credibility_scores.append(current_score)
        
        if len(credibility_scores) < 2:
            return "Initial analysis - consistency patterns will develop with more conversation."
        
        # Calculate consistency metrics
        score_variance = statistics.variance(credibility_scores) if len(credibility_scores) > 1 else 0
        avg_score = statistics.mean(credibility_scores)
        score_trend = self._calculate_trend(credibility_scores)
        
        # Analyze emotional consistency
        emotions = []
        for entry in session_history:
            emotion = entry.get("analysis", {}).get("top_emotion")
            if emotion:
                emotions.append(emotion)
        
        current_emotion = None
        if current_analysis.get("emotion_analysis"):
            current_emotion = current_analysis["emotion_analysis"][0].get("label")
            emotions.append(current_emotion)
        
        unique_emotions = len(set(emotions)) if emotions else 0
        
        # Generate insight based on patterns
        if score_variance < 100:  # Low variance
            consistency_level = "HIGH"
            if avg_score > 70:
                base_analysis = f"Speaker demonstrates {consistency_level} consistency with stable credibility (avg: {avg_score:.1f}/100). "
            elif avg_score > 40:
                base_analysis = f"Speaker shows {consistency_level} consistency in moderate credibility range (avg: {avg_score:.1f}/100). "
            else:
                base_analysis = f"Speaker maintains {consistency_level} consistency in lower credibility range (avg: {avg_score:.1f}/100). "
        elif score_variance < 400:  # Medium variance
            consistency_level = "MODERATE"
            base_analysis = f"Speaker shows {consistency_level} consistency with some credibility fluctuation (variance: {score_variance:.1f}). "
        else:  # High variance
            consistency_level = "LOW"
            base_analysis = f"Speaker exhibits {consistency_level} consistency with significant credibility swings (variance: {score_variance:.1f}). "
        
        # Add trend analysis
        if score_trend > 5:
            trend_analysis = "Credibility trend is improving over the conversation. "
        elif score_trend < -5:
            trend_analysis = "Credibility trend is declining throughout the session. "
        else:
            trend_analysis = "Credibility remains relatively stable across statements. "
        
        # Add emotional consistency
        if unique_emotions <= 2:
            emotion_analysis = f"Emotional state remains consistent ({', '.join(set(emotions[:3]))}). "
        elif unique_emotions <= 4:
            emotion_analysis = f"Shows moderate emotional variation across {unique_emotions} different states. "
        else:
            emotion_analysis = f"Displays high emotional variability with {unique_emotions} different states detected. "
        
        return base_analysis + trend_analysis + emotion_analysis
    
    def _analyze_behavioral_evolution(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """Analyze how behavior patterns have evolved"""
        
        if len(session_history) < 1:
            return "Behavioral patterns will emerge as the conversation continues."
        
        # Analyze speech rate evolution
        speech_rates = []
        hesitation_counts = []
        formality_scores = []
        
        for entry in session_history:
            # Extract speech metrics from stored analysis summaries
            # This is simplified - in a real implementation, you'd store more detailed metrics
            pass
        
        # Get current metrics
        current_linguistic = current_analysis.get("linguistic_analysis", {})
        current_speech_rate = current_linguistic.get("speech_rate_wpm", 0)
        current_hesitation = current_linguistic.get("hesitation_count", 0)
        current_formality = current_linguistic.get("formality_score", 0)
        
        # Analyze session duration impact
        session_duration = session_context.get("session_duration", 0)
        analysis_count = session_context.get("previous_analyses", 0) + 1
        
        # Generate behavioral evolution insight
        if session_duration < 5:  # Short session
            duration_impact = "In this brief interaction, "
        elif session_duration < 15:  # Medium session
            duration_impact = "Over this moderate conversation length, "
        else:  # Long session
            duration_impact = "Throughout this extended conversation, "
        
        # Analyze linguistic sophistication trends
        if current_formality > 60:
            formality_trend = "speaker maintains formal communication patterns"
        elif current_formality > 30:
            formality_trend = "speaker uses moderately formal language"
        else:
            formality_trend = "speaker employs casual communication style"
        
        # Analyze stress/comfort evolution
        if current_hesitation > 8:
            comfort_level = "showing increased verbal hesitation suggesting possible stress or uncertainty"
        elif current_hesitation > 3:
            comfort_level = "displaying moderate hesitation patterns typical of thoughtful responses"
        else:
            comfort_level = "demonstrating fluid speech patterns indicating comfort with the topic"
        
        # Speech pace analysis
        if current_speech_rate > 180:
            pace_analysis = f" Speaking at {current_speech_rate} WPM indicates heightened engagement or potential nervousness."
        elif current_speech_rate < 120:
            pace_analysis = f" Speaking at {current_speech_rate} WPM suggests deliberate, careful communication."
        else:
            pace_analysis = f" Maintains normal speech pace at {current_speech_rate} WPM."
        
        return f"{duration_impact}the {formality_trend}, {comfort_level}.{pace_analysis} Analysis #{analysis_count} shows {'consistent' if analysis_count <= 2 else 'evolving'} behavioral patterns."
    
    def _analyze_risk_trajectory(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """Analyze risk level progression"""
        
        # Get risk assessments from history
        risk_levels = []
        deception_flags_counts = []
        
        for entry in session_history:
            risk_level = entry.get("analysis", {}).get("overall_risk")
            flags_count = entry.get("analysis", {}).get("red_flags_count", 0)
            if risk_level:
                risk_levels.append(risk_level)
            deception_flags_counts.append(flags_count)
        
        current_risk = current_analysis.get("risk_assessment", {}).get("overall_risk", "unknown")
        current_flags = len(current_analysis.get("red_flags_per_speaker", {}).get("Speaker 1", []))
        
        risk_levels.append(current_risk)
        deception_flags_counts.append(current_flags)
        
        # Convert risk levels to numeric for trend analysis
        risk_values = []
        for risk in risk_levels:
            if risk == "low":
                risk_values.append(1)
            elif risk == "medium":
                risk_values.append(2)
            elif risk == "high":
                risk_values.append(3)
        
        if len(risk_values) < 2:
            return f"Initial risk assessment: {current_risk.upper()} risk level detected with {current_flags} deception indicators."
        
        # Calculate risk trend
        risk_trend = self._calculate_trend(risk_values)
        flags_trend = self._calculate_trend(deception_flags_counts)
        
        # Generate risk trajectory insight
        if risk_trend > 0.3:
            trajectory = "ESCALATING"
            trend_desc = "Risk levels are increasing throughout the conversation"
        elif risk_trend < -0.3:
            trajectory = "DECREASING"
            trend_desc = "Risk levels are declining as the conversation progresses"
        else:
            trajectory = "STABLE"
            trend_desc = "Risk levels remain relatively consistent"
        
        # Analyze deception indicators trend
        if flags_trend > 0.5:
            flags_desc = f" Deception indicators are increasing (current: {current_flags})."
        elif flags_trend < -0.5:
            flags_desc = f" Deception indicators are decreasing (current: {current_flags})."
        else:
            flags_desc = f" Deception indicators remain steady (current: {current_flags})."
        
        # Risk level context
        current_risk_desc = ""
        if current_risk == "high":
            current_risk_desc = " Current session shows multiple concerning patterns requiring attention."
        elif current_risk == "medium":
            current_risk_desc = " Current session shows moderate risk factors worth monitoring."
        else:
            current_risk_desc = " Current session shows minimal risk indicators."
        
        return f"{trajectory} risk trajectory detected. {trend_desc}.{flags_desc}{current_risk_desc}"
    
    def _analyze_conversation_dynamics(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """Analyze overall conversation flow and dynamics"""
        
        analysis_count = session_context.get("previous_analyses", 0) + 1
        session_duration = session_context.get("session_duration", 0)
        
        # Calculate conversation pace
        if session_duration > 0:
            analyses_per_minute = analysis_count / session_duration
        else:
            analyses_per_minute = 0
        
        # Get recent transcripts for length analysis
        recent_transcripts = session_context.get("recent_transcripts", [])
        current_transcript = current_analysis.get("transcript", "")
        all_transcripts = recent_transcripts + [current_transcript]
        
        # Calculate response lengths
        response_lengths = [len(transcript.split()) for transcript in all_transcripts if transcript]
        avg_response_length = statistics.mean(response_lengths) if response_lengths else 0
        
        # Analyze conversation flow
        if analyses_per_minute > 2:
            pace_desc = "rapid-fire conversation with quick exchanges"
        elif analyses_per_minute > 0.5:
            pace_desc = "moderate conversation pace with regular interaction"
        else:
            pace_desc = "deliberate conversation with extended pauses between responses"
        
        # Response detail analysis
        if avg_response_length > 100:
            detail_level = "providing detailed, comprehensive responses"
        elif avg_response_length > 30:
            detail_level = "giving moderate-length responses with adequate detail"
        else:
            detail_level = "providing brief, concise responses"
        
        # Engagement pattern analysis
        current_word_count = len(current_transcript.split()) if current_transcript else 0
        if len(response_lengths) > 1:
            length_variance = statistics.variance(response_lengths)
            if length_variance > 500:
                engagement_pattern = "Response length varies significantly, suggesting changing engagement levels"
            else:
                engagement_pattern = "Response length remains consistent, indicating stable engagement"
        else:
            engagement_pattern = "Initial response establishes baseline communication pattern"
        
        # Session progression analysis
        if analysis_count == 2:
            progression = "Conversation is developing initial patterns"
        elif analysis_count <= 5:
            progression = "Conversation has established clear communication dynamics"
        else:
            progression = "Extended conversation reveals deep behavioral patterns"
        
        return f"Session shows {pace_desc} over {session_duration:.1f} minutes with speaker {detail_level} (avg: {avg_response_length:.0f} words). {engagement_pattern}. {progression} across {analysis_count} analyses."
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend in a list of values"""
        if len(values) < 2:
            return 0
        
        # Simple linear regression slope
        n = len(values)
        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_vals[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        return numerator / denominator

# Global instance for the service
session_insights_generator = SessionInsightsGenerator()
