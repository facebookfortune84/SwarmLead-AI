"""Unit tests for revenue analytics (core.services.revenue_analytics)."""

import json

import pytest

import core.services.monetization as mon
from core.services.revenue_analytics import (
    DEFAULT_CHURN_RATE,
    RevenueAnalytics,
)
from core.services.sales_pipeline import MONTHLY_VALUE, SalesPipeline


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'rev.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)
    return SalesPipeline()


@pytest.fixture
def analytics(pipeline, tmp_path):
    state = tmp_path / "growth_state.json"
    state.write_text(
        json.dumps({"revenue": {"quotes_approved": 2, "projected_mrr": 198}}),
        encoding="utf-8",
    )
    return RevenueAnalytics(pipeline=pipeline, growth_state_path=state)


def test_empty_summary(analytics):
    summary = analytics.summary()
    assert summary["mrr_cents"] == 19800  # 2 quotes at $99
    assert summary["quotes_approved"] == 2
    assert summary["closed_won_count"] == 0
    assert set(summary["tier_mix"]) == {"starter", "growth", "enterprise"}


def test_summary_with_closed_won(analytics, tmp_path, monkeypatch):
    deal = analytics.pipeline.create_deal(
        {
            "id": "L1",
            "email": "a@b.com",
            "intent_score": 92,
            "company_size": 8,
        }
    )
    analytics.pipeline.advance(
        deal["id"], "closed_won", triggered_by="closer_agent"
    )
    summary = analytics.summary()
    assert summary["closed_won_count"] == 1
    assert summary["mrr_cents"] == 19800 + MONTHLY_VALUE["growth"]
    assert summary["tier_mix"]["growth"]["count"] == 1


def test_ltv_formula(analytics):
    result = analytics.ltv(mrr_cents=10000, churn_rate=0.05)
    assert result["ltv_cents"] == 200000
    assert result["avg_customer_lifetime_months"] == 20.0


def test_ltv_defaults(analytics):
    result = analytics.ltv(mrr_cents=10000)
    assert result["churn_rate"] == DEFAULT_CHURN_RATE


def test_retention_curve(analytics):
    curve = analytics.retention_curve(months=4, churn_rate=0.1)
    assert len(curve) == 4
    assert curve[0]["retention_rate"] == pytest.approx(0.9, abs=1e-4)
    assert curve[1]["retention_rate"] == pytest.approx(0.81, abs=1e-4)


def test_churn_risk_all_safe(analytics, tmp_path, monkeypatch):
    deal = analytics.pipeline.create_deal(
        {"id": "L2", "email": "c@d.com", "intent_score": 92}
    )
    assert deal["stage"] == "qualified"
    risk = analytics.churn_risk(max_days_inactive=60)
    assert risk["risk_rate"] == 0.0
    assert risk["at_risk_deals"] == []


def test_churn_risk_old_event(analytics, tmp_path, monkeypatch):
    import datetime as dt

    import core.models  # noqa: F401
    from core.models.deal import DealStageEvent
    from core.persistence.session import SessionLocal

    deal = analytics.pipeline.create_deal(
        {"id": "L3", "email": "e@f.com", "intent_score": 92}
    )
    db = SessionLocal()
    db.query(DealStageEvent).filter(DealStageEvent.deal_id == deal["id"]).delete()
    db.add(
        DealStageEvent(
            deal_id=deal["id"],
            from_stage="qualified",
            to_stage="qualified",
            triggered_by="test",
            occurred_at=dt.datetime.utcnow() - dt.timedelta(days=200),
        )
    )
    db.commit()
    db.close()

    risk = analytics.churn_risk(max_days_inactive=60)
    assert risk["at_risk_deals"][0]["deal_id"] == deal["id"]
    assert risk["at_risk_deals"][0]["days_inactive"] > 60


def test_ltv_defaults_from_summary(analytics):
    result = analytics.ltv()
    assert result["mrr_cents"] == analytics.summary()["mrr_cents"]


def test_monetization_billing_options(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    options = mon.MonetizationMaximizer().billing_options()
    assert options["annual_multiplier"] == 10
    assert options["tiers"]["growth"]["annual_savings_cents"] == 9900 * 2


def test_dunning_notice_content():
    notice = mon.MonetizationMaximizer().dunning_notice(
        "x@y.com", {"id": "inv_1"}
    )
    assert notice["kind"] == "dunning_retry"
    assert notice["to_email"] == "x@y.com"
    assert "inv_1" in notice["body"]
    assert notice["grace_days"] == 7


def test_usage_bill_math():
    bill = mon.MonetizationMaximizer().usage_bill(3.5, 100)
    assert bill["total_cents"] == 350
    assert bill["subtotal_usd"] == 3.5


def test_annual_offer(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    offer = mon.MonetizationMaximizer().offer_for(
        {"email": "x@y.com", "company_size": 5}, billing="annual"
    )
    assert offer["tier"] == "growth"
    assert offer["annual_price_cents"] == 99000
    assert offer["monthly_price_cents"] == 9900
    # growth annual = 10x $99 = $990, savings = $198
    assert offer["annual_savings_cents"] == 19800
    assert "2 months free" in offer["message"]


def test_annual_checkout_uses_annual_price(monkeypatch):
    created = {}

    class FakeProduct:
        @staticmethod
        def create(**kwargs):
            return type("P", (), {"id": "prod_1"})()

    class FakePrice:
        @staticmethod
        def create(**kwargs):
            created["unit_amount"] = kwargs.get("unit_amount")
            created["interval"] = kwargs.get("recurring", {}).get("interval")
            return type("Pr", (), {"id": "price_1"})()

    class FakeStripe:
        Product = FakeProduct
        Price = FakePrice

        class checkout:
            class Session:
                @staticmethod
                def create(**kwargs):
                    return type("S", (), {"url": "https://checkout.stripe.com/s"})()
                    # pragma: no cover

    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_123")
    m = mon.MonetizationMaximizer()
    m.stripe = FakeStripe()
    url = m.create_checkout_url(tier="enterprise", billing="annual")
    assert url is not None
    assert created["unit_amount"] == 299000
    assert created["interval"] == "year"