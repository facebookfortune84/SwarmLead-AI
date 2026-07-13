import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from core.persistence.base import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"
    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex[:12])
    project_id = Column(String, index=True, nullable=True)
    event_type = Column(String)
    amount = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)