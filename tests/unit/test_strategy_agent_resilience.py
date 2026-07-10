import pytest


@pytest.mark.asyncio
async def test_strategy_agent_handles_source_only(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.strategy.strategy_agent import StrategyAgent

    config = ConfigLoader.load()
    agent = StrategyAgent("strategy_agent", config)

    # monkeypatch loader
    agent.asset_loader.data = {"archetypes": {"architect": [{"source": "legacy fallback"}]}}

    async def fake_llm(prompt, **kwargs):
        return '{"angles": [], "hooks": [], "summary": "ok"}'

    monkeypatch.setattr(agent, "call_llm", fake_llm)

    result = await agent.execute(
        {"product": "x", "audience": "y", "goal": "growth"},
        context={},
        trace_id=None,
    )

    assert result["summary"] == "ok"


@pytest.mark.asyncio
async def test_strategy_agent_handles_empty_assets(monkeypatch):
    from configs.config_loader import ConfigLoader
    from core.agents.strategy.strategy_agent import StrategyAgent

    config = ConfigLoader.load()
    agent = StrategyAgent("strategy_agent", config)

    agent.asset_loader.data = {"archetypes": {}}

    async def fake_llm(prompt, **kwargs):
        return '{"angles": [], "hooks": [], "summary": "ok"}'

    monkeypatch.setattr(agent, "call_llm", fake_llm)

    result = await agent.execute(
        {"product": "x", "audience": "y", "goal": "growth"},
        context={},
        trace_id=None,
    )

    assert result["summary"] == "ok"
