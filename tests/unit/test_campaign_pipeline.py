import pytest

from core.analytics.event_tracker import EventTracker
from core.workflows.campaign_pipeline import CampaignPipeline


@pytest.mark.asyncio
async def test_pipeline_with_outreach():
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
    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {"success": True}

    async def mock_outreach(*args, **kwargs):
        return {
            "success": True,
            "result": {},
        }

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is True
    assert result["strategy"] == {}


@pytest.mark.asyncio
async def test_pipeline_missing_outreach_result():
    pipeline = CampaignPipeline()

    async def mock_strategy(*args, **kwargs):
        return {
            "success": True,
            "result": {
                "angles": ["a"],
            },
        }

    async def mock_outreach(*args, **kwargs):
        return {"success": True}

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    result = await pipeline.run({"product": "x"})

    assert result["success"] is True
    assert result["outreach"] == {}


@pytest.mark.asyncio
async def test_pipeline_outreach_failure():
    pipeline = CampaignPipeline()

    async def failing(*args, **kwargs):
        raise ValueError("outreach failed")

    pipeline.strategy_agent.run = failing

    result = await pipeline.run({"product": "x"})

    assert result["success"] is False


@pytest.mark.asyncio
async def test_pipeline_triggers_feedback(
    monkeypatch,
):
    pipeline = CampaignPipeline()

    called = {"hit": False}

    def fake_record(
        *args,
        **kwargs,
    ):
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

    async def mock_strategy(
        *args,
        **kwargs,
    ):
        return {
            "success": True,
            "result": {
                "angles": ["angle1"],
            },
        }

    async def mock_outreach(
        *args,
        **kwargs,
    ):
        return {
            "success": True,
            "result": {
                "messages": ["msg1"],
            },
        }

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


@pytest.mark.asyncio
async def test_campaign_events_emitted():
    tracker = EventTracker()

    pipeline = CampaignPipeline(
        event_tracker=tracker,
    )

    async def mock_strategy(
        *args,
        **kwargs,
    ):
        return {
            "success": True,
            "result": {
                "angles": ["a"],
            },
        }

    async def mock_outreach(
        *args,
        **kwargs,
    ):
        return {
            "success": True,
            "result": {
                "messages": ["m"],
            },
        }

    pipeline.strategy_agent.run = mock_strategy
    pipeline.outreach_agent.run = mock_outreach

    await pipeline.run(
        {"goal": "growth"},
        trace_id="pipeline-trace",
    )

    assert len(tracker.filter("campaign_started")) == 1

    assert len(tracker.filter("campaign_completed")) == 1


@pytest.mark.asyncio
async def test_campaign_failure_emits_error():
    tracker = EventTracker()

    pipeline = CampaignPipeline(
        event_tracker=tracker,
    )

    async def failing(
        *args,
        **kwargs,
    ):
        raise RuntimeError("boom")

    pipeline.strategy_agent.run = failing

    result = await pipeline.run(
        {"goal": "growth"},
        trace_id="trace-error",
    )

    assert result["success"] is False

    errors = tracker.filter("error")

    assert len(errors) == 1
