"""Tests for the Nurture Engine and Outreach Maximizer services."""

import pytest

from core.services.nurture_engine import NURTURE_TOUCHES, nurture_engine
from core.services.outreach_maximization import LEVERS, outreach_maximizer

# ------------------------------------------------------------------ nurture


def test_plan_has_five_touches():
    plan = nurture_engine.plan("lead@acme.com")
    assert plan["total"] == 5
    assert plan["touches"][0]["label"] == "intro"
    assert plan["touches"][-1]["label"] == "breakup"


def test_advance_cadence():
    step1 = nurture_engine.advance(0)
    assert step1["next"]["seq"] == 1
    final = nurture_engine.advance(5)
    assert final["next"] is None
    assert final["is_final"] is True


def test_reactivation_threshold():
    assert nurture_engine.should_reactivate(20) is False
    assert nurture_engine.should_reactivate(22) is True


@pytest.mark.parametrize(
    "reply,action",
    [
        ("unsubscribe please", "suppress"),
        ("yes let's book a call", "escalate_to_closer"),
        ("no thanks too expensive", "winback_or_mark_lost"),
        ("how much does it cost?", "answer_and_offer_demo"),
        ("", "continue_cadence"),
        ("some random reply", "human_review"),
    ],
)
def test_reply_classification(reply, action):
    out = nurture_engine.apply(reply)
    assert out["action"] == action


def test_status_snapshot():
    st = nurture_engine.status()
    assert st["touches"] == len(NURTURE_TOUCHES)


# -------------------------------------------------------------- maximizer


def test_catalog_has_18_levers():
    assert len(LEVERS) >= 18
    assert outreach_maximizer.count() == len(LEVERS)


def test_score_band_ideal_for_hot_lead():
    score = outreach_maximizer.score(
        {"email": "owner@acme.com", "company": "Acme Co", "intent_score": 95,
         "details": {"signals": {"budget": True, "need": True, "authority": True, "timeline": True}}}
    )
    assert score["score"] >= 80
    assert score["band"] == "ideal"


def test_score_cool_for_cold_lead():
    score = outreach_maximizer.score({"email": "", "intent_score": 0})
    assert score["band"] == "cool"


def test_applicable_levers_sorted_by_relevance():
    lead = {"email": "a@b.co", "intent_score": 70, "details": {"signals": {"budget": True}}}
    levers = outreach_maximizer.applicable_levers(lead)
    assert levers
    assert levers[0]["relevance"] >= levers[-1]["relevance"]


def test_maximize_returns_draft_and_counts():
    lead = {"email": "owner@biz.com", "name": "Alice", "company": "BizCo", "intent_score": 90,
            "source": "voice", "details": {"signals": {"budget": True, "need": True, "authority": True}}}
    out = outreach_maximizer.maximize(lead)
    assert out["score"] > 0
    assert out["ready"] is True
    assert out["suggested_subject"]
    assert out["_counts"]["total_levers"] == len(LEVERS)


def test_all_levers_have_keys():
    for lever in outreach_maximizer.all_levers():
        assert set(lever) >= {"key", "label", "category", "action"}
        assert lever["category"] in {"accuracy", "acquisition", "nurture", "conversion"}
