"""
Integration Test
"""

from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.ticket_service import (
    TicketService,
)


def test_ticket_creation_lifecycle():

    init_db()

    db = SessionLocal()

    try:
        service = TicketService(db)

        ticket = service.create_ticket(
            title="Lifecycle Ticket",
            instruction="Lifecycle",
            priority="medium",
        )

        assert ticket is not None

        assert ticket.id

    finally:
        db.close()
