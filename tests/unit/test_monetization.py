"""Unit tests for the MonetizationMaximizer (core.services.monetization)."""

import pytest

from core.services.monetization import TIERS, MonetizationMaximizer


@pytest.fixture
def monetizer(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    return MonetizationMaximizer()


def test_tiers_match_pricing_page():
    from core.services.monetization import ANNUAL_MULTIPLIER

    assert {t: {k: spec[k] for k in ("price_cents", "name")} for t, spec in TIERS.items()} == {
        "starter": {"price_cents": 2900, "name": "Starter"},
        "growth": {"price_cents": 9900, "name": "Growth"},
        "enterprise": {"price_cents": 29900, "name": "Enterprise"},
    }
    assert ANNUAL_MULTIPLIER == 10
    # annual = 10x monthly (2 months free)
    assert TIERS["growth"]["annual_price_cents"] == 99000
    assert TIERS["growth"]["annual_savings_cents"] == 19800


def test_ready_false_without_api_key(monetizer):
    assert monetizer.ready is False


def test_ready_true_with_api_key(monkeypatch):
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_123")
    assert MonetizationMaximizer().ready is True


def test_create_checkout_url_none_when_not_ready(monetizer):
    assert monetizer.create_checkout_url() is None


def test_create_checkout_url_with_price_id(monetizer, monkeypatch):
    class FakeStripe:
        class checkout:
            class Session:
                @staticmethod
                def create(**kwargs):
                    return type("S", (), {"url": "https://checkout.stripe.com/sess"})()
                    # pragma: no cover - never reached

    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_123")
    monetizer.stripe = FakeStripe()
    url = monetizer.create_checkout_url(tier="growth", price_id="price_growth", customer_email="a@b.com")
    assert url == "https://checkout.stripe.com/sess"


def test_create_checkout_url_creates_product_without_price_id(monetizer, monkeypatch):
    created = {}

    class FakeProduct:
        @staticmethod
        def create(**kwargs):
            return type("P", (), {"id": "prod_1"})()

    class FakePrice:
        @staticmethod
        def create(**kwargs):
            created["unit_amount"] = kwargs.get("unit_amount")
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
    monetizer.stripe = FakeStripe()
    url = monetizer.create_checkout_url(tier="enterprise")
    assert url is not None
    assert created["unit_amount"] == 29900


def test_create_checkout_url_failure_returns_none(monetizer, monkeypatch):
    class BrokenStripe:
        class checkout:
            class Session:
                @staticmethod
                def create(**kwargs):
                    raise RuntimeError("stripe down")

    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    monetizer.stripe = BrokenStripe()
    assert monetizer.create_checkout_url() is None


def test_referral_program():
    program = MonetizationMaximizer().referral_program()
    assert program["program_name"] == "SwarmOS Referral Program"
    assert program["referrer_reward"] == "20% of first monthly payment"
    assert program["attribution_window_days"] == 30


def test_upsell_recommendations_high_intent_lead():
    monetizer = MonetizationMaximizer()
    recs = monetizer.upsell_recommendations({"intent_score": 90})
    tiers = [r["tier"] for r in recs]
    assert "growth" in tiers
    assert "enterprise" in tiers


def test_upsell_recommendations_no_lead():
    monetizer = MonetizationMaximizer()
    recs = monetizer.upsell_recommendations()
    assert [r["tier"] for r in recs] == ["enterprise"]


def test_offer_for_small_company(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    monetizer = MonetizationMaximizer()
    offer = monetizer.offer_for({"email": "x@y.com", "company_size": 5})
    assert offer["tier"] == "growth"
    assert "$99/mo" in offer["message"]
    assert offer["checkout_url"] is None  # stripe not ready


def test_offer_for_large_company(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    monetizer = MonetizationMaximizer()
    offer = monetizer.offer_for({"email": "x@y.com", "company_size": 50})
    assert offer["tier"] == "enterprise"
    assert "$299/mo" in offer["message"]
