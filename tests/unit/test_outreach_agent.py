from unittest.mock import AsyncMock, Mock

import pytest

from configs.config_loader import ConfigLoader
from core.agents.outreach.outreach_agent import OutreachAgent
from core.analytics.event_tracker import EventTracker
from core.memory.long_term_memory.long_term_memory import LongTermMemory


@pytest.fixture
def config():
    return ConfigLoader.load()


@pytest.fixture
def agent(config, tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))

    tracker = EventTracker()

    return OutreachAgent(
        "outreach_agent",
        config,
        long_term_memory=memory,
        event_tracker=tracker,
    )


@pytest.mark.asyncio
async def test_outreach_agent_success(agent):
    agent.call_llm = AsyncMock(
        return_value="""
{
    "messages": [
        "msg1",
        "msg2",
        "msg3"
    ]
}
"""
    )

    result = await agent.execute(
        {"angles": ["ang1e1", "angle2"]},
        {
            "product": "AI Tool",
            "audience": "developers",
        },
        None,
    )
    assert len(result["messages"]) == 3
    assert result is not None


@pytest.mark.asyncio
async def test_outreach_agent_fallback_parsing(
    agent,
):
    agent.call_llm = AsyncMock(return_value="fallback")
    result = await agent.execute(
        {"angles": ["angle1"]},
        {},
        None,
    )
    assert result["messages"][0] == "fallback"


@pytest.mark.asyncio
async def test_outreach_agent_empty_angles(agent):
    agent.call_llm = AsyncMock(return_value=""" {"messages": ["fallback"]}""")
    result = await agent.execute(
        {},
        {},
        None,
    )
    assert result["messages"][0] == "fallback"


@pytest.mark.asyncio
async def test_outreach_agent_trace_propagation(
    agent,
):
    captured = {}

    async def fake_llm(
        prompt,
        trace_id=None,
    ):
        captured["trace_id"] = trace_id

        return """
{
    "messages": [
        "ok"
    ]
}    
"""

    agent.call_llm = fake_llm

    await agent.execute(
        {"angles": ["a"]},
        {},
        "trace-123",
    )

    assert captured["trace_id"] == "trace-123"


@pytest.mark.asyncio
async def test_vector_store_called(
    agent,
):
    agent.vector_store.search = Mock(return_value=[])

    agent.call_llm = AsyncMock(return_value='{"messages":[]}')

    await agent.execute(
        {"angles": ["angle1"]},
        {
            "product": "AI",
            "audience": "developers",
        },
        None,
    )

    agent.vector_store.search.assert_called_once()


@pytest.mark.asyncio
async def test_feedback_memories_added_to_prompt(
    agent,
):
    agent.long_term_memories_added_to_prompt(
        content=("Personalized first lines outperform generic intros"),
        memory_type="feedback",
    )

    agent.vector_store.search = Mock(return_value=[])

    captured = {}

    async def fake_llm(
        prompt,
        trace_id=None,
    ):

        captured["prompt"] = prompt

        return '{"messages":["ok"]}'

    agent.call_llm = fake_llm

    await agent.execute(
        {},
        {},
        None,
    )

    assert "Personalized first lines" in captured["prompt"]


@pytest.mark.asyncio
async def test_tracks_outreach_events(
    agent,
):
    agent.call_llm = AsyncMock(return_value='{"messages":[]}')

    await agent.execute(
        {},
        {},
        "trace-1",
    )

    assert len(agent.event_tracker.filter("outreach_started")) == 1

    assert len(agent.event_tracker.filter("outreach_completed")) == 1


@pytest.mark.asyncio
async def test_tracks_errors(
    agent,
):
    agent.call_llm = AsyncMock(side_effect=RuntimeError("boom"))

    with pytest.raises(RuntimeError):
        await agent.execute(
            {},
            {},
            None,
        )

    errors = agent.event_tracker.filter("error")

    assert len(errors) == 1


def test_parse_response_valid_json(
    agent,
):

    result = agent._parse_response(
        """
{
    "messages": [
        "one",
        "two"
    ]
}
"""
    )

    assert result["messages"] == [
        "one",
        "two",
    ]


def test_parse_response_invalid_json(
    agent,
):
    result = agent._parse_response("fallback message")

    assert result["messages"] == ["fallback message"]
