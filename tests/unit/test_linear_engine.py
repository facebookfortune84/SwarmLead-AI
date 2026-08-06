"""Unit tests for the LinearEngine persistence facade (core.persistence.linear_engine)."""

import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import core.models  # noqa: F401
from core.persistence.base import Base
from core.persistence.linear_engine import LinearEngine, get_swarm_db


@pytest.fixture
def engine_db(tmp_path):
    db_path = tmp_path / "linear.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_create_and_get_lead(engine_db):
    engine = LinearEngine(db=engine_db)
    lead_id = engine.create_lead("a@b.com", name="Ann", company="ACME", metadata={"src": "x"})
    assert lead_id
    lead = engine.get_lead(lead_id)
    assert lead["email"] == "a@b.com"
    assert lead["name"] == "Ann"
    assert lead["company"] == "ACME"
    assert "src" in lead["metadata"]


def test_create_lead_minimal(engine_db):
    engine = LinearEngine(db=engine_db)
    lead_id = engine.create_lead("only@email.com")
    lead = engine.get_lead(lead_id)
    assert lead["name"] is None
    assert lead["metadata"] is None


def test_list_leads_orders_by_created_desc(engine_db):
    engine = LinearEngine(db=engine_db)
    id1 = engine.create_lead("first@b.com")
    id2 = engine.create_lead("second@b.com")
    leads = engine.list_leads()
    assert [lead["id"] for lead in leads][:2] == [id2, id1]


def test_list_leads_respects_limit(engine_db):
    engine = LinearEngine(db=engine_db)
    engine.create_lead("one@b.com")
    engine.create_lead("two@b.com")
    engine.create_lead("three@b.com")
    assert len(engine.list_leads(limit=2)) == 2


def test_get_missing_lead_returns_none(engine_db):
    engine = LinearEngine(db=engine_db)
    assert engine.get_lead("missing") is None


def test_create_and_get_ticket(engine_db):
    engine = LinearEngine(db=engine_db)
    lead_id = engine.create_lead("lead@b.com")
    ticket_id = engine.create_ticket(lead_id, "sales", "Follow up", "Call tomorrow")
    ticket = engine.get_ticket(ticket_id)
    assert ticket["project_id"] == lead_id
    assert ticket["department"] == "sales"
    assert ticket["title"] == "Follow up"
    assert ticket["status"] == "OPEN"


def test_get_missing_ticket_returns_none(engine_db):
    engine = LinearEngine(db=engine_db)
    assert engine.get_ticket("missing") is None


def test_list_tickets(engine_db):
    engine = LinearEngine(db=engine_db)
    lead_id = engine.create_lead("lead@b.com")
    t1 = engine.create_ticket(lead_id, "sales", "A", "x")
    t2 = engine.create_ticket(lead_id, "support", "B", "y")
    tickets = engine.list_tickets()
    ids = [t["id"] for t in tickets]
    assert t1 in ids and t2 in ids
    assert tickets[0]["title"] in ("A", "B")


def test_record_and_list_usage(engine_db):
    engine = LinearEngine(db=engine_db)
    event_id = engine.record_usage("p1", "outreach_sent", amount="10", metadata={"k": "v"})
    assert event_id
    usage = engine.list_usage(project_id="p1")
    assert len(usage) == 1
    assert usage[0]["event_type"] == "outreach_sent"
    assert "k" in usage[0]["metadata"]


def test_record_usage_minimal(engine_db):
    engine = LinearEngine(db=engine_db)
    event_id = engine.record_usage(None, "page_view")
    usage = engine.list_usage()
    assert any(u["id"] == event_id for u in usage)
    assert usage[0]["amount"] is None


def test_list_usage_without_project(engine_db):
    engine = LinearEngine(db=engine_db)
    engine.record_usage("p1", "a")
    engine.record_usage("p2", "b")
    assert len(engine.list_usage()) == 2


def test_close(engine_db):
    engine = LinearEngine(db=engine_db)
    engine.close()


def test_get_swarm_db_singleton(monkeypatch):
    from core.persistence import linear_engine as le

    monkeypatch.setattr(le, "_swarm_db", None)
    first = get_swarm_db()
    second = get_swarm_db()
    assert first is second
