"""Unit tests for the NotificationService (core.services.notification_service)."""

import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import core.models  # noqa: F401
from core.models.user import User
from core.persistence.base import Base
from core.services.notification_service import NotificationService


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "notif.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_create_notification_persists(db):
    svc = NotificationService(db)
    notif = svc.create_notification("u1", "info", "Hi", "Hello there", {"a": 1})
    assert notif.user_id == "u1"
    assert notif.type == "info"
    assert notif.title == "Hi"
    assert "a" in notif.metadata_json
    assert notif.id is not None


def test_create_notification_without_metadata(db):
    svc = NotificationService(db)
    notif = svc.create_notification("u1", "success", "T", "M")
    assert notif.metadata_json is None


def test_notify_ticket_created_skips_without_assignee(db):
    svc = NotificationService(db)
    ticket = type("T", (), {"assignee_id": None, "id": "t1", "title": "T"})()
    svc.notify_ticket_created(ticket)  # must not raise


def test_notify_ticket_created_assignee(db):
    svc = NotificationService(db)
    ticket = type("T", (), {"assignee_id": "u1", "id": "t1", "title": "Fix bug"})()
    svc.notify_ticket_created(ticket)
    notif = db.query(
        __import__("core.models.notification", fromlist=["Notification"]).Notification
    ).first()
    assert notif.user_id == "u1"
    assert "Fix bug" in notif.message


def test_notify_ticket_resolved_skips_without_reporter(db):
    svc = NotificationService(db)
    ticket = type("T", (), {"reporter_id": None, "id": "t1", "title": "T"})()
    svc.notify_ticket_resolved(ticket)


def test_notify_ticket_resolved_reporter(db):
    svc = NotificationService(db)
    ticket = type("T", (), {"reporter_id": "u9", "id": "t1", "title": "Done"})()
    svc.notify_ticket_resolved(ticket)
    notif = svc.db.query(
        __import__("core.models.notification", fromlist=["Notification"]).Notification
    ).first()
    assert notif.user_id == "u9"
    assert notif.type == "success"


def test_notify_task_failed_no_admins(db):
    svc = NotificationService(db)
    svc.notify_task_failed("task_1", "boom")  # no admins -> no notifications


def test_notify_task_failed_with_admin(db):
    admin = User(email="admin@x.com", role="admin", is_active=True,
                 password_hash="h", full_name="Admin")
    db.add(admin)
    db.commit()
    svc = NotificationService(db)
    svc.notify_task_failed("task_9", "crash")
    notif = svc.db.query(
        __import__("core.models.notification", fromlist=["Notification"]).Notification
    ).first()
    assert notif.user_id == admin.id
    assert "task_9" in notif.message


def test_broadcast_system_event(db):
    admin = User(email="boss@x.com", role="superadmin", is_active=True,
                 password_hash="h", full_name="Boss")
    db.add(admin)
    db.commit()
    svc = NotificationService(db)
    svc.broadcast_system_event("deployment.completed", "All good")
    notif = svc.db.query(
        __import__("core.models.notification", fromlist=["Notification"]).Notification
    ).first()
    assert notif.type == "info"
    assert "deployment.completed" in notif.title


def test_get_admin_user_ids_filters_inactive(db):
    db.add(User(email="a@x.com", role="admin", is_active=True,
                password_hash="h", full_name="A"))
    db.add(User(email="b@x.com", role="admin", is_active=False,
                password_hash="h", full_name="B"))
    db.add(User(email="c@x.com", role="user", is_active=True,
                password_hash="h", full_name="C"))
    db.commit()
    svc = NotificationService(db)
    ids = svc._get_admin_user_ids()
    assert len(ids) == 1


def test_ws_push_never_raises(db):
    svc = NotificationService(db)
    notif = svc.create_notification("u1", "info", "T", "M")
    svc._ws_push("u1", notif)  # best-effort; must not raise
