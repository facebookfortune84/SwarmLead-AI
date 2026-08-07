"""
Revenue analytics API — read-only reporting over the sales pipeline,
growth-loop quote state, and monetization billing configuration.
"""

from fastapi import APIRouter, Query

from core.services.monetization import monetization
from core.services.revenue_analytics import revenue_analytics

router = APIRouter(prefix="/api/revenue", tags=["Revenue"])


@router.get("/summary")
async def summary():
    return revenue_analytics.summary()


@router.get("/tiers")
async def tiers():
    return monetization.billing_options()


@router.get("/churn")
async def churn(
    lookback_days: int = Query(60, ge=1, le=365),
    churn_rate: float | None = Query(None, ge=0.0, le=1.0),
    months: int = Query(12, ge=1, le=60),
):
    return {
        "risk": revenue_analytics.churn_risk(max_days_inactive=lookback_days),
        "retention_curve": revenue_analytics.retention_curve(
            months=months, churn_rate=churn_rate
        ),
        "ltv": revenue_analytics.ltv(churn_rate=churn_rate),
    }


@router.get("/dunning")
async def dunning_draft(
    email: str,
    invoice_id: str | None = None,
):
    """Draft (never sends) the dunning email for a failed payment."""
    return monetization.dunning_notice(email, {"id": invoice_id} if invoice_id else {})


@router.get("/usage")
async def usage_bill(
    units: float = Query(..., gt=0),
    rate_cents: float = Query(50, gt=0),
    label: str = "compute hours",
):
    """Estimate a usage-based invoice (never charges)."""
    return monetization.usage_bill(units, rate_cents, label)


@router.get("/referral")
async def referral(email: str | None = Query(None)):
    """Referral program config + a stable share code per account."""
    return monetization.referral_program(email)


@router.get("/upsell")
async def upsell(lead_email: str | None = Query(None)):
    """Expansion recommendations for existing accounts."""
    lead = {"intent_score": 90} if lead_email else None
    return {"recommendations": monetization.upsell_recommendations(lead)}


@router.get("/map")
async def leverage_map():
    """The monetization map — every active lever + projected MRR uplift."""
    return monetization.leverage_map()
