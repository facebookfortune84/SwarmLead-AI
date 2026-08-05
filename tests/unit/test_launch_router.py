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


def test_launch_activity_endpoint_returns_metrics(monkeypatch, tmp_path):
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker

    import core.models  # noqa: F401
    from core.persistence.base import Base

    db_path = tmp_path / "activity.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", test_session)

    from datetime import datetime, timedelta

    from core.models import Lead

    db = test_session()
    try:
        db.add_all(
            [
                Lead(
                    email="v@example.com",
                    status="NEW",
                    intent_score=85,
                    metadata_json='{"source": "voice", "origin": "voice_capture"}',
                    created_at=datetime.utcnow(),
                ),
                Lead(
                    email="q@example.com",
                    status="NEW",
                    intent_score=90,
                    metadata_json='{"source": "plan_quiz", "origin": "landing"}',
                    created_at=datetime.utcnow() - timedelta(hours=1),
                ),
                Lead(
                    email="old@example.com",
                    status="NEW",
                    intent_score=50,
                    metadata_json='{"source": "discovery"}',
                    created_at=datetime.utcnow() - timedelta(days=30),
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    client = _client()
    response = client.get("/api/launch/activity")
    assert response.status_code == 200
    body = response.json()
    assert body["leads_since_launch"] == 2
    assert body["leads_by_source"]["voice"] == 1
    assert body["leads_by_source"]["plan_quiz"] == 1
    assert body["high_intent_leads"] == 2
    assert body["launch_week"] is True


def test_launch_activity_never_raises_when_db_down(monkeypatch):
    def boom():
        raise RuntimeError("db down")

    monkeypatch.setattr("core.persistence.session.SessionLocal", boom)

    client = _client()
    response = client.get("/api/launch/activity")
    assert response.status_code == 200
    body = response.json()
    assert body["leads_since_launch"] == 0
    assert body["high_intent_leads"] == 0
