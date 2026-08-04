"""Unit tests for the growth-loop traffic phase (launch traffic drafts)."""

import pytest

from core.services.growth_automation import GrowthAutomation


@pytest.fixture
def growth(tmp_path):
    return GrowthAutomation(state_path=tmp_path / "growth_state.json")


@pytest.mark.asyncio
async def test_traffic_phase_queues_drafts_during_launch_week(growth):
    result = await growth._phase_traffic()
    assert result["status"] == "ok"
    assert result["drafts_queued"] >= 1
    kinds = {a["kind"] for a in growth.pending_actions()}
    assert "traffic_post" in kinds


@pytest.mark.asyncio
async def test_traffic_phase_deduplicates_across_cycles(growth):
    await growth._phase_traffic()
    first = len(growth.pending_actions())
    await growth._phase_traffic()
    second = len(growth.pending_actions())
    assert second == first  # no duplicate drafts


@pytest.mark.asyncio
async def test_traffic_phase_respects_cycle_cap(growth):
    await growth._phase_traffic()
    queued = [
        a for a in growth.pending_actions() if a["kind"] == "traffic_post"
    ]
    assert len(queued) <= 2


@pytest.mark.asyncio
async def test_approve_traffic_post_marks_approved(growth):
    await growth._phase_traffic()
    action = next(
        a for a in growth.pending_actions() if a["kind"] == "traffic_post"
    )
    result = await growth.approve(action["id"])
    assert result["status"] == "approved"
    assert result["result"]["status"] == "approved_for_manual_post"
    assert "share_links" in result["result"]
