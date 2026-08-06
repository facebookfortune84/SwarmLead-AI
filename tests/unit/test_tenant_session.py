"""Unit tests for tenant-scoped sessions (core.persistence.tenant_session)."""

import pytest
import sqlalchemy

from core.persistence.tenant_session import (
    _tenant_engines,
    get_tenant_engine,
    get_tenant_id_from_request,
    get_tenant_session,
)


@pytest.fixture(autouse=True)
def clear_engine_cache():
    _tenant_engines.clear()
    yield
    _tenant_engines.clear()


def test_get_tenant_engine_sqlite_caches(monkeypatch, tmp_path):
    db_path = tmp_path / "swarmlead.db"
    monkeypatch.setenv("SWARM_DB_URL", f"sqlite:///{db_path.as_posix()}")
    engine = get_tenant_engine("t1")
    assert engine is not None
    assert get_tenant_engine("t1") is engine


def test_get_tenant_session_yields_and_commits(monkeypatch, tmp_path):
    db_path = tmp_path / "swarmlead.db"
    monkeypatch.setenv("SWARM_DB_URL", f"sqlite:///{db_path.as_posix()}")
    with get_tenant_session("t1") as session:
        assert session is not None
        result = session.execute(sqlalchemy.text("SELECT 1")).scalar()
        assert result == 1


def test_get_tenant_session_rolls_back_on_error(monkeypatch, tmp_path):
    db_path = tmp_path / "swarmlead.db"
    monkeypatch.setenv("SWARM_DB_URL", f"sqlite:///{db_path.as_posix()}")
    with pytest.raises(RuntimeError):
        with get_tenant_session("t1") as session:
            session.execute(sqlalchemy.text("SELECT 1"))
            raise RuntimeError("boom")


def test_get_tenant_id_from_request_ok():
    request = type("Req", (), {"state": type("St", (), {"tenant_id": "t1"})()})()
    assert get_tenant_id_from_request(request) == "t1"


def test_get_tenant_id_from_request_missing():
    request = type("Req", (), {"state": type("St", (), {"tenant_id": None})()})()
    with pytest.raises(ValueError):
        get_tenant_id_from_request(request)
