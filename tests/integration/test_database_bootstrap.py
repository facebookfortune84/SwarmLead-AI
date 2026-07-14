"""
Integration Test

Verify database bootstrap creates tables.
"""

from sqlalchemy import inspect

from core.persistence.session import (
    engine,
    init_db,
)


def test_database_bootstrap():

    init_db()

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    assert len(tables) > 0


def test_leads_table_exists():

    init_db()

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    assert "leads" in tables


def test_usage_table_exists():

    init_db()

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    assert "usage_events" in tables
