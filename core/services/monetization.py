"""
Monetization maximizer for the autonomous growth loop.

Wraps Stripe checkout, referral-program configuration, and upsell
recommendations so the growth loop can turn qualified leads into
revenue opportunities. Charging a customer is always a human-gated
action; this service only builds the checkout link / offer.

Env: STRIPE_API_KEY (live or test), FRONTEND_URL for success/cancel URLs.
"""

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger("Monetization")

TIERS = {
    "starter": {"price_cents": 2900, "name": "Starter"},
    "growth": {"price_cents": 9900, "name": "Growth"},
    "enterprise": {"price_cents": 29900, "name": "Enterprise"},
}


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
    ) -> Optional[str]:
        """Create a Stripe Checkout session and return its hosted URL."""
        if not self.ready:
            logger.warning("Stripe not ready; no checkout URL created")
            return None

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        success_url = f"{frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{frontend_url}/cancel"

        try:
            price_id = price_id or os.getenv(f"STRIPE_PRICE_ID_{tier.upper()}")
            if price_id:
                line_item = {"price": price_id, "quantity": 1}
            else:
                tier_spec = TIERS.get(tier, TIERS["growth"])
                product = self.stripe.Product.create(name=tier_spec["name"])
                price = self.stripe.Price.create(
                    product=product.id,
                    unit_amount=tier_spec["price_cents"],
                    currency="usd",
                    recurring={"interval": "month"},
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

    def offer_for(self, lead: Dict) -> Dict:
        """Compose the full monetization offer for a lead."""
        tier = "growth"
        if lead.get("company_size", 0) and lead["company_size"] >= 20:
            tier = "enterprise"
        checkout_url = self.create_checkout_url(
            tier=tier,
            customer_email=lead.get("email"),
        )
        return {
            "tier": tier,
            "checkout_url": checkout_url,
            "message": (
                "Your workspace is provisioned and ready. Start your Growth plan "
                f"(${TIERS[tier]['price_cents'] // 100}/mo) now — cancel anytime."
            ),
        }


monetization = MonetizationMaximizer()
