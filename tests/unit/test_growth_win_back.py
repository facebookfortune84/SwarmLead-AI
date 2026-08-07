"""
Unit tests for the monetize-phase win-back inside the growth loop:

- priority quoting: best leads are quoted first
- win-back: recently-lost deals get an incentive quote
- hot leads get annual-first (2-months-free) quotes
"""

import pytest

from tests.unit.test_growth_automation_extra import _make_instance


def _make_win_back_offer():
    def offer_for(lead=None, **kwargs):
        return {
            "tier": "growth",
            "billing": "annual"
            if kwargs.get("annual_first", False) or kwargs.get("billing") == "annual"
            else "monthly",
            "checkout_url": "https://checkout.stripe.com/c/wb",
            "message": "Your workspace is provisioned and ready",
        }

    return offer_for


def test_priority_quote_leads_sorts_best_first(tmp_path, monkeypatch):
    instance = _make_instance(tmp_path, monkeypatch)
    instance._high_intent_leads = lambda limit: [
        {"email": "low@x.com", "intent_score": 70, "company": "Tiny Shop"},
        {"email": "high@x.com", "intent_score": 95, "company": "Pix Group LLC"},
        {"email": "mid@x.com", "intent_score": 85, "company": "Lane Co"},
    ]
    picked = [lead["email"] for lead in instance._priority_quote_leads(limit=2)]
    assert picked[0] == "high@x.com"  # highest intent + company-size boost
    assert picked[1] == "mid@x.com"


def test_priority_quote_leads_skips_already_quoted(tmp_path, monkeypatch):
    instance = _make_instance(tmp_path, monkeypatch)
    instance._enqueue(
        "quote_send",
        {"to_email": "hot@x.com", "subject": "s", "body": "b", "tier": "growth"},
    )
    instance._high_intent_leads = lambda limit: [
        {"email": "hot@x.com", "intent_score": 99, "company": ""},
        {"email": "next@x.com", "intent_score": 80, "company": ""},
    ]
    picked = [lead["email"] for lead in instance._priority_quote_leads(limit=2)]
    assert "hot@x.com" not in picked
    assert picked == ["next@x.com"]


def test_win_back_prepares_incentive_quote(tmp_path, monkeypatch):
    import core.services.sales_pipeline as sp_mod
    from core.services.monetization import monetization

    class FakePipeline:
        def list_deals(self, stage=None, limit=None):
            if stage == "closed_lost":
                return [
                    {
                        "email": "lost@x.com",
                        "amount_cents": 9900,
                        "intent_score": 70,
                        "closed_at": "2026-07-20T00:00:00",
                    }
                ]
            return []

    monkeypatch.setattr(sp_mod, "sales_pipeline", FakePipeline())
    monkeypatch.setattr(monetization, "offer_for", _make_win_back_offer())

    instance = _make_instance(tmp_path, monkeypatch)
    count = instance._win_back_quotes(limit=1)

    assert count == 1
    actions = [
        a
        for a in instance.state.get("approval_queue", [])
        if a["kind"] == "quote_send" and a["payload"]["to_email"] == "lost@x.com"
    ]
    assert actions
    assert actions[0]["payload"]["incentive_pct"] == 20
    assert actions[0]["payload"]["checkout_url"]


def test_win_back_skips_old_lost_deals(tmp_path, monkeypatch):
    import core.services.sales_pipeline as sp_mod

    class FakePipeline:
        def list_deals(self, stage=None, limit=None):
            if stage == "closed_lost":
                return [
                    {
                        "email": "ancient@x.com",
                        "amount_cents": 9900,
                        "intent_score": 70,
                        "closed_at": "2025-01-01T00:00:00",  # > 45 days ago
                    }
                ]
            return []

    monkeypatch.setattr(sp_mod, "sales_pipeline", FakePipeline())
    instance = _make_instance(tmp_path, monkeypatch)
    assert instance._win_back_quotes(limit=1) == 0


@pytest.mark.asyncio
async def test_monetize_phase_uses_annual_first_for_hot_leads(tmp_path, monkeypatch):
    from core.services.monetization import monetization

    captured = {}

    def fake_offer(lead, **kwargs):
        captured.update(kwargs)
        return {
            "tier": "growth",
            "billing": "annual" if kwargs.get("annual_first", False) else "monthly",
            "checkout_url": "https://checkout.stripe.com/c/hot",
            "message": "ready",
        }

    monkeypatch.setattr(monetization, "offer_for", fake_offer)
    instance = _make_instance(tmp_path, monkeypatch)
    instance._high_intent_leads = lambda limit: [
        {"email": "hot@x.com", "name": "H", "intent_score": 92}
    ]
    monkeypatch.setattr(
        instance,
        "_funnel_snapshot",
        lambda: {"visitors": 100, "leads": 1, "users": 1, "tickets": 0,
                 "activation_rate": 1.0, "conversion_rate": 0.1},
    )

    result = await instance._phase_monetize()
    assert result["quotes_prepared"] == 1
    assert captured.get("annual_first") is True
    quotes = [
        a["payload"]
        for a in instance.state.get("approval_queue", [])
        if a["kind"] == "quote_send" and a["payload"]["to_email"] == "hot@x.com"
    ]
    assert quotes[0]["billing"] == "annual"