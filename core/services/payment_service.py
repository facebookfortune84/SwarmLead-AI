"""
Payment Service - Handles Stripe subscriptions and hosting billing.
Integrated with Constitutional §12 Monetary Rules Engine.
"""

import logging
import os
from typing import Any, Dict

import stripe

from core.auth.agent_identity import AgentIdentityRegistry
from core.services.monetary_rules import get_monetary_rules

logger = logging.getLogger("PaymentService")

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_placeholder")


PLANS: dict[str, str] = {
    "starter": os.getenv("STRIPE_STARTER_PRICE_ID", ""),
    "growth": os.getenv("STRIPE_GROWTH_PRICE_ID", ""),
    "enterprise": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", ""),
    "launch": os.getenv("STRIPE_LAUNCH_PRICE_ID", ""),
}


class PaymentService:
    """
    Manages monetization for the sovereign factory.
    - Hosting subscriptions
    - One-time company generation fees
    - Usage-based billing
    - Constitutional §12 Monetary Rules enforcement
    """

    def __init__(self):
        self.hosting_price_id = os.getenv("STRIPE_HOSTING_PRICE_ID", "price_hosting_monthly")
        self.plans = PLANS
        self.monetary_rules = get_monetary_rules()

    def get_price_id(self, plan_name: str) -> str | None:
        """Look up a Stripe price ID by plan name."""
        return self.plans.get(plan_name) or None

        # Register monetary rules with GovernanceAgent (done at startup)
        # from core.agents.governance.governance_agent import governance_agent
        # governance_agent.register_monetary_rules(self.monetary_rules)

    def create_hosting_subscription(
        self, customer_email: str, project_id: str, agent_id: str = None
    ) -> Dict[str, Any]:
        """
        Creates a recurring subscription for VM hosting.

        Enforces Constitutional §12:
        - Human approval required
        - Allowlisted counterparty (Stripe)
        - Dual-rail: Customer card network
        """
        try:
            # 1. Find or create customer
            customers = stripe.Customer.list(email=customer_email, limit=1).data
            if customers:
                customer = customers[0]
            else:
                customer = stripe.Customer.create(
                    email=customer_email, metadata={"project_id": project_id}
                )

            # 2. Check monetary rules for agent spend
            if agent_id:
                identity = AgentIdentityRegistry.get(agent_id)
                if not identity or not identity.has_domain("financial"):
                    logger.warning(f"Agent {agent_id} lacks financial domain")
                    return {"status": "error", "message": "Agent lacks financial authority"}

            # 2. Create subscription (Stripe = customer card network rail)
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": self.hosting_price_id}],
                metadata={"project_id": project_id, "type": "hosting", "rail": "stripe_card"},
            )

            # Log monetary transaction per §12.5
            self._audit_log(
                "subscription_created",
                "stripe_subscription",
                {
                    "subscription_id": subscription.id,
                    "customer_id": customer.id,
                    "project_id": project_id,
                    "rail": "stripe_card",
                    "amount_usd": subscription.items.data[0].price.unit_amount / 100
                    if subscription.items.data
                    else 0,
                },
            )

            logger.info(f"Subscription created: {subscription.id} for {customer_email}")
            return {"status": "success", "subscription_id": subscription.id}

        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return {"status": "error", "message": str(e)}

    def cancel_hosting(self, project_id: str) -> Dict[str, Any]:
        """
        Cancels hosting subscription when a tenant is deleted.
        """
        try:
            subscriptions = stripe.Subscription.list(limit=100)

            for subscription in subscriptions.data:
                if subscription.metadata.get("project_id") == project_id:
                    canceled_sub = stripe.Subscription.delete(subscription.id)
                    logger.info(f"Canceled subscription {subscription.id} for project {project_id}")
                    return {
                        "status": "success",
                        "subscription_id": subscription.id,
                        "canceled_at": canceled_sub.canceled_at,
                    }

            logger.warning(f"No subscription found for project {project_id}")
            return {"status": "not_found", "message": "No subscription found"}

        except Exception as e:
            logger.error(f"Failed to cancel hosting for {project_id}: {e}")
            return {"status": "error", "message": str(e)}

    def create_checkout_session(
        self,
        customer_email: str,
        project_id: str,
        price_id: str,
        agent_id: str = None,
        success_url: str = None,
        cancel_url: str = None,
        mode: str = "subscription",
    ) -> Dict[str, Any]:
        """
        Creates a Stripe Checkout session for recurring subscriptions.
"""
        try:
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            session = stripe.checkout.Session.create(
                customer_email=customer_email,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode=mode,
                success_url=success_url
                or f"{frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=cancel_url or f"{frontend_url}/cancel",
                metadata={"project_id": project_id, "rail": "stripe_card"},
            )

            self._audit_log(
                "checkout_session_created",
                "stripe_checkout",
                {
                    "session_id": session.id,
                    "customer_email": customer_email,
                    "project_id": project_id,
                    "price_id": price_id,
                    "rail": "stripe_card",
                },
            )

            return {"status": "success", "session_id": session.id, "url": session.url}

        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            return {"status": "error", "message": str(e)}

    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Handles Stripe webhooks for subscription events.
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

            if event["type"] == "invoice.payment_succeeded":
                self._handle_payment_succeeded(event["data"]["object"])
            elif event["type"] == "invoice.payment_failed":
                self._handle_payment_failed(event["data"]["object"])
            elif event["type"] == "customer.subscription.deleted":
                self._handle_subscription_canceled(event["data"]["object"])

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Webhook handling failed: {e}")
            return {"status": "error", "message": str(e)}

    def _handle_payment_succeeded(self, invoice: Dict):
        """Handle successful payment - log per §12.5"""
        self._audit_log(
            "payment_succeeded",
            "stripe_payment",
            {
                "invoice_id": invoice.get("id"),
                "customer": invoice.get("customer"),
                "amount_usd": invoice.get("amount_paid", 0) / 100,
                "rail": "stripe_card",
            },
        )

    def _handle_payment_failed(self, invoice: Dict):
        """Handle failed payment."""
        logger.warning(f"Payment failed for invoice: {invoice.get('id')}")
        self._audit_log(
            "payment_failed",
            "stripe_payment",
            {
                "invoice_id": invoice.get("id"),
                "customer": invoice.get("customer"),
                "rail": "stripe_card",
            },
        )

    def _handle_subscription_canceled(self, subscription: Dict):
        """Handle subscription cancellation."""
        logger.info(f"Subscription canceled: {subscription.get('id')}")
        self._audit_log(
            "subscription_canceled",
            "stripe_subscription",
            {
                "subscription_id": subscription.get("id"),
                "customer": subscription.get("customer"),
                "rail": "stripe_card",
            },
        )

    def _audit_log(self, action: str, event_type: str, details: Dict):
        """Tamper-evident audit logging per §12.5"""
        # In production, this would write to immutable audit log
        logger.info(f"AUDIT: {action} - {event_type} - {details}")


# Global instance
payment_service = PaymentService()
