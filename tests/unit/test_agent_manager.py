import pytest


@pytest.mark.asyncio
async def test_register_and_list_agents(agent_manager, simple_agent):
    agent_manager.register_agent("test_agent", simple_agent)

    agents = agent_manager.list_agents()

    assert "test_agent" in agents
    assert agents["test_agent"]["version"] == "1.0"


@pytest.mark.asyncio
async def test_successful_execution(agent_manager, simple_agent, sample_input):
    agent_manager.register_agent("echo", simple_agent)

    result = await agent_manager.execute("echo", sample_input)

    assert result["success"] is True
    assert result["result"]["echo"] == sample_input
    assert result["latency"] >= 0


@pytest.mark.asyncio
async def test_execution_failure(agent_manager, failing_agent):
    agent_manager.register_agent("fail_agent", failing_agent)

    result = await agent_manager.execute("fail_agent", {})

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_invalid_agent(agent_manager):
    with pytest.raises(Exception):
        await agent_manager.execute("nonexistent", {})


@pytest.mark.asyncio
async def test_batch_execution(agent_manager, simple_agent):
    agent_manager.register_agent("a1", simple_agent)
    agent_manager.register_agent("a2", simple_agent)

    results = await agent_manager.execute_batch(
        {
            "a1": {"x": 1},
            "a2": {"x": 2},
        }
    )

    assert "a1" in results
    assert "a2" in results
    assert results["a1"]["success"] is True


@pytest.mark.asyncio
async def test_latency_tracking(agent_manager, slow_agent):
    agent_manager.register_agent("slow", slow_agent)

    result = await agent_manager.execute("slow", {})

    assert result["latency"] > 0.04  # confirms async delay applied


@pytest.mark.asyncio
async def test_agent_overwrite_warning(agent_manager, simple_agent):
    agent_manager.register_agent("dup", simple_agent)
    agent_manager.register_agent("dup", simple_agent)  # overwrite

    agents = agent_manager.list_agents()

    assert "dup" in agents


@pytest.mark.asyncio
async def test_sync_agent_execution(agent_manager):
    def sync_agent(input_data, context):
        return {"sync": True}

    agent_manager.register_agent("sync_agent", sync_agent)

    result = await agent_manager.execute("sync_agent", {})

    assert result["success"] is True
    assert result["result"]["sync"] is True


@pytest.mark.asyncio
async def test_get_agent(agent_manager, simple_agent):
    agent_manager.register_agent("a1", simple_agent)

    agent = agent_manager.get_agent("a1")

    assert agent is not None
