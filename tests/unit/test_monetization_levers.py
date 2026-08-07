"""
Unit tests for the monetization levers:

- setup fees on enterprise offers
- incentive (win-back) discounts
- annual-first upgrades for hot leads
- risk-reversal guarantee line
- referral codes + share URL
- the monetization leverage map
"""

from core.services.monetization import MonetizationMaximizer
from core.services.pricing import TIERS


def _monetizer(monkeypatch):
    monkeypatch.delenv("STRIPE_API_KEY", raising=False)
    return MonetizationMaximizer()


# ----------------------------------------------------------- setup fee
def test_enterprise_offer_carries_setup_fee(monkeypatch):
    offer = _monetizer(monkeypatch).offer_for({"email": "a@x.com", "company_size": 50})
    assert offer["tier"] == "enterprise"
    assert offer["setup_fee_cents"] > 0
    assert f"${offer['setup_fee_cents'] // 100} setup" in offer["message"]


def test_growth_offer_has_no_setup_fee(monkeypatch):
    offer = _monetizer(monkeypatch).offer_for({"email": "a@x.com", "company_size": 5})
    assert offer["tier"] == "growth"
    assert offer["setup_fee_cents"] == 0


# ----------------------------------------------------------- incentives
def test_win_back_incentive_discounts_first_payment(monkeypatch):
    offer = _monetizer(monkeypatch).offer_for(
        {"email": "a@x.com", "company_size": 5}, incentive_pct=20
    )
    monthly = TIERS["growth"]["price_cents"]
    assert offer["incentive_cents"] == int(monthly * 0.20)
    assert f"${offer['incentive_cents'] // 100} off" in offer["message"]


def test_incentive_clamped_to_100(monkeypatch):
    offer = _monetizer(monkeypatch).offer_for(
        {"email": "a@x.com", "company_size": 0}, incentive_pct=500
    )
    assert offer["incentive_cents"] <= TIERS[offer["tier"]]["price_cents"]


def test_no_incentive_by_default(monkeypatch):
    offer = _monetizer(monkeypatch).offer_for({"email": "a@x.com"})
    assert offer["incentive_cents"] == 0


# ---------------------------------------------------------- annual-first
def test_annual_first_upgrades_hot_lead(monkeypatch):
    offer = _monetizer(monkeypatch).offer_for(
        {"email": "a@x.com", "intent_score": 90, "annual_first": True}
    )
    assert offer["billing"] == "annual"
    assert "2 months free" in offer["message"]


def test_annual_first_low_intent_stays_monthly(monkeypatch):
    offer = _monetizer(monkeypatch).offer_for(
        {"email": "a@x.com", "intent_score": 40, "annual_first": True}
    )
    assert offer["billing"] == "monthly"


# ---------------------------------------------------------- guarantee
def test_guarantee_toggle(monkeypatch):
    with_guarantee = _monetizer(monkeypatch).offer_for({"email": "a@x.com"})
    without = _monetizer(monkeypatch).offer_for(
        {"email": "a@x.com"}, include_guarantee=False
    )
    assert "money-back guarantee" in with_guarantee["message"]
    assert "money-back guarantee" not in without["message"]
    assert without["guarantee"] is None


# ---------------------------------------------------------- referral
def test_referral_code_stable_per_email(monkeypatch):
    monetizer = _monetizer(monkeypatch)
    program = monetizer.referral_program("Owner@SmithPlumbing.com")
    again = monetizer.referral_program("owner@smithplumbing.com")
    assert program["referral_code"] == again["referral_code"]
    assert program["referral_code"].startswith("swarm-")
    assert "ref=swarm-" in program["share_url"]


def test_referral_without_email_no_code(monkeypatch):
    program = _monetizer(monkeypatch).referral_program()
    assert program["referral_code"] is None
    assert program["share_url"] is None


# ---------------------------------------------------------- leverage map
def test_leverage_map_lists_all_levers(monkeypatch):
    map_data = _monetizer(monkeypatch).leverage_map()
    keys = {lever["key"] for lever in map_data["levers"]}
    assert {
        "annual_first", "setup_fee", "win_back", "referrals", "upsells",
        "risk_reversal",
    } <= keys
    assert map_data["projected_uplift_cents_per_month"] > 0
    assert map_data["grace_days"] == 7