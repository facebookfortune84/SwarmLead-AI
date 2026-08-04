"""Unit tests for the MonitoringAgent (core.agents.monitoring.monitoring_agent)."""

import asyncio

import pytest

from core.agents.monitoring.monitoring_agent import MonitoringAgent


@pytest.mark.asyncio
async def test_run_reports_status_and_checks():
    agent = MonitoringAgent()
    result = await agent.run(input_data={}, context={})
    assert result["role"] == "Monitoring Agent"
    assert "system_status" in result
    assert isinstance(result["checks"], list)
    assert "summary" in result


@pytest.mark.asyncio
async def test_run_without_input():
    agent = MonitoringAgent()
    result = await agent.run()
    assert "system_status" in result


@pytest.mark.asyncio
async def test_get_status_and_run_checks():
    agent = MonitoringAgent()
    status = await agent.get_status()
    assert isinstance(status, dict)
    checks = await agent.run_checks()
    assert isinstance(checks, list)


@pytest.mark.asyncio
async def test_start_stop_loop():
    agent = MonitoringAgent()
    await agent.start(interval_seconds=1)
    assert agent._running is True
    await asyncio.sleep(0.05)
    await agent.stop()
    assert agent._running is False
    assert agent._task is None or agent._task.done()


@pytest.mark.asyncio
async def test_start_registers_recovery_actions():
    agent = MonitoringAgent()
    await agent.start(interval_seconds=1)
    assert set(agent._recovery_actions) == {"database", "redis", "ollama", "agents"}
    await agent.stop()


@pytest.mark.asyncio
async def test_recovery_actions_return_false():
    agent = MonitoringAgent()
    check = type("C", (), {})()
    assert await agent._recover_database(check) is False
    assert await agent._recover_redis(check) is False
    assert await agent._recover_ollama(check) is False
    assert await agent._recover_agents(check) is False


@pytest.mark.asyncio
async def test_monitor_loop_swallows_check_errors(monkeypatch):
    agent = MonitoringAgent()
    async def boom():
        raise RuntimeError("monitor broke")

    monkeypatch.setattr(agent.monitor, "run_checks", boom)
    await agent.start(interval_seconds=1)
    await asyncio.sleep(0.05)
    assert agent._running is True
    await agent.stop()
