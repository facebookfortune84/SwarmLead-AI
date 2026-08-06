"""Unit tests for the tenant context middleware (core.middleware.tenant_context)."""

from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from core.auth.agent_identity import (
    AgentDomain,
    AgentIdentity,
    AgentIdentityRegistry,
)
from core.middleware.tenant_context import (
    TenantContextMiddleware,
    get_agent_id,
    get_agent_identity,
    get_tenant_id,
    get_user_id,
    is_agent_request,
    require_agent_context,
    require_tenant_context,
)
from interfaces.api.auth.jwt_handler import create_access_token


@pytest.fixture
def app():
    application = FastAPI()

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    @application.get("/api/protected")
    async def protected(request: Request):
        return {
            "tenant_id": get_tenant_id(request),
            "agent_id": get_agent_id(request),
            "user_id": get_user_id(request),
            "is_agent": is_agent_request(request),
        }

    @application.get("/api/agent-only")
    async def agent_only(request: Request):
        identity = require_agent_context(request)
        return {"agent": identity.agent_id}

    @application.get("/api/tenant-only")
    async def tenant_only(request: Request):
        require_tenant_context(request)
        return {"ok": True}

    application.add_middleware(TenantContextMiddleware)
    return application


def _client(app, token=None, headers=None):
    client = TestClient(app)
    client.headers.update(headers or {})
    if token:
        client.headers.update({"Authorization": f"Bearer {token}"})
    return client


def test_public_path_skips_authentication(app):
    response = _client(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_auth_header_rejected(app):
    response = _client(app).get("/api/protected")
    assert response.status_code == 401


def test_malformed_auth_header_rejected(app):
    response = _client(app, headers={"Authorization": "Basic abc"}).get("/api/protected")
    assert response.status_code == 401


def test_invalid_token_rejected(app):
    response = _client(app, headers={"Authorization": "Bearer not.a.jwt"}).get("/api/protected")
    assert response.status_code == 401


def test_valid_human_token_attaches_tenant_context(app):
    token = create_access_token(
        data={"sub": "user_1", "tenant_id": "tenant_1", "scopes": ["read"]}
    )
    response = _client(app, token=token).get("/api/protected")
    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant_1"
    assert body["user_id"] == "user_1"
    assert body["is_agent"] is False


def test_token_without_tenant_id_rejected_for_human(app):
    token = create_access_token(data={"sub": "user_2"})
    response = _client(app, token=token).get("/api/protected")
    assert response.status_code == 401
    assert "tenant_id" in response.json()["detail"]


def test_agent_request_with_known_identity(app):
    AgentIdentityRegistry._identities = {}
    AgentIdentityRegistry.register(
        AgentIdentity(
            agent_id="strategy_agent",
            agent_type="StrategyAgent",
            display_name="Strategy Agent",
            domains={AgentDomain.SIMULATION},
            tool_allowlist={"*"},
            data_allowlist={"*"},
        )
    )
    token = create_access_token(data={"agent_id": "strategy_agent"})
    response = _client(app, token=token).get("/api/protected")
    assert response.status_code == 200
    body = response.json()
    assert body["agent_id"] == "strategy_agent"
    assert body["is_agent"] is True
    assert body["tenant_id"] is None


def test_agent_request_with_unknown_identity_rejected(app):
    token = create_access_token(data={"agent_id": "ghost_agent"})
    response = _client(app, token=token).get("/api/protected")
    assert response.status_code == 401
    assert "Unknown agent" in response.json()["detail"]


def test_agent_request_with_expired_identity_rejected(app):
    AgentIdentityRegistry._identities = {}
    AgentIdentityRegistry.register(
        AgentIdentity(
            agent_id="expired_agent",
            agent_type="ExpiredAgent",
            display_name="Expired",
            domains={AgentDomain.SIMULATION},
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
    )
    token = create_access_token(data={"agent_id": "expired_agent"})
    response = _client(app, token=token).get("/api/protected")
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_agent_context_required_endpoint(app):
    AgentIdentityRegistry._identities = {}
    AgentIdentityRegistry.register(
        AgentIdentity(
            agent_id="monitoring_agent",
            agent_type="MonitoringAgent",
            display_name="Monitoring",
            domains={AgentDomain.SIMULATION},
            tool_allowlist={"*"},
            data_allowlist={"*"},
        )
    )
    token = create_access_token(data={"agent_id": "monitoring_agent"})
    response = _client(app, token=token).get("/api/agent-only")
    assert response.status_code == 200
    assert response.json()["agent"] == "monitoring_agent"


def test_agent_context_required_without_identity_rejected(app):
    token = create_access_token(data={"agent_id": "nope"})
    response = _client(app, token=token).get("/api/agent-only")
    assert response.status_code == 401


def test_require_tenant_context_raises_without_state():
    request = Request({"type": "http", "method": "GET", "path": "/boom"})
    with pytest.raises(Exception):
        require_tenant_context(request)


def test_helpers_return_defaults_when_unset():
    request = Request({"type": "http", "method": "GET", "path": "/x"})
    assert get_agent_id(request) is None
    assert get_user_id(request) is None
    assert is_agent_request(request) is False
    assert get_agent_identity(request) is None
    with pytest.raises(Exception):
        get_tenant_id(request)


def test_require_tenant_context_passthrough_with_state():
    request = Request({"type": "http", "method": "GET", "path": "/x"})
    request.state.tenant_id = "tenant_9"
    assert require_tenant_context(request) == "tenant_9"
