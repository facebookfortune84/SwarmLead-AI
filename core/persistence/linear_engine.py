"""
Lightweight persistence facade used by migrated routers.

Provides compatibility for:

    get_swarm_db()

while using migrated v3 models.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from core.models.lead import Lead
from core.models.ticket import Ticket
from core.models.usage import UsageEvent
from core.persistence.session import SessionLocal

logger = logging.getLogger("LinearEngine")


class LinearEngine:
    def __init__(
        self,
        db: Session | None = None,
    ):
        self.db = db or SessionLocal()

    # =====================================================
    # LEADS
    # =====================================================

    def create_lead(
        self,
        email: str,
        name: str | None = None,
        company: str | None = None,
        metadata: dict | None = None,
    ) -> str:

        lead = Lead(
            email=email,
            name=name,
            company=company,
            metadata_json=str(metadata) if metadata else None,
        )

        self.db.add(lead)

        self.db.commit()

        self.db.refresh(lead)

        return str(lead.id)

    def list_leads(
        self,
        limit: int = 100,
    ):

        rows = self.db.query(Lead).order_by(Lead.created_at.desc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "email": r.email,
                "name": r.name,
                "company": r.company,
                "status": r.status,
                "metadata": r.metadata_json,
                "created_at": (r.created_at.isoformat() if r.created_at else None),
            }
            for r in rows
        ]

    def get_lead(
        self,
        lead_id: str,
    ):

        row = self.db.query(Lead).filter(Lead.id == lead_id).first()

        if not row:
            return None

        return {
            "id": row.id,
            "email": row.email,
            "name": row.name,
            "company": row.company,
            "status": row.status,
            "metadata": row.metadata_json,
            "created_at": (row.created_at.isoformat() if row.created_at else None),
        }

    # =====================================================
    # TICKETS
    # =====================================================

    def create_ticket(
        self,
        lead_id: str,
        department: str,
        title: str,
        instruction: str,
    ) -> str:

        ticket = Ticket(
            project_id=lead_id,
            department=department,
            title=title,
            instruction=instruction,
            status="OPEN",
        )

        self.db.add(ticket)

        self.db.commit()

        self.db.refresh(ticket)

        logger.info(
            "Created ticket %s for lead %s",
            ticket.id,
            lead_id,
        )

        return str(ticket.id)

    def list_tickets(
        self,
        limit: int = 100,
    ):

        rows = self.db.query(Ticket).order_by(Ticket.created_at.desc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "project_id": r.project_id,
                "department": r.department,
                "title": r.title,
                "instruction": r.instruction,
                "status": r.status,
                "priority": r.priority,
                "assignee_id": r.assignee_id,
                "reporter_id": r.reporter_id,
                "due_date": (r.due_date.isoformat() if r.due_date else None),
                "created_at": (r.created_at.isoformat() if r.created_at else None),
            }
            for r in rows
        ]

    def get_ticket(
        self,
        ticket_id: str,
    ):

        row = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not row:
            return None

        return {
            "id": row.id,
            "project_id": row.project_id,
            "department": row.department,
            "title": row.title,
            "instruction": row.instruction,
            "status": row.status,
            "priority": row.priority,
            "assignee_id": row.assignee_id,
            "reporter_id": row.reporter_id,
            "due_date": (row.due_date.isoformat() if row.due_date else None),
            "created_at": (row.created_at.isoformat() if row.created_at else None),
        }

    # =====================================================
    # USAGE
    # =====================================================

    def record_usage(
        self,
        project_id: str | None,
        event_type: str,
        amount: str | None = None,
        metadata: dict | None = None,
    ) -> str:

        event = UsageEvent(
            project_id=project_id,
            event_type=event_type,
            amount=str(amount) if amount else None,
            metadata_json=str(metadata) if metadata else None,
        )

        self.db.add(event)

        self.db.commit()

        self.db.refresh(event)

        return str(event.id)

    def list_usage(
        self,
        project_id: str | None = None,
        limit: int = 100,
    ):

        query = self.db.query(UsageEvent).order_by(UsageEvent.created_at.desc())

        if project_id:
            query = query.filter(UsageEvent.project_id == project_id)

        rows = query.limit(limit).all()

        return [
            {
                "id": r.id,
                "project_id": r.project_id,
                "event_type": r.event_type,
                "amount": r.amount,
                "metadata": r.metadata_json,
                "created_at": (r.created_at.isoformat() if r.created_at else None),
            }
            for r in rows
        ]

    def close(self):

        self.db.close()


_swarm_db = None


def get_swarm_db():

    global _swarm_db

    if _swarm_db is None:
        _swarm_db = LinearEngine()

    return _swarm_db
