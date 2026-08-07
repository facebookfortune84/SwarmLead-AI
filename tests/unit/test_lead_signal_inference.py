"""
Unit tests for the signal-inference upgrades in lead discovery.

Covers BANT-lite signal inference from crawled pages (_infer_signals) and
the enriched intent scoring (_score_lead) that rewards real businesses
with pricing, decision-maker inboxes and booking/urgency signals.
"""

from core.services import lead_discovery as mod


def test_score_lead_signal_boosts_cap_at_99():
    scored = mod._score_lead(
        "smithplumbing.com",
        "mx.smithplumbing.com",
        title="Smith Plumbing",
        signals={"budget": True, "authority": True, "need": True, "timeline": True},
    )
    # 60 base + 20 business + 10 MX + 4*4 signals = 106 -> capped at 99
    assert scored == 99


def test_score_lead_signal_boost_no_signals():
    assert mod._score_lead(
        "smithplumbing.com", "mx.smithplumbing.com"
    ) == 90  # unchanged, signals default to None


def test_score_lead_some_signals():
    scored = mod._score_lead(
        "smithplumbing.com",
        "implicit-A",
        signals={"budget": True, "need": True},
    )
    assert scored == 60 + 20 + 8  # base + business + 2 signals


def test_infer_signals_budget_from_pricing_page():
    html = "<h1>Dental Plans & Pricing</h1><p>Starting at $99/year for new patients.</p>"
    signals = mod._infer_signals(html, "Bright Smile Dental", "smileco.com")
    assert signals["budget"] is True


def test_infer_signals_bookability_is_need():
    html = "<a href='/book'>Book an appointment</a> Schedule a visit now."
    signals = mod._infer_signals(html, "Trade Shop", "tradeshop.com")
    assert signals["need"] is True


def test_infer_signals_hiring_implies_timeline():
    html = "We are now hiring! Grand opening this month — come see our new location."
    signals = mod._infer_signals(html, "Smith & Sons", "smithsons.com")
    assert signals["timeline"] is True


def test_infer_signals_authority_from_owner_title():
    signals = mod._infer_signals("<html></html>", "Owner & Founder", "owner.com")
    assert signals["authority"] is True


def test_infer_signals_mixed_page_flags_targeted_signals():
    html = (
        "Pricing starts at $199. Call to schedule your estimate today. "
        "Now hiring technicians."
    )
    signals = mod._infer_signals(html, "Pro Plumbing", "proplumbing.com")
    assert signals["budget"] is True
    assert signals["need"] is True
    assert signals["timeline"] is True


def test_infer_signals_blank_page_no_signals():
    signals = mod._infer_signals("", "Index", "")
    assert signals == {"budget": False, "authority": False, "need": False, "timeline": False}


def test_infer_signals_role_inbox_is_not_authority():
    signals = mod._infer_signals("No title clues", "", "info")
    assert signals["authority"] is False