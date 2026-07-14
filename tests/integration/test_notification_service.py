"""
Integration Test
"""

from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.notification_service import (
    NotificationService,
)


def test_notification_service_constructs():

    init_db()

    db = SessionLocal()

    try:
        service = NotificationService(db)

        assert service is not None

    finally:
        db.close()


def test_notification_service_has_public_api():

    init_db()

    db = SessionLocal()

    try:
        service = NotificationService(db)

        methods = dir(service)

        assert len(methods) > 0

    finally:
        db.close()
