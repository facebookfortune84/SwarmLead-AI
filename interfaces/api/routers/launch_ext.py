"""
Company launch / growth ballistics API.

Exposes the voice-driven Company Concierge, outreach maximization, and nurture
engines to the frontend and CLI:

- POST /api/launch/concierge/start       - begin a guided company-creation session
- POST /api/launch/concierge/message     - advance the session with a founder reply
- GET  /api/launch/concierge/{id}        - fetch session brief / status
- POST /api/launch/concierge/{id}/end    - close a session
- GET  /api/launch/concierge/status      - concierge overview
- GET  /api/launch/maximize              - outreach maximization score + levers
- GET  /api/launch/nurture               - nurture plan + reply classifier
"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from core.services.company_concierge import company_concierge
from core.services.nurture_engine import nurture_engine
from core.services.outreach_maximization import outreach_maximizer

router = APIRouter(prefix="/api/launch", tags=["Launch"])


class ConciergeStart(BaseModel):
    founder_name: Optional[str] = ""
    opening_line: Optional[str] = ""


class ConciergeMessage(BaseModel):
    session_id: str
    text: str


class MaximizeProbe(BaseModel):
    email: Optional[str] = ""
    name: Optional[str] = ""
    company: Optional[str] = ""
    intent_score: Optional[int] = None
    source: Optional[str] = ""
    details: Optional[dict] = None


class NurtureProbe(BaseModel):
    email: Optional[str] = ""
    reply: Optional[str] = ""
    days_since_contact: Optional[int] = 0


@router.post("/concierge/start")
async def concierge_start(payload: ConciergeStart):
    """Start a guided (voice/text) company-creation conversation."""
    result = company_concierge.start(
        founder_name=payload.founder_name or "",
        opening_line=payload.opening_line or "",
    )
    return result


@router.post("/concierge/message")
async def concierge_message(payload: ConciergeMessage):
    """Advance the concierge with the founder's reply."""
    return company_concierge.advance(payload.session_id, payload.text)


@router.get("/concierge/status")
async def concierge_status():
    """Concierge registry overview."""
    return company_concierge.status()


@router.get("/concierge/{session_id}")
async def concierge_get(session_id: str):
    """Fetch the concierge brief / status for a session."""
    if session_id in {"status"}:
        return company_concierge.status()
    brief = company_concierge.brief_for(session_id)
    if brief is None:
        return {"session_id": session_id, "found": False}
    return {"session_id": session_id, "found": True, "brief": brief}


@router.post("/concierge/{session_id}/end")
async def concierge_end(session_id: str):
    """Close a concierge session (cleanup)."""
    removed = company_concierge.end(session_id)
    return {"session_id": session_id, "ended": removed}


@router.post("/maximize")
async def maximize(payload: MaximizeProbe):
    """Score an outbound opportunity and return applicable maximization levers."""
    lead = {
        "email": payload.email,
        "name": payload.name,
        "company": payload.company,
        "intent_score": payload.intent_score,
        "source": payload.source,
        "details": payload.details or {},
    }
    return outreach_maximizer.maximize(lead)


@router.get("/maximize/levers")
async def maximize_levers():
    """The full outreach maximization lever catalog."""
    return {"total": outreach_maximizer.count(), "levers": outreach_maximizer.all_levers()}


@router.post("/nurture/plan")
async def nurture_plan(payload: NurtureProbe):
    """Return the deterministic 5-touch nurture plan for a lead."""
    return nurture_engine.plan(payload.email or "")


@router.post("/nurture/classify")
async def nurture_classify(payload: NurtureProbe):
    """Classify an inbound reply and decide the next nurture action."""
    return nurture_engine.apply(payload.reply or "")


@router.get("/nurture/status")
async def nurture_status():
    return nurture_engine.status()