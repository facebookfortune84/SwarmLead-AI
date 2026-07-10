import pytest


@pytest.mark.asyncio
async def test_pipeline_with_outreach(monkeypatch):
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    # mock strategy
    async def mock_strategy(*args, **kwargs):
        return {
            "success": True,
            "result": {
                "angles": ["angle1"],
            },
        }

    # mock outreach
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
    assert "strategy" in result
    assert "outreach" in result
    assert result["outreach"]["messages"] == ["msg1"]


@pytest.mark.asyncio
async def test_pipeline_missing_strategy_result(monkeypatch):
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {"success": True}  # ✅ NO "result"

    async def mock_outreach(*args, **kwargs):
        return {"success": True, "result": {}}

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is True
    assert result["strategy"] == {}  # ✅ fallback path


@pytest.mark.asyncio
async def test_pipeline_missing_outreach_result(monkeypatch):
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {"success": True, "result": {"angles": ["a"]}}

    async def mock_outreach(*args, **kwargs):
        return {"success": True}  # ✅ NO "result"

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is True
    assert result["outreach"] == {}  # ✅ fallback path


@pytest.mark.asyncio
async def test_pipeline_outreach_failure(monkeypatch):
    from core.workflows.campaign_pipeline import CampaignPipeline

    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {"success": True, "result": {"angles": ["a"]}}

    async def failing_outreach(*args, **kwargs):
        raise ValueError("outreach failed")

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = failing_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is False
    assert "error" in result
