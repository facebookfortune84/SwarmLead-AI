"""
SDR Agent — the AI sales development representative.

Responsibilities (all internal; external contact stays behind the human
approval gate):
- BANT-lite qualification of discovered leads into the sales pipeline
- Cadence-aware follow-up drafting (escalating value across touches)
- Lead reactivation for dormant, previously engaged prospects

The agent is deterministic by design: with LLMs disabled it still produces
useful, testable behavior, and every "message" it produces flows through
the growth loop approval queue before any SMTP delivery.
"""

import logging
import re
from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent
from core.services.sales_pipeline import (
    QUALIFY_INTENT_THRESHOLD,
    SalesPipeline,
    sales_pipeline,
)

logger = logging.getLogger("SDRAgent")

# Escalating cadence: (delay_days, angle) — each touch adds a new reason to respond.
CADENCE = [
    (0, "The 19-agent workforce: 19 agents doing outreach, SEO and follow-ups on one plan"),
    (3, "Programmatic SEO pages that rank for every industry you target — already live"),
    (7, "Voice agent on your landing page that answers and captures leads 24/7"),
    (14, "The growth loop: discovery, outreach, content and quoting on autopilot"),
]

MAX_TOUCHES = len(CADENCE)

REACTIVATION_ANGLES = [
    "Found the best time to walk through the workspace you provisioned",
    "Fresh case study: a dental clinic added 31 booked appointments in 30 days",
    "Your SEO pages started ranking — here's what to ship next",
]


class SDRAgent(BaseAgent):
    """Qualifies leads, drafts cadence-aware outreach and reactivates cold deals."""

    def __init__(
        self,
        name: str,
        config,
        pipeline: Optional[SalesPipeline] = None,
    ) -> None:
        super().__init__(name, config)
        self.pipeline = pipeline if pipeline is not None else sales_pipeline

    # ------------------------------------------------------------------ run
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        action = input_data.get("action", "qualify")
        if action == "qualify":
            return await self._qualify(input_data, trace_id)
        if action == "draft_followup":
            return self._draft_followup(input_data)
        if action == "reactivate":
            return self._reactivate(input_data)
        raise ValueError(f"unknown action: {action}")

    # ------------------------------------------------------------ qualify
    async def _qualify(
        self,
        input_data: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        leads = input_data.get("leads", [])
        owner = input_data.get("owner_agent", "sdr_agent")
        result = self.pipeline.sync_from_leads(leads, owner_agent=owner)
        result["status"] = "ok"
        result["threshold"] = QUALIFY_INTENT_THRESHOLD
        if leads:
            result["sample"] = [
                {
                    "email": lead.get("email"),
                    "intent_score": lead.get("intent_score"),
                }
                for lead in leads[:5]
            ]
        return result

    # --------------------------------------------------------- follow-up
    def _draft_followup(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Draft the next cadence email for a lead's current touch count."""
        email = input_data.get("email", "")
        name = input_data.get("name") or "there"
        company = input_data.get("company") or "your company"
        touch = max(0, min(int(input_data.get("touch", 0)), MAX_TOUCHES - 1))

        delay_days, angle = CADENCE[touch]
        subject = self._subject_for_touch(touch, company)
        body = (
            f"Hi {name},\n\n"
            f"Quick one about {company}: {angle}.\n\n"
            f"If it's useful, I can send a 5-minute walkthrough video. "
            f"Otherwise no need to reply — the workspace stays provisioned "
            f"either way.\n\n"
            f"Best,\nThe SwarmOS Team"
        )
        return {
            "status": "ok",
            "email": email,
            "touch": touch,
            "delay_days": delay_days,
            "subject": subject,
            "body": body,
            "total_touches": MAX_TOUCHES,
        }

    @staticmethod
    def _subject_for_touch(touch: int, company: str) -> str:
        if touch == 0:
            return f"Meet the AI that answers for {company}"
        if touch == 1:
            return "Re: your SEO pages are ranking"
        if touch == 2:
            return "Your voice agent is live"
        return "Last thought on {company}".format(company=company)

    # --------------------------------------------------------- reactivate
    def _reactivate(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Craft a reactivation message for a dormant deal."""
        email = input_data.get("email", "")
        name = input_data.get("name") or "there"
        company = input_data.get("company") or "your company"
        angle = input_data.get("angle") or self._pick_angle(company)
        body = (
            f"Hi {name},\n\n"
            f"{angle}\n\n"
            f"Happy to set up a 10-minute session for {company} whenever "
            f"it's useful.\n\nBest,\nThe SwarmOS Team"
        )
        return {
            "status": "ok",
            "email": email,
            "subject": f"One more for {company}",
            "body": body,
        }

    @staticmethod
    def _pick_angle(company: str) -> str:
        # Deterministic pick so the same lead gets a stable angle.
        idx = sum(ord(c) for c in (company or "swarm")) % len(REACTIVATION_ANGLES)
        return REACTIVATION_ANGLES[idx]

    # ------------------------------------------------------------ helper
    @staticmethod
    def _clean_email(body: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", body).strip()


__all__ = ["SDRAgent", "CADENCE", "REACTIVATION_ANGLES"]
