import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from backend.db.base import Base


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    company_id = Column(String, ForeignKey("company_tenants.id"), nullable=True)
    # pending/running/paused/completed/failed
    status = Column(String, default="pending")
    current_step = Column(Integer, default=0)
    steps_json = Column(Text, nullable=False)  # JSON array of step definitions
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
