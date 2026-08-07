"""
SQLAlchemy model for the sales pipeline (deals + stage tracking).

A Deal wraps a qualified Lead as it moves through the sales funnel:
qualified -> contacted -> engaged -> quoted -> closed_won / closed_lost.
Each stage transition is recorded so the sales team can report on
conversion and pipeline value end to end.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)

from core.persistence.base import Base


class Deal(Base):
    """A revenue opportunity derived from a qualified lead."""

    __tablename__ = "deals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False, index=True)
    email = Column(String, index=True)
    company = Column(String, nullable=True)

    # Pipeline stage: qualified, discovery, engaged, closed_won, closed_lost
    stage = Column(String(32), nullable=False, default="qualified")

    # Deal economics
    amount_cents = Column(Integer, nullable=False, default=0)
    probability = Column(Float, nullable=False, default=0.2)

    # Qualification context (BANT-lite)
    budget = Column(Boolean, default=False)
    authority = Column(Boolean, default=False)
    need = Column(Boolean, default=False)
    timeline = Column(Boolean, default=False)
    intent_score = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Lifecycle
    owner_agent = Column(String(64), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Hot path: stage filtering in snapshot / list / win-back scans.
    __table_args__ = (
        Index("ix_deals_stage_active", "stage", "active"),
    )


class DealStageEvent(Base):
    """Audit trail of every deal stage transition."""

    __tablename__ = "deal_stage_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(String, ForeignKey("deals.id"), nullable=False, index=True)
    from_stage = Column(String(32), nullable=True)
    to_stage = Column(String(32), nullable=False)
    triggered_by = Column(String(64), nullable=False)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)