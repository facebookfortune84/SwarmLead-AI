import pytest


@pytest.mark.asyncio
async def test_full_agent_pipeline(router, agent_manager):

    async def strategy_agent(data, context):
        return {"strategy": "defined"}

    async def audience_agent(data, context):
        return {"audience": "expanded"}

    agent_manager.register_agent("strategy", strategy_agent)
    agent_manager.register_agent("audience", audience_agent)

    res1 = await router.route("strategy", {"idea": "test"})

    assert res1["success"] is True
    assert res1["result"]["strategy"] == "defined"

    res2 = await router.route("audience", res1["result"])

    assert res2["success"] is True
    assert res2["result"]["audience"] == "expanded"
