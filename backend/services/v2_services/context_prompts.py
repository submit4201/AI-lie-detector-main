"""Prompt construction and context injection for v2 services.

This module provides helpers to build prompts with strict JSON schemas,
incorporating AnalysisContext data (transcript, audio, metrics, speakers, history).
"""
from __future__ import annotations

from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def build_context_report(ctx: "AnalysisContext") -> Dict[str, Any]:  # type: ignore
    """Build a compact context report from AnalysisContext for prompt injection.
    
    Returns a dict with sanitized, privacy-safe context summary.
    """
    report = {}
    
    # Transcript info (length, not full content for privacy)
    if ctx.transcript_final:
        report["transcript_status"] = "final"
        report["transcript_length"] = len(ctx.transcript_final)
        report["transcript_word_count"] = len(ctx.transcript_final.split())
    elif ctx.transcript_partial:
        report["transcript_status"] = "partial"
        report["transcript_length"] = len(ctx.transcript_partial)
        report["transcript_word_count"] = len(ctx.transcript_partial.split())
    else:
        report["transcript_status"] = "none"
    
    # Audio info
    if ctx.audio_summary:
        report["audio_available"] = True
        report["audio_summary"] = {
            "duration": ctx.audio_summary.get("duration"),
            "quality_metrics": ctx.audio_summary.get("quality_metrics", {}),
        }
    else:
        report["audio_available"] = bool(ctx.audio_bytes)
    
    # Metrics info
    if ctx.quantitative_metrics:
        report["metrics_available"] = True
        report["metrics_keys"] = list(ctx.quantitative_metrics.keys())
    else:
        report["metrics_available"] = False
    
    # Speaker info
    if ctx.speaker_segments:
        report["speaker_segments_count"] = len(ctx.speaker_segments)
        report["unique_speakers"] = len(set(seg.get("speaker") for seg in ctx.speaker_segments if seg.get("speaker")))
    else:
        report["speaker_segments_count"] = 0
    
    # Session summary
    if ctx.session_summary:
        report["session_summary"] = ctx.session_summary
    
    return report


def build_manipulation_prompt(ctx: "AnalysisContext", phase: str = "coarse") -> Tuple[str, Dict[str, Any]]:  # type: ignore
    """Build manipulation analysis prompt with JSON schema.
    
    Args:
        ctx: AnalysisContext with transcript, audio, metrics, etc.
        phase: "coarse" for early analysis, "final" for complete analysis
    
    Returns:
        Tuple of (prompt_text, json_schema)
    """
    transcript = ctx.transcript_final or ctx.transcript_partial or ""
    
    # Build context summary
    context_report = build_context_report(ctx)
    
    # Schema for manipulation analysis
    schema = {
        "type": "object",
        "properties": {
            "overall_risk_score": {"type": "number", "minimum": 0, "maximum": 100},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "manipulation_patterns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "evidence": {"type": "string"},
                    },
                    "required": ["pattern", "severity", "evidence"]
                }
            },
            "tactics": {
                "type": "array",
                "items": {"type": "string"}
            },
            "rationale": {"type": "string"},
        },
        "required": ["overall_risk_score", "confidence", "manipulation_patterns", "tactics", "rationale"]
    }
    
    # Check if audio is available to add audio analysis reminder
    audio_reminder = ""
    if ctx.audio_bytes or ctx.audio_summary:
        audio_reminder = """
IMPORTANT: Audio data is available for this analysis. When analyzing, pay close attention to:
- Vocal tone and emotional inflections
- Speaking pace and rhythm changes
- Hesitations, pauses, and stammering
- Pitch variations and stress patterns
- Voice quality indicators (trembling, shakiness, confidence)
- Prosodic features that may indicate deception or manipulation

Use both the transcript text AND the audio characteristics to inform your analysis.
"""
    
    prompt = f"""Analyze the following transcript for signs of manipulation and deception.

Transcript:
"{transcript}"

Context information:
{_format_context(context_report)}
{audio_reminder}
Phase: {phase}
{"This is an early coarse analysis. Focus on obvious patterns." if phase == "coarse" else "This is the final detailed analysis. Be thorough."}

Provide your analysis as a JSON object matching the following schema:
{schema}

Focus on:
- Emotional manipulation tactics
- Gaslighting or reality distortion
- Guilt-tripping or victim-blaming  
- False urgency or pressure
- Love bombing or excessive flattery
- Projection or blame-shifting
- Minimization or denial of concerns

Return only valid JSON.
"""
    
    return prompt, schema


def build_argument_prompt(ctx: "AnalysisContext", phase: str = "coarse") -> Tuple[str, Dict[str, Any]]:  # type: ignore
    """Build argument structure analysis prompt with JSON schema.
    
    Args:
        ctx: AnalysisContext with transcript, audio, metrics, etc.
        phase: "coarse" for early analysis, "final" for complete analysis
    
    Returns:
        Tuple of (prompt_text, json_schema)
    """
    transcript = ctx.transcript_final or ctx.transcript_partial or ""
    
    # Build context summary
    context_report = build_context_report(ctx)
    
    # Schema for argument analysis
    schema = {
        "type": "object",
        "properties": {
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "support": {"type": "array", "items": {"type": "string"}},
                        "contradictions": {"type": "array", "items": {"type": "string"}},
                        "speaker": {"type": "string"},
                    },
                    "required": ["claim", "confidence", "support"]
                }
            },
            "logical_fallacies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "location": {"type": "string"},
                    },
                    "required": ["type", "description"]
                }
            },
            "argument_quality": {
                "type": "object",
                "properties": {
                    "coherence": {"type": "number", "minimum": 0, "maximum": 100},
                    "evidence_strength": {"type": "number", "minimum": 0, "maximum": 100},
                    "logical_consistency": {"type": "number", "minimum": 0, "maximum": 100},
                },
                "required": ["coherence", "evidence_strength", "logical_consistency"]
            },
            "hesitations": {
                "type": "array",
                "items": {"type": "string"}
            },
        },
        "required": ["claims", "logical_fallacies", "argument_quality"]
    }
    
    # Check if audio is available to add audio analysis reminder
    audio_reminder = ""
    if ctx.audio_bytes or ctx.audio_summary:
        audio_reminder = """
IMPORTANT: Audio data is available for this analysis. When analyzing, pay close attention to:
- Vocal tone and emotional inflections
- Speaking pace and rhythm changes
- Hesitations, pauses, and stammering
- Pitch variations and stress patterns
- Voice quality indicators (trembling, shakiness, confidence)
- Prosodic features that may reveal argument weakness or uncertainty

Use both the transcript text AND the audio characteristics to inform your analysis.
"""
    
    prompt = f"""Analyze the logical structure and argumentation in the following transcript.

Transcript:
"{transcript}"

Context information:
{_format_context(context_report)}
{audio_reminder}
Phase: {phase}
{"This is an early coarse analysis. Identify main claims and obvious issues." if phase == "coarse" else "This is the final detailed analysis. Provide comprehensive argument mapping."}

Provide your analysis as a JSON object matching the following schema:
{schema}

Focus on:
- Main claims and their supporting evidence
- Logical fallacies (ad hominem, straw man, false dichotomy, etc.)
- Contradictions within the argument
- Quality of evidence and reasoning
- Hesitations or uncertainty markers
- Speaker attribution if multiple speakers present

Return only valid JSON.
"""
    
    return prompt, schema


def _format_context(context_report: Dict[str, Any]) -> str:
    """Format context report for inclusion in prompts."""
    lines = []
    for key, value in context_report.items():
        if isinstance(value, dict):
            lines.append(f"- {key}:")
            for sub_key, sub_value in value.items():
                lines.append(f"  - {sub_key}: {sub_value}")
        else:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)
