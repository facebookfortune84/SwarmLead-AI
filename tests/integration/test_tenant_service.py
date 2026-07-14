"""
Integration Test

Tenant service integration tests.
"""

from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.tenant_service import (
    TenantService,
)


def test_tenant_service_constructs():

    init_db()

    db = SessionLocal()

    try:
        service = TenantService(db)

        assert service is not None

    finally:
        db.close()


def test_tenant_registration():

    init_db()

    db = SessionLocal()

    try:
        service = TenantService(db)

        tenant = service.register(name="Integration Testing Company")

        assert tenant is not None

        assert tenant.name == ("Integration Testing Company")

    finally:
        db.close()
