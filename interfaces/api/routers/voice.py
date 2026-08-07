"""
Voice session API.

Exposes endpoints for the frontend VoiceLandingAgent:
- POST /session  -> create a session and get the greeting (text + audio)
- POST /message  -> process a user message and get a guided reply (text + audio)
- POST /end      -> end / cleanup a session
"""

import logging
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from core.services.voice_agent_service import voice_agent_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice"])


class CreateSessionRequest(BaseModel):
    greeting_type: str = "proactive"
    visitor_id: Optional[str] = None
    tenant_id: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    visitor_id: str
    greeting: str
    greeting_audio_b64: Optional[str] = None


class MessageRequest(BaseModel):
    session_id: str
    text: str


class MessageResponse(BaseModel):
    session_id: str
    reply: str
    reply_audio_b64: Optional[str] = None
    intent: str = "general"


class EndSessionRequest(BaseModel):
    session_id: str


class LeadCaptureRequest(BaseModel):
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    session_id: Optional[str] = None
    source: str = "voice"
    intent_score: Optional[int] = None


class LeadCaptureResponse(BaseModel):
    created: bool
    lead_id: Optional[str] = None
    email: str


@router.post("/session", response_model=CreateSessionResponse)
async def create_voice_session(payload: CreateSessionRequest):
    """
    Create a voice session and return the proactive greeting.

    The frontend speaks the greeting audio immediately so the assistant
    leads the conversation from the moment the visitor arrives.
    """
    result = await voice_agent_service.create_session(payload.greeting_type)
    logger.info(
        "Created voice session: %s for visitor: %s (greeting: %s)",
        result["session_id"],
        result["visitor_id"],
        payload.greeting_type,
    )
    return result


@router.post("/message", response_model=MessageResponse)
async def send_voice_message(payload: MessageRequest):
    """
    Process a user message and return the assistant's guided reply.

    Runs the full duplex loop: user text -> LLM guided reply -> TTS audio.
    """
    result = await voice_agent_service.process_message(payload.session_id, payload.text)
    logger.info(
        "Voice message processed for %s (intent: %s)",
        result["session_id"],
        result.get("intent"),
    )
    return result


@router.post("/end")
async def end_voice_session(payload: EndSessionRequest):
    """End and clean up a voice session."""
    removed = voice_agent_service.end_session(payload.session_id)
    return {"session_id": payload.session_id, "ended": removed}


@router.get("/models")
async def voice_models():
    """Report which LLM model is powering the voice assistant right now."""
    return voice_agent_service.model_status()


@router.post("/capture", response_model=LeadCaptureResponse)
async def capture_voice_lead(payload: LeadCaptureRequest):
    """
    Persist a lead captured during a voice conversation.

    The voice agent asks for name + email; the frontend posts it here and the
    visitor becomes a high-intent lead (source: voice) that flows into the
    pipeline exactly like discovered leads.
    """
    result = voice_agent_service.capture_lead(
        email=payload.email,
        name=payload.name,
        company=payload.company,
        source=payload.source,
        intent_score=payload.intent_score,
    )
    logger.info("Voice lead capture: %s", result)
    return result


class ConciergeStartRequest(BaseModel):
    founder_name: Optional[str] = None
    opening_line: Optional[str] = None


class ConciergeTurnRequest(BaseModel):
    session_id: str
    text: str


@router.post("/concierge/start")
async def concierge_start(payload: ConciergeStartRequest):
    """Start a voice-driven company-creation session (name, domain, audience, offer)."""
    return await voice_agent_service.concierge_start(
        founder_name=payload.founder_name or "",
        opening_line=payload.opening_line or "",
    )


@router.post("/concierge/turn")
async def concierge_turn(payload: ConciergeTurnRequest):
    """Advance the voice-led company concierge with the founder's answer."""
    return await voice_agent_service.concierge_turn(payload.session_id, payload.text)
