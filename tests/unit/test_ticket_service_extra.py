"""Unit tests for TicketService — CRUD, lifecycle transitions, SLA, and metrics.

Uses a throwaway SQLite engine (tmp_path) with Base.metadata.create_all and
monkeypatches core.persistence.session.SessionLocal so the real DB is untouched.
"""

from datetime import datetime, timedelta

import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from core.models.ticket import Ticket
from core.models.ticket_history import TicketHistory
from core.persistence.base import Base
from core.services.ticket_service import (
    ESCALATION_MAP,
    VALID_PRIORITIES,
    VALID_STATUSES,
    TicketService,
)

import core.models  # noqa: F401  (register all models on Base.metadata)


@pytest.fixture
def db_session(monkeypatch, tmp_path):
    db_path = tmp_path / "tickets.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    db = test_session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def service(db_session):
    return TicketService(db_session)


# --------------------------------------------------------------------- #
# Construction & constants                                              #
# --------------------------------------------------------------------- #


def test_service_constructs(db_session):
    svc = TicketService(db_session)
    assert svc.db is db_session


def test_module_constants():
    assert VALID_PRIORITIES == {"low", "medium", "high", "critical"}
    assert VALID_STATUSES == {"OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"}
    assert ESCALATION_MAP == {
        "low": "medium",
        "medium": "high",
        "high": "critical",
        "critical": "critical",
    }


# --------------------------------------------------------------------- #
# create_ticket                                                          #
# --------------------------------------------------------------------- #


def test_create_ticket_defaults(service):
    ticket = service.create_ticket(title="My Ticket", instruction="do the thing")
    assert ticket.id
    assert ticket.title == "My Ticket"
    assert ticket.instruction == "do the thing"
    assert ticket.priority == "medium"
    assert ticket.status == "OPEN"
    assert ticket.sla_hours == 24
    assert ticket.created_at is not None


def test_create_ticket_invalid_priority_falls_back_to_medium(service):
    ticket = service.create_ticket(title="t", instruction="i", priority="p0")
    assert ticket.priority == "medium"


def test_create_ticket_with_all_fields(service):
    due = datetime(2025, 12, 31, 23, 59, 59)
    ticket = service.create_ticket(
        title="Full",
        instruction="instr",
        project_id="proj-1",
        department="engineering",
        priority="high",
        assignee_id="assignee-1",
        reporter_id="reporter-1",
        due_date=due,
        sla_hours=48,
        tags="a,b,c",
        parent_ticket_id=None,
        estimated_hours=3.5,
    )
    assert ticket.project_id == "proj-1"
    assert ticket.department == "engineering"
    assert ticket.priority == "high"
    assert ticket.assignee_id == "assignee-1"
    assert ticket.reporter_id == "reporter-1"
    assert ticket.due_date == due
    assert ticket.sla_hours == 48
    assert ticket.tags == "a,b,c"
    assert ticket.estimated_hours == 3.5


def test_create_ticket_records_history(service, db_session):
    ticket = service.create_ticket(title="My Title", instruction="i", reporter_id="reporter-1")
    entry = (
        db_session.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket.id)
        .order_by(TicketHistory.created_at.asc())
        .first()
    )
    assert entry is not None
    assert entry.action == "created"
    assert entry.user_id == "reporter-1"
    assert entry.new_value == "My Title"


# --------------------------------------------------------------------- #
# get_ticket                                                             #
# --------------------------------------------------------------------- #


def test_get_ticket_found(service):
    ticket = service.create_ticket(title="t", instruction="i")
    assert service.get_ticket(ticket.id).id == ticket.id


def test_get_ticket_not_found(service):
    assert service.get_ticket("NOPE") is None


# --------------------------------------------------------------------- #
# list_tickets                                                           #
# --------------------------------------------------------------------- #


def test_list_tickets_empty(service):
    assert service.list_tickets() == []


def test_list_tickets_all_ordered_newest_first(service):
    t1 = service.create_ticket(title="first", instruction="i")
    t2 = service.create_ticket(title="second", instruction="i")
    t3 = service.create_ticket(title="third", instruction="i")
    result = service.list_tickets()
    assert [t.id for t in result] == [t3.id, t2.id, t1.id]


def test_list_tickets_filter_status(service):
    open_t = service.create_ticket(title="open", instruction="i")
    closed_t = service.create_ticket(title="closed", instruction="i")
    service.close(closed_t.id, user_id="u")
    result = service.list_tickets(status="CLOSED")
    assert [t.id for t in result] == [closed_t.id]
    result = service.list_tickets(status="OPEN")
    assert [t.id for t in result] == [open_t.id]


def test_list_tickets_filter_priority_and_assignee(service):
    hi = service.create_ticket(title="hi", instruction="i", priority="high", assignee_id="a1")
    lo = service.create_ticket(title="lo", instruction="i", priority="low", assignee_id="a2")
    result = service.list_tickets(priority="high", assignee_id="a1")
    assert [t.id for t in result] == [hi.id]
    assert service.list_tickets(priority="low", assignee_id="a1") == []


def test_list_tickets_filter_date_range(service, db_session):
    t1 = service.create_ticket(title="t1", instruction="i")
    t2 = service.create_ticket(title="t2", instruction="i")
    t1.created_at = datetime(2025, 1, 1, 12, 0, 0)
    t2.created_at = datetime(2025, 3, 1, 12, 0, 0)
    db_session.commit()
    result = service.list_tickets(
        date_from=datetime(2025, 1, 15),
        date_to=datetime(2025, 3, 15),
    )
    assert [t.id for t in result] == [t2.id]


def test_list_tickets_skip_limit(service):
    tickets = [service.create_ticket(title=f"t{i}", instruction="i") for i in range(3)]
    assert len(service.list_tickets(limit=2)) == 2
    skipped = service.list_tickets(skip=1, limit=1)
    assert [t.id for t in skipped] == [tickets[1].id]


# --------------------------------------------------------------------- #
# update_ticket                                                          #
# --------------------------------------------------------------------- #


def test_update_ticket_updates_field_and_records_history(service, db_session):
    ticket = service.create_ticket(title="old", instruction="i")
    updated = service.update_ticket(ticket.id, user_id="u", title="new")
    assert updated.title == "new"
    entry = (
        db_session.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket.id)
        .filter(TicketHistory.action == "title_changed")
        .first()
    )
    assert entry.old_value == "old"
    assert entry.new_value == "new"
    assert entry.user_id == "u"


def test_update_ticket_multiple_fields(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i")
    updated = service.update_ticket(
        ticket.id, user_id="u", title="new", department="eng", priority="high"
    )
    assert updated.department == "eng"
    assert updated.priority == "high"
    actions = {
        r[0]
        for r in db_session.query(TicketHistory.action)
        .filter(TicketHistory.ticket_id == ticket.id)
        .all()
    }
    assert {"title_changed", "department_changed", "priority_changed"} <= actions


def test_update_ticket_unknown_id_returns_none(service):
    assert service.update_ticket("NOPE", user_id="u", title="x") is None


def test_update_ticket_skips_none_and_unknown_fields(service, db_session):
    ticket = service.create_ticket(title="orig", instruction="i")
    updated = service.update_ticket(ticket.id, user_id="u", nonexistent_field="x", title=None)
    assert updated.title == "orig"
    count = db_session.query(TicketHistory).filter(TicketHistory.ticket_id == ticket.id).count()
    assert count == 1  # only the "created" entry


# --------------------------------------------------------------------- #
# delete_ticket                                                          #
# --------------------------------------------------------------------- #


def test_delete_ticket_success(service):
    ticket = service.create_ticket(title="t", instruction="i")
    assert service.delete_ticket(ticket.id) is True
    assert service.get_ticket(ticket.id) is None


def test_delete_ticket_not_found(service):
    assert service.delete_ticket("NOPE") is False


# --------------------------------------------------------------------- #
# assign / escalate / resolve / close                                    #
# --------------------------------------------------------------------- #


def test_assign_updates_assignee(service):
    ticket = service.create_ticket(title="t", instruction="i")
    result = service.assign(ticket.id, assignee_id="a1", user_id="u")
    assert result.assignee_id == "a1"


def test_assign_unknown_ticket(service):
    assert service.assign("NOPE", assignee_id="a1", user_id="u") is None


@pytest.mark.parametrize(
    "priority,expected",
    [
        ("low", "medium"),
        ("medium", "high"),
        ("high", "critical"),
        ("critical", "critical"),
    ],
)
def test_escalate_upgrades_priority(service, priority, expected):
    ticket = service.create_ticket(title="t", instruction="i", priority=priority)
    result = service.escalate(ticket.id, user_id="u")
    assert result.priority == expected


def test_escalate_none_priority_uses_medium(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i")
    ticket.priority = None
    db_session.commit()
    result = service.escalate(ticket.id, user_id="u")
    assert result.priority == "high"


def test_escalate_unknown_priority_uses_high(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i")
    ticket.priority = "urgent"
    db_session.commit()
    result = service.escalate(ticket.id, user_id="u")
    assert result.priority == "high"


def test_escalate_unknown_ticket(service):
    assert service.escalate("NOPE", user_id="u") is None


def test_resolve_sets_status_and_resolved_at(service):
    ticket = service.create_ticket(title="t", instruction="i")
    resolved = service.resolve(ticket.id, user_id="u")
    assert resolved.status == "RESOLVED"
    assert resolved.resolved_at is not None


def test_resolve_with_actual_hours(service):
    ticket = service.create_ticket(title="t", instruction="i")
    resolved = service.resolve(ticket.id, user_id="u", actual_hours=5.5)
    assert resolved.actual_hours == 5.5
    assert resolved.status == "RESOLVED"


def test_resolve_unknown_ticket(service):
    assert service.resolve("NOPE", user_id="u") is None


def test_resolve_swallows_event_bus_errors(service, monkeypatch):
    from core.events.event_bus import event_bus

    def boom(*args, **kwargs):
        raise RuntimeError("bus down")

    monkeypatch.setattr(event_bus, "publish", boom)
    ticket = service.create_ticket(title="t", instruction="i")
    resolved = service.resolve(ticket.id, user_id="u")
    assert resolved.status == "RESOLVED"


def test_close_sets_status(service):
    ticket = service.create_ticket(title="t", instruction="i")
    closed = service.close(ticket.id, user_id="u")
    assert closed.status == "CLOSED"


def test_close_unknown_ticket(service):
    assert service.close("NOPE", user_id="u") is None


# --------------------------------------------------------------------- #
# comments                                                                #
# --------------------------------------------------------------------- #


def test_add_comment(service):
    ticket = service.create_ticket(title="t", instruction="i")
    comment = service.add_comment(ticket.id, user_id="u", content="hello")
    assert comment.ticket_id == ticket.id
    assert comment.user_id == "u"
    assert comment.content == "hello"
    assert comment.created_at is not None


def test_add_comment_long_content_truncates_history(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i")
    service.add_comment(ticket.id, user_id="u", content="x" * 500)
    entry = (
        db_session.query(TicketHistory)
        .filter(TicketHistory.action == "comment_added")
        .first()
    )
    assert entry.new_value == "x" * 200


def test_get_comments_empty(service):
    ticket = service.create_ticket(title="t", instruction="i")
    assert service.get_comments(ticket.id) == []


def test_get_comments_chronological(service):
    ticket = service.create_ticket(title="t", instruction="i")
    c1 = service.add_comment(ticket.id, user_id="u1", content="first")
    c2 = service.add_comment(ticket.id, user_id="u2", content="second")
    result = service.get_comments(ticket.id)
    assert [c.id for c in result] == [c1.id, c2.id]


# --------------------------------------------------------------------- #
# SLA                                                                    #
# --------------------------------------------------------------------- #


def test_check_sla_no_breaches(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i")
    ticket.created_at = datetime.utcnow()
    db_session.commit()
    assert service.check_sla_breaches() == []


def test_check_sla_breached_escalates(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i", priority="low")
    ticket.created_at = datetime.utcnow() - timedelta(hours=48)
    db_session.commit()
    breached = service.check_sla_breaches()
    assert len(breached) == 1
    assert breached[0].id == ticket.id
    assert breached[0].priority == "medium"  # escalated low -> medium
    entry = (
        db_session.query(TicketHistory)
        .filter(TicketHistory.action == "sla_breached")
        .first()
    )
    assert entry is not None
    assert entry.new_value == "high"


def test_check_sla_breached_critical_stays_critical(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i", priority="critical")
    ticket.created_at = datetime.utcnow() - timedelta(hours=48)
    db_session.commit()
    breached = service.check_sla_breaches()
    assert len(breached) == 1
    assert breached[0].priority == "critical"


def test_check_sla_breach_with_sla_hours_none_uses_default(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i", sla_hours=None)
    ticket.created_at = datetime.utcnow() - timedelta(hours=30)
    db_session.commit()
    breached = service.check_sla_breaches()
    assert len(breached) == 1  # None -> 24h default


def test_check_sla_ignores_closed_and_resolved(service, db_session):
    closed = service.create_ticket(title="closed", instruction="i")
    resolved = service.create_ticket(title="resolved", instruction="i")
    closed.created_at = resolved.created_at = datetime.utcnow() - timedelta(hours=100)
    db_session.commit()
    service.close(closed.id, user_id="u")
    service.resolve(resolved.id, user_id="u")
    assert service.check_sla_breaches() == []


def test_check_sla_notification_error_swallowed(service, db_session, monkeypatch):
    class BoomNotificationService:
        def __init__(self, db):
            self.db = db

        def notify_task_failed(self, **kwargs):
            raise RuntimeError("notify down")

    monkeypatch.setattr(
        "core.services.notification_service.NotificationService",
        BoomNotificationService,
    )
    ticket = service.create_ticket(title="t", instruction="i", priority="low")
    ticket.created_at = datetime.utcnow() - timedelta(hours=48)
    db_session.commit()
    breached = service.check_sla_breaches()
    assert len(breached) == 1
    assert breached[0].priority == "medium"


# --------------------------------------------------------------------- #
# Metrics                                                                #
# --------------------------------------------------------------------- #


def test_get_metrics_empty(service):
    assert service.get_metrics() == {"total": 0, "by_status": {}, "by_priority": {}}


def test_get_metrics_counts_by_status_and_priority(service):
    service.create_ticket(title="t1", instruction="i", priority="high")
    service.create_ticket(title="t2", instruction="i", priority="low")
    metrics = service.get_metrics()
    assert metrics["total"] == 2
    assert metrics["by_status"] == {"OPEN": 2}
    assert metrics["by_priority"] == {"high": 1, "low": 1}


def test_get_metrics_none_priority_falls_back_to_medium(service, db_session):
    ticket = service.create_ticket(title="t", instruction="i")
    ticket.priority = None
    db_session.commit()
    metrics = service.get_metrics()
    assert metrics["total"] == 1
    assert metrics["by_priority"] == {"medium": 1}
    assert metrics["by_status"] == {"OPEN": 1}
