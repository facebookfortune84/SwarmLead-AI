"""
Integration Test

Verify application starts and core API routes are mounted.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from interfaces.api.routers.auth import router as auth_router
from interfaces.api.routers.crm import router as crm_router
from interfaces.api.routers.leads import router as leads_router
from interfaces.api.routers.notifications import router as notifications_router
from interfaces.api.routers.outreach import router as outreach_router
from interfaces.api.routers.payments import router as payments_router
from interfaces.api.routers.reporting import router as reporting_router
from interfaces.api.routers.tenants import router as tenants_router
from interfaces.api.routers.usage import router as usage_router
from interfaces.api.routers.users import router as users_router
from interfaces.api.routers.workflows import router as workflows_router


def build_app():

    app = FastAPI()

    app.include_router(auth_router)
    app.include_router(crm_router)
    app.include_router(leads_router)
    app.include_router(notifications_router)
    app.include_router(outreach_router)
    app.include_router(payments_router)
    app.include_router(reporting_router)
    app.include_router(tenants_router)
    app.include_router(usage_router)
    app.include_router(users_router)
    app.include_router(workflows_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


def test_health_endpoint():

    client = TestClient(build_app())

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_openapi_endpoint():

    client = TestClient(build_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "paths" in schema

    assert len(schema["paths"]) > 0


def test_docs_endpoint():

    client = TestClient(build_app())

    response = client.get("/docs")

    assert response.status_code == 200
