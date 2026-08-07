"""
Unit tests for the sales pipeline service (core.services.sales_pipeline).

Uses a tmp sqlite DB with core.persistence.session.SessionLocal patched to
the test session so no production data is touched.
"""

import pytest

import core.models  # noqa: F401
from core.persistence.base import Base
from core.services.sales_pipeline import (
    MONTHLY_VALUE,
    QUALIFY_INTENT_THRESHOLD,
    STAGES,
    SalesPipeline,
)


@pytest.fixture
def db(tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'sales.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    return test_session


@pytest.fixture
def pipeline(db):
    return SalesPipeline()


def _lead(score=70, budget=True, authority=True, need=True, timeline=True, size=3, lead_id="L1", email="owner@acme.com"):
    return {
        "id": lead_id,
        "email": email,
        "company": f"Acme {size}",
        "intent_score": score,
        "company_size": size,
        "metadata": {
            "budget": budget,
            "authority": authority,
            "need": need,
            "timeline": timeline,
        },
    }


def test_stages_ordered_and_terminal():
    assert STAGES.index("qualified") < STAGES.index("closed_won")
    assert "closed_won" in STAGES and "closed_lost" in STAGES


def test_create_deal_creates_and_serializes(db, pipeline):
    deal = pipeline.create_deal(_lead(score=70))
    assert deal["stage"] == "qualified"
    assert deal["amount_cents"] == MONTHLY_VALUE["starter"]
    assert deal["probability"] == 0.15
    assert deal["lead_id"] == "L1"
    # Audit event recorded
    history = pipeline.deal_history(deal["id"])
    assert history[0]["from_stage"] is None
    assert history[0]["to_stage"] == "qualified"


def test_create_deal_idempotent(db, pipeline):
    first = pipeline.create_deal(_lead())
    second = pipeline.create_deal(_lead())
    assert first["id"] == second["id"]


def test_create_deal_suggested_amount_by_size(db, pipeline):
    assert pipeline.create_deal(_lead(size=2, lead_id="L1", email="s@x.com"))["amount_cents"] == MONTHLY_VALUE["starter"]
    assert pipeline.create_deal(_lead(size=8, lead_id="L2", email="g@x.com"))["amount_cents"] == MONTHLY_VALUE["growth"]
    assert pipeline.create_deal(_lead(size=25, lead_id="L3", email="e@x.com"))["amount_cents"] == MONTHLY_VALUE["enterprise"]


def test_qualify_high_intent_creates_deal(db, pipeline):
    result = pipeline.qualify(_lead(score=80))
    assert result["qualified"] is True
    assert result["deal"]["email"] == "owner@acme.com"


def test_qualify_low_intent_rejected(db, pipeline):
    result = pipeline.qualify(_lead(score=30, budget=False, authority=False, need=False, timeline=False))
    assert result["qualified"] is False
    assert "below threshold" in result["reason"]


def test_qualify_threshold_boundary(db, pipeline):
    high = pipeline.qualify(_lead(score=QUALIFY_INTENT_THRESHOLD, budget=True, authority=True, need=True, timeline=True))
    assert high["qualified"] is True


def test_advance_moves_stage_and_records_event(db, pipeline):
    deal = pipeline.create_deal(_lead())
    moved = pipeline.advance(deal["id"], "engaged", triggered_by="closer_agent")
    assert moved["stage"] == "engaged"
    assert moved["probability"] == 0.50
    events = pipeline.deal_history(deal["id"])
    assert events[-1]["to_stage"] == "engaged"
    assert events[-1]["triggered_by"] == "closer_agent"


def test_advance_unknown_stage_raises(db, pipeline):
    deal = pipeline.create_deal(_lead())
    with pytest.raises(ValueError):
        pipeline.advance(deal["id"], "nonsense")


def test_advance_missing_deal_returns_none(db, pipeline):
    assert pipeline.advance("nope", "engaged") is None


def test_close_won_deactivates_and_marks_closed(db, pipeline):
    deal = pipeline.create_deal(_lead())
    won = pipeline.close_won(deal["id"], note="signed")
    assert won["stage"] == "closed_won"
    assert won["active"] is False
    assert won["closed_at"] is not None
    assert "signed" in won["notes"]


def test_close_lost_sets_probability_zero(db, pipeline):
    deal = pipeline.create_deal(_lead())
    lost = pipeline.close_lost(deal["id"])
    assert lost["stage"] == "closed_lost"
    assert lost["probability"] == 0.0


def test_pipeline_snapshot_aggregates(db, pipeline):
    pipeline.create_deal(_lead(score=80, size=8, lead_id="L1", email="one@x.com"))  # growth
    pipeline.create_deal(_lead(score=70, size=25, lead_id="L2", email="two@x.com"))  # enterprise
    snapshot = pipeline.pipeline_snapshot()
    assert snapshot["total_deals"] == 2
    qualified_row = next(s for s in snapshot["stages"] if s["stage"] == "qualified")
    assert qualified_row["count"] == 2
    expect_weighted = (9900 + 29900) * 0.15
    assert snapshot["weighted_pipeline_cents"] == int(expect_weighted)


def test_forecast_computes_annual_impact(db, pipeline):
    deal = pipeline.create_deal(_lead(size=5))
    pipeline.close_won(deal["id"])
    forecast = pipeline.forecast()
    assert forecast["closed_won_count"] == 1
    assert forecast["closed_won_mrr_cents"] == 9900
    assert forecast["closed_won_annual_cents"] == 9900 * 12
    assert forecast["annual_contract_cents"] == 9900 * 10


def test_sync_from_leads_qualifies_batch(db, pipeline):
    leads = [
        _lead(score=80, email="a@x.com", lead_id="L1"),
        {"id": "L2", "email": "cold@x.com", "intent_score": 10, "metadata": {}},
    ]
    result = pipeline.sync_from_leads(leads)
    assert result["deals_created"] == 1
    assert result["leads_rejected"] == 1


def test_get_deal_and_list_filter(db, pipeline):
    deal = pipeline.create_deal(_lead())
    assert pipeline.get_deal(deal["id"])["id"] == deal["id"]
    assert pipeline.get_deal("missing") is None
    assert len(pipeline.list_deals(stage="qualified")) == 1
    assert len(pipeline.list_deals(stage="closed_won")) == 0