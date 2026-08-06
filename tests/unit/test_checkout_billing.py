"""Tests for annual/monthly billing in the Stripe checkout router."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def fake_stripe(monkeypatch):
    calls = {}

    class FakeProduct:
        @staticmethod
        def create(**kwargs):
            return type("P", (), {"id": "prod_1"})()

    class FakePrice:
        @staticmethod
        def create(**kwargs):
            calls["price"] = kwargs
            return type("Pr", (), {"id": "price_1"})()

    class FakeSession:
        @staticmethod
        def create(**kwargs):
            calls["session"] = kwargs
            return type("S", (), {"id": "cs_1", "url": "https://checkout.stripe.com/x"})()

    class FakeError(Exception):
        pass

    class FakeCheckout:
        Session = FakeSession

    class FakeStripeModule:
        Product = FakeProduct
        Price = FakePrice
        checkout = FakeCheckout()
        error = FakeError

    monkeypatch.setattr("interfaces.api.routers.payments.stripe", FakeStripeModule)
    return calls


@pytest.fixture
def client():
    _app = FastAPI()
    from interfaces.api.routers.payments import router

    _app.include_router(router)
    return TestClient(_app)


def test_monthly_checkout_default(fake_stripe, client):
    response = client.post(
        "/api/stripe/create-checkout-session",
        json={"product_name": "Growth", "amount_cents": 9900, "billing": "monthly"},
    )
    assert response.status_code == 200
    assert fake_stripe["price"]["unit_amount"] == 9900
    assert fake_stripe["price"]["recurring"]["interval"] == "month"


def test_annual_checkout_is_ten_x(fake_stripe, client):
    response = client.post(
        "/api/stripe/create-checkout-session",
        json={"product_name": "Growth", "amount_cents": 9900, "billing": "annual"},
    )
    assert response.status_code == 200
    assert fake_stripe["price"]["unit_amount"] == 99000
    assert fake_stripe["price"]["recurring"]["interval"] == "year"


def test_annual_checkout_signed_url(fake_stripe, client):
    response = client.post(
        "/api/stripe/create-checkout-session",
        json={"product_name": "Starter", "amount_cents": 2900, "billing": "annual"},
    )
    assert response.json()["url"].startswith("https://checkout.stripe.com/")


def test_price_id_branch_ignores_amount(fake_stripe, client):
    response = client.post(
        "/api/stripe/create-checkout-session",
        json={"price_id": "price_fixed", "billing": "annual"},
    )
    assert response.status_code == 200
    assert "price" not in fake_stripe  # no dynamic price created
    assert fake_stripe["session"]["line_items"] == [{"price": "price_fixed", "quantity": 1}]