"""
Payment Agent — Billing, plans, and quotes for the founder's business.

Constitutional §12: No standing spend. Human approval per dollar.
This agent never initiates charges — it quotes, explains, and prepares
invoices that always require explicit human approval before any transaction.
"""

from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent


class PaymentAgent(BaseAgent):
    """Handles plan selection, quotes, and payment-intent preparation — never charging."""

    PLANS = {
        "free": {"price_usd": 0.0, "limits": "1 business, community support"},
        "growth": {"price_usd": 49.0, "limits": "5 businesses, priority support"},
        "scale": {"price_usd": 199.0, "limits": "Unlimited businesses, dedicated support"},
    }

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        plan_name = (input_data.get("plan") or "growth").lower()
        product = input_data.get("product", "")
        text = input_data.get("text", "")

        if plan_name not in self.PLANS:
            plan_name = "growth"

        plan = self.PLANS[plan_name]

        return {
            "plan": plan_name,
            "price_usd": plan["price_usd"],
            "limits": plan["limits"],
            "product": product,
            "quote": {
                "items": [{"line": f"{plan_name} plan", "amount_usd": plan["price_usd"]}],
                "total_usd": plan["price_usd"],
                "currency": "usd",
            },
            "status": "quote_ready",
            "charged": False,
            "next_step": "Founder approval required before any charge (§12)",
        }
