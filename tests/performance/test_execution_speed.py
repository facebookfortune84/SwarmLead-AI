import pytest
import time


@pytest.mark.asyncio
async def test_parallel_execution_speed(agent_manager):

    async def fast_agent(data, context):
        return {"ok": True}

    agent_manager.register_agent("a1", fast_agent)
    agent_manager.register_agent("a2", fast_agent)
    agent_manager.register_agent("a3", fast_agent)

    start = time.time()

    await agent_manager.execute_batch({
        "a1": {},
        "a2": {},
        "a3": {},
    })

    duration = time.time() - start

    assert duration < 1.0  # sanity check for async execution