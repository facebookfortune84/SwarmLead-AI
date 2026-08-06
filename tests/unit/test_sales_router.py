"""Unit tests for the sales API router (interfaces.api.routers.sales)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import core.services.sales_pipeline as sp_module
import interfaces.api.routers.sales as sales_module
from core.services.sales_pipeline import SalesPipeline
from interfaces.api.routers.sales import router


@pytest.fixture
def client(tmp_path, monkeypatch):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401
    from core.persistence.base import Base

    engine = sqlalchemy.create_engine(f"sqlite:///{tmp_path / 'sales_api.db'}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    instance = SalesPipeline()
    monkeypatch.setattr(sp_module, "sales_pipeline", instance)
    monkeypatch.setattr(sales_module, "sales_pipeline", instance)

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_pipeline_snapshot_endpoint(client):
    response = client.get("/api/sales/pipeline")
    assert response.status_code == 200
    body = response.json()
    assert body["total_deals"] == 0
    assert body["weighted_pipeline_cents"] == 0
    assert len(body["stages"]) == 6


def test_create_and_get_deal(client):
    create = client.post(
        "/api/sales/deals",
        json={
            "lead_id": "L1",
            "email": "a@b.com",
            "intent_score": 80,
            "company_size": 5,
        },
    )
    assert create.status_code == 200
    deal = create.json()
    assert deal["stage"] == "qualified"

    got = client.get(f"/api/sales/deals/{deal['id']}")
    assert got.status_code == 200
    assert got.json()["history"][0]["to_stage"] == "qualified"


def test_get_missing_deal_404(client):
    assert client.get("/api/sales/deals/nope").status_code == 404


def test_advance_deal(client):
    deal = client.post(
        "/api/sales/deals",
        json={"lead_id": "L2", "email": "c@d.com", "intent_score": 70},
    ).json()
    advanced = client.post("/api/sales/advance", json={"deal_id": deal["id"], "stage": "engaged"})
    assert advanced.status_code == 200
    assert advanced.json()["stage"] == "engaged"


def test_advance_invalid_stage_422(client):
    deal = client.post(
        "/api/sales/deals",
        json={"lead_id": "L3", "email": "e@f.com", "intent_score": 70},
    ).json()
    resp = client.post("/api/sales/advance", json={"deal_id": deal["id"], "stage": "warp"})
    assert resp.status_code == 422


def test_close_deal(client):
    deal = client.post(
        "/api/sales/deals",
        json={"lead_id": "L4", "email": "g@h.com", "intent_score": 80},
    ).json()
    closed = client.post("/api/sales/close", json={"deal_id": deal["id"], "won": True})
    assert closed.status_code == 200
    assert closed.json()["stage"] == "closed_won"


def test_forecast_endpoint(client):
    assert client.get("/api/sales/forecast").status_code == 200


def test_qualify_endpoint(client):
    resp = client.post(
        "/api/sales/qualify",
        json={"leads": [{"id": "L9", "email": "q@z.com", "intent_score": 92}]},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["result"]["deals_created"] == 1


def test_objection_endpoint(client):
    resp = client.post("/api/sales/objection?text=too expensive")
    assert resp.status_code == 200
    assert resp.json()["objection"] == "price"
