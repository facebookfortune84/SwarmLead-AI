import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from backend.db.base import Base


class MessageThread(Base):
    __tablename__ = "message_threads"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = Column(String, nullable=False)
    participants_json = Column(Text, nullable=False)  # JSON array of user_ids
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
