"""Pure unit tests for TenantService using a throwaway sqlite engine.

Every test uses a fresh tmp_path sqlite database so nothing touches the real DB,
Docker, or the network. BoxDeployer methods and subprocess.run are mocked.
"""

import json
import subprocess
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import core.models  # noqa: F401  (register models on Base.metadata)
from core.models.tenant import CompanyTenant
from core.persistence.base import Base
from core.services.tenant_service import TenantService


@pytest.fixture
def session_factory(tmp_path, monkeypatch):
    db_path = tmp_path / "tenants.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr("core.persistence.session.SessionLocal", factory)
    monkeypatch.setattr("core.services.tenant_service.SessionLocal", factory)
    return factory


def _make_tenant(id="TEN-TEST", slug="acme", name="Acme", box_url=None):
    return CompanyTenant(
        id=id,
        slug=slug,
        name=name,
        subdomain=f"{slug}.realms2riches.tech",
        box_url=box_url or f"https://{slug}.realms2riches.tech",
    )


def _mock_deployer(service, deploy_result=None, box_status=None, hyperv=None, deploy_exc=None):
    deployer = Mock()
    if hyperv is not None:
        deployer.provision_hyperv_vm.return_value = hyperv
    if deploy_exc is not None:
        deployer.deploy_docker_box.side_effect = deploy_exc
    elif deploy_result is not None:
        deployer.deploy_docker_box.return_value = deploy_result
    if box_status is not None:
        deployer.box_status.return_value = box_status
    service.deployer = deployer
    return deployer


# --------------------------------------------------------------------------- #
# register
# --------------------------------------------------------------------------- #
def test_register_new_tenant_uses_provided_slug(session_factory, monkeypatch):
    monkeypatch.setenv("TECH_DOMAIN", "example.test")
    service = TenantService(db=session_factory())
    tenant = service.register(name="My Big Company", slug="my-co")

    assert tenant.id.startswith("TEN-")
    assert tenant.slug == "my-co"
    assert tenant.subdomain == "my-co.example.test"
    assert tenant.box_url == "https://my-co.example.test"
    assert tenant.status == "pending"


def test_register_without_slug_slugifies_name(session_factory):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Hello  World!!")

    assert tenant.slug == "hello-world"
    assert tenant.name == "Hello  World!!"


def test_register_existing_slug_returns_existing(session_factory):
    service = TenantService(db=session_factory())
    first = service.register(name="Acme", slug="acme")
    second = service.register(name="Acme Again", slug="acme")

    assert second.id == first.id
    assert second.name == "Acme"


def test_register_rolls_back_and_reraises_on_error(session_factory):
    session = session_factory()
    session.commit = Mock(side_effect=Exception("db error"))
    service = TenantService(db=session)

    with pytest.raises(Exception, match="db error"):
        service.register(name="Boom Co")


# --------------------------------------------------------------------------- #
# list_tenants
# --------------------------------------------------------------------------- #
def test_list_tenants_orders_by_created_at_desc(session_factory):
    session = session_factory()
    service = TenantService(db=session)
    now = datetime.utcnow()
    session.add_all(
        [
            _make_tenant("TEN-1", "one", "One", "https://one.test"),
            _make_tenant("TEN-2", "two", "Two", "https://two.test"),
            _make_tenant("TEN-3", "three", "Three", "https://three.test"),
        ]
    )
    for tenant, delta in zip(session.new, (timedelta(seconds=2), timedelta(seconds=1), timedelta(seconds=0))):
        tenant.created_at = now - delta
        tenant.updated_at = now
    session.commit()

    ids = [t.id for t in service.list_tenants()]

    assert ids == ["TEN-3", "TEN-2", "TEN-1"]


# --------------------------------------------------------------------------- #
# get
# --------------------------------------------------------------------------- #
def test_get_by_id_with_external_db(session_factory):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Get Co")

    assert service.get(tenant.id).id == tenant.id


def test_get_by_id_with_passed_session(session_factory):
    service = TenantService()
    session = session_factory()
    session.add(_make_tenant("TEN-9", "nine", "Nine", "https://nine.test"))
    session.commit()

    assert service.get("TEN-9", db=session).id == "TEN-9"


def test_get_by_id_with_internal_session(session_factory):
    service = TenantService()
    session = session_factory()
    session.add(_make_tenant("TEN-9", "nine", "Nine", "https://nine.test"))
    session.commit()
    session.close()

    assert service.get("TEN-9").id == "TEN-9"


def test_get_missing_returns_none(session_factory):
    service = TenantService(db=session_factory())

    assert service.get("TEN-NOPE") is None


# --------------------------------------------------------------------------- #
# close
# --------------------------------------------------------------------------- #
def test_close_closes_external_db(session_factory):
    session = session_factory()
    real_close = session.close
    session.close = Mock(wraps=real_close)
    service = TenantService(db=session)

    service.close()

    session.close.assert_called_once()


def test_close_without_external_db_is_noop():
    service = TenantService()

    service.close()


def test_close_survives_close_exception(session_factory):
    session = session_factory()
    session.close = Mock(side_effect=RuntimeError("boom"))
    service = TenantService(db=session)

    service.close()  # should swallow the exception and log a warning


# --------------------------------------------------------------------------- #
# session_scope
# --------------------------------------------------------------------------- #
def test_session_scope_external_yields_session_without_closing(session_factory):
    session = session_factory()
    service = TenantService(db=session)

    with service.session_scope() as yielded:
        assert yielded is session
    assert session.is_active is True


def test_session_scope_internal_creates_and_closes(session_factory):
    service = TenantService()
    captured = {}

    with service.session_scope() as yielded:
        yielded.add(_make_tenant("TEN-1", "one", "One", "https://one.test"))
        yielded.commit()
        captured["session"] = yielded
        real_close = yielded.close
        yielded.close = Mock(wraps=real_close)

    assert captured["session"] is not None
    captured["session"].close.assert_called_once()


# --------------------------------------------------------------------------- #
# _string_value
# --------------------------------------------------------------------------- #
def test_string_value_none_returns_empty():
    assert TenantService._string_value(None) == ""


def test_string_value_coerces_to_str():
    assert TenantService._string_value(123) == "123"
    assert TenantService._string_value("abc") == "abc"


# --------------------------------------------------------------------------- #
# _to_dict
# --------------------------------------------------------------------------- #
def test_to_dict_populated_row():
    service = TenantService()
    tenant = _make_tenant(
        "TEN-1", "acme", "Acme", "https://acme.realms2riches.tech"
    )
    tenant.status = "running"
    tenant.vm_id = "vm-1"
    tenant.container_id = "c1"
    tenant.last_error = None
    tenant.created_at = datetime(2024, 1, 1, 12, 30, 0)
    tenant.updated_at = datetime(2024, 1, 2, 8, 0, 0)

    d = service._to_dict(tenant)

    assert d["id"] == "TEN-1"
    assert d["slug"] == "acme"
    assert d["name"] == "Acme"
    assert d["status"] == "running"
    assert d["vm_id"] == "vm-1"
    assert d["container_id"] == "c1"
    assert d["box_url"] == "https://acme.realms2riches.tech"
    assert d["last_error"] is None
    assert d["created_at"] == "2024-01-01T12:30:00"
    assert d["updated_at"] == "2024-01-02T08:00:00"


def test_to_dict_none_returns_none():
    service = TenantService()

    assert service._to_dict(None) is None


def test_to_dict_missing_timestamps():
    service = TenantService()
    tenant = _make_tenant("TEN-1", "acme", "Acme", "https://acme.test")

    d = service._to_dict(tenant)

    assert d["created_at"] is None
    assert d["updated_at"] is None


# --------------------------------------------------------------------------- #
# _deploy_docker_fallback
# --------------------------------------------------------------------------- #
def test_deploy_docker_fallback_success(monkeypatch, session_factory):
    service = TenantService(db=session_factory())
    tenant = _make_tenant("TEN-1", "acme", "Acme", "https://acme.test")
    result = Mock(returncode=0, stdout="a1b2c3d4e5f6deadbeef\n", stderr="")
    monkeypatch.setattr(subprocess, "run", Mock(return_value=result))

    out = service._deploy_docker_fallback(tenant)

    assert out == {
        "status": "running",
        "container_id": "a1b2c3d4e5f6",
        "box_url": tenant.box_url,
    }


def test_deploy_docker_fallback_existing_container_starts(monkeypatch, session_factory):
    service = TenantService(db=session_factory())
    tenant = _make_tenant("TEN-1", "acme", "Acme", "https://acme.test")
    run_result = Mock(returncode=1, stdout="", stderr="Conflict")
    start_result = Mock(returncode=0, stdout="", stderr="")
    inspect_result = Mock(returncode=0, stdout="deadbeefdeadbeefcafe\n", stderr="")
    monkeypatch.setattr(
        subprocess, "run", Mock(side_effect=[run_result, start_result, inspect_result])
    )

    out = service._deploy_docker_fallback(tenant)

    assert out == {
        "status": "running",
        "container_id": "deadbeefdead",
        "box_url": tenant.box_url,
    }


def test_deploy_docker_fallback_failed(monkeypatch, session_factory):
    service = TenantService(db=session_factory())
    tenant = _make_tenant("TEN-1", "acme", "Acme", "https://acme.test")
    run_result = Mock(returncode=1, stdout="", stderr="cannot create")
    start_result = Mock(returncode=1, stdout="", stderr="cannot start")
    monkeypatch.setattr(
        subprocess, "run", Mock(side_effect=[run_result, start_result])
    )

    out = service._deploy_docker_fallback(tenant)

    assert out == {"status": "failed", "error": "cannot create"}


def test_deploy_docker_fallback_cli_missing(monkeypatch, session_factory):
    service = TenantService(db=session_factory())
    tenant = _make_tenant("TEN-1", "acme", "Acme", "https://acme.test")
    monkeypatch.setattr(subprocess, "run", Mock(side_effect=FileNotFoundError()))

    out = service._deploy_docker_fallback(tenant)

    assert out == {"status": "failed", "error": "Docker CLI not available"}


def test_deploy_docker_fallback_timeout(monkeypatch, session_factory):
    service = TenantService(db=session_factory())
    tenant = _make_tenant("TEN-1", "acme", "Acme", "https://acme.test")
    monkeypatch.setattr(
        subprocess, "run", Mock(side_effect=subprocess.TimeoutExpired("docker run", 60))
    )

    out = service._deploy_docker_fallback(tenant)

    assert out == {"status": "failed", "error": "Docker command timed out"}


# --------------------------------------------------------------------------- #
# provision
# --------------------------------------------------------------------------- #
def test_provision_unknown_tenant_raises_valueerror(session_factory):
    service = TenantService(db=session_factory())

    with pytest.raises(ValueError, match="tenant not found"):
        service.provision("TEN-NOPE")


def test_provision_vm_path_success(session_factory):
    service = TenantService(db=session_factory())
    tenant = service.register(name="VM Co", slug="vm-co")
    deployer = _mock_deployer(
        service,
        hyperv={"status": "submitted", "vm_name": "r2r-vm-co"},
        deploy_result={
            "status": "running",
            "container_id": "deadbeef",
            "box_url": "https://vm-co.realms2riches.tech",
        },
    )

    out = service.provision(tenant.id, use_vm=True)

    assert out.status == "running"
    assert out.container_id == "deadbeef"
    assert out.box_url == "https://vm-co.realms2riches.tech"
    deployer.provision_hyperv_vm.assert_called_once_with(tenant.id, "r2r-vm-co")
    meta = json.loads(out.metadata_json)
    assert meta["vm"]["status"] == "submitted"
    assert meta["docker"]["status"] == "running"


def test_provision_deployer_success(session_factory):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Box Co", slug="box-co")
    deployer = _mock_deployer(
        service,
        deploy_result={
            "status": "running",
            "container_id": "deadbeef",
            "box_url": "https://box-co.realms2riches.tech",
        },
    )

    out = service.provision(tenant.id)

    assert out.status == "running"
    assert out.container_id == "deadbeef"
    assert out.box_url == "https://box-co.realms2riches.tech"
    deployer.provision_hyperv_vm.assert_not_called()


def test_provision_deployer_failure_falls_back_to_docker(session_factory, monkeypatch):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Fallback Co", slug="fallback-co")
    _mock_deployer(service, deploy_exc=RuntimeError("docker down"))
    fallback = Mock(
        return_value={
            "status": "running",
            "container_id": "f4llb4ck",
            "box_url": "https://fallback-co.realms2riches.tech",
        }
    )
    monkeypatch.setattr(service, "_deploy_docker_fallback", fallback)

    out = service.provision(tenant.id)

    assert out.status == "running"
    assert out.container_id == "f4llb4ck"
    assert out.box_url == "https://fallback-co.realms2riches.tech"
    fallback.assert_called_once_with(tenant)


def test_provision_fallback_running_uses_default_box_url(session_factory, monkeypatch):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Default URL Co", slug="default-url")
    _mock_deployer(service, deploy_exc=RuntimeError("docker down"))
    monkeypatch.setattr(
        service,
        "_deploy_docker_fallback",
        Mock(return_value={"status": "running", "container_id": "abc123"}),
    )

    out = service.provision(tenant.id)

    assert out.status == "running"
    assert out.container_id == "abc123"
    assert out.box_url == tenant.box_url


@pytest.mark.parametrize(
    "fallback_result",
    [
        {"status": "failed", "error": "Docker CLI not available"},
        {"status": "failed", "error": "Docker command timed out"},
        {"status": "failed", "error": "generic failure"},
    ],
)
def test_provision_fallback_failure_outcomes(session_factory, monkeypatch, fallback_result):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Failed Co", slug="failed-co")
    _mock_deployer(service, deploy_exc=RuntimeError("docker down"))
    monkeypatch.setattr(service, "_deploy_docker_fallback", Mock(return_value=fallback_result))

    out = service.provision(tenant.id)

    assert out.status == "failed"
    assert out.last_error == fallback_result["error"]


def test_provision_exception_marks_failed_and_reraises(session_factory, monkeypatch):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Boom Co", slug="boom-co")
    _mock_deployer(service, deploy_exc=RuntimeError("deploy down"))
    monkeypatch.setattr(
        service, "_deploy_docker_fallback", Mock(side_effect=RuntimeError("fallback boom"))
    )

    with pytest.raises(RuntimeError, match="fallback boom"):
        service.provision(tenant.id)

    reloaded = service.get(tenant.id)
    assert reloaded.status == "failed"
    assert reloaded.last_error == "fallback boom"


# --------------------------------------------------------------------------- #
# refresh_status
# --------------------------------------------------------------------------- #
def test_refresh_status_unknown_tenant_returns_none(session_factory):
    service = TenantService(db=session_factory())

    assert service.refresh_status("TEN-NOPE") is None


def test_refresh_status_running(session_factory):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Status Co", slug="status-co")
    _mock_deployer(service, box_status={"status": "running"})

    out = service.refresh_status(tenant.id)

    assert out.status == "running"


@pytest.mark.parametrize("docker_status", ["exited", "dead"])
def test_refresh_status_exited_or_dead(session_factory, docker_status):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Status Co", slug="status-co")
    _mock_deployer(service, box_status={"status": docker_status})

    out = service.refresh_status(tenant.id)

    assert out.status == "failed"
    assert out.last_error == f"container {docker_status}"


def test_refresh_status_unknown_status_unchanged(session_factory):
    service = TenantService(db=session_factory())
    tenant = service.register(name="Status Co", slug="status-co")
    _mock_deployer(service, box_status={"status": "paused"})

    out = service.refresh_status(tenant.id)

    assert out.status == "pending"
    assert out.last_error is None
