"""
Integration Test — Onboarding Flow

Verifies OnboardingAgent processes steps correctly, validates
required fields, and progresses through the full 6-step flow.
"""

import pytest

from core.agents.onboarding.onboarding_agent import OnboardingAgent


@pytest.fixture
def agent():
    return OnboardingAgent(name="test_onboarding", config={})


@pytest.mark.asyncio
async def test_full_onboarding_flow(agent):
    result = await agent.start_onboarding(
        session_id="test_session",
        user_context={"source": "landing_page"},
    )

    assert result["step"] == "welcome"
    assert result["next_step"] == "business_profile"
    assert result["text"] is not None

    steps_data = [
        ("business_profile", {"company_name": "TestCo", "industry": "tech", "description": "AI platform"}),
        ("goals", {"primary_goal": "launch", "target_metric": "revenue", "timeline": "3 months"}),
        ("voice_setup", {"voice_id": "default", "language": "en"}),
        ("integrations", {}),
    ]

    for step, input_data in steps_data:
        result = await agent.process_step(step, input_data)
        assert result["step"] == step
        assert result["completed"] is True
        assert result["next_step"] is not None or step == "launch"

    complete = await agent.complete_onboarding("test_session")
    assert complete["completed"] is True
    assert "next_steps" in complete


@pytest.mark.asyncio
async def test_onboarding_missing_required_fields(agent):
    result = await agent.process_step("business_profile", {"company_name": "TestCo"})

    assert "error" in result
    assert "Missing required fields" in result["error"]


@pytest.mark.asyncio
async def test_onboarding_unknown_step(agent):
    result = await agent.process_step("nonexistent_step", {})

    assert "error" in result
    assert "Unknown step" in result["error"]


@pytest.mark.asyncio
async def test_onboarding_progress_tracking(agent):
    await agent.start_onboarding("progress_session", {})

    progress = await agent.get_progress("progress_session")
    assert "current_step" in progress
    assert "total_steps" in progress
    assert progress["total_steps"] == 6
