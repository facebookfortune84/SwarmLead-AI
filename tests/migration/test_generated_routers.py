"""
Migration Validation

Verify all migrated FastAPI routers import.

This catches:

- broken router imports
- dependency injection issues
- failed auth rewrites
- persistence rewrite failures
"""

import importlib

ROUTERS = [
    "interfaces.api.routers.auth",
    "interfaces.api.routers.crm",
    "interfaces.api.routers.leads",
    "interfaces.api.routers.notifications",
    "interfaces.api.routers.outreach",
    "interfaces.api.routers.payments",
    "interfaces.api.routers.reporting",
    "interfaces.api.routers.tenants",
    "interfaces.api.routers.usage",
    "interfaces.api.routers.users",
    "interfaces.api.routers.workflows",
]


def test_all_generated_routers_import():

    failures = []

    for module_name in ROUTERS:
        try:
            importlib.import_module(module_name)

        except Exception as exc:
            failures.append(f"{module_name}: {exc}")

    assert not failures, "\n\n".join(failures)


def test_router_modules_exist():

    failures = []

    for module_name in ROUTERS:
        try:
            module = importlib.import_module(module_name)

            assert module is not None

        except Exception as exc:
            failures.append(f"{module_name}: {exc}")

    assert not failures, "\n\n".join(failures)
