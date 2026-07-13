"""
Migration Validation

Verify migrated services can be constructed.

This catches:

- constructor failures
- hidden import failures
- persistence issues
"""

from core.persistence.session import SessionLocal
from core.services.notification_service import (
    NotificationService,
)
from core.services.tenant_service import (
    TenantService,
)
from core.services.ticket_service import (
    TicketService,
)
from core.services.workflow_service import (
    WorkflowService,
)


def test_notification_service_constructs():

    db = SessionLocal()

    try:
        service = NotificationService(db)

        assert service is not None

    finally:
        db.close()


def test_ticket_service_constructs():

    db = SessionLocal()

    try:
        service = TicketService(db)

        assert service is not None

    finally:
        db.close()


def test_workflow_service_constructs():

    db = SessionLocal()

    try:
        service = WorkflowService(db)

        assert service is not None

    finally:
        db.close()


def test_tenant_service_constructs():

    db = SessionLocal()

    try:
        service = TenantService(db)

        assert service is not None

    finally:
        db.close()
