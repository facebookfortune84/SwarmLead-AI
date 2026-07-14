"""
Integration Test

Verify data persists across sessions.
"""

from core.persistence.linear_engine import (
    get_swarm_db,
)
from core.persistence.session import (
    SessionLocal,
    init_db,
)


def test_lead_persists_between_sessions():

    init_db()

    swarm_db = get_swarm_db()

    lead_id = swarm_db.create_lead(
        email="persist@example.com",
        name="Persistence Test",
        company="Persistence Co",
    )

    db = SessionLocal()

    try:
        from core.models.lead import Lead

        lead = db.query(Lead).filter(Lead.id == lead_id).first()

        assert lead is not None

        assert lead.email == "persist@example.com"

    finally:
        db.close()
