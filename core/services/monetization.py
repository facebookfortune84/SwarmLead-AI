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

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger("Monetization")

ANNUAL_MULTIPLIER = 10  # 2 months free vs 12x monthly
DUNNING_GRACE_DAYS = 7

TIERS = {
    "starter": {"price_cents": 2900, "name": "Starter"},
    "growth": {"price_cents": 9900, "name": "Growth"},
    "enterprise": {"price_cents": 29900, "name": "Enterprise"},
}

for _tier_spec in TIERS.values():
    _tier_spec["annual_price_cents"] = (
        _tier_spec["price_cents"] * ANNUAL_MULTIPLIER
    )
    _tier_spec["annual_savings_cents"] = (
        _tier_spec["price_cents"] * 12 - _tier_spec["annual_price_cents"]
    )


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

    def referral_program(self) -> Dict:
        """Referral-program configuration exposed to the frontend."""
        return {
            "program_name": "SwarmOS Referral Program",
            "referrer_reward": "20% of first monthly payment",
            "referee_discount": "20% off first month",
            "attribution_window_days": 30,
        }

    def upsell_recommendations(self, lead: Optional[Dict] = None) -> List[Dict]:
        """Expansion recommendations for existing accounts."""
        recommendations = []
        if lead and lead.get("intent_score", 0) >= 70:
            recommendations.append(
                {
                    "tier": "growth",
                    "reason": "High-intent lead with clear provisioning need",
                    "estimated_monthly_value": 99,
                }
            )
        recommendations.append(
            {
                "tier": "enterprise",
                "reason": "Multi-workflow teams need the enterprise tier",
                "estimated_monthly_value": 299,
            }
        )
        return recommendations

    def offer_for(self, lead: Dict, billing: str = "monthly") -> Dict:
        """Compose the full monetization offer for a lead."""
        tier = "growth"
        if lead.get("company_size", 0) and lead["company_size"] >= 20:
            tier = "enterprise"
        checkout_url = self.create_checkout_url(
            tier=tier,
            customer_email=lead.get("email"),
            billing=billing,
        )
        tier_spec = TIERS[tier]
        if billing == "annual":
            message = (
                "Your workspace is provisioned and ready. Start your Growth plan "
                f"annual billing (${tier_spec['price_cents'] // 100}/mo billed "
                f"yearly at ${tier_spec['annual_price_cents'] // 100}) — "
                f"2 months free, cancel anytime."
            )
        else:
            message = (
                "Your workspace is provisioned and ready. Start your Growth plan "
                f"(${tier_spec['price_cents'] // 100}/mo) now — cancel anytime."
            )
        return {
            "tier": tier,
            "billing": billing,
            "checkout_url": checkout_url,
            "monthly_price_cents": tier_spec["price_cents"],
            "annual_price_cents": tier_spec["annual_price_cents"],
            "annual_savings_cents": tier_spec["annual_savings_cents"],
            "message": message,
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
