import asyncio
import time

import pytest


@pytest.mark.asyncio
async def test_parallel_execution_speed(agent_manager):

    async def fast_agent(data, context):
        return {"ok": True}

    agent_manager.register_agent("a1", fast_agent)
    agent_manager.register_agent("a2", fast_agent)
    agent_manager.register_agent("a3", fast_agent)

    start = time.time()

    results = await asyncio.gather(
        agent_manager.execute_agent("a1", {}),
        agent_manager.execute_agent("a2", {}),
        agent_manager.execute_agent("a3", {}),
    )

    duration = time.time() - start

    assert all(result["success"] for result in results)
    assert duration < 1.0  # sanity check for async execution
