import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.monitoring.system_monitor import (  # noqa: E402
    HealthCheck,
    HealthStatus,
    SystemMonitor,
)


class FakeClock:
    now = datetime(2024, 1, 1, 0, 0, 0)

    @classmethod
    def advance(cls, seconds):
        cls.now = cls.now + timedelta(seconds=seconds)

    @classmethod
    def reset(cls):
        cls.now = datetime(2024, 1, 1, 0, 0, 0)

    @classmethod
    def utcnow(cls):
        return cls.now


class FakeMem:
    def __init__(self, percent, available):
        self.percent = percent
        self.available = available


class FakeDisk:
    def __init__(self, used, total, free):
        self.used = used
        self.total = total
        self.free = free


def patch_clock(monkeypatch):
    monkeypatch.setattr("core.monitoring.system_monitor.datetime", FakeClock)
    FakeClock.reset()


# ------------------------------------------------------------------
# HealthStatus enum + HealthCheck dataclass
# ------------------------------------------------------------------


def test_health_status_values():
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.DEGRADED.value == "degraded"
    assert HealthStatus.UNHEALTHY.value == "unhealthy"


def test_health_check_defaults():
    check = HealthCheck("cpu", HealthStatus.HEALTHY, "ok")
    assert check.latency_ms == 0.0
    assert check.details == {}
    assert check.timestamp is not None


# ------------------------------------------------------------------
# _check_cpu
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_cpu_normal(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda interval: 40)
    check = await SystemMonitor()._check_cpu()
    assert check.name == "cpu"
    assert check.status == HealthStatus.HEALTHY
    assert "normal" in check.message
    assert check.details["percent"] == 40


@pytest.mark.asyncio
async def test_check_cpu_degraded(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda interval: 80)
    check = await SystemMonitor()._check_cpu()
    assert check.status == HealthStatus.DEGRADED
    assert "High CPU" in check.message


@pytest.mark.asyncio
async def test_check_cpu_unhealthy(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda interval: 95)
    check = await SystemMonitor()._check_cpu()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Critical CPU" in check.message


@pytest.mark.asyncio
async def test_check_cpu_boundary_70(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda interval: 70)
    check = await SystemMonitor()._check_cpu()
    assert check.status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_check_cpu_boundary_90(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda interval: 90)
    check = await SystemMonitor()._check_cpu()
    assert check.status == HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_check_cpu_latency(monkeypatch):
    patch_clock(monkeypatch)

    def cpu_advance(interval):
        FakeClock.advance(1.5)
        return 10

    monkeypatch.setattr("psutil.cpu_percent", cpu_advance)
    check = await SystemMonitor()._check_cpu()
    assert check.latency_ms == 1500.0


# ------------------------------------------------------------------
# _check_memory
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_memory_normal(monkeypatch):
    monkeypatch.setattr("psutil.virtual_memory", lambda: FakeMem(50, 10e9))
    check = await SystemMonitor()._check_memory()
    assert check.status == HealthStatus.HEALTHY
    assert "normal" in check.message
    assert check.details["available_gb"] == 10.0


@pytest.mark.asyncio
async def test_check_memory_degraded(monkeypatch):
    monkeypatch.setattr("psutil.virtual_memory", lambda: FakeMem(85, 10e9))
    check = await SystemMonitor()._check_memory()
    assert check.status == HealthStatus.DEGRADED
    assert "High memory" in check.message


@pytest.mark.asyncio
async def test_check_memory_unhealthy(monkeypatch):
    monkeypatch.setattr("psutil.virtual_memory", lambda: FakeMem(95, 10e9))
    check = await SystemMonitor()._check_memory()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Critical memory" in check.message


@pytest.mark.asyncio
async def test_check_memory_boundary_80(monkeypatch):
    monkeypatch.setattr("psutil.virtual_memory", lambda: FakeMem(80, 10e9))
    check = await SystemMonitor()._check_memory()
    assert check.status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_check_memory_boundary_90(monkeypatch):
    monkeypatch.setattr("psutil.virtual_memory", lambda: FakeMem(90, 10e9))
    check = await SystemMonitor()._check_memory()
    assert check.status == HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_check_memory_latency(monkeypatch):
    patch_clock(monkeypatch)

    def mem_advance():
        FakeClock.advance(0.25)
        return FakeMem(30, 10e9)

    monkeypatch.setattr("psutil.virtual_memory", mem_advance)
    check = await SystemMonitor()._check_memory()
    assert check.latency_ms == 250.0


# ------------------------------------------------------------------
# _check_disk
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_disk_normal(monkeypatch):
    monkeypatch.setattr("psutil.disk_usage", lambda path: FakeDisk(50, 100, 50))
    check = await SystemMonitor()._check_disk()
    assert check.status == HealthStatus.HEALTHY
    assert "normal" in check.message
    assert check.details["percent"] == 50.0
    assert check.details["free_gb"] == 5e-08


@pytest.mark.asyncio
async def test_check_disk_degraded(monkeypatch):
    monkeypatch.setattr("psutil.disk_usage", lambda path: FakeDisk(90, 100, 10))
    check = await SystemMonitor()._check_disk()
    assert check.status == HealthStatus.DEGRADED
    assert "High disk" in check.message


@pytest.mark.asyncio
async def test_check_disk_unhealthy(monkeypatch):
    monkeypatch.setattr("psutil.disk_usage", lambda path: FakeDisk(97, 100, 3))
    check = await SystemMonitor()._check_disk()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Critical disk" in check.message


@pytest.mark.asyncio
async def test_check_disk_boundary_85(monkeypatch):
    monkeypatch.setattr("psutil.disk_usage", lambda path: FakeDisk(85, 100, 15))
    check = await SystemMonitor()._check_disk()
    assert check.status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_check_disk_boundary_95(monkeypatch):
    monkeypatch.setattr("psutil.disk_usage", lambda path: FakeDisk(95, 100, 5))
    check = await SystemMonitor()._check_disk()
    assert check.status == HealthStatus.DEGRADED


# ------------------------------------------------------------------
# _check_database
# ------------------------------------------------------------------


class FakeSession:
    def __init__(self, on_execute=None):
        self._on_execute = on_execute
        self.closed = False

    def execute(self, statement):
        if self._on_execute:
            self._on_execute()
        return self

    def scalar(self):
        return 1

    def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_check_database_healthy(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr("core.persistence.session.SessionLocal", lambda: session)
    check = await SystemMonitor()._check_database()
    assert check.status == HealthStatus.HEALTHY
    assert "responsive" in check.message
    assert session.closed is True


@pytest.mark.asyncio
async def test_check_database_slow_degraded(monkeypatch):
    patch_clock(monkeypatch)

    def slow_execute():
        FakeClock.advance(2)

    session = FakeSession(on_execute=slow_execute)
    monkeypatch.setattr("core.persistence.session.SessionLocal", lambda: session)
    check = await SystemMonitor()._check_database()
    assert check.status == HealthStatus.DEGRADED
    assert "Slow database" in check.message
    assert check.latency_ms == 2000.0


@pytest.mark.asyncio
async def test_check_database_fast_boundary(monkeypatch):
    patch_clock(monkeypatch)

    def fast_execute():
        FakeClock.advance(1)

    session = FakeSession(on_execute=fast_execute)
    monkeypatch.setattr("core.persistence.session.SessionLocal", lambda: session)
    check = await SystemMonitor()._check_database()
    assert check.status == HealthStatus.HEALTHY
    assert check.latency_ms == 1000.0


@pytest.mark.asyncio
async def test_check_database_error(monkeypatch):
    def failing_execute(statement):
        raise RuntimeError("db down")

    session = FakeSession(on_execute=failing_execute)
    monkeypatch.setattr("core.persistence.session.SessionLocal", lambda: session)
    check = await SystemMonitor()._check_database()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Database error" in check.message


@pytest.mark.asyncio
async def test_check_database_error_on_construct(monkeypatch):
    def failing_construct():
        raise OSError("no connection")

    monkeypatch.setattr("core.persistence.session.SessionLocal", failing_construct)
    check = await SystemMonitor()._check_database()
    assert check.status == HealthStatus.UNHEALTHY


# ------------------------------------------------------------------
# _check_redis
# ------------------------------------------------------------------


class FakeRedisClient:
    def __init__(self, on_ping=None, on_close=None):
        self._on_ping = on_ping
        self._on_close = on_close
        self.closed = False

    async def ping(self):
        if self._on_ping:
            self._on_ping()
        return True

    async def close(self):
        self.closed = True
        if self._on_close:
            self._on_close()


@pytest.mark.asyncio
async def test_check_redis_healthy(monkeypatch):
    client = FakeRedisClient()
    monkeypatch.setattr("redis.asyncio.from_url", lambda url: client)
    check = await SystemMonitor()._check_redis()
    assert check.status == HealthStatus.HEALTHY
    assert "responsive" in check.message
    assert client.closed is True


@pytest.mark.asyncio
async def test_check_redis_slow_degraded(monkeypatch):
    patch_clock(monkeypatch)

    def slow_ping():
        FakeClock.advance(1)

    client = FakeRedisClient(on_ping=slow_ping)
    monkeypatch.setattr("redis.asyncio.from_url", lambda url: client)
    check = await SystemMonitor()._check_redis()
    assert check.status == HealthStatus.DEGRADED
    assert "Slow Redis" in check.message
    assert check.latency_ms == 1000.0


@pytest.mark.asyncio
async def test_check_redis_boundary_500(monkeypatch):
    patch_clock(monkeypatch)

    def ping_advance():
        FakeClock.advance(0.5)

    client = FakeRedisClient(on_ping=ping_advance)
    monkeypatch.setattr("redis.asyncio.from_url", lambda url: client)
    check = await SystemMonitor()._check_redis()
    assert check.status == HealthStatus.HEALTHY
    assert check.latency_ms == 500.0


@pytest.mark.asyncio
async def test_check_redis_error(monkeypatch):
    async def failing_ping():
        raise ConnectionError("redis down")

    class FailingRedisClient(FakeRedisClient):
        async def ping(self):
            raise ConnectionError("redis down")

    monkeypatch.setattr("redis.asyncio.from_url", lambda url: FailingRedisClient())
    check = await SystemMonitor()._check_redis()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Redis error" in check.message


@pytest.mark.asyncio
async def test_check_redis_uses_redis_url_env(monkeypatch):
    captured = {}

    def from_url(url):
        captured["url"] = url
        return FakeRedisClient()

    monkeypatch.setenv("REDIS_URL", "redis://cache.internal:9999/2")
    monkeypatch.setattr("redis.asyncio.from_url", from_url)
    check = await SystemMonitor()._check_redis()
    assert check.status == HealthStatus.HEALTHY
    assert captured["url"] == "redis://cache.internal:9999/2"


# ------------------------------------------------------------------
# _check_agents
# ------------------------------------------------------------------


ALL_REQUIRED = {
    "strategy_agent": None,
    "outreach_agent": None,
    "builder_agent": None,
    "repair_agent": None,
    "review_agent": None,
    "governance_agent": None,
    "audit_agent": None,
    "monitoring_agent": None,
}


class FakeAgentManager:
    def __init__(self, agents=None):
        self.agents = agents or {}

    def get_all_agents(self):
        return self.agents


@pytest.mark.asyncio
async def test_check_agents_healthy(monkeypatch):
    monkeypatch.setattr(
        "core.orchestration.agent_manager.agent_manager", FakeAgentManager(ALL_REQUIRED)
    )
    check = await SystemMonitor()._check_agents()
    assert check.status == HealthStatus.HEALTHY
    assert "All 8 required agents registered" in check.message
    assert check.details["missing"] == []


@pytest.mark.asyncio
async def test_check_agents_missing(monkeypatch):
    monkeypatch.setattr(
        "core.orchestration.agent_manager.agent_manager",
        FakeAgentManager({"strategy_agent": None, "builder_agent": None}),
    )
    check = await SystemMonitor()._check_agents()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Missing required agents" in check.message
    assert "repair_agent" in check.details["missing"]
    assert len(check.details["missing"]) == 6


@pytest.mark.asyncio
async def test_check_agents_error(monkeypatch):
    class Boom:
        def get_all_agents(self):
            raise RuntimeError("registry broken")

    monkeypatch.setattr("core.orchestration.agent_manager.agent_manager", Boom())
    check = await SystemMonitor()._check_agents()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Agent check error" in check.message


# ------------------------------------------------------------------
# _check_ollama
# ------------------------------------------------------------------


class MockOllamaResponse:
    def __init__(self, status_code, models):
        self.status_code = status_code
        self._models = models

    def json(self):
        return {"models": self._models}


class MockOllamaClient:
    def __init__(self, response, on_get=None):
        self._response = response
        self._on_get = on_get

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, url, timeout=None):
        if self._on_get:
            self._on_get()
        return self._response


@pytest.mark.asyncio
async def test_check_ollama_healthy(monkeypatch):
    monkeypatch.setattr(
        "httpx.AsyncClient",
        lambda *a, **k: MockOllamaClient(MockOllamaResponse(200, ["llama3", "mistral"])),
    )
    check = await SystemMonitor()._check_ollama()
    assert check.status == HealthStatus.HEALTHY
    assert "2 models" in check.message


@pytest.mark.asyncio
async def test_check_ollama_healthy_zero_models(monkeypatch):
    monkeypatch.setattr(
        "httpx.AsyncClient", lambda *a, **k: MockOllamaClient(MockOllamaResponse(200, []))
    )
    check = await SystemMonitor()._check_ollama()
    assert check.status == HealthStatus.HEALTHY
    assert "0 models" in check.message


@pytest.mark.asyncio
async def test_check_ollama_degraded_status(monkeypatch):
    monkeypatch.setattr(
        "httpx.AsyncClient", lambda *a, **k: MockOllamaClient(MockOllamaResponse(503, []))
    )
    check = await SystemMonitor()._check_ollama()
    assert check.status == HealthStatus.DEGRADED
    assert "Ollama status: 503" in check.message


@pytest.mark.asyncio
async def test_check_ollama_error(monkeypatch):
    class ErrorClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, timeout=None):
            raise httpx_connect_error()

    def httpx_connect_error():
        import httpx

        return httpx.ConnectError("unreachable")

    monkeypatch.setattr("httpx.AsyncClient", lambda *a, **k: ErrorClient())
    check = await SystemMonitor()._check_ollama()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Ollama error" in check.message


@pytest.mark.asyncio
async def test_check_ollama_uses_base_env(monkeypatch):
    captured = {}

    def make_client(*a, **k):
        client = MockOllamaClient(MockOllamaResponse(200, ["x"]))

        async def get(url, timeout=None):
            captured["url"] = url
            return MockOllamaResponse(200, ["x"])

        client.get = get
        return client

    monkeypatch.setenv("OLLAMA_API_BASE", "http://ollama.internal:8080")
    monkeypatch.setattr("httpx.AsyncClient", make_client)
    check = await SystemMonitor()._check_ollama()
    assert check.status == HealthStatus.HEALTHY
    assert captured["url"] == "http://ollama.internal:8080/api/tags"


@pytest.mark.asyncio
async def test_check_ollama_slow_latency(monkeypatch):
    patch_clock(monkeypatch)

    def slow_get():
        FakeClock.advance(0.75)

    client = MockOllamaClient(MockOllamaResponse(200, ["x"]), on_get=slow_get)
    monkeypatch.setattr("httpx.AsyncClient", lambda *a, **k: client)
    check = await SystemMonitor()._check_ollama()
    assert check.status == HealthStatus.HEALTHY
    assert check.latency_ms == 750.0


# ------------------------------------------------------------------
# _check_constitutional_compliance
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_constitutional_healthy(monkeypatch):
    check = await SystemMonitor()._check_constitutional_compliance()
    assert check.status == HealthStatus.HEALTHY
    assert "All compliance checks passed" in check.message
    assert check.details["tenant_isolation"] is True


@pytest.mark.asyncio
async def test_check_constitutional_degraded(monkeypatch):
    def fake_all(values):
        return False

    monkeypatch.setattr("builtins.all", fake_all)
    check = await SystemMonitor()._check_constitutional_compliance()
    assert check.status == HealthStatus.DEGRADED
    assert "Compliance issues" in check.message


@pytest.mark.asyncio
async def test_check_constitutional_error(monkeypatch):
    def failing_all(values):
        raise RuntimeError("compliance engine error")

    monkeypatch.setattr("builtins.all", failing_all)
    check = await SystemMonitor()._check_constitutional_compliance()
    assert check.status == HealthStatus.UNHEALTHY
    assert "Compliance check error" in check.message


# ------------------------------------------------------------------
# run_checks
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_checks_collects_all(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda interval: 30)
    monkeypatch.setattr("psutil.virtual_memory", lambda: FakeMem(40, 10e9))
    monkeypatch.setattr("psutil.disk_usage", lambda path: FakeDisk(50, 100, 50))
    session = FakeSession()
    monkeypatch.setattr("core.persistence.session.SessionLocal", lambda: session)
    monkeypatch.setattr("redis.asyncio.from_url", lambda url: FakeRedisClient())
    monkeypatch.setattr(
        "core.orchestration.agent_manager.agent_manager", FakeAgentManager(ALL_REQUIRED)
    )
    monkeypatch.setattr(
        "httpx.AsyncClient", lambda *a, **k: MockOllamaClient(MockOllamaResponse(200, ["x"]))
    )

    monitor = SystemMonitor()
    checks = await monitor.run_checks()

    names = [c.name for c in checks]
    assert names == [
        "cpu",
        "memory",
        "disk",
        "database",
        "redis",
        "agents",
        "ollama",
        "constitutional",
    ]
    assert len(checks) == 8
    assert monitor.checks == checks
    assert all(c.status == HealthStatus.HEALTHY for c in checks)


@pytest.mark.asyncio
async def test_run_checks_mixed_statuses(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda interval: 95)
    monkeypatch.setattr("psutil.virtual_memory", lambda: FakeMem(85, 10e9))
    monkeypatch.setattr("psutil.disk_usage", lambda path: FakeDisk(97, 100, 3))
    session = FakeSession()
    monkeypatch.setattr("core.persistence.session.SessionLocal", lambda: session)
    monkeypatch.setattr("redis.asyncio.from_url", lambda url: FakeRedisClient())
    monkeypatch.setattr(
        "core.orchestration.agent_manager.agent_manager",
        FakeAgentManager({"strategy_agent": None}),
    )
    monkeypatch.setattr(
        "httpx.AsyncClient", lambda *a, **k: MockOllamaClient(MockOllamaResponse(503, []))
    )

    checks = await SystemMonitor().run_checks()

    statuses = [c.status for c in checks]
    assert HealthStatus.UNHEALTHY in statuses
    assert HealthStatus.DEGRADED in statuses


# ------------------------------------------------------------------
# get_status
# ------------------------------------------------------------------


def test_get_status_empty():
    monitor = SystemMonitor()
    status = monitor.get_status()
    assert status == {"overall": "unknown", "checks": {}}


def test_get_status_healthy():
    monitor = SystemMonitor()
    monitor.checks = [
        HealthCheck("cpu", HealthStatus.HEALTHY, "cpu ok", 1.5, {"percent": 10}),
        HealthCheck("memory", HealthStatus.HEALTHY, "mem ok", 2.0),
    ]
    status = monitor.get_status()
    assert status["overall"] == "healthy"
    assert status["checks"]["cpu"]["status"] == "healthy"
    assert status["checks"]["cpu"]["latency_ms"] == 1.5
    assert status["checks"]["cpu"]["details"] == {"percent": 10}
    assert status["checks"]["memory"]["message"] == "mem ok"


def test_get_status_degraded():
    monitor = SystemMonitor()
    monitor.checks = [
        HealthCheck("cpu", HealthStatus.HEALTHY, "ok"),
        HealthCheck("disk", HealthStatus.DEGRADED, "high disk"),
    ]
    status = monitor.get_status()
    assert status["overall"] == "degraded"


def test_get_status_unhealthy_wins():
    monitor = SystemMonitor()
    monitor.checks = [
        HealthCheck("cpu", HealthStatus.UNHEALTHY, "bad"),
        HealthCheck("memory", HealthStatus.DEGRADED, "high"),
        HealthCheck("disk", HealthStatus.HEALTHY, "ok"),
    ]
    status = monitor.get_status()
    assert status["overall"] == "unhealthy"


def test_get_status_renders_check_fields():
    monitor = SystemMonitor()
    monitor.checks = [
        HealthCheck(
            "redis",
            HealthStatus.DEGRADED,
            "slow redis",
            600.0,
            {"host": "localhost"},
        )
    ]
    entry = monitor.get_status()["checks"]["redis"]
    assert entry == {
        "status": "degraded",
        "message": "slow redis",
        "latency_ms": 600.0,
        "details": {"host": "localhost"},
    }
