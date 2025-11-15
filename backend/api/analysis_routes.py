import os
import pathlib
pathlib.Path(__file__).parent.parent.resolve()
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import tempfile
import os
import logging
import asyncio # Added for running async pipeline if needed in future, though route is already async
from typing import Optional, Dict, Any # Added Dict, Any
from pydub import AudioSegment

from backend.models import AnalyzeResponse, ErrorResponse # Ensure AnalyzeResponse matches the new structure
from backend.services.audio_service import assess_audio_quality # Removed streaming_audio_analysis_pipeline as it will be updated later
# Keep query_gemini and validate_and_structure_gemini_response for /analyze_text
from backend.services.gemini_service import (
    query_gemini, 
    validate_and_structure_gemini_response,
    full_audio_analysis_pipeline # Added new pipeline
)
from backend.services.linguistic_service import analyze_linguistic_patterns
from backend.services.session_service import conversation_history_service
from backend.services.session_insights_service import SessionInsightsGenerator
from backend.services.streaming_service import analysis_streamer, stream_analysis_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()

session_insights_generator = SessionInsightsGenerator()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time analysis updates"""
    await analysis_streamer.connect(websocket, session_id)
    try:
        ping_interval = 20  # seconds
        timeout = 30  # seconds
        last_pong = asyncio.get_event_loop().time()

        while True:
            try:
                # Send a ping to the client
                await websocket.send_ping()

                # Wait for a message or pong response with a timeout
                done, pending = await asyncio.wait(
                    [
                        websocket.receive_text(),
                        websocket.receive_pong(),
                    ],
                    timeout=timeout,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Handle received messages or pongs
                for task in done:
                    if task is websocket.receive_text():
                        data = task.result()
                        # Could handle client commands here if needed
                    elif task is websocket.receive_pong():
                        last_pong = asyncio.get_event_loop().time()

                # Check if the client has stopped responding
                if asyncio.get_event_loop().time() - last_pong > ping_interval:
                    logger.warning(f"Client {session_id} unresponsive, closing connection.")
                    break

            except asyncio.TimeoutError:
                logger.warning(f"Timeout waiting for client {session_id}, closing connection.")
                break
            except WebSocketDisconnect:
                logger.info(f"Client {session_id} disconnected.")
                break
    except WebSocketDisconnect:
        analysis_streamer.disconnect(session_id)

@router.post(
    "/analyze/stream",
    tags=["Analysis"],
    summary="Stream Audio Analysis",
    description="Uploads an audio file and streams analysis results as they complete. Returns Server-Sent Events with real-time updates.",
)
async def stream_analyze_audio(
    audio: UploadFile = File(..., description="Audio file to be analyzed"),
    session_id_form: Optional[str] = Form(None, alias="session_id")
):
    """Stream analysis results as they complete"""
    temp_audio_path = None # Initialize to ensure it's defined in finally block
    try:
        # Resolve session_id
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        logger.info(f"Starting streaming analysis for session: {current_session_id}")
        
        # Validate audio file
        valid_audio_types = ['audio/', 'video/']
        valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm', '.flac']
        
        is_valid_content_type = (audio.content_type and 
                               any(audio.content_type.startswith(t) for t in valid_audio_types))
        is_valid_extension = (audio.filename and 
                            any(audio.filename.lower().endswith(ext) for ext in valid_extensions))
        
        if not (is_valid_content_type or is_valid_extension):
            raise HTTPException(status_code=422, detail="Invalid audio file type")
          # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename or ".wav")[1]) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        # Get session context for the streaming pipeline
        session_context_data = conversation_history_service.get_session_context(current_session_id)

        # Return streaming response
        return StreamingResponse(
            stream_analysis_pipeline(temp_audio_path, current_session_id, session_context_data),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming analysis: {e}")
        # Clean up temp file on error
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except Exception as unlink_e:
                logger.error(f"Error unlinking temp file during streaming error handling: {unlink_e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze Audio File",
    description="Uploads an audio file and performs a comprehensive analysis for deception, emotion, and other speech patterns. Returns detailed results including a transcript, audio quality assessment, emotion scores, and AI-driven insights.",    responses={
        200: {"description": "Successful analysis"},
        400: {"model": ErrorResponse, "description": "Invalid input (e.g., not an audio file, file too short, unintelligible audio)."},
        413: {"model": ErrorResponse, "description": "File too large."},
        422: {"model": ErrorResponse, "description": "Validation error (e.g., invalid file type by content)."},
        500: {"model": ErrorResponse, "description": "Internal server error during analysis."}
    }
)
async def analyze_audio_route(
    audio: UploadFile = File(..., description="Audio file to be analyzed (WAV, MP3, OGG, WEBM). Max size 15MB."),
    session_id_form: Optional[str] = Form(None, alias="session_id", description="Optional session ID for conversation continuity. If not provided, a new session will be created.")
):
    try:
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        logger.info(f"Starting analysis for session: {current_session_id}")
        # ... existing audio file validation and size check ...
        valid_audio_types = ['audio/', 'video/']
        valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm', '.flac']
        
        is_valid_content_type = (audio.content_type and 
                               any(audio.content_type.startswith(t) for t in valid_audio_types))
        is_valid_extension = (audio.filename and 
                            any(audio.filename.lower().endswith(ext) for ext in valid_extensions))
        
        if not (is_valid_content_type or is_valid_extension):
            raise HTTPException(status_code=400, detail="File must be an audio file (MP3, WAV, M4A, AAC, OGG, WEBM, FLAC).")

        audio_content = await audio.read()
        file_size = len(audio_content)

        logger.info(f"Received audio file: {audio.filename or 'unnamed'}, Content-Type: {audio.content_type}, Size: {file_size} bytes for session {current_session_id}")

        MAX_FILE_SIZE = 15 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size {file_size} bytes exceeds {MAX_FILE_SIZE}MB limit.")
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")

        suffix = os.path.splitext(audio.filename or "")[1] if audio.filename and os.path.splitext(audio.filename)[1] else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio_content)
            temp_audio_path = temp_audio.name
        del audio_content

        wav_path = None
        pipeline_output: Dict[str, Any] = {} # Ensure it's defined for the scope after loop
        audio_quality_metrics: Dict[str, Any] = {} # Ensure it's defined
        transcript_text_from_pipeline: str = ""

        try:
            audio_segments = []
            audio_segment_pydub = AudioSegment.from_file(temp_audio_path)
            if audio_segment_pydub.duration_seconds < 1:
                raise HTTPException(status_code=400, detail="Audio file is too short. Please provide audio that is at least 1 second long.")
            
            # Segmentation logic (existing)
            if audio_segment_pydub.duration_seconds > 120:
                for i in range(0, len(audio_segment_pydub), 120000):
                    audio_segments.append(audio_segment_pydub[i:i+120000])
            else:
                audio_segments.append(audio_segment_pydub)
            
            session_context_data = conversation_history_service.get_session_context(current_session_id)

            for current_segment_pydub in audio_segments: # Iterate over Pydub segments
                logger.info(f"Processing segment of {current_segment_pydub.duration_seconds} seconds for session {current_session_id}")
                current_audio_quality_metrics = assess_audio_quality(current_segment_pydub)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_segment:
                    wav_path_segment = temp_wav_segment.name
                current_segment_pydub.export(wav_path_segment, format="wav")
                
                try:
                    # Call the new full_audio_analysis_pipeline
                    # Pass session_context_data which might be used by services
                    logger.info(f"Calling full_audio_analysis_pipeline for segment: {wav_path_segment}")
                    current_pipeline_output = await full_audio_analysis_pipeline(
                        audio_path=wav_path_segment, 
                        existing_transcript=None, # Pipeline handles transcription
                        session_context=session_context_data
                    )
                    logger.info(f"Pipeline analysis for segment completed.")
                    # The pipeline output is now a dictionary of Pydantic models or dicts
                    # For simplicity, the loop currently overwrites; last segment's results are used.
                    # This matches previous behavior but could be improved for multi-segment aggregation.
                    pipeline_output = current_pipeline_output 
                    audio_quality_metrics = current_audio_quality_metrics
                    transcript_text_from_pipeline = pipeline_output.get('transcript', "No transcript from pipeline.")

                except Exception as e:
                    logger.error(f"Error during full_audio_analysis_pipeline for segment {wav_path_segment}: {e}", exc_info=True)
                    # If pipeline fails for a segment, we might use fallback or skip
                    # For now, if it fails, pipeline_output might not be updated for this segment
                    # Consider how to handle partial failures if segments are to be combined.
                    # For now, let it proceed, subsequent code will use last successful pipeline_output.
                    # If no segment succeeds, pipeline_output will be empty.
                    # A more robust approach would be to collect all segment results and merge.
                    # To ensure pipeline_output is not from a failed run, only assign on success.
                    # However, the services in the pipeline have their own fallbacks.
                    # Let's assume pipeline_output will contain default models if services failed internally.
                    # If the pipeline itself raises an exception, then current_pipeline_output won't be assigned.
                    raise HTTPException(status_code=500, detail=f"Core analysis pipeline failed for a segment: {str(e)}")
                finally:
                    if os.path.exists(wav_path_segment):
                        os.unlink(wav_path_segment)
            
            # Ensure pipeline_output is not empty if all segments failed before assignment
            if not pipeline_output:
                 logger.error("No segment processed successfully by the analysis pipeline.")
                 raise HTTPException(status_code=500, detail="Analysis pipeline failed to process any audio segment.")

            # Construct final response using the (last segment's) pipeline_output
            final_result_data: Dict[str, Any] = {
                "session_id": current_session_id,
                "speaker_name": "Speaker 1",  # Default speaker name, consider making dynamic
                "transcript": transcript_text_from_pipeline, # From the last processed segment
                "audio_quality": audio_quality_metrics, # From the last processed segment
                **pipeline_output # Spread all analysis fields from the pipeline output
            }
            
            # Add session insights (uses the pipeline_output from the last segment)
            if session_context_data.get("previous_analyses", 0):
                session_history = conversation_history_service.get_session_history(current_session_id)
                session_insights = session_insights_generator.generate_session_insights(
                    session_context_data, 
                    pipeline_output, # Pass the full output of the last segment's pipeline
                    session_history
                )
                if session_insights:
                    final_result_data['session_insights'] = session_insights

            conversation_history_service.add_analysis(current_session_id, transcript_text_from_pipeline, final_result_data)
            logger.info(f"Analysis completed successfully for session {current_session_id}. Returning AnalyzeResponse.")
            return AnalyzeResponse(**final_result_data)

        except HTTPException: # Re-raise HTTPExceptions directly
            raise
        except Exception as e: # Catch-all for other unexpected errors during processing
            logger.error(f"Unexpected error processing audio file {audio.filename or 'unnamed'} in session {current_session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during audio processing: {str(e)}")
        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            # wav_path was for the whole file if not segmented, segments use wav_path_segment
            # if wav_path and os.path.exists(wav_path):
            #     os.unlink(wav_path) # This wav_path is not used in the new segment logic

    except HTTPException: # Re-raise HTTPExceptions from initial checks
        raise
    except Exception as e: # Catch-all for truly unexpected errors
        logger.error(f"Critical unexpected error in /analyze endpoint for session {session_id_form}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"A critical unexpected error occurred: {str(e)}")

@router.post(
    "/analyze_text",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze Text Input",
    description="Analyzes text input for deception, manipulation, and other linguistic patterns. Useful for testing UI components."
)
async def analyze_text_input(
    request: dict, # Changed from AnalyzeTextRequest to dict to match existing code
    session_id: Optional[str] = None # Changed from session_id_form to session_id
):
    """
    Analyze text input for testing the new UI components.
    """
    try:
        text = request.get("text", "")
        speaker_name = request.get("speaker_name", "Speaker")
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text must be at least 10 characters long")
        if not session_id:
            session_id = conversation_history_service.get_or_create_session()
        
        session_context_data = conversation_history_service.get_session_context(session_id)
        linguistic_analysis_results = analyze_linguistic_patterns(text) # Renamed variable
        
        gemini_raw_response = query_gemini(text, linguistic_analysis_results, session_context_data)
        # The validate_and_structure_gemini_response expects linguistic_analysis as the third param in some versions.
        # The current gemini_service.py version of validate_and_structure_gemini_response takes (raw_response, transcript)
        # Let's assume it's (raw_response, transcript) for now.
        validated_gemini_analysis = validate_and_structure_gemini_response(gemini_raw_response, text)

        final_result_data: Dict[str, Any] = {
            "session_id": session_id,
            "speaker_name": speaker_name,
            "transcript": text,
            "audio_quality": { # Default for text-only
                "duration": 0.0, "sample_rate": 0, "channels": 0, "loudness": 0.0,
                "quality_score": 0, "overall_quality": "N/A", "signal_to_noise_ratio": 0,
                "clarity_score": 0, "volume_consistency": 0, "background_noise_level": 0
            },
            "emotion_analysis": [],  # Default for text-only
            # The new pipeline output has specific keys for each analysis type.
            # validated_gemini_analysis from query_gemini is structured to match this.
            **validated_gemini_analysis # This should spread all the fields like manipulation_assessment etc.
        }
        
        # Ensure linguistic_analysis and quantitative_metrics are correctly placed if not spread by validated_gemini_analysis
        # query_gemini is prompted to return these within its structure.
        # If they are separate in AnalyzeResponse and not in validated_gemini_analysis top level, add them:
        if 'linguistic_analysis' not in validated_gemini_analysis:
            final_result_data['linguistic_analysis'] = linguistic_analysis_results
        if 'quantitative_metrics' not in validated_gemini_analysis and 'quantitative_metrics' in linguistic_analysis_results:
             final_result_data['quantitative_metrics'] = linguistic_analysis_results['quantitative_metrics']
        elif 'quantitative_metrics' not in validated_gemini_analysis:
            # If linguistic_analysis_results doesn't nest quantitative_metrics, it might be flat
            # This depends on analyze_linguistic_patterns output and AnalyzeResponse model
            # For now, assume query_gemini provides it within validated_gemini_analysis.
            pass 

        if session_context_data.get("previous_analyses", 0) > 0 and 'session_insights' not in validated_gemini_analysis:
            session_history = conversation_history_service.get_session_history(session_id)
            session_insights = session_insights_generator.generate_session_insights(
                session_context_data, 
                validated_gemini_analysis, 
                session_history
            )
            if session_insights:
                final_result_data['session_insights'] = session_insights
        
        conversation_history_service.add_analysis(session_id, text, final_result_data)
        return AnalyzeResponse(**final_result_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")
