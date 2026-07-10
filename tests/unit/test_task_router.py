import pytest


@pytest.mark.asyncio
async def test_route_to_registered_agent(router, agent_manager, simple_agent):
    agent_manager.register_agent("agent1", simple_agent)
    router.register_route("task1", "agent1")

    result = await router.route("task1", {"x": 1})

    assert result["type"] == "agent"
    assert result["agent"] == "agent1"
    assert result["result"]["success"] is True


@pytest.mark.asyncio
async def test_pipeline_priority(router):
    async def pipeline(data, context):
        return {"pipeline": True}

    router.register_pipeline("task1", pipeline)

    result = await router.route("task1", {})

    assert result["type"] == "pipeline"
    assert result["result"]["pipeline"] is True


@pytest.mark.asyncio
async def test_missing_route(router):
    with pytest.raises(ValueError):
        await router.route("missing", {})


@pytest.mark.asyncio
async def test_pipeline_overrides_route(router, agent_manager, simple_agent):
    agent_manager.register_agent("agent1", simple_agent)

    router.register_route("task1", "agent1")

    async def pipeline(data, context):
        return {"override": True}

    router.register_pipeline("task1", pipeline)

    result = await router.route("task1", {})

    assert result["type"] == "pipeline"


@pytest.mark.asyncio
async def test_list_routes_and_pipelines(router, agent_manager, simple_agent):
    agent_manager.register_agent("agent1", simple_agent)

    router.register_route("task1", "agent1")

    async def dummy_pipeline(data, context):
        return {"ok": True}

    router.register_pipeline("pipeline1", dummy_pipeline)

    routes = router.list_routes()
    pipelines = router.list_pipelines()

    assert "task1" in routes
    assert "pipeline1" in pipelines
