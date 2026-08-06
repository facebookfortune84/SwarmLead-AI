"""
Sales pipeline service — the AI sales team's operating core.

Qualifies discovered leads into Deal records and moves them through a
classic B2B funnel:

    qualified -> discovery -> engaged -> quoted -> closed_won / closed_lost

The service is database-backed (``deals`` + ``deal_stage_events`` tables)
so the pipeline survives restarts. Qualification uses the BANT-lite
signals available on the lead record (intent score, company size, need
signals, timeline) and every stage transition is audited.

The growth loop calls :meth:`sync_from_leads` each cycle so newly
discovered, high-intent leads automatically enter the pipeline, and the
SDR/Closer agents operate on the resulting deals.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from core.models.deal import Deal, DealStageEvent

logger = logging.getLogger("SalesPipeline")

# Ordered pipeline. closed_won / closed_lost are terminal.
STAGES = [
    "qualified",
    "discovery",
    "engaged",
    "quoted",
    "closed_won",
    "closed_lost",
]
TERMINAL = {"closed_won", "closed_lost"}

# Minimum intent score for a discovered lead to enter the pipeline.
QUALIFY_INTENT_THRESHOLD = 55

# Stage -> probability of closing (used for pipeline value forecast).
STAGE_PROBABILITY = {
    "qualified": 0.15,
    "discovery": 0.30,
    "engaged": 0.50,
    "quoted": 0.70,
    "closed_won": 1.0,
    "closed_lost": 0.0,
}

# Annual plan multiplier vs monthly (2 months free).
ANNUAL_MULTIPLIER = 10  # 10x monthly == 2 months free on an annual contract

MONTHLY_VALUE = {
    "starter": 2900,
    "growth": 9900,
    "enterprise": 29900,
}


class SalesPipeline:
    """Deal creation, qualification, stage transitions and forecasting."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self._db = db

    # ------------------------------------------------------------- helpers
    def _session(self) -> Session:
        if self._db is not None:
            return self._db
        from core.persistence.session import SessionLocal

        return SessionLocal()

    @staticmethod
    def _serialize(deal: Deal) -> Dict[str, Any]:
        return {
            "id": deal.id,
            "lead_id": deal.lead_id,
            "email": deal.email,
            "company": deal.company,
            "stage": deal.stage,
            "amount_cents": deal.amount_cents,
            "probability": deal.probability,
            "budget": deal.budget,
            "authority": deal.authority,
            "need": deal.need,
            "timeline": deal.timeline,
            "intent_score": deal.intent_score,
            "notes": deal.notes,
            "owner_agent": deal.owner_agent,
            "active": deal.active,
            "created_at": deal.created_at.isoformat() if deal.created_at else None,
            "updated_at": deal.updated_at.isoformat() if deal.updated_at else None,
            "closed_at": deal.closed_at.isoformat() if deal.closed_at else None,
            "weighted_value_cents": int(
                (deal.amount_cents or 0) * (deal.probability or 0)
            ),
        }

    # ------------------------------------------------------------ lifecycle
    def create_deal(
        self,
        lead: Dict[str, Any],
        owner_agent: str = "sdr_agent",
    ) -> Dict[str, Any]:
        """Create a deal from a lead dict (must contain id + email)."""
        db = self._session()
        try:
            existing = (
                db.query(Deal)
                .filter(Deal.lead_id == lead["id"], Deal.active.is_(True))
                .first()
            )
            if existing:
                return self._serialize(existing)

            deal = Deal(
                lead_id=lead["id"],
                email=lead.get("email"),
                company=lead.get("company"),
                stage="qualified",
                intent_score=lead.get("intent_score"),
                amount_cents=self._suggest_amount(lead),
                probability=STAGE_PROBABILITY["qualified"],
                owner_agent=owner_agent,
                budget=self._signal(lead, "budget"),
                authority=self._signal(lead, "authority"),
                need=self._signal(lead, "need"),
                timeline=self._signal(lead, "timeline"),
            )
            db.add(deal)
            db.flush()
            db.add(
                DealStageEvent(
                    deal_id=deal.id,
                    from_stage=None,
                    to_stage="qualified",
                    triggered_by=owner_agent,
                )
            )
            db.commit()
            logger.info("Deal %s created for lead %s", deal.id, lead["id"])
            return self._serialize(deal)
        except Exception:
            db.rollback()
            raise
        finally:
            if self._db is None:
                db.close()

    @staticmethod
    def _signal(lead: Dict[str, Any], key: str) -> bool:
        meta = lead.get("metadata", {}) or {}
        value = meta.get(key)
        if value is None:
            return False
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "y"}
        return bool(value)

    @staticmethod
    def _suggest_amount(lead: Dict[str, Any]) -> int:
        """Map a lead to a sensible starting deal value (monthly MRR)."""
        size = lead.get("company_size") or 0
        if size >= 20:
            return MONTHLY_VALUE["enterprise"]
        if size >= 5:
            return MONTHLY_VALUE["growth"]
        return MONTHLY_VALUE["starter"]

    # ---------------------------------------------------------- qualification
    def qualify(
        self,
        lead: Dict[str, Any],
        owner_agent: str = "sdr_agent",
    ) -> Dict[str, Any]:
        """BANT-lite qualification. Returns the deal when qualified, else
        a rejection summary so the SDR can explain why."""
        intent = lead.get("intent_score") or 0
        signals = {
            "budget": self._signal(lead, "budget"),
            "authority": self._signal(lead, "authority"),
            "need": self._signal(lead, "need"),
            "timeline": self._signal(lead, "timeline"),
        }
        score = intent * 0.6 + (sum(signals.values()) / 4) * 40
        qualified = score >= QUALIFY_INTENT_THRESHOLD

        if not qualified:
            return {
                "qualified": False,
                "reason": f"intent {intent} below threshold {QUALIFY_INTENT_THRESHOLD}",
                "score": round(score, 1),
            }

        deal = self.create_deal(lead, owner_agent=owner_agent)
        return {
            "qualified": True,
            "score": round(score, 1),
            "deal": deal,
        }

    # --------------------------------------------------------- stage moves
    def advance(
        self,
        deal_id: str,
        to_stage: str,
        triggered_by: str = "sales_pipeline",
        note: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Move a deal to the given stage (must be in STAGES)."""
        if to_stage not in STAGES:
            raise ValueError(f"Unknown stage: {to_stage}")
        db = self._session()
        try:
            deal = db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                return None
            if deal.stage == to_stage:
                return self._serialize(deal)

            old_stage = deal.stage
            deal.stage = to_stage
            deal.probability = STAGE_PROBABILITY[to_stage]
            if to_stage in TERMINAL:
                deal.active = False
                deal.closed_at = datetime.utcnow()
            if note:
                deal.notes = ((deal.notes or "") + "\n" + note).strip()
            db.add(
                DealStageEvent(
                    deal_id=deal.id,
                    from_stage=old_stage,
                    to_stage=to_stage,
                    triggered_by=triggered_by,
                )
            )
            db.commit()
            logger.info("Deal %s moved %s -> %s", deal_id, old_stage, to_stage)
            return self._serialize(deal)
        except Exception:
            db.rollback()
            raise
        finally:
            if self._db is None:
                db.close()

    def close_won(
        self,
        deal_id: str,
        triggered_by: str = "closer_agent",
        note: str = "",
    ) -> Optional[Dict[str, Any]]:
        return self.advance(deal_id, "closed_won", triggered_by, note)

    def close_lost(
        self,
        deal_id: str,
        triggered_by: str = "closer_agent",
        note: str = "",
    ) -> Optional[Dict[str, Any]]:
        return self.advance(deal_id, "closed_lost", triggered_by, note)

    # ------------------------------------------------------------- queries
    def list_deals(self, stage: Optional[str] = None, limit: int = 200) -> List[Dict]:
        db = self._session()
        try:
            q = db.query(Deal).order_by(Deal.updated_at.desc())
            if stage:
                q = q.filter(Deal.stage == stage)
            return [self._serialize(d) for d in q.limit(limit).all()]
        finally:
            if self._db is None:
                db.close()

    def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        db = self._session()
        try:
            deal = db.query(Deal).filter(Deal.id == deal_id).first()
            return self._serialize(deal) if deal else None
        finally:
            if self._db is None:
                db.close()

    def deal_history(self, deal_id: str) -> List[Dict[str, Any]]:
        db = self._session()
        try:
            events = (
                db.query(DealStageEvent)
                .filter(DealStageEvent.deal_id == deal_id)
                .order_by(DealStageEvent.occurred_at)
                .all()
            )
            return [
                {
                    "from_stage": e.from_stage,
                    "to_stage": e.to_stage,
                    "triggered_by": e.triggered_by,
                    "occurred_at": e.occurred_at.isoformat(),
                }
                for e in events
            ]
        finally:
            if self._db is None:
                db.close()

    # -------------------------------------------------------------- pipeline
    def pipeline_snapshot(self) -> Dict[str, Any]:
        """Stage-by-stage counts + weighted pipeline value for the sales board."""
        deals = self.list_deals(limit=10000)
        by_stage: Dict[str, List[Dict]] = {s: [] for s in STAGES}
        for deal in deals:
            by_stage.setdefault(deal["stage"], []).append(deal)

        stages = []
        total_weighted = 0
        for stage in STAGES:
            rows = by_stage.get(stage, [])
            weighted = sum(d["weighted_value_cents"] for d in rows)
            total_weighted += weighted
            stages.append(
                {
                    "stage": stage,
                    "count": len(rows),
                    "weighted_value_cents": weighted,
                    "probability": STAGE_PROBABILITY[stage],
                }
            )

        return {
            "stages": stages,
            "total_deals": len(deals),
            "open_deals": sum(1 for d in deals if d["active"]),
            "weighted_pipeline_cents": total_weighted,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------- revenue impact
    def forecast(self, annual_multiplier: int = ANNUAL_MULTIPLIER) -> Dict[str, Any]:
        """Projected revenue from open deals + closed-won annualized value."""
        snapshot = self.pipeline_snapshot()
        open_weighted = snapshot["weighted_pipeline_cents"]

        closed = self.list_deals(stage="closed_won", limit=10000)
        won_mrr_cents = sum(d["amount_cents"] for d in closed)
        won_annual_cents = won_mrr_cents * 12

        return {
            "open_weighted_mrr_cents": open_weighted,
            "open_weighted_annual_cents": open_weighted * 12,
            "closed_won_mrr_cents": won_mrr_cents,
            "closed_won_annual_cents": won_annual_cents,
            "closed_won_count": len(closed),
            "annual_contract_cents": int(
                sum(d["amount_cents"] for d in closed) * annual_multiplier
            ),
            "as_of": datetime.utcnow().isoformat(),
        }

    # -------------------------------------------------------- growth sync
    def sync_from_leads(
        self,
        leads: List[Dict[str, Any]],
        owner_agent: str = "sdr_agent",
    ) -> Dict[str, Any]:
        """Qualify a batch of discovered leads into deals (idempotent)."""
        created = 0
        rejected = 0
        for lead in leads:
            result = self.qualify(lead, owner_agent=owner_agent)
            if result.get("qualified"):
                created += 1
            else:
                rejected += 1
        return {"deals_created": created, "leads_rejected": rejected}


sales_pipeline = SalesPipeline()
