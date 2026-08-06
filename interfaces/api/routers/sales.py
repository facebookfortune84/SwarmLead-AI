"""
Sales API — control surface for the AI sales team.

Endpoints:
- GET    /api/sales/pipeline     stage-by-stage pipeline + weighted value
- GET    /api/sales/deals        list deals (filter by stage)
- GET    /api/sales/deals/{id}   single deal + stage history
- POST   /api/sales/deals        create a deal from a lead
- POST   /api/sales/advance      move a deal to the next stage
- POST   /api/sales/close        close won/lost
- GET    /api/sales/forecast     projected revenue (monthly + annual)
- POST   /api/sales/qualify      run SDR qualification over leads
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.agents.sales.closer_agent import CloserAgent
from core.agents.sales.sdr_agent import SDRAgent
from core.services.sales_pipeline import SalesPipeline, sales_pipeline

router = APIRouter(prefix="/api/sales", tags=["Sales"])


class DealCreate(BaseModel):
    lead_id: str
    email: str
    company: str | None = None
    intent_score: int | None = None
    company_size: int | None = None
    metadata: dict | None = None


class AdvanceRequest(BaseModel):
    deal_id: str
    stage: str
    note: str = ""


class CloseRequest(BaseModel):
    deal_id: str
    won: bool
    note: str = ""


class QualifyRequest(BaseModel):
    leads: list[dict]


def _svc() -> SalesPipeline:
    return sales_pipeline


@router.get("/pipeline")
async def pipeline():
    return _svc().pipeline_snapshot()


@router.get("/deals")
async def list_deals(stage: str | None = None, limit: int = 200):
    return {"deals": _svc().list_deals(stage=stage, limit=limit)}


@router.get("/deals/{deal_id}")
async def get_deal(deal_id: str):
    deal = _svc().get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return {**deal, "history": _svc().deal_history(deal_id)}


@router.post("/deals")
async def create_deal(payload: DealCreate):
    lead = payload.model_dump()
    lead["id"] = lead.pop("lead_id")
    lead["metadata"] = payload.metadata or {}
    return _svc().create_deal(lead)


@router.post("/advance")
async def advance(payload: AdvanceRequest):
    try:
        deal = _svc().advance(payload.deal_id, payload.stage, note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.post("/close")
async def close(payload: CloseRequest):
    deal = _svc().advance(
        payload.deal_id,
        "closed_won" if payload.won else "closed_lost",
        triggered_by="closer_agent",
        note=payload.note,
    )
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.get("/forecast")
async def forecast():
    return _svc().forecast()


@router.post("/qualify")
async def qualify(payload: QualifyRequest):
    sdr = SDRAgent("sdr_agent", None, pipeline=_svc())
    return await sdr.run({"action": "qualify", "leads": payload.leads})


@router.post("/objection")
async def objection(text: str):
    closer = CloserAgent("closer_agent", None, pipeline=_svc())
    return closer._handle_objection({"objection": text})
