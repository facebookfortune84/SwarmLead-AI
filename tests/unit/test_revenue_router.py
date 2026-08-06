"""Unit tests for the revenue API router (interfaces.api.routers.revenue)."""

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import core.services.revenue_analytics as ra_module
import interfaces.api.routers.revenue as router_module
from core.services.revenue_analytics import RevenueAnalytics
from interfaces.api.routers.revenue import router


@pytest.fixture
def client(tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'rev_api.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    state_path = tmp_path / "growth_state.json"
    state_path.write_text(
        json.dumps({"revenue": {"quotes_approved": 3, "projected_mrr": 198}}),
        encoding="utf-8",
    )
    analytics = RevenueAnalytics(growth_state_path=state_path)
    monkeypatch.setattr(ra_module, "revenue_analytics", analytics)
    monkeypatch.setattr(router_module, "revenue_analytics", analytics)

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_summary_endpoint(client):
    response = client.get("/api/revenue/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["mrr_cents"] == 19800
    assert body["quotes_approved"] == 3


def test_tiers_endpoint(client):
    response = client.get("/api/revenue/tiers")
    assert response.status_code == 200
    body = response.json()
    assert body["annual_multiplier"] == 10
    assert body["tiers"]["growth"]["annual_cents"] == 99000


def test_churn_endpoint(client):
    response = client.get("/api/revenue/churn?churn_rate=0.1&months=3")
    assert response.status_code == 200
    body = response.json()
    assert len(body["retention_curve"]) == 3
    assert body["ltv"]["churn_rate"] == 0.1


def test_dunning_endpoint(client):
    response = client.get(
        "/api/revenue/dunning?email=x@y.com&invoice_id=inv_1"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "dunning_retry"
    assert body["to_email"] == "x@y.com"
    assert "inv_1" in body["body"]


def test_usage_endpoint(client):
    response = client.get("/api/revenue/usage?units=3.5&rate_cents=100")
    assert response.status_code == 200
    body = response.json()
    assert body["total_cents"] == 350


def test_usage_requires_units(client):
    assert client.get("/api/revenue/usage?rate_cents=100").status_code == 422