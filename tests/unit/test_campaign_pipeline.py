import pytest


@pytest.mark.asyncio
async def test_pipeline_with_outreach():
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {
            "success": True,
            "result": {
                "angles": ["angle1"],
            },
        }

    async def mock_outreach(*args, **kwargs):
        return {
            "success": True,
            "result": {
                "messages": ["msg1"],
            },
        }

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    result = await pipeline.run(
        {
            "product": "AI Tool",
            "audience": "developers",
            "goal": "growth",
        }
    )

    assert result["success"] is True
    assert result["outreach"]["messages"] == ["msg1"]
    assert "learning" in result


@pytest.mark.asyncio
async def test_pipeline_missing_strategy_result():
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {"success": True}

    async def mock_outreach(*args, **kwargs):
        return {"success": True, "result": {}}

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is True
    assert result["strategy"] == {}


@pytest.mark.asyncio
async def test_pipeline_missing_outreach_result():
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {"success": True, "result": {"angles": ["a"]}}

    async def mock_outreach(*args, **kwargs):
        return {"success": True}

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is True
    assert result["outreach"] == {}


@pytest.mark.asyncio
async def test_pipeline_outreach_failure():
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {"success": True, "result": {"angles": ["a"]}}

    async def failing_outreach(*args, **kwargs):
        raise ValueError("outreach failed")

    pipeline.strategy_agent.run = failing_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is False


@pytest.mark.asyncio
async def test_pipeline_triggers_feedback(monkeypatch):
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    called = {"hit": False}

    def fake_record(*args, **kwargs):
        called["hit"] = True

        return {
            "updated": True,
            "weights": {},
        }

    monkeypatch.setattr(
        pipeline.feedback,
        "record_result",
        fake_record,
    )

    async def mock_strategy(*args, **kwargs):
        return {"success": True, "result": {"angles": ["angle1"]}}

    async def mock_outreach(*args, **kwargs):
        return {"success": True, "result": {"messages": ["msg1"]}}

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    await pipeline.run(
        {
            "product": "AI Tool",
            "audience": "developers",
            "goal": "growth",
        }
    )

    assert called["hit"] is True
