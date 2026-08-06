"""
Closer Agent — the AI account executive.

Turns qualified deals into signed customers:
- Composes tiered offers (starter/growth/enterprise) from deal signals
- Offers annual contracts at 2-months-free when the deal value justifies it
- Answers common objections with deterministic, honest responses
- Records won/lost outcomes back into the sales pipeline

External actions (sending the offer, charging) remain human-gated; this
agent only *prepares* the pitch and updates internal deal state.
"""

import logging
from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent
from core.services.sales_pipeline import MONTHLY_VALUE, SalesPipeline, sales_pipeline

logger = logging.getLogger("CloserAgent")

OBJECTION_RESPONSES = {
    "price": (
        "The Growth plan is $99/mo and includes the full 15-agent workforce, "
        "programmatic SEO, outreach and the voice agent. Annual billing drops "
        "that to $82.50/mo (2 months free)."
    ),
    "time": (
        "There is no setup — the growth loop provisions the workspace and "
        "runs the first discovery + SEO cycle within an hour."
    ),
    "competitor": (
        "SwarmOS bundles discovery, outreach, SEO, content, voice and quoting "
        "into one loop — competitors sell each as a separate product."
    ),
    "trust": (
        "Start on the Starter plan with Stripe billing — cancel anytime, and "
        "every external action stays behind your approval gate."
    ),
    "features": (
        "Every plan includes the full agent workforce; tiers differ on volume "
        "and multi-tenant seats, not capabilities."
    ),
}

# Synonyms mapped onto the canonical objection keys above. Order matters:
# more specific phrases are checked first.
OBJECTION_KEYWORDS = {
    "price": ["price", "cost", "expensive", "too much", "budget", "afford"],
    "time": ["no time", "busy", "later", "not now", "don't have time", "schedule"],
    "competitor": ["competitor", "other tool", "another product", "already use"],
    "trust": ["trust", "scam", "legit", "sure", "guarantee", "refund"],
    "features": ["features", "missing", "does it do", "capabilities", "integrations"],
}

DEFAULT_OBJECTION = (
    "Happy to walk through the plan details — tell me what matters most and "
    "I'll map it to the right tier."
)


class CloserAgent(BaseAgent):
    """Composes offers, handles objections and closes deals."""

    def __init__(
        self,
        name: str,
        config,
        pipeline: Optional[SalesPipeline] = None,
    ) -> None:
        super().__init__(name, config)
        self.pipeline = pipeline if pipeline is not None else sales_pipeline

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        action = input_data.get("action", "compose_offer")
        if action == "compose_offer":
            return self._compose_offer(input_data)
        if action == "handle_objection":
            return self._handle_objection(input_data)
        if action == "record_outcome":
            return self._record_outcome(input_data)
        return {"status": "error", "error": f"unknown action: {action}"}

    # -------------------------------------------------------- compose offer
    def _compose_offer(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pick the tier + billing period for a deal and draft the pitch."""
        deal = input_data.get("deal") or {}
        amount_cents = deal.get("amount_cents") or 0
        intent = deal.get("intent_score") or 0
        size = input_data.get("company_size") or 0

        tier = self._tier_for(size, amount_cents, intent)
        monthly_cents = MONTHLY_VALUE[tier]
        annual = input_data.get("annual", False)
        annual_cents = int(monthly_cents * 10) if annual else None

        pitch = (
            f"I'd recommend the {tier.title()} plan "
            f"(${monthly_cents // 100}/mo"
            + (f", ${annual_cents // 100}/mo on annual — 2 months free)" if annual else ")")
            + ". It fits what you're building and scales with you."
        )
        return {
            "status": "ok",
            "tier": tier,
            "monthly_cents": monthly_cents,
            "annual_cents": annual_cents,
            "pitch": pitch,
            "deal_id": deal.get("id"),
        }

    @staticmethod
    def _tier_for(size: int, amount_cents: int, intent: int) -> str:
        if size >= 20 or amount_cents >= 29900:
            return "enterprise"
        if size >= 5 or amount_cents >= 9900 or intent >= 75:
            return "growth"
        return "starter"

    # --------------------------------------------------------- objections
    def _handle_objection(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        objection = (input_data.get("objection") or "").lower()
        for key, keywords in OBJECTION_KEYWORDS.items():
            if any(kw in objection for kw in keywords):
                return {"status": "ok", "objection": key, "response": OBJECTION_RESPONSES[key]}
        return {"status": "ok", "objection": "general", "response": DEFAULT_OBJECTION}

    # --------------------------------------------------------- outcomes
    def _record_outcome(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        deal_id = input_data.get("deal_id")
        won = bool(input_data.get("won"))
        note = input_data.get("note", "")
        if not deal_id:
            return {"status": "error", "error": "deal_id required"}
        if won:
            self.pipeline.close_won(deal_id, triggered_by="closer_agent", note=note)
        else:
            self.pipeline.close_lost(deal_id, triggered_by="closer_agent", note=note)
        return {"status": "ok", "deal_id": deal_id, "won": won}


__all__ = ["CloserAgent", "OBJECTION_RESPONSES", "OBJECTION_KEYWORDS"]
