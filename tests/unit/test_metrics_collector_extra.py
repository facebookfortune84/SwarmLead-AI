import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core.monitoring import metrics_collector as mc
from core.monitoring.metrics_collector import (
    MetricsCollector,
    get_metrics,
    record_agent_llm_call,
    record_agent_memory_op,
    record_agent_task,
    record_monetary_transaction,
    record_tenant_operation,
    record_voice_session,
    track_agent_task,
    track_api_request,
    track_barge_in,
    track_voice_operation,
    update_active_agents,
    update_active_tenants,
    update_active_voice_sessions,
)


def _parse(output):
    """Parse Prometheus text format into {name: labels_str: value}."""
    metrics = {}
    for line in output.decode().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "{" in line:
            name, rest = line.split("{", 1)
            labels_str, value = rest.split("} ", 1)
        else:
            name, value = line.rsplit(" ", 1)
            labels_str = ""
        if name.endswith("_created"):
            continue
        metrics[(name, labels_str)] = float(value)
    return metrics


def _labels(labels):
    if not labels:
        return ""
    return ",".join(f'{key}="{value}"' for key, value in sorted(labels.items()))


def current(name, labels=None):
    return _parse(get_metrics()).get((name, _labels(labels)), 0.0)


def test_get_metrics_returns_bytes():
    output = get_metrics()

    assert isinstance(output, bytes)
    assert len(output) > 0
    assert b"genesis_api_requests_total" in output


def test_get_metrics_reflects_recorded_data():
    update_active_tenants(7)

    output = get_metrics()

    assert b"genesis_active_tenants 7.0" in output


def test_track_api_request_success():
    before_total = current(
        "genesis_api_requests_total", {"method": "GET", "endpoint": "/health", "status": "success"}
    )
    before_dur = current("genesis_api_request_duration_seconds_count", {"method": "GET", "endpoint": "/health"})

    async def run():
        async with track_api_request("GET", "/health"):
            pass

    asyncio.run(run())

    assert (
        current("genesis_api_requests_total", {"method": "GET", "endpoint": "/health", "status": "success"})
        - before_total
        == 1
    )
    assert current("genesis_api_request_duration_seconds_count", {"method": "GET", "endpoint": "/health"}) - before_dur == 1


@pytest.mark.asyncio
async def test_track_api_request_error():
    before_total = current(
        "genesis_api_requests_total", {"method": "POST", "endpoint": "/fail", "status": "error"}
    )
    before_dur = current("genesis_api_request_duration_seconds_count", {"method": "POST", "endpoint": "/fail"})

    with pytest.raises(ValueError):
        async with track_api_request("POST", "/fail"):
            raise ValueError("boom")

    assert (
        current("genesis_api_requests_total", {"method": "POST", "endpoint": "/fail", "status": "error"})
        - before_total
        == 1
    )
    assert current("genesis_api_request_duration_seconds_count", {"method": "POST", "endpoint": "/fail"}) - before_dur == 1


def test_track_agent_task_success():
    before_total = current(
        "genesis_agent_tasks_total", {"agent_name": "researcher", "task_type": "search", "status": "success"}
    )
    before_dur = current("genesis_agent_task_duration_seconds_count", {"agent_name": "researcher", "task_type": "search"})

    async def run():
        async with track_agent_task("researcher", "search"):
            pass

    asyncio.run(run())

    assert (
        current(
            "genesis_agent_tasks_total", {"agent_name": "researcher", "task_type": "search", "status": "success"}
        )
        - before_total
        == 1
    )
    assert current("genesis_agent_task_duration_seconds_count", {"agent_name": "researcher", "task_type": "search"}) - before_dur == 1


@pytest.mark.asyncio
async def test_track_agent_task_error():
    before_total = current(
        "genesis_agent_tasks_total", {"agent_name": "writer", "task_type": "draft", "status": "error"}
    )
    before_dur = current("genesis_agent_task_duration_seconds_count", {"agent_name": "writer", "task_type": "draft"})
    before_errors = current("genesis_agent_errors_total", {"agent_name": "writer", "error_type": "ValueError"})

    with pytest.raises(ValueError):
        async with track_agent_task("writer", "draft"):
            raise ValueError("bad input")

    assert (
        current("genesis_agent_tasks_total", {"agent_name": "writer", "task_type": "draft", "status": "error"})
        - before_total
        == 1
    )
    assert current("genesis_agent_task_duration_seconds_count", {"agent_name": "writer", "task_type": "draft"}) - before_dur == 1
    assert current("genesis_agent_errors_total", {"agent_name": "writer", "error_type": "ValueError"}) - before_errors == 1


def test_track_voice_operation_success():
    before = current("genesis_voice_latency_seconds_count", {"operation": "stt"})

    async def run():
        async with track_voice_operation("stt"):
            pass

    asyncio.run(run())

    assert current("genesis_voice_latency_seconds_count", {"operation": "stt"}) - before == 1


@pytest.mark.asyncio
async def test_track_voice_operation_error_still_records():
    before = current("genesis_voice_latency_seconds_count", {"operation": "llm"})

    with pytest.raises(RuntimeError):
        async with track_voice_operation("llm"):
            raise RuntimeError("llm failed")

    assert current("genesis_voice_latency_seconds_count", {"operation": "llm"}) - before == 1


def test_track_barge_in_success():
    before = current("genesis_voice_barge_in_latency_seconds_count")

    async def run():
        async with track_barge_in():
            pass

    asyncio.run(run())

    assert current("genesis_voice_barge_in_latency_seconds_count") - before == 1


@pytest.mark.asyncio
async def test_track_barge_in_error_still_records():
    before = current("genesis_voice_barge_in_latency_seconds_count")

    with pytest.raises(ValueError):
        async with track_barge_in():
            raise ValueError("interrupted")

    assert current("genesis_voice_barge_in_latency_seconds_count") - before == 1


def test_record_agent_llm_call_success():
    before = current("genesis_agent_llm_calls_total", {"agent_name": "chat", "model": "gpt-4", "status": "success"})

    record_agent_llm_call("chat", "gpt-4", success=True)

    assert current("genesis_agent_llm_calls_total", {"agent_name": "chat", "model": "gpt-4", "status": "success"}) - before == 1


def test_record_agent_llm_call_error():
    before = current("genesis_agent_llm_calls_total", {"agent_name": "chat", "model": "gpt-4", "status": "error"})

    record_agent_llm_call("chat", "gpt-4", success=False)

    assert current("genesis_agent_llm_calls_total", {"agent_name": "chat", "model": "gpt-4", "status": "error"}) - before == 1


def test_record_agent_memory_op():
    before = current(
        "genesis_agent_memory_operations_total",
        {"agent_name": "chat", "operation": "store", "memory_type": "vector"},
    )

    record_agent_memory_op("chat", "store", "vector")

    assert (
        current(
            "genesis_agent_memory_operations_total",
            {"agent_name": "chat", "operation": "store", "memory_type": "vector"},
        )
        - before
        == 1
    )


def test_record_voice_session_started():
    before = current("genesis_voice_sessions_total", {"status": "started"})

    record_voice_session("started")

    assert current("genesis_voice_sessions_total", {"status": "started"}) - before == 1


def test_record_monetary_transaction_success():
    before = current("genesis_monetary_transactions_total", {"type": "payment", "status": "success"})

    record_monetary_transaction("payment", success=True)

    assert current("genesis_monetary_transactions_total", {"type": "payment", "status": "success"}) - before == 1


def test_record_monetary_transaction_failed():
    before = current("genesis_monetary_transactions_total", {"type": "refund", "status": "failed"})

    record_monetary_transaction("refund", success=False)

    assert current("genesis_monetary_transactions_total", {"type": "refund", "status": "failed"}) - before == 1


def test_record_tenant_operation_success():
    before = current("genesis_tenant_operations_total", {"operation": "provision", "status": "success"})

    record_tenant_operation("provision", success=True)

    assert current("genesis_tenant_operations_total", {"operation": "provision", "status": "success"}) - before == 1


def test_record_tenant_operation_failed():
    before = current("genesis_tenant_operations_total", {"operation": "backup", "status": "failed"})

    record_tenant_operation("backup", success=False)

    assert current("genesis_tenant_operations_total", {"operation": "backup", "status": "failed"}) - before == 1


def test_update_active_tenants():
    update_active_tenants(3)

    assert current("genesis_active_tenants") == 3.0


def test_update_active_tenants_zero():
    update_active_tenants(0)

    assert current("genesis_active_tenants") == 0.0


def test_update_active_agents():
    update_active_agents(5)

    assert current("genesis_active_agents") == 5.0


def test_update_active_voice_sessions():
    update_active_voice_sessions(2)

    assert current("genesis_active_voice_sessions") == 2.0


def test_record_agent_task_default_status():
    before = current("genesis_agent_tasks_total", {"agent_name": "a", "task_type": "t", "status": "success"})

    record_agent_task("a", "t")

    assert current("genesis_agent_tasks_total", {"agent_name": "a", "task_type": "t", "status": "success"}) - before == 1


def test_record_agent_task_custom_status():
    before = current("genesis_agent_tasks_total", {"agent_name": "a", "task_type": "t", "status": "failed"})

    record_agent_task("a", "t", status="failed")

    assert current("genesis_agent_tasks_total", {"agent_name": "a", "task_type": "t", "status": "failed"}) - before == 1


def test_record_functions_accept_empty_labels():
    record_agent_llm_call("", "", success=True)
    record_agent_memory_op("", "", "")
    record_voice_session("")
    record_agent_task("", "", status="")
    record_monetary_transaction("", success=False)
    record_tenant_operation("", success=False)

    assert current("genesis_voice_sessions_total", {"status": ""}) > 0


@pytest.mark.asyncio
async def test_start_creates_update_task(monkeypatch):
    collector = MetricsCollector()
    collected = AsyncMock()
    monkeypatch.setattr(collector, "_collect_system_metrics", collected)

    await collector.start()

    assert collector._update_task is not None
    assert not collector._update_task.done()

    await collector.stop()


@pytest.mark.asyncio
async def test_start_stop_roundtrip(monkeypatch):
    collector = MetricsCollector()
    collected = AsyncMock()
    monkeypatch.setattr(collector, "_collect_system_metrics", collected)

    await collector.start()
    await asyncio.sleep(0.05)
    assert collected.await_count >= 1

    await collector.stop()
    assert collector._update_task.cancelled()


@pytest.mark.asyncio
async def test_stop_noop_when_no_task():
    collector = MetricsCollector()

    await collector.stop()


@pytest.mark.asyncio
async def test_stop_awaits_cancelled_task():
    collector = MetricsCollector()
    real_sleep = asyncio.sleep

    async def slow():
        await real_sleep(100)

    collector._update_task = asyncio.create_task(slow())

    await collector.stop()

    assert collector._update_task.cancelled()


@pytest.mark.asyncio
async def test_collect_loop_recovers_from_errors(monkeypatch):
    collector = MetricsCollector()
    real_sleep = asyncio.sleep
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("boom")

    async def fast_sleep(_seconds):
        if calls["n"] >= 3:
            raise asyncio.CancelledError()
        await real_sleep(0)

    monkeypatch.setattr(collector, "_collect_system_metrics", flaky)
    monkeypatch.setattr(mc.asyncio, "sleep", fast_sleep)

    with pytest.raises(asyncio.CancelledError):
        await collector._collect_loop()

    assert calls["n"] == 3


@pytest.mark.asyncio
async def test_collect_system_metrics_sets_gauges(monkeypatch):
    collector = MetricsCollector()

    class FakeMem:
        used = 123456

    class FakeProcess:
        def memory_info(self):
            return None

    monkeypatch.setattr(mc.psutil, "virtual_memory", lambda: FakeMem())
    monkeypatch.setattr(mc.psutil, "cpu_percent", lambda interval=None: 42.5)
    monkeypatch.setattr(mc.psutil, "disk_usage", lambda _path: None)
    monkeypatch.setattr(mc.psutil, "Process", lambda: FakeProcess())

    await collector._collect_system_metrics()

    assert current("genesis_memory_usage_bytes") == 123456.0
    assert current("genesis_cpu_usage_percent") == 42.5
