import pytest

from core.auth.agent_identity import AgentIdentityRegistry


@pytest.mark.asyncio
async def test_register_and_list_agents(agent_manager, simple_agent):
    agent_manager.register_agent("test_agent", simple_agent)
    agents = agent_manager.get_all_agents()
    assert "test_agent" in agents


@pytest.mark.asyncio
async def test_successful_execution(agent_manager, simple_agent, sample_input):
    agent_manager.register_agent("echo", simple_agent)
    result = await agent_manager.execute_agent("echo", sample_input)
    assert result["success"] is True
    assert result["result"]["echo"] == sample_input


@pytest.mark.asyncio
async def test_execution_failure(agent_manager, failing_agent):
    agent_manager.register_agent("fail_agent", failing_agent)
    result = await agent_manager.execute_agent("fail_agent", {})
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_invalid_agent(agent_manager):
    result = await agent_manager.execute_agent("nonexistent", {})
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_get_agent(agent_manager, simple_agent):
    agent_manager.register_agent("a1", simple_agent)
    agent = agent_manager.get_agent("a1")
    assert agent is not None


@pytest.mark.asyncio
async def test_duplicate_registration_raises_error(agent_manager, simple_agent):
    agent_manager.register_agent("dup", simple_agent)
    with pytest.raises(ValueError, match="already registered"):
        agent_manager.register_agent("dup", simple_agent)


@pytest.mark.asyncio
async def test_missing_identity_raises_error(agent_manager):
    async def orphan_agent(data, ctx):
        return {"ok": True}
    with pytest.raises(ValueError, match="not found in identity registry"):
        agent_manager.register_agent("unknown_agent", orphan_agent)


@pytest.mark.asyncio
async def test_unregister_agent(agent_manager, simple_agent):
    agent_manager.register_agent("test_agent", simple_agent)
    assert agent_manager.get_agent("test_agent") is not None
    agent_manager.unregister_agent("test_agent")
    assert agent_manager.get_agent("test_agent") is None


@pytest.mark.asyncio
async def test_get_all_agents(agent_manager, simple_agent):
    agent_manager.register_agent("a1", simple_agent)
    agent_manager.register_agent("a2", simple_agent)
    all_agents = agent_manager.get_all_agents()
    assert "a1" in all_agents
    assert "a2" in all_agents
    assert len(all_agents) == 2


@pytest.mark.asyncio
async def test_sync_agent_execution(agent_manager):
    def sync_agent(input_data, context):
        return {"sync": True}
    agent_manager.register_agent("sync_agent", sync_agent)
    result = await agent_manager.execute_agent("sync_agent", {})
    assert result["success"] is True
    assert result["result"]["sync"] is True
