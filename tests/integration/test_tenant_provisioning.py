"""
Integration Test
"""

from unittest.mock import Mock

from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.tenant_service import (
    TenantService,
)


def test_tenant_register():

    init_db()

    db = SessionLocal()

    try:
        svc = TenantService(db)

        tenant = svc.register("Provision Tenant")

        assert tenant is not None

    finally:
        db.close()
