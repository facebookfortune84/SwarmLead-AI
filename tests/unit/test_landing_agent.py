import sys
from pathlib import Path
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core.agents.landing.landing_agent import LandingAgent, LandingFlow, VisitorContext


@pytest.fixture
def agent():
    return LandingAgent(name="landing", config={})


def test_flows_registered(agent):
    assert set(agent.flows.keys()) == {
        "lead_qualification",
        "founder_discovery",
        "business_launch",
        "product_recommendation",
    }


def test_visitor_context_defaults():
    vc = VisitorContext(visitor_id="v1")
    assert vc.visitor_id == "v1"
    assert vc.referrer is None
    assert vc.session_duration == 0
    assert vc.return_visitor is False


def test_landing_flow_dataclass():
    flow = LandingFlow(
        name="Test",
        trigger="proactive",
        greeting="hi",
        questions=["q1"],
        qualification_criteria={},
        next_steps=["a"],
    )
    assert flow.name == "Test"
    assert flow.trigger == "proactive"


@pytest.mark.asyncio
async def test_greet_visitor_no_voice(agent):
    result = await agent.greet_visitor(
        "session_1",
        {"is_returning": True},
    )
    assert result["session_id"] == "session_1"
    assert result["flow"] == "lead_qualification"
    assert result["text"]
    assert result["audio"] is None
    assert result["options"]


@pytest.mark.asyncio
async def test_greet_visitor_with_voice(agent):
    fake_voice = AsyncMock()
    fake_voice.text_to_speech = AsyncMock(return_value=b"audio-bytes")
    agent.voice_agent = fake_voice
    result = await agent.greet_visitor("s", {"is_returning": False, "source": "founder_community"})
    assert result["flow"] == "founder_discovery"
    fake_voice.text_to_speech.assert_awaited_once()
    assert result["audio"] == b"audio-bytes"


def test_select_flow_returning():
    agent = LandingAgent("l", {})
    assert agent._select_flow({"is_returning": True}) == "lead_qualification"


def test_select_flow_founder():
    agent = LandingAgent("l", {})
    assert agent._select_flow({"source": "founder_community"}) == "founder_discovery"


def test_select_flow_business_keyword():
    agent = LandingAgent("l", {})
    assert agent._select_flow({"keywords": ["startup", "funding"]}) == "business_launch"


def test_select_flow_default():
    agent = LandingAgent("l", {})
    assert agent._select_flow({}) == "product_recommendation"


def test_generate_greeting_known_flow():
    agent = LandingAgent("l", {})
    greeting = agent._generate_greeting({}, "business_launch")
    assert "Ready to launch" in greeting


def test_generate_greeting_unknown_flow():
    agent = LandingAgent("l", {})
    assert agent._generate_greeting({}, "nope") == "Welcome! How can I help you today?"


def test_get_flow_options_default():
    agent = LandingAgent("l", {})
    assert agent._get_flow_options("nope") == ["Explore features", "Talk to human", "Schedule demo"]


@pytest.mark.asyncio
async def test_execute_flow_unknown(agent):
    result = await agent.execute_flow("bogus", "s", {})
    assert result == {"error": "Unknown flow: bogus"}


@pytest.mark.asyncio
async def test_execute_flow_known(agent):
    result = await agent.execute_flow("lead_qualification", "s", {})
    assert result["flow"] == "continue"
    assert result["question"].startswith("company_stage:")


@pytest.mark.asyncio
async def test_flow_lead_qualification(agent):
    result = await agent._flow_lead_qualification("s", {})
    assert result["flow"] == "continue"
    assert "Options: Pre-seed, Seed, Series A, Growth" in result["question"]


@pytest.mark.asyncio
async def test_flow_founder_discovery(agent):
    result = await agent._flow_founder_discovery("s", {})
    assert result["key"] == "vision"
    assert "What's your big vision?" in result["question"]


@pytest.mark.asyncio
async def test_flow_business_launch(agent):
    result = await agent._flow_business_launch("s", {})
    assert result["key"] == "entity_type"
    assert "LLC" in result["question"]


@pytest.mark.asyncio
async def test_flow_product_recommendation(agent):
    result = await agent._flow_product_recommendation("s", {})
    assert result["key"] == "category"
    assert "CRM" in result["question"]


@pytest.mark.asyncio
async def test_execute_conversation_flow_empty_questions(agent):
    result = await agent._execute_conversation_flow("s", "lead_qualification", [])
    assert result == {"flow": "completed", "results": {}}
