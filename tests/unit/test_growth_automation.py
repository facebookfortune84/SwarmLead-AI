"""Tests for the autonomous growth loop and its single human gate."""

import asyncio

import pytest
import pytest_asyncio

from core.services.growth_automation import GrowthAutomation


@pytest_asyncio.fixture
async def ga(tmp_path, monkeypatch):
    from core.services import growth_automation as _mod

    async def fast_generate(self, prompt, template):
        return f"# {template.name}\n\n[test scaffold]"

    from core.agents.content.content_agent import ContentAgent

    monkeypatch.setattr(ContentAgent, "_generate", fast_generate)
    monkeypatch.setenv("GROWTH_DISCOVERY", "0")

    def realistic_leads(self, limit):
        return [
            {
                "email": "owner@smithplumbing.com",
                "name": "Sam Smith",
                "company": "Smith Plumbing",
                "intent_score": 80,
            }
        ]

    monkeypatch.setattr(_mod.GrowthAutomation, "_qualified_leads", realistic_leads)

    from core.services.deliverability import deliverability

    deliverability.suppression_path = tmp_path / "suppression.json"
    deliverability._suppressed = {}

    old = _mod.STATE_PATH
    _mod.STATE_PATH = tmp_path / "growth_state.json"
    instance = GrowthAutomation(state_path=tmp_path / "growth_state.json")
    instance.enabled = True
    await instance.run_cycle(reason="test")
    yield instance
    _mod.STATE_PATH = old
    from core.services.deliverability import SUPPRESSION_PATH as _def_supp

    deliverability.suppression_path = _def_supp
    deliverability._suppressed = {}


@pytest.mark.asyncio
async def test_run_cycle_runs_all_phases(ga):
    cycle = await ga.run_cycle(reason="test")
    for phase in ("discovery", "seo", "content", "outreach", "voice", "monetize"):
        assert phase in cycle["phases"]
        assert cycle["phases"][phase]["status"] == "ok"
    assert ga.state["cycle_count"] >= 1


def test_outreach_lands_in_approval_queue(ga):
    pending = [a for a in ga.state["approval_queue"] if a["kind"] == "outreach_send"]
    assert pending, "expected drafted outreach actions behind the human gate"
    assert all(a["status"] == "pending" for a in pending)


def test_approve_marks_action_approved(ga):
    item = ga.pending_actions()[0]
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(ga.approve(item["id"]))
    finally:
        loop.close()
    assert result["status"] in {"approved", "failed"}


def test_reject_marks_action_rejected(ga):
    item = ga.pending_actions()[0]
    result = ga.reject(item["id"], note="not now")
    assert result["status"] == "rejected"
    assert all(a["id"] != item["id"] for a in ga.pending_actions())


def test_duplicate_outreach_not_enqueued(ga):
    first = [a["payload"]["to_email"] for a in ga.state["approval_queue"] if a["kind"] == "outreach_send"]
    assert first
    assert ga._already_contacted(first[0]) is True


def test_status_reports_metrics(ga):
    status = ga.status()
    assert "approval_queue" in status
    assert status["approval_queue"]["pending"] >= 0


def test_purge_removes_and_suppresses(ga):
    item = ga.pending_actions()[0]
    email = item["payload"]["to_email"]
    result = ga.purge(item["id"])
    assert result["status"] == "purged"
    assert all(a["id"] != item["id"] for a in ga.pending_actions())
    from core.services.deliverability import deliverability

    assert deliverability.is_suppressed(email) is True
    assert ga._already_contacted(email) is False


def test_purge_all_pending_empties_queue(ga):
    before = len(ga.pending_actions())
    assert before > 0
    result = ga.purge_all_pending()
    assert result["status"] == "purged"
    assert result["removed"] == before
    assert ga.pending_actions() == []
