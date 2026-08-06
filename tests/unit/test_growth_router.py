"""Unit tests for the growth autonomy API router (interfaces.api.routers.growth)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import core.services.growth_automation as ga_module
import interfaces.api.routers.growth as growth_router_module
from core.services.growth_automation import GrowthAutomation
from interfaces.api.auth.middleware import get_current_active_user
from interfaces.api.routers.growth import router


@pytest.fixture
def client(monkeypatch, tmp_path):
    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    instance.enabled = True
    monkeypatch.setattr(ga_module, "growth_automation", instance)
    monkeypatch.setattr(growth_router_module, "growth_automation", instance)

    async def fake_user():
        return {"id": "u1", "email": "founder@test.local", "role": "admin"}

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_active_user] = fake_user
    return TestClient(app)


def test_growth_status_endpoint(client):
    response = client.get("/api/growth/status")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert "auto_approve" in body


def test_growth_queue_endpoint(client):
    response = client.get("/api/growth/queue")
    assert response.status_code == 200
    assert "items" in response.json()


def test_growth_toggle_endpoint(client):
    response = client.post("/api/growth/toggle?enabled=false")
    assert response.status_code == 200
    assert response.json() == {"enabled": False}


def test_growth_auto_approve_endpoint(client):
    response = client.post("/api/growth/auto-approve?auto_approve=true")
    assert response.status_code == 200
    assert response.json() == {"auto_approve": True}


def test_growth_approve_missing_action_404(client):
    response = client.post("/api/growth/approve/nope")
    assert response.status_code == 404


def test_growth_reject_missing_action_404(client):
    response = client.post("/api/growth/reject/nope")
    assert response.status_code == 404


def test_growth_approve_queued_action(client, monkeypatch):
    async def fake_approve(action_id):
        return {"status": "approved", "action_id": action_id}

    monkeypatch.setattr(growth_router_module.growth_automation, "approve", fake_approve)
    response = client.post("/api/growth/approve/abc123")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_growth_run_now_endpoint(client, monkeypatch):
    async def fake_run_now():
        return {"status": "started"}

    monkeypatch.setattr(growth_router_module.growth_automation, "run_now", fake_run_now)
    response = client.post("/api/growth/run-now")
    assert response.status_code == 200
    assert response.json()["status"] == "started"
