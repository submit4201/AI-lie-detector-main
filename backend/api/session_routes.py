from fastapi import APIRouter, HTTPException, Path, Depends
import logging

from backend.models import (
    NewSessionResponse,
    SessionHistoryResponse,
    SessionHistoryItem,  # Needed for constructing response
    DeleteSessionResponse,
    ErrorResponse,
)
from datetime import datetime
from ..services.session_service import conversation_history_service # Import the instance

router = APIRouter()

@router.post(
    "/new",
    response_model=NewSessionResponse,
    tags=["Session Management"],
    summary="Create New Session",
    description="Initializes a new conversation session and returns a unique session ID.",
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error during session creation."}
    }
)
async def create_new_session_endpoint():
    try:
        session_id = conversation_history_service.get_or_create_session()
        # Include creation timestamp to satisfy the response model
        return NewSessionResponse(session_id=session_id, created_at=datetime.utcnow(), message="New session created successfully.")
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get(
    "/{session_id}/history",
    response_model=SessionHistoryResponse,
    tags=["Session Management"],
    summary="Get Session History",
    description="Retrieves the conversation history for a given session ID. History includes summaries of past analyses.",
    responses={
        404: {"model": ErrorResponse, "description": "Session not found."},
        500: {"model": ErrorResponse, "description": "Internal server error."}
    }
)
async def get_session_history_endpoint(
    session_id: str = Path(..., description="The ID of the session to retrieve history for.")
):
    try:
        # Check if session exists first to provide a clear 404
        if session_id not in conversation_history_service.sessions:
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found.")

        history_items_data = conversation_history_service.get_session_history_for_api(session_id)

        # Convert data to SessionHistoryItem model instances
        history_items = [SessionHistoryItem(**item) for item in history_items_data]

        return SessionHistoryResponse(session_id=session_id, history=history_items)
    except HTTPException:
        raise # Re-raise HTTPException
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history: {str(e)}")


@router.delete(
    "/{session_id}",
    response_model=DeleteSessionResponse,
    tags=["Session Management"],
    summary="Delete Session",
    description="Deletes all data associated with a given session ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Session not found."},
        500: {"model": ErrorResponse, "description": "Internal server error."}
    }
)
async def delete_session_endpoint(
    session_id: str = Path(..., description="The ID of the session to delete.")
):
    try:
        if not conversation_history_service.delete_session(session_id):
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found or already deleted.")
        return DeleteSessionResponse(session_id=session_id, message="Session deleted successfully.")
    except HTTPException:
        raise # Re-raise HTTPException
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
