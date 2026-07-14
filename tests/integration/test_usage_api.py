"""
Integration Test

Usage API integration tests.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.persistence.session import init_db
from interfaces.api.routers.usage import router


def build_app():

    init_db()

    app = FastAPI()

    app.include_router(router)

    return app


def test_record_usage():

    client = TestClient(build_app())

    response = client.post(
        "/api/usage/record",
        json={
            "project_id": "TEST-001",
            "event_type": "integration_test",
            "amount": "1",
        },
    )

    assert response.status_code in (
        200,
        201,
    )
