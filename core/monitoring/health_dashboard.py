"""
Health Dashboard

Constitutional §5: Monitoring = operational visibility
Provides /health and /ready endpoints for k8s and load balancers.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.monitoring.metrics_collector import get_metrics
from core.persistence.session import get_db


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str
    checks: Dict[str, Any]


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    ready: bool
    timestamp: str
    checks: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Liveness probe - service is running.

    Returns 200 if process is alive, regardless of dependencies.
    Used by load balancer to detect crashed processes.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="1.0.0",
        checks={"process": "running", "timestamp": datetime.utcnow().isoformat()},
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe - service can handle requests.

    Returns 200 only if all critical dependencies are healthy:
    - Database connectivity
    - Redis connectivity
    - Critical agents registered
    - Configuration valid

    Returns 503 if any critical dependency is unhealthy.
    """
    checks = {}
    all_healthy = True

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        all_healthy = False

    # Redis check
    try:
        import os

        import redis.asyncio as redis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url)
        await redis_client.ping()
        await redis_client.close()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
        all_healthy = False

    # Agent registration check
    from core.orchestration.agent_manager import agent_manager

    registered_agents = agent_manager.get_all_agents()
    required_agents = [
        "strategy_agent",
        "outreach_agent",
        "builder_agent",
        "repair_agent",
        "review_agent",
        "governance_agent",
        "audit_agent",
        "monitoring_agent",
    ]
    missing = [a for a in required_agents if a not in registered_agents]
    if missing:
        checks["agents"] = {"status": "degraded", "missing": missing}
        all_healthy = False
    else:
        checks["agents"] = {"status": "healthy", "count": len(registered_agents)}

    # Configuration check
    from configs.config_loader import ConfigLoader

    try:
        ConfigLoader.load()
        checks["config"] = {"status": "valid"}
    except Exception as e:
        checks["config"] = {"status": "invalid", "error": str(e)}
        all_healthy = False

    # Ollama LLM check
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                checks["ollama"] = {"status": "healthy"}
            else:
                checks["ollama"] = {"status": "degraded", "status_code": resp.status_code}
    except Exception as e:
        checks["ollama"] = {"status": "unhealthy", "error": str(e)}
        # Don't fail readiness for Ollama - it's a fallback

    if not all_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ReadinessResponse(
                ready=False, timestamp=datetime.utcnow().isoformat() + "Z", checks=checks
            ).model_dump(),
        )

    return ReadinessResponse(
        ready=True, timestamp=datetime.utcnow().isoformat() + "Z", checks=checks
    )


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response

    return Response(content=get_metrics(), media_type="text/plain")


@router.get("/version")
async def version():
    """Version information."""
    return {
        "version": "1.0.0",
        "build": "genesis-v1.0.0",
        "constitution_version": "1.0",
        "build_date": "2026-07-26",
    }


# Additional detailed health endpoints for debugging
@router.get("/health/detailed")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """Detailed health information for debugging."""

    # Database details
    db_info = {}
    try:
        result = await db.execute(text("SELECT version()"))
        db_info["version"] = result.scalar()
        result = await db.execute(text("SELECT count(*) FROM pg_stat_activity"))
        db_info["connections"] = result.scalar()
    except Exception as e:
        db_info["error"] = str(e)

    # Agent details
    from core.orchestration.agent_manager import agent_manager

    agents = {}
    for name, agent in agent_manager.get_all_agents().items():
        agents[name] = {"type": type(agent).__name__, "registered": True}

    # System info
    import psutil

    process = psutil.Process()
    mem = process.memory_info()
    psutil.virtual_memory()

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": db_info,
        "agents": agents,
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "process_memory_mb": mem.rss / 1024 / 1024,
            "process_cpu_percent": process.cpu_percent(),
        },
        "uptime_seconds": psutil.boot_time(),
    }


class HealthDashboard:
    """
    HealthDashboard class - provides programmatic access to health checks.

    Wraps the health check functions for programmatic use by MonitoringAgent.
    """

    def __init__(self):
        self.start_time = datetime.utcnow()
        self._checks: Dict[str, callable] = {}
        self._register_default_checks()

    def _register_default_checks(self):
        """Register core health checks."""
        self.register_check("database", self._check_database)
        self.register_check("redis", self._check_redis)
        self.register_check("memory", self._check_memory)
        self.register_check("disk", self._check_disk)
        self.register_check("llm", self._check_llm)

    def register_check(self, name: str, check_fn: callable):
        """Register a custom health check."""
        self._checks[name] = check_fn

    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        from sqlalchemy import text

        from core.persistence.session import SessionLocal

        start = datetime.utcnow()
        try:
            session = SessionLocal()
            session.execute(text("SELECT 1")).scalar()
            session.close()
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return {
                "status": "healthy",
                "latency_ms": latency,
                "message": f"PostgreSQL responsive ({latency:.0f}ms)",
            }
        except Exception as e:
            return {"status": "unhealthy", "latency_ms": 0, "message": f"Database error: {str(e)}"}

    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        import os

        import redis.asyncio as redis

        start = datetime.utcnow()
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            client = redis.from_url(redis_url)
            await client.ping()
            await client.close()
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return {
                "status": "healthy",
                "latency_ms": latency,
                "message": f"Redis responsive ({latency:.0f}ms)",
            }
        except Exception as e:
            return {"status": "unhealthy", "latency_ms": 0, "message": f"Redis error: {str(e)}"}

    async def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        import psutil

        mem = psutil.virtual_memory()
        return {
            "status": "healthy"
            if mem.percent < 80
            else "degraded"
            if mem.percent < 90
            else "unhealthy",
            "message": f"Memory usage: {mem.percent:.1f}%",
            "details": {"percent": mem.percent, "available_gb": mem.available / 1e9},
        }

    async def _check_disk(self) -> Dict[str, Any]:
        """Check disk space."""
        import psutil

        disk = psutil.disk_usage("/")
        percent = (disk.used / disk.total) * 100
        return {
            "status": "healthy" if percent < 85 else "degraded" if percent < 95 else "unhealthy",
            "message": f"Disk usage: {percent:.1f}%",
            "details": {"percent": percent, "free_gb": disk.free / 1e9},
        }

    async def _check_llm(self) -> Dict[str, Any]:
        """Check Ollama LLM availability."""
        import os

        import httpx

        start = datetime.utcnow()
        ollama_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{ollama_base}/api/tags", timeout=5)
                latency = (datetime.utcnow() - start).total_seconds() * 1000
                if resp.status_code == 200:
                    return {
                        "status": "healthy",
                        "latency_ms": latency,
                        "message": f"Ollama available with {len(resp.json().get('models', []))} models",
                    }
                else:
                    return {
                        "status": "degraded",
                        "latency_ms": latency,
                        "message": f"Ollama status: {resp.status_code}",
                    }
        except Exception as e:
            latency = (datetime.utcnow() - datetime.utcnow()).total_seconds() * 1000
            return {"status": "unhealthy", "latency_ms": 0, "message": f"Ollama error: {e}"}

    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks and return results."""
        results = {}
        for name, check_fn in self._checks.items():
            try:
                result = await check_fn()
                results[name] = result
            except Exception as e:
                results[name] = {"status": "unhealthy", "message": f"Check failed: {str(e)}"}
        self.checks = results
        return results

    async def check_health(self, detailed: bool = False) -> Dict[str, Any]:
        """Check health and return status."""
        results = await self.run_checks()
        statuses = [r.get("status", "unknown") for r in results.values()]
        if "unhealthy" in statuses:
            overall = "unhealthy"
        elif "degraded" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        response = {
            "status": overall,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        if detailed:
            response["checks"] = results
        return response

    def get_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        if not getattr(self, "checks", None):
            return {"overall": "unknown", "checks": {}}

        statuses = [c.get("status", "unknown") for c in self.checks.values()]
        if "unhealthy" in statuses:
            overall = "unhealthy"
        elif "degraded" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        return {"overall": overall, "checks": self.checks}


# Export router and class
__all__ = ["router", "HealthDashboard", "HealthResponse", "ReadinessResponse"]
