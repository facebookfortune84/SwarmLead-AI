"""
Integration Test

Ticket service integration tests.
"""

from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.ticket_service import (
    TicketService,
)


def test_ticket_service_constructs():

    init_db()

    db = SessionLocal()

    try:
        service = TicketService(db)

        assert service is not None

    finally:
        db.close()


def test_create_ticket():

    init_db()

    db = SessionLocal()

    try:
        service = TicketService(db)

        ticket = service.create_ticket(
            title="Integration Test Ticket",
            instruction="Created during integration testing",
            priority="medium",
        )

        assert ticket is not None

    finally:
        db.close()
