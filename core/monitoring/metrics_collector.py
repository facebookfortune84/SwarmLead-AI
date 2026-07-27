"""
Metrics Collector - Prometheus Metrics

Collects and exports Prometheus-compatible metrics for monitoring.
Constitutional requirement: Observable system health.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Optional

import psutil
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

# Global registry
registry = CollectorRegistry()

# Counters
api_requests_total = Counter(
    "genesis_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

agent_tasks_total = Counter(
    "genesis_agent_tasks_total",
    "Total agent tasks executed",
    ["agent_name", "task_type", "status"],
    registry=registry,
)

voice_sessions_total = Counter(
    "genesis_voice_sessions_total",
    "Total voice sessions",
    ["status"],  # started, completed, interrupted, failed
    registry=registry,
)

monetary_transactions_total = Counter(
    "genesis_monetary_transactions_total",
    "Total monetary transactions",
    ["type", "status"],  # type: payment/refund/fee, status: success/failed
    registry=registry,
)

tenant_operations_total = Counter(
    "genesis_tenant_operations_total",
    "Total tenant operations",
    ["operation", "status"],  # provision, deprovision, backup, etc.
    registry=registry,
)

# Histograms
api_request_duration = Histogram(
    "genesis_api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)

agent_task_duration = Histogram(
    "genesis_agent_task_duration_seconds",
    "Agent task execution duration",
    ["agent_name", "task_type"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=registry,
)

voice_latency = Histogram(
    "genesis_voice_latency_seconds",
    "Voice processing latency (STT + LLM + TTS)",
    ["operation"],  # stt, llm, tts, total
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=registry,
)

voice_barge_in_latency = Histogram(
    "genesis_voice_barge_in_latency_seconds",
    "Barge-in interruption latency",
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry,
)

db_query_duration = Histogram(
    "genesis_db_query_duration_seconds",
    "Database query duration",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry,
)

# Gauges
active_tenants = Gauge("genesis_active_tenants", "Number of active tenants", registry=registry)

active_agents = Gauge("genesis_active_agents", "Number of active agents", registry=registry)

active_voice_sessions = Gauge(
    "genesis_active_voice_sessions", "Active voice sessions", registry=registry
)

memory_usage_bytes = Gauge(
    "genesis_memory_usage_bytes", "Process memory usage in bytes", registry=registry
)

cpu_usage_percent = Gauge("genesis_cpu_usage_percent", "CPU usage percentage", registry=registry)

# Agent-specific metrics
agent_llm_calls = Counter(
    "genesis_agent_llm_calls_total",
    "Total LLM calls by agents",
    ["agent_name", "model", "status"],
    registry=registry,
)

agent_memory_operations = Counter(
    "genesis_agent_memory_operations_total",
    "Agent memory operations",
    ["agent_name", "operation", "memory_type"],  # session, long_term, vector
    registry=registry,
)

agent_errors = Counter(
    "genesis_agent_errors_total", "Agent errors", ["agent_name", "error_type"], registry=registry
)


class MetricsCollector:
    """Collects and updates system metrics."""

    def __init__(self):
        self._update_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start periodic metric collection."""
        self._update_task = asyncio.create_task(self._collect_loop())

    async def stop(self):
        """Stop metric collection."""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

    async def _collect_loop(self):
        """Periodic metric collection loop."""
        while True:
            try:
                await self._collect_system_metrics()
            except Exception:
                pass  # Log but don't crash
            await asyncio.sleep(15)  # Collect every 15 seconds

    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        # Memory
        mem = psutil.virtual_memory()
        memory_usage_bytes.set(mem.used)

        # CPU
        cpu_usage_percent.set(psutil.cpu_percent(interval=0.1))

        # Disk
        psutil.disk_usage("/")
        # Could add disk gauges here

        # Process-specific
        process = psutil.Process()
        process.memory_info()
        # Could add process-specific gauges


# Context managers for timing
@asynccontextmanager
async def track_api_request(method: str, endpoint: str):
    """Context manager to track API request duration and status."""
    start = time.time()
    status = "success"
    try:
        yield
    except Exception:
        status = "error"
        raise
    finally:
        duration = time.time() - start
        api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()


@asynccontextmanager
async def track_agent_task(agent_name: str, task_type: str):
    """Track agent task execution."""
    start = time.time()
    status = "success"
    try:
        yield
    except Exception as e:
        status = "error"
        agent_errors.labels(agent_name=agent_name, error_type=type(e).__name__).inc()
        raise
    finally:
        duration = time.time() - start
        agent_task_duration.labels(agent_name=agent_name, task_type=task_type).observe(duration)
        agent_tasks_total.labels(agent_name=agent_name, task_type=task_type, status=status).inc()


@asynccontextmanager
async def track_voice_operation(operation: str):
    """Track voice operation latency."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        voice_latency.labels(operation=operation).observe(duration)


@asynccontextmanager
async def track_barge_in():
    """Track barge-in interruption latency."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        voice_barge_in_latency.observe(duration)


def record_agent_llm_call(agent_name: str, model: str, success: bool):
    """Record agent LLM call."""
    agent_llm_calls.labels(
        agent_name=agent_name, model=model, status="success" if success else "error"
    ).inc()


def record_agent_memory_op(agent_name: str, operation: str, memory_type: str):
    """Record agent memory operation."""
    agent_memory_operations.labels(
        agent_name=agent_name, operation=operation, memory_type=memory_type
    ).inc()


def record_voice_session(status: str):
    """Record voice session lifecycle."""
    voice_sessions_total.labels(status=status).inc()


def record_monetary_transaction(transaction_type: str, success: bool):
    """Record monetary transaction."""
    monetary_transactions_total.labels(
        type=transaction_type, status="success" if success else "failed"
    ).inc()


def record_tenant_operation(operation: str, success: bool):
    """Record tenant lifecycle operation."""
    tenant_operations_total.labels(
        operation=operation, status="success" if success else "failed"
    ).inc()


def update_active_tenants(count: int):
    """Update active tenant count."""
    active_tenants.set(count)


def update_active_agents(count: int):
    """Update active agent count."""
    active_agents.set(count)


def update_active_voice_sessions(count: int):
    """Update active voice session count."""
    active_voice_sessions.set(count)


def record_agent_task(agent_name: str, task_type: str, status: str = "success"):
    """Record agent task execution."""
    agent_tasks_total.labels(agent_name=agent_name, task_type=task_type, status=status).inc()


def get_metrics() -> bytes:
    """Generate Prometheus metrics output."""
    return generate_latest(registry)
