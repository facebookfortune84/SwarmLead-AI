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
from core.services.pricing import ANNUAL_MULTIPLIER, MONTHLY_VALUE

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
            existing = self._existing_active(db, lead)
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

    def _existing_active(
        self, db: Session, lead: Dict[str, Any]
    ) -> Optional[Deal]:
        """Find the active deal for this lead — by lead_id or by email."""
        existing = (
            db.query(Deal)
            .filter(Deal.lead_id == lead["id"], Deal.active.is_(True))
            .first()
        )
        if existing:
            return existing
        email = lead.get("email")
        if email:
            return (
                db.query(Deal)
                .filter(Deal.email == email, Deal.active.is_(True))
                .order_by(Deal.created_at.desc())
                .first()
            )
        return None

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
        a rejection summary so the SDR can explain why.

        Scoring reflects true buyer intent, not just traffic: intent score
        (best proxy available on discovered leads) is combined with fit
        signals (budget/authority/need/timeline) and a business-domain
        boost that rewards real companies over free-inbox prospects.

        A qualified deal is immediately handed to the demand team: the
        qualified -> discovery transition (``triggered_by=sdr_agent``) is
        recorded so the funnel always shows the handoff.
        """
        intent = lead.get("intent_score") or 0
        signals = {
            "budget": self._signal(lead, "budget"),
            "authority": self._signal(lead, "authority"),
            "need": self._signal(lead, "need"),
            "timeline": self._signal(lead, "timeline"),
        }
        business_domain = lead.get("metadata", {}).get("business_domain", True)
        reasons = []
        reasons.append(f"intent={intent}")
        for k in ("budget", "authority", "need", "timeline"):
            reasons.append(f"{k}:{'y' if signals[k] else 'n'}")
        score = intent * 0.6 + (sum(signals.values()) / 4) * 40
        if business_domain:
            score += 2  # business-domain companies close at real rates
            reasons.append("business_domain:+2")
        else:
            reasons.append("business_domain:no")
        qualified = score >= QUALIFY_INTENT_THRESHOLD

        if not qualified:
            return {
                "qualified": False,
                "reason": f"intent {intent} below threshold {QUALIFY_INTENT_THRESHOLD} ({' '.join(reasons)})",
                "score": round(score, 1),
                "reasons": reasons,
            }

        deal = self.create_deal(lead, owner_agent=owner_agent)
        # SDR -> demand-team handoff: enter discovery immediately.
        if deal.get("stage") == "qualified":
            deal = self.advance(
                deal["id"], "discovery", triggered_by="sdr_agent",
                note="SDR qualification complete — handed to demand team",
            )
        return {
            "qualified": True,
            "score": round(score, 1),
            "reasons": reasons,
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
        """Move a deal forward through the funnel (must be in STAGES).

        Funnel integrity: moves are forward-only along the ordered pipeline.
        Terminal stages are locked — a closed deal never reopens. Jumping
        ahead (e.g. discovery -> quoted) is allowed; moving backwards raises
        ValueError so the pipeline stays an honest record.
        """
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
            if deal.stage in TERMINAL:
                raise ValueError(f"Deal {deal_id} is terminal ({deal.stage}); it cannot move")
            if old_stage in STAGES and to_stage not in TERMINAL:
                if STAGES.index(to_stage) < STAGES.index(old_stage):
                    raise ValueError(
                        f"Cannot move deal {deal_id} backwards {old_stage} -> {to_stage}"
                    )

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
            "sales_velocity_days": self.velocity_stats().get("median_close_days"),
            "as_of": datetime.utcnow().isoformat(),
        }

    def velocity_stats(self) -> Dict[str, Any]:
        """Time-to-first-sale: how fast deals go from creation to closed_won.

        Median close days is the headline number (robust to outliers); the
        oldest open deal days shows where the funnel is stalling.
        """
        db = self._session()
        try:
            won = (
                db.query(Deal)
                .filter(Deal.stage == "closed_won")
                .all()
            )
            close_days = []
            for d in won:
                if d.created_at and d.closed_at:
                    close_days.append(
                        (d.closed_at - d.created_at).total_seconds() / 86400
                    )
            median = 0.0
            if close_days:
                close_days.sort()
                n = len(close_days)
                median = (
                    close_days[n // 2]
                    if n % 2
                    else (close_days[n // 2 - 1] + close_days[n // 2]) / 2
                )
            open_rows = (
                db.query(Deal)
                .filter(Deal.active.is_(True))
                .order_by(Deal.created_at.asc())
                .first()
            )
            oldest_days = 0.0
            if open_rows and open_rows.created_at:
                oldest_days = (
                    datetime.utcnow() - open_rows.created_at
                ).total_seconds() / 86400
            return {
                "median_close_days": round(median, 1),
                "wins_count": len(close_days),
                "oldest_open_deal_days": round(oldest_days, 1),
            }
        except Exception:
            db.rollback()
            raise
        finally:
            if self._db is None:
                db.close()

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
