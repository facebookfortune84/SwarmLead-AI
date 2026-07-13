import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from backend.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex[:8].upper())
    project_id = Column(String, index=True)
    department = Column(String)
    title = Column(String)
    instruction = Column(Text)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)
    # Phase 2 additions
    priority = Column(String, default="medium")  # low/medium/high/critical
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    sla_hours = Column(Integer, default=24)
    tags = Column(String, nullable=True)  # comma-separated
    parent_ticket_id = Column(String, ForeignKey("tickets.id"), nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
