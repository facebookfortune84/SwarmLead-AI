"""Unit tests for the Closer agent (core.agents.sales.closer_agent)."""

import asyncio

import pytest

import core.models  # noqa: F401
from core.agents.sales.closer_agent import OBJECTION_RESPONSES, CloserAgent
from core.persistence.base import Base


@pytest.fixture
def db(tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'closer.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    return test_session


@pytest.fixture
def agent(db):
    return CloserAgent("closer_agent", None)


def test_compose_offer_starter_for_small(agent):
    offer = agent._compose_offer({"deal": {"amount_cents": 2900, "intent_score": 50}})
    assert offer["tier"] == "starter"
    assert offer["monthly_cents"] == 2900


def test_compose_offer_growth_high_intent(agent):
    offer = agent._compose_offer({"deal": {"amount_cents": 2900, "intent_score": 80}})
    assert offer["tier"] == "growth"


def test_compose_offer_enterprise_by_size(agent):
    offer = agent._compose_offer({"company_size": 25, "deal": {"amount_cents": 0, "intent_score": 0}})
    assert offer["tier"] == "enterprise"
    assert offer["monthly_cents"] == 29900


def test_compose_offer_annual_price(agent):
    offer = agent._compose_offer({"deal": {"amount_cents": 9900, "intent_score": 50}, "annual": True})
    assert offer["annual_cents"] == 99000
    assert "2 months free" in offer["pitch"]


def test_tier_for_rules():
    assert CloserAgent._tier_for(0, 0, 0) == "starter"
    assert CloserAgent._tier_for(5, 0, 0) == "growth"
    assert CloserAgent._tier_for(0, 29900, 0) == "enterprise"
    assert CloserAgent._tier_for(0, 0, 90) == "growth"


def test_handle_objection_known_responds(agent):
    result = agent._handle_objection({"objection": "It is too expensive for us"})
    assert result["objection"] == "price"
    assert result["response"] == OBJECTION_RESPONSES["price"]


def test_handle_objection_no_free_time(agent):
    result = agent._handle_objection({"objection": "I don't have time right now"})
    assert result["objection"] == "time"


def test_handle_objection_competitor(agent):
    result = agent._handle_objection({"objection": "we already use a competitor tool"})
    assert result["objection"] == "competitor"


def test_handle_objection_unknown_general(agent):
    result = agent._handle_objection({"objection": "hmm let me think"})
    assert result["objection"] == "general"


def test_handle_objection_all_keys_present():
    for key in ("price", "time", "competitor", "trust", "features"):
        assert key in OBJECTION_RESPONSES


def test_record_outcome_won_closes_deal(agent):
    deal = agent.pipeline.create_deal(
        {"id": "L1", "email": "a@b.com", "intent_score": 80, "metadata": {}}
    )
    agent._record_outcome({"deal_id": deal["id"], "won": True, "note": "signed annual"})
    updated = agent.pipeline.get_deal(deal["id"])
    assert updated["stage"] == "closed_won"
    assert updated["active"] is False


def test_record_outcome_lost(agent):
    deal = agent.pipeline.create_deal(
        {"id": "L2", "email": "c@d.com", "intent_score": 80, "metadata": {}}
    )
    agent._record_outcome({"deal_id": deal["id"], "won": False})
    updated = agent.pipeline.get_deal(deal["id"])
    assert updated["stage"] == "closed_lost"


def test_record_outcome_missing_deal_id(agent):
    assert agent._record_outcome({"won": True})["status"] == "error"


def test_execute_dispatches_actions(agent):
    result = asyncio.run(
        agent.run({"action": "compose_offer", "deal": {"amount_cents": 0, "intent_score": 0}})
    )
    assert result["success"] is True
    assert result["result"]["tier"] in {"starter", "growth", "enterprise"}