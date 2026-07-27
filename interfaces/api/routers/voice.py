"""
Voice session API.

Exposes endpoints for creating and managing voice sessions
used by the frontend VoiceLandingAgent component.
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice"])


class CreateSessionRequest(BaseModel):
    greeting_type: str = "proactive"
    visitor_id: Optional[str] = None
    tenant_id: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    visitor_id: str


@router.post("/session", response_model=CreateSessionResponse)
async def create_voice_session(payload: CreateSessionRequest):
    """
    Create a new voice session.

    Returns a session ID that the frontend VoiceLandingAgent
    uses to track the conversation.  The session is ephemeral
    (in-memory) until a backend VoiceSessionManager is wired.
    """
    visitor_id = payload.visitor_id or f"visitor_{uuid.uuid4().hex[:12]}"
    session_id = f"voice_{uuid.uuid4().hex[:12]}"

    logger.info(
        "Created voice session: %s for visitor: %s (greeting: %s)",
        session_id,
        visitor_id,
        payload.greeting_type,
    )

    return CreateSessionResponse(
        session_id=session_id,
        visitor_id=visitor_id,
    )
