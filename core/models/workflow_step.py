import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from core.persistence.base import Base


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, ForeignKey("workflows.id"), index=True, nullable=False)
    step_name = Column(String, nullable=False)
    # ticket/notification/approval/condition
    step_type = Column(String, nullable=False)
    # pending/running/completed/failed/skipped
    status = Column(String, default="pending")
    input_json = Column(Text, nullable=True)
    output_json = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)