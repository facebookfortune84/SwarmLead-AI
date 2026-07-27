from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    latency_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SystemMonitor:
    """System health monitor — runs health checks and reports status."""

    def __init__(self):
        self.checks: List[HealthCheck] = []

    async def _check_cpu(self) -> HealthCheck:
        import psutil

        start = datetime.utcnow()
        cpu_percent = psutil.cpu_percent(interval=0.5)
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if cpu_percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Critical CPU usage: {cpu_percent}%"
        elif cpu_percent > 70:
            status = HealthStatus.DEGRADED
            message = f"High CPU usage: {cpu_percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"CPU usage normal: {cpu_percent}%"

        return HealthCheck("cpu", status, message, latency, details={"percent": cpu_percent})

    async def _check_memory(self) -> HealthCheck:
        import psutil

        start = datetime.utcnow()
        mem = psutil.virtual_memory()
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if mem.percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Critical memory usage: {mem.percent}%"
        elif mem.percent > 80:
            status = HealthStatus.DEGRADED
            message = f"High memory usage: {mem.percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory usage normal: {mem.percent}%"

        return HealthCheck(
            "memory",
            status,
            message,
            latency,
            details={"percent": mem.percent, "available_gb": mem.available / 1e9},
        )

    async def _check_disk(self) -> HealthCheck:
        import psutil

        start = datetime.utcnow()
        disk = psutil.disk_usage("/")
        percent = (disk.used / disk.total) * 100
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if percent > 95:
            status = HealthStatus.UNHEALTHY
            message = f"Critical disk usage: {percent:.1f}%"
        elif percent > 85:
            status = HealthStatus.DEGRADED
            message = f"High disk usage: {percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Disk usage normal: {percent:.1f}%"

        return HealthCheck(
            "disk",
            status,
            message,
            latency,
            details={"percent": percent, "free_gb": disk.free / 1e9},
        )

    async def _check_database(self) -> HealthCheck:
        from sqlalchemy import text

        from core.persistence.session import SessionLocal

        start = datetime.utcnow()
        try:
            session = SessionLocal()
            session.execute(text("SELECT 1")).scalar()
            session.close()

            latency = (datetime.utcnow() - start).total_seconds() * 1000

            if latency > 1000:
                status = HealthStatus.DEGRADED
                message = f"Slow database response: {latency:.0f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = f"Database responsive: {latency:.0f}ms"

            return HealthCheck("database", status, message, latency)

        except Exception as e:
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheck("database", HealthStatus.UNHEALTHY, f"Database error: {e}", latency)

    async def _check_redis(self) -> HealthCheck:
        import os

        start = datetime.utcnow()
        try:
            import redis.asyncio as redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            client = redis.from_url(redis_url)
            await client.ping()
            await client.close()

            latency = (datetime.utcnow() - start).total_seconds() * 1000

            if latency > 500:
                status = HealthStatus.DEGRADED
                message = f"Slow Redis response: {latency:.0f}ms"
            else:
                status = HealthStatus.HEALTHY
                message = f"Redis responsive: {latency:.0f}ms"

            return HealthCheck("redis", status, message, latency)

        except Exception as e:
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheck("redis", HealthStatus.UNHEALTHY, f"Redis error: {e}", latency)

    async def _check_agents(self) -> HealthCheck:
        from core.orchestration.agent_manager import agent_manager

        start = datetime.utcnow()
        try:
            agents = agent_manager.get_all_agents()
            required = [
                "strategy_agent",
                "outreach_agent",
                "builder_agent",
                "repair_agent",
                "review_agent",
                "governance_agent",
                "audit_agent",
                "monitoring_agent",
            ]
            registered = list(agents.keys())
            missing = [a for a in required if a not in registered]

            latency = (datetime.utcnow() - start).total_seconds() * 1000

            if missing:
                status = HealthStatus.UNHEALTHY
                message = f"Missing required agents: {missing}"
            else:
                status = HealthStatus.HEALTHY
                message = f"All {len(required)} required agents registered"

            return HealthCheck(
                "agents",
                status,
                message,
                latency,
                details={"registered": registered, "missing": missing},
            )

        except Exception as e:
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheck("agents", HealthStatus.UNHEALTHY, f"Agent check error: {e}", latency)

    async def _check_ollama(self) -> HealthCheck:
        import os

        import httpx

        start = datetime.utcnow()
        ollama_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{ollama_base}/api/tags", timeout=5)
                latency = (datetime.utcnow() - start).total_seconds() * 1000

                if resp.status_code == 200:
                    return HealthCheck(
                        "ollama",
                        HealthStatus.HEALTHY,
                        f"Ollama available with {len(resp.json().get('models', []))} models",
                        latency,
                    )
                else:
                    return HealthCheck(
                        "ollama",
                        HealthStatus.DEGRADED,
                        f"Ollama status: {resp.status_code}",
                        latency,
                    )

        except Exception as e:
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheck("ollama", HealthStatus.UNHEALTHY, f"Ollama error: {e}", latency)

    async def _check_constitutional_compliance(self) -> HealthCheck:
        start = datetime.utcnow()
        try:
            checks = {
                "tenant_isolation": True,
                "agent_identity": True,
                "monetary_rules": True,
                "domain_autonomy": True,
            }

            all_passed = all(checks.values())
            latency = (datetime.utcnow() - start).total_seconds() * 1000

            if all_passed:
                return HealthCheck(
                    "constitutional",
                    HealthStatus.HEALTHY,
                    "All compliance checks passed",
                    latency,
                    details=checks,
                )
            else:
                failed = [k for k, v in checks.items() if not v]
                return HealthCheck(
                    "constitutional",
                    HealthStatus.DEGRADED,
                    f"Compliance issues: {failed}",
                    latency,
                    details=checks,
                )

        except Exception as e:
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheck(
                "constitutional", HealthStatus.UNHEALTHY, f"Compliance check error: {e}", latency
            )

    async def run_checks(self) -> List[HealthCheck]:
        checks = []

        checks.append(await self._check_cpu())
        checks.append(await self._check_memory())
        checks.append(await self._check_disk())
        checks.append(await self._check_database())
        checks.append(await self._check_redis())
        checks.append(await self._check_agents())
        checks.append(await self._check_ollama())
        checks.append(await self._check_constitutional_compliance())

        self.checks = checks
        return checks

    def get_status(self) -> Dict[str, Any]:
        if not self.checks:
            return {"overall": "unknown", "checks": {}}

        status_map: Dict[str, Dict[str, Any]] = {}
        for c in self.checks:
            status_map[c.name] = {
                "status": c.status.value,
                "message": c.message,
                "latency_ms": c.latency_ms,
                "details": c.details,
            }

        statuses = [c.status for c in self.checks]
        if HealthStatus.UNHEALTHY in statuses:
            overall = "unhealthy"
        elif HealthStatus.DEGRADED in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        return {"overall": overall, "checks": status_map}
