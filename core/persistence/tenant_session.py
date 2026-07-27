"""
Tenant-scoped database session management with RLS.
Constitutional §4.6: Portfolio isolation.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from core.persistence.session import get_db_url

# Cache for tenant-specific engines
_tenant_engines: dict = {}


def get_tenant_engine(tenant_id: str):
    """Get or create tenant-scoped database engine."""
    if tenant_id in _tenant_engines:
        return _tenant_engines[tenant_id]

    # Get base URL
    base_url = get_db_url()

    # For PostgreSQL, use schema-based isolation
    if base_url.startswith("postgresql"):
        tenant_url = base_url
        engine = create_engine(
            tenant_url,
            poolclass=None,  # Use default pool
            connect_args={"options": f"-c search_path=tenant_{tenant_id},public"},
        )

        # Set up RLS context on connect
        @event.listens_for(engine, "connect")
        def set_tenant_context(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute(f"SET LOCAL app.current_tenant = '{tenant_id}'")
            cursor.close()

    else:
        # SQLite - use separate file per tenant
        import os

        base_url = get_db_url()
        if base_url.startswith("sqlite:///"):
            db_dir = os.path.dirname(base_url.replace("sqlite:///", ""))
        else:
            db_dir = os.path.dirname(base_url.replace("sqlite:///", ""))
        tenant_db = os.path.join(db_dir, f"swarmlead_{tenant_id}.db")
        tenant_url = f"sqlite:///{tenant_db}"
        engine = create_engine(tenant_url, connect_args={"check_same_thread": False})

    _tenant_engines[tenant_id] = engine
    return engine


@contextmanager
def get_tenant_session(tenant_id: str) -> Generator[Session, None, None]:
    """Get tenant-scoped database session."""
    engine = get_tenant_engine(tenant_id)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    try:
        # Set tenant context for RLS
        session.execute(text(f"SET LOCAL app.current_tenant = '{tenant_id}'"))
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_tenant_id_from_request(request) -> str:
    """Extract tenant_id from request state (set by middleware)."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise ValueError("Tenant context not initialized. Middleware required.")
    return tenant_id
