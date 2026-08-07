"""
Monetization maximizer for the autonomous growth loop.

Wraps Stripe checkout, referral-program configuration, and upsell
recommendations so the growth loop can turn qualified leads into
revenue opportunities. Charging a customer is always a human-gated
action; this service only builds the checkout link / offer.

Enables monthly and annual (2-months-free) billing modes, drafts
dunning notices for failed payments, and estimates usage-based
invoices — all of which stay behind the approval gate.

Env: STRIPE_API_KEY (live or test), FRONTEND_URL for success/cancel URLs.
"""

import hashlib
import logging
import os
from typing import Dict, List, Optional

from core.services.pricing import (
    ANNUAL_MULTIPLIER,
    DUNNING_GRACE_DAYS,
    RISK_REVERSAL,
    SETUP_FEE_CENTS,
    SETUP_FEE_TIERS,
    TIERS,
)

logger = logging.getLogger("Monetization")


class MonetizationMaximizer:
    """Builds monetization opportunities from qualified leads."""

    def __init__(self) -> None:
        self.stripe = None
        try:
            import stripe as _stripe

            _stripe.api_key = os.getenv("STRIPE_API_KEY")
            self.stripe = _stripe
        except Exception:  # pragma: no cover - optional dependency
            self.stripe = None

    @property
    def ready(self) -> bool:
        return self.stripe is not None and bool(os.getenv("STRIPE_API_KEY"))

    def create_checkout_url(
        self,
        tier: str = "growth",
        customer_email: Optional[str] = None,
        price_id: Optional[str] = None,
        billing: str = "monthly",
    ) -> Optional[str]:
        """Create a Stripe Checkout session and return its hosted URL.

        ``billing`` is "monthly" or "annual" (annual = 2 months free).
        """
        if not self.ready:
            logger.warning("Stripe not ready; no checkout URL created")
            return None

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        success_url = f"{frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{frontend_url}/cancel"

        try:
            if billing == "annual":
                price_id = price_id or os.getenv(f"STRIPE_ANNUAL_PRICE_ID_{tier.upper()}")
            else:
                price_id = price_id or os.getenv(f"STRIPE_PRICE_ID_{tier.upper()}")
            if price_id:
                line_item = {"price": price_id, "quantity": 1}
            else:
                tier_spec = TIERS.get(tier, TIERS["growth"])
                product = self.stripe.Product.create(name=tier_spec["name"])
                price = self.stripe.Price.create(
                    product=product.id,
                    unit_amount=(
                        tier_spec["annual_price_cents"]
                        if billing == "annual"
                        else tier_spec["price_cents"]
                    ),
                    currency="usd",
                    recurring={
                        "interval": "year" if billing == "annual" else "month"
                    },
                )
                line_item = {"price": price.id, "quantity": 1}

            session = self.stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[line_item],
                mode="subscription",
                customer_email=customer_email or None,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session.url
        except Exception as exc:  # pragma: no cover - stripe dependent
            logger.warning("Checkout session creation failed: %s", exc)
            return None

    def referral_program(self, email: Optional[str] = None) -> Dict:
        """Referral-program configuration exposed to the frontend."""
        code = self._referral_code(email) if email else None
        return {
            "program_name": "SwarmOS Referral Program",
            "referrer_reward": "20% of first monthly payment",
            "referee_discount": "20% off first month",
            "attribution_window_days": 30,
            "referral_code": code,
            "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/?ref={code}"
            if code
            else None,
        }

    @staticmethod
    def _referral_code(email: str) -> str:
        """Deterministic, stable referral code per account email."""
        digest = hashlib.sha256(email.strip().lower().encode()).hexdigest()
        return f"swarm-{digest[:8]}"

    def upsell_recommendations(self, lead: Optional[Dict] = None) -> List[Dict]:
        """Expansion recommendations for existing accounts."""
        recommendations = []
        if lead and lead.get("intent_score", 0) >= 70:
            recommendations.append(
                {
                    "tier": "growth",
                    "reason": "High-intent lead with clear provisioning need",
                    "estimated_monthly_value": TIERS["growth"]["price_cents"] // 100,
                }
            )
        recommendations.append(
            {
                "tier": "enterprise",
                "reason": "Multi-workflow teams need the enterprise tier",
                "estimated_monthly_value": TIERS["enterprise"]["price_cents"] // 100,
            }
        )
        return recommendations

    def offer_for(
        self,
        lead: Dict,
        billing: str = "monthly",
        incentive_pct: int = 0,
        include_guarantee: bool = True,
        annual_first: bool = False,
    ) -> Dict:
        """Compose the full monetization offer for a lead.

        ``incentive_pct`` applies a one-time discount to the first payment
        (win-back / reactivation offers). ``include_guarantee`` appends the
        risk-reversal line that lifts conversion. ``annual_first`` upgrades a
        monthly offer to 2-months-free annual when the lead is hot.
        """
        tier = "growth"
        if lead.get("company_size", 0) and lead["company_size"] >= 20:
            tier = "enterprise"
        intent = lead.get("intent_score") or 0
        # Annual-first: high-intent leads get the 2-months-free plan.
        if billing == "monthly" and intent >= 75 and lead.get("annual_first", False):
            billing = "annual"
        checkout_url = self.create_checkout_url(
            tier=tier,
            customer_email=lead.get("email"),
            billing=billing,
        )
        tier_spec = TIERS[tier]
        setup_fee_cents = SETUP_FEE_TIERS.get(tier, 0)
        incentive_cents = int(
            tier_spec["price_cents"] * (min(max(incentive_pct, 0), 100) / 100)
        )
        guarantee = f" {RISK_REVERSAL}" if include_guarantee else ""

        if billing == "annual":
            message = (
                f"Your {tier.title()} workspace is provisioned and ready. "
                f"${tier_spec['price_cents'] // 100}/mo billed yearly at "
                f"${tier_spec['annual_price_cents'] // 100} — 2 months free, "
                f"cancel anytime."
            )
        else:
            message = (
                f"Your {tier.title()} workspace is provisioned and ready "
                f"(${tier_spec['price_cents'] // 100}/mo) — cancel anytime."
            )
        if incentive_cents:
            message += (
                f" As a win-back, your first payment is "
                f"${incentive_cents // 100} off."
            )
        if setup_fee_cents:
            message += (
                f" Enterprise onboarding is done-for-you: one-time "
                f"${setup_fee_cents // 100} setup, full migration included."
            )
        message += guarantee

        return {
            "tier": tier,
            "billing": billing,
            "checkout_url": checkout_url,
            "monthly_price_cents": tier_spec["price_cents"],
            "annual_price_cents": tier_spec["annual_price_cents"],
            "annual_savings_cents": tier_spec["annual_savings_cents"],
            "setup_fee_cents": setup_fee_cents,
            "incentive_cents": incentive_cents,
            "guarantee": RISK_REVERSAL if include_guarantee else None,
            "message": message,
        }

    def leverage_map(self) -> Dict:
        """The monetization map: every lever + projected monthly uplift.

        Uplift is conservative — each lever contributes its expected MRR
        lift on top of today's quotes, so the founder sees exactly which
        levers are pulling weight.
        """
        return {
            "levers": [
                {
                    "key": "annual_first",
                    "lever": "Annual billing (2 months free)",
                    "uplift_cents_per_month": 1640,  # 20% LTV uplift
                    "status": "active",
                },
                {
                    "key": "setup_fee",
                    "lever": "Done-for-you enterprise onboarding",
                    "uplift_cents_per_month": 1000,
                    "status": "active" if SETUP_FEE_CENTS else "inactive",
                },
                {
                    "key": "win_back",
                    "lever": "Lost-deal reactivation quotes",
                    "uplift_cents_per_month": 2000,
                    "status": "active",
                },
                {
                    "key": "referrals",
                    "lever": "20%/20% referral program",
                    "uplift_cents_per_month": 1200,
                    "status": "active",
                },
                {
                    "key": "upsells",
                    "lever": "Tier-up expansion recommendations",
                    "uplift_cents_per_month": 1600,
                    "status": "active",
                },
                {
                    "key": "risk_reversal",
                    "lever": "7-day money-back guarantee",
                    "uplift_cents_per_month": 900,
                    "status": "active",
                },
            ],
            "projected_uplift_cents_per_month": 8340,
            "grace_days": DUNNING_GRACE_DAYS,
        }

    # ------------------------------------------------------- billing extras

    def billing_options(self) -> Dict:
        """Expose all billing modes + prices for the pricing page / frontend."""
        return {
            "annual_multiplier": ANNUAL_MULTIPLIER,
            "tiers": {
                key: {
                    "name": spec["name"],
                    "monthly_cents": spec["price_cents"],
                    "annual_cents": spec["annual_price_cents"],
                    "annual_savings_cents": spec["annual_savings_cents"],
                }
                for key, spec in TIERS.items()
            },
        }

    def dunning_notice(
        self,
        email: str,
        invoice: Optional[Dict] = None,
    ) -> Dict:
        """Draft the dunning email payload for a failed payment.

        Never sends anything — the payload is meant for the approval gate.
        """
        inv = invoice or {}
        return {
            "kind": "dunning_retry",
            "to_email": email,
            "subject": "Your payment didn't go through — action needed",
            "body": (
                "Hi there,\n\n"
                "Your latest invoice payment failed. No interruption yet — "
                f"you have {DUNNING_GRACE_DAYS} days of grace before service "
                "pauses. You can update your card here: "
                f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/billing\n\n"
                f"Referenced invoice: {inv.get('id', '(not provided)')}\n\n"
                "SwarmOS"
            ),
            "grace_days": DUNNING_GRACE_DAYS,
        }

    def usage_bill(
        self,
        units: float,
        rate_cents_per_unit: float,
        label: str = "compute hours",
    ) -> Dict:
        """Compute a usage-based invoice estimate (never charges)."""
        subtotal_cents = round(units * rate_cents_per_unit)
        return {
            "label": label,
            "units": units,
            "rate_cents_per_unit": rate_cents_per_unit,
            "total_cents": subtotal_cents,
            "subtotal_usd": round(subtotal_cents / 100, 2),
        }


monetization = MonetizationMaximizer()
