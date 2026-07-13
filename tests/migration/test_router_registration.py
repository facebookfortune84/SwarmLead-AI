"""
Migration Validation

Verify migrated routers successfully register routes.

This catches:

- broken APIRouter definitions
- failed decorator registration
- route import regressions
- migration damage to endpoint definitions
"""

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

ROUTERS = {
    "auth": auth_router,
    "crm": crm_router,
    "leads": leads_router,
    "notifications": notifications_router,
    "outreach": outreach_router,
    "payments": payments_router,
    "reporting": reporting_router,
    "tenants": tenants_router,
    "usage": usage_router,
    "users": users_router,
    "workflows": workflows_router,
}


def test_all_routers_have_routes():

    failures = []

    for name, router in ROUTERS.items():
        route_count = len(router.routes)

        if route_count == 0:
            failures.append(f"{name}: router contains no routes")

    assert not failures, "\n".join(failures)


def test_router_prefixes_are_defined():

    failures = []

    for name, router in ROUTERS.items():
        prefix = getattr(
            router,
            "prefix",
            None,
        )

        if prefix is None:
            failures.append(f"{name}: missing prefix")

    assert not failures, "\n".join(failures)


def test_router_tags_exist():

    failures = []

    for name, router in ROUTERS.items():
        tags = getattr(
            router,
            "tags",
            None,
        )

        if not tags:
            failures.append(f"{name}: missing tags")

    assert not failures, "\n".join(failures)
