import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from core.persistence.base import Base


class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex[:8].upper())
    email = Column(String, index=True)
    name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    status = Column(String, default="NEW")
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Phase 3: outreach-pipeline extensions
    website = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    intent_score = Column(Integer, nullable=True)
    needs_review = Column(Boolean, default=False)
    email_invalid = Column(Boolean, default=False)