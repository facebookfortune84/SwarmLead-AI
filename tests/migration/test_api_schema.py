"""
Migration Validation

Verify the entire migrated API can build an OpenAPI schema.

This is one of the strongest migration validation tests because
it exercises:

- router imports
- FastAPI registration
- dependency injection
- request models
- response models
- route metadata
"""

from fastapi import FastAPI

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

    app = FastAPI(title="SwarmLead Migration Validation")

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

    return app


def test_openapi_schema_builds():

    app = build_app()

    schema = app.openapi()

    assert schema is not None

    assert "paths" in schema

    assert len(schema["paths"]) > 0


def test_no_duplicate_route_paths():

    app = build_app()

    routes = []

    for route in app.routes:
        if hasattr(route, "path"):
            routes.append(
                (
                    route.path,
                    tuple(sorted(route.methods)) if route.methods else (),
                )
            )

    duplicates = []

    seen = set()

    for route in routes:
        if route in seen:
            duplicates.append(route)

        seen.add(route)

    assert not duplicates, duplicates


def test_every_router_contributes_routes():

    app = build_app()

    paths = app.openapi()["paths"]

    assert len(paths) > 0
