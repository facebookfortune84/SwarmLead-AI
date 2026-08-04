"""
Extra Health Dashboard Tests

Covers router handlers and HealthDashboard class methods in
core/monitoring/health_dashboard.py, including healthy, degraded,
unhealthy, and error-handling branches. No real DB/Redis/network.

Run with:
    pytest tests/unit/test_health_dashboard_extra.py -v
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import HTTPException
from fastapi.responses import Response

from core.monitoring.health_dashboard import (
    HealthDashboard,
    HealthResponse,
    HealthStatus,
    ReadinessResponse,
    detailed_health,
    health_check,
    metrics,
    readiness_check,
    version,
)

REQUIRED_AGENTS = [
    "strategy_agent",
    "outreach_agent",
    "builder_agent",
    "repair_agent",
    "review_agent",
    "governance_agent",
    "audit_agent",
    "monitoring_agent",
]


def _full_agent_dict():
    return {name: Mock() for name in REQUIRED_AGENTS}


def _async_client_mock(status_code=200, json_data=None, error=None):
    """Return a mock usable as `async with httpx.AsyncClient() as client:`."""
    client = Mock()
    if error is not None:
        client.get = AsyncMock(side_effect=error)
    else:
        resp = Mock()
        resp.status_code = status_code
        resp.json.return_value = json_data if json_data is not None else {}
        client.get = AsyncMock(return_value=resp)
    ctx = Mock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


def _redis_client_mock(ping_error=None, close_error=None):
    client = Mock()
    if ping_error is not None:
        client.ping = AsyncMock(side_effect=ping_error)
    else:
        client.ping = AsyncMock(return_value=True)
    if close_error is not None:
        client.close = AsyncMock(side_effect=close_error)
    else:
        client.close = AsyncMock()
    return client


class TestModelsAndEnum:
    def test_health_status_values(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"

    def test_health_response_model(self):
        model = HealthResponse(
            status="healthy",
            timestamp="2026-08-01T00:00:00Z",
            version="1.0.0",
            checks={"process": "running"},
        )
        assert model.status == "healthy"
        assert model.timestamp == "2026-08-01T00:00:00Z"
        assert model.version == "1.0.0"
        assert model.checks == {"process": "running"}
        assert "timestamp" in model.model_dump()

    def test_readiness_response_model(self):
        model = ReadinessResponse(
            ready=True,
            timestamp="2026-08-01T00:00:00Z",
            checks={"database": {"status": "healthy"}},
        )
        assert model.ready is True
        assert model.timestamp == "2026-08-01T00:00:00Z"
        assert model.checks == {"database": {"status": "healthy"}}
        dump = model.model_dump()
        assert dump["ready"] is True


class TestRouterHandlers:
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        result = await health_check()
        assert isinstance(result, HealthResponse)
        assert result.status == "healthy"
        assert result.version == "1.0.0"
        assert result.timestamp.endswith("Z")
        assert result.checks["process"] == "running"

    @pytest.mark.asyncio
    async def test_version_endpoint(self):
        result = await version()
        assert result["version"] == "1.0.0"
        assert result["build"] == "genesis-v1.0.0"
        assert result["constitution_version"] == "1.0"
        assert result["build_date"] == "2026-07-26"

    @pytest.mark.asyncio
    @patch("core.monitoring.health_dashboard.get_metrics")
    async def test_metrics_endpoint(self, mock_get_metrics):
        mock_get_metrics.return_value = b"# HELP test\n"
        result = await metrics()
        assert isinstance(result, Response)
        assert result.body == b"# HELP test\n"
        assert result.media_type == "text/plain"
        mock_get_metrics.assert_called_once()


class TestReadinessCheck:
    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    @patch("configs.config_loader.ConfigLoader.load")
    @patch("core.orchestration.agent_manager.agent_manager")
    @patch("redis.asyncio.from_url")
    async def test_readiness_all_healthy(
        self, mock_from_url, mock_agent_manager, mock_config_load, mock_async_client
    ):
        mock_db = Mock()
        mock_db.execute = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = _full_agent_dict()
        mock_config_load.return_value = Mock()
        mock_async_client.return_value = _async_client_mock(status_code=200)
        mock_from_url.return_value = _redis_client_mock()

        result = await readiness_check(mock_db)

        assert isinstance(result, ReadinessResponse)
        assert result.ready is True
        assert result.checks["database"]["status"] == "healthy"
        assert result.checks["redis"]["status"] == "healthy"
        assert result.checks["agents"]["status"] == "healthy"
        assert result.checks["agents"]["count"] == len(REQUIRED_AGENTS)
        assert result.checks["config"]["status"] == "valid"
        assert result.checks["ollama"]["status"] == "healthy"
        mock_db.execute.assert_called_once()
        mock_from_url.return_value.ping.assert_awaited_once()
        mock_from_url.return_value.close.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("core.orchestration.agent_manager.agent_manager")
    async def test_readiness_db_failure_raises_503(self, mock_agent_manager):
        mock_db = Mock()
        mock_db.execute = AsyncMock(side_effect=RuntimeError("db down"))
        mock_agent_manager.get_all_agents.return_value = _full_agent_dict()

        with pytest.raises(HTTPException) as exc_info:
            await readiness_check(mock_db)

        assert exc_info.value.status_code == 503
        detail = exc_info.value.detail
        assert detail["ready"] is False
        assert detail["checks"]["database"]["status"] == "unhealthy"
        assert "db down" in detail["checks"]["database"]["error"]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    @patch("configs.config_loader.ConfigLoader.load")
    @patch("core.orchestration.agent_manager.agent_manager")
    @patch("redis.asyncio.from_url")
    async def test_readiness_redis_failure_raises_503(
        self, mock_from_url, mock_agent_manager, mock_config_load, mock_async_client
    ):
        mock_db = Mock()
        mock_db.execute = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = _full_agent_dict()
        mock_config_load.return_value = Mock()
        mock_async_client.return_value = _async_client_mock(status_code=200)
        mock_from_url.return_value = _redis_client_mock(
            ping_error=ConnectionError("redis refused")
        )

        with pytest.raises(HTTPException) as exc_info:
            await readiness_check(mock_db)

        assert exc_info.value.status_code == 503
        detail = exc_info.value.detail
        assert detail["ready"] is False
        assert detail["checks"]["redis"]["status"] == "unhealthy"
        assert "redis refused" in detail["checks"]["redis"]["error"]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    @patch("configs.config_loader.ConfigLoader.load")
    @patch("core.orchestration.agent_manager.agent_manager")
    @patch("redis.asyncio.from_url")
    async def test_readiness_missing_agents_raises_503(
        self, mock_from_url, mock_agent_manager, mock_config_load, mock_async_client
    ):
        mock_db = Mock()
        mock_db.execute = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = {
            "strategy_agent": Mock(),
            "outreach_agent": Mock(),
        }
        mock_config_load.return_value = Mock()
        mock_async_client.return_value = _async_client_mock(status_code=200)
        mock_from_url.return_value = _redis_client_mock()

        with pytest.raises(HTTPException) as exc_info:
            await readiness_check(mock_db)

        assert exc_info.value.status_code == 503
        detail = exc_info.value.detail
        assert detail["ready"] is False
        assert detail["checks"]["agents"]["status"] == "degraded"
        assert "repair_agent" in detail["checks"]["agents"]["missing"]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    @patch("configs.config_loader.ConfigLoader.load")
    @patch("core.orchestration.agent_manager.agent_manager")
    @patch("redis.asyncio.from_url")
    async def test_readiness_config_failure_raises_503(
        self, mock_from_url, mock_agent_manager, mock_config_load, mock_async_client
    ):
        mock_db = Mock()
        mock_db.execute = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = _full_agent_dict()
        mock_config_load.side_effect = RuntimeError("bad config")
        mock_async_client.return_value = _async_client_mock(status_code=200)
        mock_from_url.return_value = _redis_client_mock()

        with pytest.raises(HTTPException) as exc_info:
            await readiness_check(mock_db)

        assert exc_info.value.status_code == 503
        detail = exc_info.value.detail
        assert detail["ready"] is False
        assert detail["checks"]["config"]["status"] == "invalid"
        assert "bad config" in detail["checks"]["config"]["error"]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    @patch("configs.config_loader.ConfigLoader.load")
    @patch("core.orchestration.agent_manager.agent_manager")
    @patch("redis.asyncio.from_url")
    async def test_readiness_ollama_non_200_degraded_still_ready(
        self, mock_from_url, mock_agent_manager, mock_config_load, mock_async_client
    ):
        mock_db = Mock()
        mock_db.execute = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = _full_agent_dict()
        mock_config_load.return_value = Mock()
        mock_from_url.return_value = _redis_client_mock()
        mock_async_client.return_value = _async_client_mock(status_code=500)

        result = await readiness_check(mock_db)

        assert result.ready is True
        assert result.checks["ollama"]["status"] == "degraded"
        assert result.checks["ollama"]["status_code"] == 500

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    @patch("configs.config_loader.ConfigLoader.load")
    @patch("core.orchestration.agent_manager.agent_manager")
    @patch("redis.asyncio.from_url")
    async def test_readiness_ollama_error_still_ready(
        self, mock_from_url, mock_agent_manager, mock_config_load, mock_async_client
    ):
        mock_db = Mock()
        mock_db.execute = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = _full_agent_dict()
        mock_config_load.return_value = Mock()
        mock_from_url.return_value = _redis_client_mock()
        mock_async_client.return_value = _async_client_mock(
            error=ConnectionError("no ollama")
        )

        result = await readiness_check(mock_db)

        assert result.ready is True
        assert result.checks["ollama"]["status"] == "unhealthy"
        assert "no ollama" in result.checks["ollama"]["error"]


class TestDetailedHealth:
    @pytest.mark.asyncio
    @patch("core.orchestration.agent_manager.agent_manager")
    async def test_detailed_health_db_success(self, mock_agent_manager):
        mock_result = Mock()
        mock_result.scalar.side_effect = ["PostgreSQL 15", 4]
        mock_db = Mock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_agent_manager.get_all_agents.return_value = {
            "strategy_agent": Mock(),
            "outreach_agent": Mock(),
        }

        result = await detailed_health(mock_db)

        assert result["database"]["version"] == "PostgreSQL 15"
        assert result["database"]["connections"] == 4
        assert result["agents"]["strategy_agent"]["registered"] is True
        assert result["agents"]["strategy_agent"]["type"] == "Mock"
        assert "system" in result
        assert "cpu_percent" in result["system"]
        assert "memory_percent" in result["system"]
        assert "process_memory_mb" in result["system"]
        assert "process_cpu_percent" in result["system"]
        assert "uptime_seconds" in result
        assert result["timestamp"].endswith("Z")

    @pytest.mark.asyncio
    @patch("core.orchestration.agent_manager.agent_manager")
    async def test_detailed_health_db_failure(self, mock_agent_manager):
        mock_db = Mock()
        mock_db.execute = AsyncMock(side_effect=RuntimeError("query failed"))
        mock_agent_manager.get_all_agents.return_value = {}

        result = await detailed_health(mock_db)

        assert "error" in result["database"]
        assert "query failed" in result["database"]["error"]
        assert "version" not in result["database"]
        assert result["agents"] == {}


class TestHealthDashboardChecks:
    def test_init_registers_default_checks(self):
        dashboard = HealthDashboard()
        assert set(dashboard._checks.keys()) == {
            "database",
            "redis",
            "memory",
            "disk",
            "llm",
        }
        assert isinstance(dashboard.start_time, datetime)

    def test_register_check(self):
        dashboard = HealthDashboard()
        fake = Mock()
        dashboard.register_check("custom", fake)
        assert dashboard._checks["custom"] is fake

    @pytest.mark.asyncio
    @patch("core.persistence.session.SessionLocal")
    async def test_check_database_healthy(self, mock_session_local):
        mock_session = Mock()
        mock_result = Mock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result
        mock_session_local.return_value = mock_session

        result = await HealthDashboard()._check_database()

        assert result["status"] == "healthy"
        assert "latency_ms" in result
        assert "PostgreSQL responsive" in result["message"]
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    @patch("core.persistence.session.SessionLocal")
    async def test_check_database_unhealthy(self, mock_session_local):
        mock_session = Mock()
        mock_session.execute.side_effect = RuntimeError("connection refused")
        mock_session_local.return_value = mock_session

        result = await HealthDashboard()._check_database()

        assert result["status"] == "unhealthy"
        assert result["latency_ms"] == 0
        assert "Database error" in result["message"]
        assert "connection refused" in result["message"]

    @pytest.mark.asyncio
    @patch("redis.asyncio.from_url")
    async def test_check_redis_healthy(self, mock_from_url):
        client = _redis_client_mock()
        mock_from_url.return_value = client

        result = await HealthDashboard()._check_redis()

        assert result["status"] == "healthy"
        assert "latency_ms" in result
        assert "Redis responsive" in result["message"]
        client.ping.assert_awaited_once()
        client.close.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("redis.asyncio.from_url")
    async def test_check_redis_unhealthy(self, mock_from_url):
        mock_from_url.return_value = _redis_client_mock(
            ping_error=ConnectionError("redis down")
        )

        result = await HealthDashboard()._check_redis()

        assert result["status"] == "unhealthy"
        assert result["latency_ms"] == 0
        assert "Redis error" in result["message"]
        assert "redis down" in result["message"]

    @pytest.mark.asyncio
    @patch("psutil.virtual_memory")
    async def test_check_memory_healthy(self, mock_vm):
        mock_vm.return_value = Mock(percent=30.0, available=8e9)

        result = await HealthDashboard()._check_memory()

        assert result["status"] == "healthy"
        assert "Memory usage" in result["message"]
        assert result["details"]["percent"] == 30.0
        assert result["details"]["available_gb"] == 8.0

    @pytest.mark.asyncio
    @patch("psutil.virtual_memory")
    async def test_check_memory_degraded(self, mock_vm):
        mock_vm.return_value = Mock(percent=85.0, available=1e9)

        result = await HealthDashboard()._check_memory()

        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    @patch("psutil.virtual_memory")
    async def test_check_memory_unhealthy(self, mock_vm):
        mock_vm.return_value = Mock(percent=95.0, available=1e8)

        result = await HealthDashboard()._check_memory()

        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    @patch("psutil.disk_usage")
    async def test_check_disk_healthy(self, mock_disk_usage):
        mock_disk_usage.return_value = Mock(used=50e9, total=100e9, free=50e9)

        result = await HealthDashboard()._check_disk()

        assert result["status"] == "healthy"
        assert "Disk usage" in result["message"]
        assert result["details"]["free_gb"] == 50.0

    @pytest.mark.asyncio
    @patch("psutil.disk_usage")
    async def test_check_disk_degraded(self, mock_disk_usage):
        mock_disk_usage.return_value = Mock(used=90e9, total=100e9, free=10e9)

        result = await HealthDashboard()._check_disk()

        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    @patch("psutil.disk_usage")
    async def test_check_disk_unhealthy(self, mock_disk_usage):
        mock_disk_usage.return_value = Mock(used=97e9, total=100e9, free=3e9)

        result = await HealthDashboard()._check_disk()

        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_check_llm_healthy(self, mock_async_client):
        mock_async_client.return_value = _async_client_mock(
            status_code=200, json_data={"models": [{"name": "llama3"}, {"name": "mistral"}]}
        )

        result = await HealthDashboard()._check_llm()

        assert result["status"] == "healthy"
        assert "latency_ms" in result
        assert "Ollama available with 2 models" in result["message"]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_check_llm_degraded(self, mock_async_client):
        mock_async_client.return_value = _async_client_mock(status_code=404)

        result = await HealthDashboard()._check_llm()

        assert result["status"] == "degraded"
        assert "Ollama status: 404" in result["message"]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_check_llm_unhealthy(self, mock_async_client):
        mock_async_client.return_value = _async_client_mock(
            error=ConnectionError("cannot reach ollama")
        )

        result = await HealthDashboard()._check_llm()

        assert result["status"] == "unhealthy"
        assert result["latency_ms"] == 0
        assert "Ollama error" in result["message"]
        assert "cannot reach ollama" in result["message"]


class TestHealthDashboardAggregate:
    @pytest.mark.asyncio
    async def test_run_checks_aggregates_results(self):
        dashboard = HealthDashboard()
        dashboard._checks.clear()

        async def healthy():
            return {"status": "healthy"}

        async def degraded():
            return {"status": "degraded"}

        dashboard.register_check("a", healthy)
        dashboard.register_check("b", degraded)

        results = await dashboard.run_checks()

        assert results["a"] == {"status": "healthy"}
        assert results["b"] == {"status": "degraded"}
        assert dashboard.checks == results

    @pytest.mark.asyncio
    async def test_run_checks_catches_exceptions(self):
        dashboard = HealthDashboard()
        dashboard._checks.clear()

        async def boom():
            raise RuntimeError("boom")

        dashboard.register_check("broken", boom)

        results = await dashboard.run_checks()

        assert results["broken"]["status"] == "unhealthy"
        assert "boom" in results["broken"]["message"]

    @pytest.mark.asyncio
    async def test_check_health_healthy(self):
        dashboard = HealthDashboard()
        dashboard._checks.clear()

        async def healthy():
            return {"status": "healthy"}

        dashboard.register_check("a", healthy)

        result = await dashboard.check_health()

        assert result["status"] == "healthy"
        assert result["timestamp"].endswith("Z")
        assert "checks" not in result

    @pytest.mark.asyncio
    async def test_check_health_degraded(self):
        dashboard = HealthDashboard()
        dashboard._checks.clear()

        async def healthy():
            return {"status": "healthy"}

        async def degraded():
            return {"status": "degraded"}

        dashboard.register_check("a", healthy)
        dashboard.register_check("b", degraded)

        result = await dashboard.check_health()

        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_check_health_unhealthy(self):
        dashboard = HealthDashboard()
        dashboard._checks.clear()

        async def unhealthy():
            return {"status": "unhealthy"}

        async def degraded():
            return {"status": "degraded"}

        dashboard.register_check("a", unhealthy)
        dashboard.register_check("b", degraded)

        result = await dashboard.check_health()

        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_check_health_detailed_includes_checks(self):
        dashboard = HealthDashboard()
        dashboard._checks.clear()

        async def healthy():
            return {"status": "healthy"}

        dashboard.register_check("a", healthy)

        result = await dashboard.check_health(detailed=True)

        assert result["status"] == "healthy"
        assert result["checks"] == {"a": {"status": "healthy"}}

    def test_get_status_unknown_without_checks(self):
        dashboard = HealthDashboard()
        status = dashboard.get_status()

        assert status == {"overall": "unknown", "checks": {}}

    def test_get_status_healthy_after_checks(self):
        dashboard = HealthDashboard()
        dashboard.checks = {
            "database": {"status": "healthy"},
            "redis": {"status": "healthy"},
        }

        status = dashboard.get_status()

        assert status["overall"] == "healthy"
        assert status["checks"] == dashboard.checks

    def test_get_status_degraded(self):
        dashboard = HealthDashboard()
        dashboard.checks = {
            "database": {"status": "healthy"},
            "llm": {"status": "degraded"},
        }

        status = dashboard.get_status()

        assert status["overall"] == "degraded"

    def test_get_status_unhealthy(self):
        dashboard = HealthDashboard()
        dashboard.checks = {
            "database": {"status": "unhealthy"},
            "llm": {"status": "degraded"},
        }

        status = dashboard.get_status()

        assert status["overall"] == "unhealthy"
