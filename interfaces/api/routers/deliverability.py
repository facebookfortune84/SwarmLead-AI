"""
Deliverability API — DNS records, sender-health score, suppression list.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from interfaces.api.auth.middleware import get_current_active_user

from core.services.deliverability import deliverability

router = APIRouter(
    prefix="/api/deliverability",
    tags=["Deliverability"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/records")
async def records(domain: str):
    """Copy-paste SPF/DKIM/DMARC records for a sending domain."""
    return deliverability.recommended_records(domain)


@router.get("/dns")
async def dns(domain: str):
    """Live SPF/DMARC TXT lookup for a domain."""
    return deliverability.check_dns(domain)


@router.get("/score")
async def score():
    """Sender-health score + warnings for the current config."""
    return deliverability.score()


@router.get("/suppression")
async def suppression():
    """Current suppression list and reason counts."""
    return {
        "stats": deliverability.suppression_stats(),
        "count": len(deliverability._suppressed),
    }


class SuppressRequest(BaseModel):
    email: str
    reason: str = "manual"


@router.post("/suppress")
async def suppress(payload: SuppressRequest):
    """Manually suppress an address (unsubscribe / do-not-contact)."""
    added = deliverability.suppress(payload.email, payload.reason)
    return {"suppressed": True, "new": added}


@router.post("/bounce")
async def bounce(payload: SuppressRequest):
    """Record a hard bounce for an address."""
    deliverability.record_bounce(payload.email, payload.reason)
    return {"recorded": True}
