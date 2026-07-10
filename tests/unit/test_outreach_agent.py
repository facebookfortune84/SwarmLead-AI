import pytest


@pytest.mark.asyncio
async def test_outreach_agent_success(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.outreach.outreach_agent import OutreachAgent

    config = ConfigLoader.load()
    agent = OutreachAgent("outreach_agent", config)

    # ✅ mock valid JSON response
    async def mock_generate(*args, **kwargs):
        return {
            "response": """
{
  "messages": ["msg1", "msg2", "msg3"]
}
"""
        }

    agent.llm_client.generate = mock_generate

    result = await agent.run(
        {"angles": ["angle1", "angle2"]},
        context={
            "product": "AI Tool",
            "audience": "developers",
        },
    )

    assert result["success"] is True
    assert len(result["result"]["messages"]) == 3
    assert result["result"]["messages"][0] == "msg1"


@pytest.mark.asyncio
async def test_outreach_agent_fallback_parsing(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.outreach.outreach_agent import OutreachAgent

    config = ConfigLoader.load()
    agent = OutreachAgent("outreach_agent", config)

    # ✅ non-JSON response → fallback path
    async def mock_generate(*args, **kwargs):
        return {"response": "Simple outreach message fallback"}

    agent.llm_client.generate = mock_generate

    result = await agent.run(
        {"angles": ["angle1"]},
        context={
            "product": "AI Tool",
            "audience": "developers",
        },
    )

    assert result["success"] is True
    assert isinstance(result["result"]["messages"], list)

    # ✅ fallback wraps raw text
    assert result["result"]["messages"][0] == "Simple outreach message fallback"


@pytest.mark.asyncio
async def test_outreach_agent_empty_angles(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.outreach.outreach_agent import OutreachAgent

    config = ConfigLoader.load()
    agent = OutreachAgent("outreach_agent", config)

    async def mock_generate(*args, **kwargs):
        return {
            "response": """
{
  "messages": ["fallback message"]
}
"""
        }

    agent.llm_client.generate = mock_generate

    result = await agent.run(
        {},  # ✅ no angles provided
        context={
            "product": "AI Tool",
            "audience": "developers",
        },
    )

    assert result["success"] is True
    assert "messages" in result["result"]


@pytest.mark.asyncio
async def test_outreach_agent_trace_propagation(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.outreach.outreach_agent import OutreachAgent

    config = ConfigLoader.load()
    agent = OutreachAgent("outreach_agent", config)

    captured = {}

    async def mock_generate(prompt, model=None, trace_id=None):
        captured["trace_id"] = trace_id
        return {"response": '{"messages": ["ok"]}'}

    agent.llm_client.generate = mock_generate

    trace_id = "outreach-trace"

    await agent.run(
        {"angles": ["angle1"]},
        context={
            "product": "AI Tool",
            "audience": "developers",
        },
        trace_id=trace_id,
    )

    # ✅ ensures trace flows into LLM layer
    assert captured["trace_id"] == trace_id
