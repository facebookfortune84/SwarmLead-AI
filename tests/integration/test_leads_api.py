"""
Integration Test

Lead API integration tests.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.persistence.session import init_db
from interfaces.api.routers.leads import router


def build_app():

    init_db()

    app = FastAPI()

    app.include_router(router)

    return app


def test_create_lead_endpoint_exists():

    app = build_app()

    client = TestClient(app)

    response = client.post(
        "/api/leads/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "company": "SwarmLead",
        },
    )

    assert response.status_code in (
        200,
        201,
    )


def test_create_lead_returns_identifier():

    app = build_app()

    client = TestClient(app)

    response = client.post(
        "/api/leads/",
        json={
            "email": "user@example.com",
            "name": "Integration User",
            "company": "Test Company",
        },
    )

    assert response.status_code in (
        200,
        201,
    )

    payload = response.json()

    assert isinstance(
        payload,
        dict,
    )

    assert "lead_id" in payload
