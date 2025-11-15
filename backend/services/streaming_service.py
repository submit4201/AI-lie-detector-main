"""
Streaming service for sending analysis results to frontend as they complete
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import WebSocket
import os

# Import services and models needed for the new pipeline
from backend.services.gemini_service import GeminiService, transcribe_with_gemini, analyze_emotions_with_gemini
from backend.services.audio_service import assess_audio_quality
from backend.services.linguistic_service import analyze_linguistic_patterns

from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService as ModularAudioAnalysisService # Alias to avoid confusion
from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.conversation_flow_service import ConversationFlowService

logger = logging.getLogger(__name__)

class AnalysisStreamer:
    """
    Handles streaming of analysis results to frontend as they complete
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a websocket for a session"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        """Disconnect websocket for a session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_analysis_update(self, session_id: str, analysis_type: str, data: Any): # data can be Dict or List
        """Send an analysis update to the frontend"""
        if session_id in self.active_connections:
            try:
                # If data is a Pydantic model, convert to dict
                if hasattr(data, 'dict') and callable(data.dict):
                    payload_data = data.dict()
                else:
                    payload_data = data

                message = {
                    "type": "analysis_update",
                    "analysis_type": analysis_type,
                    "data": payload_data,
                    "timestamp": str(time.time())
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
                logger.info(f"Sent {analysis_type} update to session {session_id}")
            except Exception as e:
                logger.error(f"Failed to send update to session {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_progress_update(self, session_id: str, step: str, progress: int, total_steps: int):
        """Send a progress update to the frontend"""
        if session_id in self.active_connections:
            try:
                message = {
                    "type": "progress_update",
                    "step": step,
                    "progress": progress,
                    "total_steps": total_steps,
                    "percentage": int((progress / total_steps) * 100)
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send progress to session {session_id}: {e}")
    
    async def send_error(self, session_id: str, error_message: str):
        """Send an error message to the frontend"""
        if session_id in self.active_connections:
            try:
                message = {
                    "type": "error",
                    "message": error_message,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send error to session {session_id}: {e}")

# Global streamer instance
analysis_streamer = AnalysisStreamer()

async def stream_analysis_pipeline(audio_path: str, session_id: str, session_context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
    """
    Streams the refactored analysis pipeline results as they complete, using modular services.
    Yields Server-Sent Events (SSE) formatted strings.
    """
    total_steps = 10 # Transcription + 8 modular services + Linguistic Analysis
    current_step = 0
    loop = asyncio.get_running_loop()

    def sse_format(data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data)}\n\n"

    try:
        gemini_service_instance = GeminiService() # Assumes GeminiService is defined and can be instantiated

        # Instantiate all modular services
        manipulation_service = ManipulationService(gemini_service_instance)
        argument_service = ArgumentService(gemini_service_instance)
        speaker_attitude_service = SpeakerAttitudeService(gemini_service_instance)
        enhanced_understanding_service = EnhancedUnderstandingService(gemini_service_instance)
        psychological_service = PsychologicalService(gemini_service_instance)
        modular_audio_analysis_service = ModularAudioAnalysisService(gemini_service_instance)
        quantitative_metrics_service = QuantitativeMetricsService(gemini_service_instance)
        conversation_flow_service = ConversationFlowService(gemini_service_instance)

        # 0. Audio Quality (Not a primary service, but good to have early)
        try:
            # assess_audio_quality expects a Pydub AudioSegment
            from pydub import AudioSegment as PydubAudioSegment
            audio_segment_pydub = await loop.run_in_executor(None, PydubAudioSegment.from_file, audio_path)
            audio_quality_data = assess_audio_quality(audio_segment_pydub)
            yield sse_format({'type': 'result', 'analysis_type': 'audio_quality', 'data': audio_quality_data})
        except Exception as e:
            logger.error(f"Streaming: Audio quality assessment failed: {e}")
            yield sse_format({'type': 'error', 'message': f'Audio quality assessment error: {str(e)}'})

        # 1. Transcription
        current_step += 1
        yield sse_format({'type': 'progress', 'step': 'Transcription', 'progress': current_step, 'total': total_steps})
        transcript_text = ""
        try:
            # transcribe_with_gemini is synchronous, run in executor
            transcript_text = await loop.run_in_executor(None, transcribe_with_gemini, audio_path)
            yield sse_format({'type': 'result', 'analysis_type': 'transcript', 'data': {'transcript': transcript_text}})
        except Exception as e:
            logger.error(f"Streaming: Transcription error: {e}", exc_info=True)
            yield sse_format({'type': 'error', 'message': f'Transcription error: {str(e)}'})
            transcript_text = "Transcription failed or audio was unintelligible."

        # If transcription fails badly, we might not want to proceed with text-based analyses.
        # However, services have fallbacks, so we can let them try.

        analysis_map = {
            "manipulation_assessment": (manipulation_service.analyze, [transcript_text, session_context]),
            "argument_analysis": (argument_service.analyze, [transcript_text, session_context]),
            "speaker_attitude": (speaker_attitude_service.analyze, [transcript_text, session_context]),
            "enhanced_understanding": (enhanced_understanding_service.analyze, [transcript_text, session_context]),
            "psychological_analysis": (psychological_service.analyze, [transcript_text, session_context]),
            "audio_specific_analysis": (modular_audio_analysis_service.analyze, [audio_path, transcript_text, session_context]), # This one needs audio_path
            "quantitative_metrics": (quantitative_metrics_service.analyze, [transcript_text, session_context]),
            "conversation_flow": (conversation_flow_service.analyze, [transcript_text, session_context]),
            # Emotion and Linguistic are not async services, run in executor
            "emotion_analysis": (lambda: loop.run_in_executor(None, analyze_emotions_with_gemini, audio_path, transcript_text), []),
            "linguistic_analysis": (lambda: loop.run_in_executor(None, analyze_linguistic_patterns, transcript_text), [])
        }
        
        # Update total_steps based on actual items in analysis_map
        total_steps = 1 + len(analysis_map) # 1 for initial transcription

        async def run_analysis(analysis_name, service_method, args):
            try:
                if asyncio.iscoroutinefunction(service_method):
                    result_data = await service_method(*args)
                elif callable(service_method) and not args:  # For the lambda wrapped executor calls
                    result_data = await service_method()
                else:  # Should not happen with current map, but as a fallback
                    result_data = await loop.run_in_executor(None, service_method, *args)
                
                # Pydantic models should be converted to dict for SSE
                if hasattr(result_data, 'dict') and callable(result_data.dict):
                    payload = result_data.dict()
                else:
                    payload = result_data
                yield sse_format({'type': 'result', 'analysis_type': analysis_name, 'data': payload})
            except Exception as e:
                logger.error(f"Streaming: Error in {analysis_name}: {e}", exc_info=True)
                yield sse_format({'type': 'error', 'message': f'Error in {analysis_name}: {str(e)}'})

        yield sse_format({'type': 'complete', 'message': 'Analysis pipeline completed'})

    except Exception as e:
        logger.error(f"Critical error in streaming_analysis_pipeline: {e}", exc_info=True)
        yield sse_format({'type': 'error', 'message': f'Critical pipeline error: {str(e)}'})
    finally:
        # Clean up temporary audio file (original audio_path is temp path from analysis_routes)
        try:
            if audio_path and os.path.exists(audio_path):
                await loop.run_in_executor(None, os.unlink, audio_path)
                logger.info(f"Cleaned up temporary file from streaming pipeline: {audio_path}")
        except Exception as e:
            logger.warning(f"Streaming: Failed to clean up temporary file {audio_path}: {e}")

# Note: The stream_analysis_pipeline in analysis_routes.py will need to pass session_context
# to this function if it's available and needed by the services.
"""
Streaming service for sending analysis results to frontend as they complete
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import WebSocket
import os

# Import services and models needed for the new pipeline
from backend.services.gemini_service import GeminiService, transcribe_with_gemini, analyze_emotions_with_gemini
from backend.services.audio_service import assess_audio_quality
from backend.services.linguistic_service import analyze_linguistic_patterns

from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService as ModularAudioAnalysisService # Alias to avoid confusion
from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.conversation_flow_service import ConversationFlowService

logger = logging.getLogger(__name__)

class AnalysisStreamer:
    """
    Handles streaming of analysis results to frontend as they complete
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a websocket for a session"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        """Disconnect websocket for a session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_analysis_update(self, session_id: str, analysis_type: str, data: Any): # data can be Dict or List
        """Send an analysis update to the frontend"""
        if session_id in self.active_connections:
            try:
                # If data is a Pydantic model, convert to dict
                if hasattr(data, 'dict') and callable(data.dict):
                    payload_data = data.dict()
                else:
                    payload_data = data

                message = {
                    "type": "analysis_update",
                    "analysis_type": analysis_type,
                    "data": payload_data,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
                logger.info(f"Sent {analysis_type} update to session {session_id}")
            except Exception as e:
                logger.error(f"Failed to send update to session {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_progress_update(self, session_id: str, step: str, progress: int, total_steps: int):
        """Send a progress update to the frontend"""
        if session_id in self.active_connections:
            try:
                message = {
                    "type": "progress_update",
                    "step": step,
                    "progress": progress,
                    "total_steps": total_steps,
                    "percentage": int((progress / total_steps) * 100)
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send progress to session {session_id}: {e}")
    
    async def send_error(self, session_id: str, error_message: str):
        """Send an error message to the frontend"""
        if session_id in self.active_connections:
            try:
                message = {
                    "type": "error",
                    "message": error_message,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send error to session {session_id}: {e}")

# Global streamer instance
analysis_streamer = AnalysisStreamer()

async def stream_analysis_pipeline(audio_path: str, session_id: str, session_context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
    """
    Streams the refactored analysis pipeline results as they complete, using modular services.
    Yields Server-Sent Events (SSE) formatted strings.
    """
    total_steps = 10 # Transcription + 8 modular services + Linguistic Analysis
    current_step = 0
    loop = asyncio.get_running_loop()

    def sse_format(data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data)}\n\n"

    try:
        gemini_service_instance = GeminiService() # Assumes GeminiService is defined and can be instantiated

        # Instantiate all modular services
        manipulation_service = ManipulationService(gemini_service_instance)
        argument_service = ArgumentService(gemini_service_instance)
        speaker_attitude_service = SpeakerAttitudeService(gemini_service_instance)
        enhanced_understanding_service = EnhancedUnderstandingService(gemini_service_instance)
        psychological_service = PsychologicalService(gemini_service_instance)
        modular_audio_analysis_service = ModularAudioAnalysisService(gemini_service_instance)
        quantitative_metrics_service = QuantitativeMetricsService(gemini_service_instance)
        conversation_flow_service = ConversationFlowService(gemini_service_instance)

        # 0. Audio Quality (Not a primary service, but good to have early)
        try:
            # assess_audio_quality expects a Pydub AudioSegment
            from pydub import AudioSegment as PydubAudioSegment
            audio_segment_pydub = await loop.run_in_executor(None, PydubAudioSegment.from_file, audio_path)
            audio_quality_data = assess_audio_quality(audio_segment_pydub)
            yield sse_format({'type': 'result', 'analysis_type': 'audio_quality', 'data': audio_quality_data})
        except Exception as e:
            logger.error(f"Streaming: Audio quality assessment failed: {e}")
            yield sse_format({'type': 'error', 'message': f'Audio quality assessment error: {str(e)}'})

        # 1. Transcription
        current_step += 1
        yield sse_format({'type': 'progress', 'step': 'Transcription', 'progress': current_step, 'total': total_steps})
        transcript_text = ""
        try:
            # transcribe_with_gemini is synchronous, run in executor
            transcript_text = await loop.run_in_executor(None, transcribe_with_gemini, audio_path)
            yield sse_format({'type': 'result', 'analysis_type': 'transcript', 'data': {'transcript': transcript_text}})
        except Exception as e:
            logger.error(f"Streaming: Transcription error: {e}", exc_info=True)
            yield sse_format({'type': 'error', 'message': f'Transcription error: {str(e)}'})
            transcript_text = "Transcription failed or audio was unintelligible."

        # If transcription fails badly, we might not want to proceed with text-based analyses.
        # However, services have fallbacks, so we can let them try.

        analysis_map = {
            "manipulation_assessment": (manipulation_service.analyze, [transcript_text, session_context]),
            "argument_analysis": (argument_service.analyze, [transcript_text, session_context]),
            "speaker_attitude": (speaker_attitude_service.analyze, [transcript_text, session_context]),
            "enhanced_understanding": (enhanced_understanding_service.analyze, [transcript_text, session_context]),
            "psychological_analysis": (psychological_service.analyze, [transcript_text, session_context]),
            "audio_specific_analysis": (modular_audio_analysis_service.analyze, [audio_path, transcript_text, session_context]), # This one needs audio_path
            "quantitative_metrics": (quantitative_metrics_service.analyze, [transcript_text, session_context]),
            "conversation_flow": (conversation_flow_service.analyze, [transcript_text, session_context]),
            # Emotion and Linguistic are not async services, run in executor
            "emotion_analysis": (lambda: loop.run_in_executor(None, analyze_emotions_with_gemini, audio_path, transcript_text), []),
            "linguistic_analysis": (lambda: loop.run_in_executor(None, analyze_linguistic_patterns, transcript_text), [])
        }
        
        # Update total_steps based on actual items in analysis_map
        total_steps = 1 + len(analysis_map) # 1 for initial transcription

        for analysis_name, (service_method, args) in analysis_map.items():
            current_step += 1
            yield sse_format({'type': 'progress', 'step': analysis_name.replace("_", " ").title(), 'progress': current_step, 'total': total_steps})
            try:
                if asyncio.iscoroutinefunction(service_method):
                    result_data = await service_method(*args)
                elif callable(service_method) and not args: # For the lambda wrapped executor calls
                    result_data = await service_method() 
                else: # Should not happen with current map, but as a fallback
                    result_data = await loop.run_in_executor(None, service_method, *args)
                
                # Pydantic models should be converted to dict for SSE
                if hasattr(result_data, 'dict') and callable(result_data.dict):
                    payload = result_data.dict()
                else:
                    payload = result_data
                yield sse_format({'type': 'result', 'analysis_type': analysis_name, 'data': payload})
            except Exception as e:
                logger.error(f"Streaming: Error in {analysis_name}: {e}", exc_info=True)
                yield sse_format({'type': 'error', 'message': f'Error in {analysis_name}: {str(e)}'})

        yield sse_format({'type': 'complete', 'message': 'Analysis pipeline completed'})

    except Exception as e:
        logger.error(f"Critical error in streaming_analysis_pipeline: {e}", exc_info=True)
        yield sse_format({'type': 'error', 'message': f'Critical pipeline error: {str(e)}'})
    finally:
        # Clean up temporary audio file (original audio_path is temp path from analysis_routes)
        try:
            if audio_path and os.path.exists(audio_path):
                await loop.run_in_executor(None, os.unlink, audio_path)
                logger.info(f"Cleaned up temporary file from streaming pipeline: {audio_path}")
        except Exception as e:
            logger.warning(f"Streaming: Failed to clean up temporary file {audio_path}: {e}")

# Note: The stream_analysis_pipeline in analysis_routes.py will need to pass session_context
# to this function if it's available and needed by the services.
