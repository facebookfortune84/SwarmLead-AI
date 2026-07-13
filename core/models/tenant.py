import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from core.persistence.base import Base


class CompanyTenant(Base):
    __tablename__ = "company_tenants"
    id = Column(String, primary_key=True)
    slug = Column(String, unique=True, index=True)
    name = Column(String)
    subdomain = Column(String, unique=True, index=True)
    status = Column(String, default="pending")  # pending, provisioning, running, failed, stopped
    vm_id = Column(String, nullable=True)
    container_id = Column(String, nullable=True)
    box_url = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)