"""Unit tests for the SDR agent (core.agents.sales.sdr_agent)."""

import asyncio

import pytest

import core.models  # noqa: F401
from core.agents.sales.sdr_agent import CADENCE, REACTIVATION_ANGLES, SDRAgent
from core.persistence.base import Base


@pytest.fixture
def db(tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'sdr.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    return test_session


@pytest.fixture
def agent(db):
    return SDRAgent("sdr_agent", None)


def _lead(lead_id="L1", score=70, email="owner@acme.com", name="Ana", company="Acme"):
    return {
        "id": lead_id,
        "email": email,
        "name": name,
        "company": company,
        "intent_score": score,
        "company_size": 5,
        "metadata": {"budget": True, "authority": True, "need": True, "timeline": True},
    }


def test_cadence_has_four_escalating_touches():
    assert len(CADENCE) == 4
    assert [c[0] for c in CADENCE] == [0, 3, 7, 14]


def test_cadence_angles_cover_key_product_pillars():
    joined = " ".join(a for _, a in CADENCE).lower()
    for keyword in ("workforce", "seo", "voice", "autopilot"):
        assert keyword in joined


def test_reactivation_angles_non_empty():
    assert len(REACTIVATION_ANGLES) >= 3


def test_qualify_action_creates_deals(agent):
    result = asyncio.run(agent.run({"action": "qualify", "leads": [_lead()]}))
    assert result["success"] is True
    body = result["result"]
    assert body["deals_created"] == 1


def test_qualify_rejects_cold_leads(agent):
    leads = [{"id": "L2", "email": "cold@x.com", "intent_score": 5, "metadata": {}}]
    result = asyncio.run(agent.run({"action": "qualify", "leads": leads}))
    assert result["result"]["deals_created"] == 0
    assert result["result"]["leads_rejected"] == 1


def test_qualify_empty_input_ok(agent):
    result = asyncio.run(agent.run({"action": "qualify", "leads": []}))
    assert result["success"] is True


def test_unknown_action_returns_error(agent):
    result = asyncio.run(agent.run({"action": "hack"}))
    assert result["success"] is False


def test_draft_followup_first_touch(agent):
    draft = agent._draft_followup({"email": "a@b.com", "name": "Ana", "company": "Acme", "touch": 0})
    assert draft["touch"] == 0
    assert draft["delay_days"] == 0
    assert "Ana" in draft["body"]
    assert "Acme" in draft["body"]


def test_draft_followup_last_touch(agent):
    draft = agent._draft_followup({"email": "a@b.com", "touch": 99})
    assert draft["touch"] == 3
    assert draft["delay_days"] == 14


def test_draft_followup_subjects_escalate(agent):
    s0 = agent._subject_for_touch(0, "Acme")
    s3 = agent._subject_for_touch(3, "Acme")
    assert s0 != s3
    assert "Acme" in s3


def test_reactivate_picks_stable_angle(agent):
    a = agent._reactivate({"email": "x@y.com", "company": "Acme"})
    b = agent._reactivate({"email": "x@y.com", "company": "Acme"})
    assert a["subject"] == b["subject"]
    assert a["body"] == b["body"]


def test_pick_angle_deterministic():
    first = SDRAgent._pick_angle("Beta LLC")
    second = SDRAgent._pick_angle("Beta LLC")
    assert first == second
    assert first in REACTIVATION_ANGLES
