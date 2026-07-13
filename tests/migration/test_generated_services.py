"""
Migration Validation

Verify all migrated services import successfully.

This catches:

- broken import rewrites
- missing dependencies
- circular imports
- invalid package moves
"""

import importlib

SERVICES = [
    "core.services.notification_service",
    "core.services.payment_service",
    "core.services.tenant_service",
    "core.services.ticket_service",
    "core.services.workflow_service",
]


def test_all_generated_services_import():

    failures = []

    for module_name in SERVICES:
        try:
            importlib.import_module(module_name)

        except Exception as exc:
            failures.append(f"{module_name}: {exc}")

    assert not failures, "\n\n".join(failures)


def test_service_modules_exist():

    failures = []

    for module_name in SERVICES:
        try:
            module = importlib.import_module(module_name)

            assert module is not None

        except Exception as exc:
            failures.append(f"{module_name}: {exc}")

    assert not failures, "\n\n".join(failures)
