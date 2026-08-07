"""
Central pricing — the single source of truth for every monetization surface.

Tier prices, annual discounts, setup fees and the risk-reversal guarantee
live here so the checkout offers, pipeline deal values, closer pitch,
revenue projections and growth-loop quote accounting can never drift.

Every surface imports from this module:
- ``monetization`` (checkout offers, billing options, upsell)
- ``sales_pipeline`` (deal value suggestions, forecast, annual contracts)
- ``closer_agent`` (tier pick + pitch)
- ``growth_automation`` (quote revenue accounting)
"""

ANNUAL_MULTIPLIER = 10  # 10x monthly == 2 months free on an annual contract
DUNNING_GRACE_DAYS = 7

TIERS = {
    "starter": {"price_cents": 2900, "name": "Starter"},
    "growth": {"price_cents": 9900, "name": "Growth"},
    "enterprise": {"price_cents": 29900, "name": "Enterprise"},
}

# One-time onboarding fee for the done-for-you enterprise path.
SETUP_FEE_CENTS = 4900
SETUP_FEE_TIERS = {"enterprise": SETUP_FEE_CENTS}

RISK_REVERSAL = (
    "Every plan carries a 7-day money-back guarantee — if it's not working, "
    "full refund, no questions."
)

for _tier_spec in TIERS.values():
    _tier_spec["monthly_cents"] = _tier_spec["price_cents"]
    _tier_spec["annual_price_cents"] = (
        _tier_spec["price_cents"] * ANNUAL_MULTIPLIER
    )
    _tier_spec["annual_savings_cents"] = (
        _tier_spec["price_cents"] * 12 - _tier_spec["annual_price_cents"]
    )

# Backwards-compatible flat map (deal values, MRR accounting).
MONTHLY_VALUE = {key: spec["price_cents"] for key, spec in TIERS.items()}
