import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from backend.db.base import Base


class Deployment(Base):
    __tablename__ = "deployments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("company_tenants.id"), index=True)
    status = Column(String, default="queued")  # queued, in_progress, success, failed, rolled_back
    strategy = Column(String)  # blue-green, canary, rolling
    version = Column(String)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
