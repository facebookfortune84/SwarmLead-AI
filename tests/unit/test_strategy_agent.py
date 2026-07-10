import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

# Ensure repo root is on sys.path so `core` package can be imported in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core.agents.strategy.strategy_agent import StrategyAgent  # type: ignore
from core.analytics.event_tracker import EventTracker
from core.memory.long_term_memory.long_term_memory import LongTermMemory


@pytest.fixture
def config():
    return {}


@pytest.fixture
def agent(config):
    agent = StrategyAgent(
        name="strategy",
        config=config,
    )

    return agent


@pytest.mark.asyncio
async def test_execute_retrieves_memory(agent):
    """
    Ensures memory retrieval is called using
    product/audience/goal query.
    """

    agent.selector.select = Mock(return_value=["archetype_a"])

    agent.asset_loader.build_context = Mock(return_value="asset context")

    agent.vector_store.search = Mock(return_value=[{"text": "historical learning"}])

    agent.call_llm = AsyncMock(
        return_value="""
        {
            "angles":["A"],
            "hooks":["H"],
            "summary":"S"
        }
        """
    )

    await agent.execute(
        {
            "product": "CRM",
            "audience": "Founders",
            "goal": "Leads",
        },
        {},
        "trace-123",
    )

    agent.vector_store.search.assert_called_once_with(
        "CRM Founders Leads",
        top_k=3,
    )


@pytest.mark.asyncio
async def test_execute_includes_memory_in_prompt(agent):
    """
    Verifies retrieved memories become
    part of LLM prompt.
    """

    agent.selector.select = Mock(return_value=["archetype_a"])

    agent.asset_loader.build_context = Mock(return_value="asset context")

    agent.vector_store.search = Mock(
        return_value=[
            {"text": "Memory One"},
            {"text": "Memory Two"},
        ]
    )

    captured_prompt = {}

    async def fake_llm(prompt, trace_id=None):
        captured_prompt["prompt"] = prompt

        return """
        {
            "angles":["A"],
            "hooks":["H"],
            "summary":"S"
        }
        """

    agent.call_llm = fake_llm

    await agent.execute(
        {
            "product": "Product",
            "audience": "Audience",
            "goal": "Goal",
        },
        {},
        None,
    )

    assert "Memory One" in captured_prompt["prompt"]
    assert "Memory Two" in captured_prompt["prompt"]


@pytest.mark.asyncio
async def test_execute_handles_no_memory_results(agent):
    agent.selector.select = Mock(return_value=["archetype_a"])

    agent.asset_loader.build_context = Mock(return_value="asset context")

    agent.vector_store.search = Mock(return_value=[])

    agent.call_llm = AsyncMock(
        return_value="""
        {
            "angles":["A"],
            "hooks":["H"],
            "summary":"S"
        }
        """
    )

    result = await agent.execute(
        {
            "product": "Product",
            "audience": "Audience",
            "goal": "Goal",
        },
        {},
        None,
    )

    assert result["angles"] == ["A"]
    assert result["hooks"] == ["H"]
    assert result["summary"] == "S"


@pytest.mark.asyncio
async def test_execute_returns_parsed_json(agent):
    agent.selector.select = Mock(return_value=["archetype_a"])

    agent.asset_loader.build_context = Mock(return_value="asset context")

    agent.vector_store.search = Mock(return_value=[])

    agent.call_llm = AsyncMock(
        return_value="""
        {
            "angles":["Angle 1","Angle 2"],
            "hooks":["Hook 1"],
            "summary":"Winning strategy"
        }
        """
    )

    result = await agent.execute(
        {
            "product": "CRM",
            "audience": "SMBs",
            "goal": "Lead gen",
        },
        {},
        None,
    )

    assert result["angles"] == [
        "Angle 1",
        "Angle 2",
    ]

    assert result["hooks"] == ["Hook 1"]

    assert result["summary"] == "Winning strategy"


def test_parse_response_handles_invalid_json(agent):
    result = agent._parse_response("plain text response")

    assert result["angles"] == []
    assert result["hooks"] == []
    assert result["summary"] == "plain text response"


def test_parse_response_handles_partial_json(agent):
    result = agent._parse_response(
        """
        {
            "summary":"Only summary"
        }
        """
    )

    assert result["angles"] == []
    assert result["hooks"] == []
    assert result["summary"] == "Only summary"


@pytest.mark.asyncio
async def test_execute_uses_top_k_three(agent):
    agent.selector.select = Mock(return_value=[])
    agent.asset_loader.build_context = Mock(return_value="")
    agent.call_llm = AsyncMock(return_value='{"angles":[],"hooks":[],"summary":"ok"}')

    agent.vector_store.search = Mock(return_value=[])

    await agent.execute(
        {
            "product": "P",
            "audience": "A",
            "goal": "G",
        },
        {},
        None,
    )

    _, kwargs = agent.vector_store.search.call_args

    assert kwargs["top_k"] == 3


@pytest.mark.asyncio
async def test_tracks_strategy_started_and_completed(
    config,
    tmp_path,
):

    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()
    agent = StrategyAgent(
        "strategy",
        config,
        long_term_memory=memory,
        event_tracker=tracker,
    )

    agent.selector.select = Mock(return_value=[])
    agent.asset_loader.build_context = Mock(return_value="")
    agent.vector_store.search = Mock(return_value=[])

    agent.call_llm = AsyncMock(return_value='{"angles":[], "hooks":[], "summary":"ok"}')

    await agent.execute(
        {},
        {},
        "trace-123",
    )

    assert len(tracker.filter("strategy_started")) == 1

    assert len(tracker.filter("strategy_completed")) == 1


@pytest.mark.asyncio
async def test_feedback_memories_are_added_to_prompt(
    config,
    tmp_path,
):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    memory.add_learning(
        content="ROI messaging wins",
        memory_type="feedback",
    )
    tracker = EventTracker()

    agent = StrategyAgent(
        "strategy",
        config,
        long_term_memory=memory,
        event_tracker=tracker,
    )

    agent.selector.select = Mock(return_value=[])
    agent.asset_loader.build_context = Mock(return_value="")
    agent.vector_store.search = Mock(return_value=[])

    captured_prompt = {}

    async def fake_call(prompt, trace_id=None):
        captured_prompt["prompt"] = prompt

        return '{"angles":[], "hooks":[], "summary":"ok"}'

    agent.call_llm = fake_call

    await agent.execute(
        {},
        {},
        None,
    )

    assert "ROI messaging wins" in captured_prompt["prompt"]


@pytest.mark.asyncio
async def test_tracks_errors(
    config,
    tmp_path,
):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    agent = StrategyAgent(
        "strategy",
        config,
        long_term_memory=memory,
        event_tracker=tracker,
    )

    agent.selector.select = Mock(side_effect=ValueError("boom"))

    with pytest.raises(ValueError):
        await agent.execute(
            {},
            {},
            "trace-err",
        )

    errors = tracker.filter("error")

    assert len(errors) == 1
