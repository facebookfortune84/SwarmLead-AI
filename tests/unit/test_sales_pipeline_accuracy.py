"""
Unit tests for the pipeline accuracy hardening:

- funnel integrity: forward-only moves, terminal stages locked
- email-level de-duplication in create_deal
- SDR qualification handoff (qualified -> discovery)
- sales velocity stats (time-to-first-sale)
"""

import pytest
from sqlalchemy.orm import sessionmaker

import core.models  # noqa: F401
from core.persistence.base import Base
from core.services.sales_pipeline import SalesPipeline


@pytest.fixture
def db(tmp_path, monkeypatch):
    import sqlalchemy

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'accuracy.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    return test_session


@pytest.fixture
def pipeline(db):
    return SalesPipeline()


@pytest.fixture
def db_session(db):
    return db()


def _lead(score=70, lead_id="L1", email="owner@acme.com"):
    return {
        "id": lead_id,
        "email": email,
        "company": "Acme",
        "intent_score": score,
        "company_size": 3,
        "metadata": {"budget": True, "authority": True, "need": True, "timeline": True},
    }


# ------------------------------------------------------------- funnel integrity
def test_advance_forward_jump_allowed(db, pipeline):
    deal = pipeline.create_deal(_lead())
    moved = pipeline.advance(deal["id"], "quoted")
    assert moved["stage"] == "quoted"


def test_advance_backwards_raises(db, pipeline):
    deal = pipeline.create_deal(_lead())
    pipeline.advance(deal["id"], "quoted")
    with pytest.raises(ValueError, match="backwards"):
        pipeline.advance(deal["id"], "discovery")


def test_advance_terminal_is_locked(db, pipeline):
    deal = pipeline.create_deal(_lead())
    pipeline.close_lost(deal["id"])
    with pytest.raises(ValueError, match="terminal"):
        pipeline.advance(deal["id"], "engaged")


def test_advance_closed_won_cannot_reopen(db, pipeline):
    deal = pipeline.create_deal(_lead())
    pipeline.close_won(deal["id"])
    with pytest.raises(ValueError, match="terminal"):
        pipeline.close_lost(deal["id"])


# ---------------------------------------------------------- de-dup by email
def test_create_deal_dedups_by_email(db, pipeline):
    first = pipeline.create_deal(_lead(lead_id="L1", email="owner@acme.com"))
    second = pipeline.create_deal(
        _lead(lead_id="L2", email="owner@acme.com")
    )  # same customer, different row id
    assert first["id"] == second["id"]
    assert len(pipeline.list_deals()) == 1


def test_create_deal_different_emails_are_distinct(db, pipeline):
    first = pipeline.create_deal(_lead(lead_id="L1", email="a@acme.com"))
    second = pipeline.create_deal(_lead(lead_id="L2", email="b@acme.com"))
    assert first["id"] != second["id"]
    assert len(pipeline.list_deals()) == 2


# ---------------------------------------------------------- SDR handoff
def test_qualify_hands_off_to_discovery(db, pipeline):
    result = pipeline.qualify(_lead(score=80))
    assert result["qualified"] is True
    assert result["deal"]["stage"] == "discovery"
    assert result["deal"]["owner_agent"] == "sdr_agent"
    history = pipeline.deal_history(result["deal"]["id"])
    to_stages = [h["to_stage"] for h in history]
    assert to_stages == ["qualified", "discovery"]


def test_qualify_reasons_breakdown(db, pipeline):
    result = pipeline.qualify(_lead(score=80))
    assert result["qualified"] is True
    assert "intent=80" in result["reasons"]
    assert any(r.startswith("budget:") for r in result["reasons"])
    assert any(r.startswith("business_domain:") for r in result["reasons"])


def test_qualify_business_domain_flag_boosts_score(db, pipeline):
    lead = _lead(score=55)
    assert lead["intent_score"] == 55
    no_flag = {**lead, "metadata": {**lead["metadata"], "business_domain": False}}
    with_flag = {**lead, "metadata": {**lead["metadata"], "business_domain": True}}
    rejected = pipeline.qualify(no_flag)
    accepted = pipeline.qualify(with_flag)
    # 55*0.6 + 40 = 73 -> 73 with flag beats 71 without
    assert rejected["score"] < accepted["score"]
    assert accepted["qualified"] is True


# ---------------------------------------------------------- sales velocity
def test_velocity_stats_empty(db, pipeline):
    stats = pipeline.velocity_stats()
    assert stats["median_close_days"] == 0.0
    assert stats["wins_count"] == 0


def test_velocity_stats_computes_median(db, db_session):
    import datetime as dt

    from core.models import Deal

    d1 = Deal(
        id="deal-1", lead_id="L1", email="a@x.com", stage="closed_won",
        amount_cents=9900, active=False,
        created_at=dt.datetime(2026, 1, 1), closed_at=dt.datetime(2026, 1, 11),
    )
    d2 = Deal(
        id="deal-2", lead_id="L2", email="b@x.com", stage="closed_won",
        amount_cents=9900, active=False,
        created_at=dt.datetime(2026, 2, 1), closed_at=dt.datetime(2026, 2, 11),
    )
    db_session.add_all([d1, d2])
    db_session.commit()
    db_session.close()

    stats = SalesPipeline().velocity_stats()
    assert stats["wins_count"] == 2
    assert stats["median_close_days"] == 10.0


def test_forecast_includes_velocity(db, pipeline):
    deal = pipeline.create_deal(_lead())
    pipeline.close_won(deal["id"])
    forecast = pipeline.forecast()
    assert "sales_velocity_days" in forecast
    assert forecast["sales_velocity_days"] == 0.0