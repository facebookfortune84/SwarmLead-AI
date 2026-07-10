import pytest


@pytest.mark.asyncio
async def test_strategy_agent_success(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.strategy.strategy_agent import StrategyAgent

    config = ConfigLoader.load()
    agent = StrategyAgent("strategy_agent", config)

    # ✅ mock LLM response
    async def mock_generate(*args, **kwargs):
        return {
            "response": """
{
  "angles": ["angle1", "angle2"],
  "hooks": ["hook1", "hook2"],
  "summary": "test summary"
}
"""
        }

    agent.llm_client.generate = mock_generate

    result = await agent.run(
        {
            "product": "AI Tool",
            "audience": "developers",
            "goal": "increase adoption",
        }
    )

    assert result["success"] is True
    assert len(result["result"]["angles"]) == 2
    assert result["result"]["summary"] == "test summary"


@pytest.mark.asyncio
async def test_strategy_agent_fallback_parsing(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.strategy.strategy_agent import StrategyAgent

    config = ConfigLoader.load()
    agent = StrategyAgent("strategy_agent", config)

    # ✅ badly formatted output
    async def mock_generate(*args, **kwargs):
        return {"response": "This is not JSON but still useful output"}

    agent.llm_client.generate = mock_generate

    result = await agent.run(
        {
            "product": "AI Tool",
            "audience": "developers",
            "goal": "growth",
        }
    )

    assert result["success"] is True

    # ✅ fallback behavior validation
    assert result["result"]["angles"] == []
    assert result["result"]["hooks"] == []

    # ✅ FIXED: correct substring (no broken pattern)
    assert "useful output" in result["result"]["summary"]
