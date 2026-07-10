import pytest


@pytest.mark.asyncio
async def test_full_agent_pipeline(router, agent_manager):

    async def strategy_agent(data, context):
        return {"strategy": "defined"}

    async def audience_agent(data, context):
        return {"audience": "expanded"}

    agent_manager.register_agent("strategy", strategy_agent)
    agent_manager.register_agent("audience", audience_agent)

    async def pipeline(data, context):
        res1 = await agent_manager.execute("strategy", data)
        res2 = await agent_manager.execute("audience", res1["result"])

        return {
            "strategy": res1,
            "audience": res2
        }

    router.register_pipeline("campaign_pipeline", pipeline)

    result = await router.route("campaign_pipeline", {"idea": "test"})

    assert result["type"] == "pipeline"
    assert "strategy" in result["result"]
    assert "audience" in result["result"]