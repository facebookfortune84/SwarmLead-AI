"""Unit tests for the launch API router (interfaces.api.routers.launch)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from interfaces.api.routers.launch import router


def _client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_launch_status_endpoint():
    client = _client()
    response = client.get("/api/launch/status")
    assert response.status_code == 200
    body = response.json()
    assert body["launched"] is True
    assert body["promo"]["code"] == "LAUNCH100"
    assert "share" in body


def test_launch_share_endpoint():
    client = _client()
    response = client.get("/api/launch/share")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"x", "facebook", "linkedin", "whatsapp", "email"}


def test_launch_traffic_drafts_endpoint():
    client = _client()
    response = client.get("/api/launch/traffic/drafts")
    assert response.status_code == 200
    drafts = response.json()
    assert len(drafts) >= 4
    assert all("text" in d and "network" in d for d in drafts)


def test_launch_traffic_queue_endpoint():
    client = _client()
    response = client.get("/api/launch/traffic/queue")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
