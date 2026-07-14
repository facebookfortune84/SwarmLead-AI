"""
Integration Test
"""

from core.models.lead import Lead
from core.persistence.session import (
    SessionLocal,
    init_db,
)


def test_lead_crud():

    init_db()

    db = SessionLocal()

    try:
        lead = Lead(
            email="crud@test.com",
        )

        db.add(lead)

        db.commit()

        db.refresh(lead)

        loaded = db.query(Lead).filter(Lead.id == lead.id).first()

        assert loaded is not None

    finally:
        db.close()
