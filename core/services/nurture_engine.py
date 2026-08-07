"""
Lead Nurture Engine - deterministic multi-touch nurture sequences that keep
every lead moving: intro -> value -> case -> risk-reversal -> cadence/repeat,
plus reactivation for silent leads and escalation for hot ones.

Central concepts:
- ``sequence()``  - a canned 5-touch nurture plan with spacing days
- ``advance()``   - return the next touch (and its delay) given prior touches
- ``classify()``  - reply sentiment => triggers escalation / winback / drop

This service is *preparation* only: it returns drafts and decisions; it never
sends anything. Sends remain behind the human approval gate.
"""

from datetime import datetime
from typing import Any, Dict, Optional

NURTURE_TOUCHES = [
    {
        "seq": 1,
        "label": "intro",
        "days": 0,
        "goal": "establish relevance + no-risk next step",
    },
    {
        "seq": 2,
        "label": "value",
        "days": 2,
        "goal": "deliver one concrete value / case",
    },
    {
        "seq": 3,
        "label": "social_proof",
        "days": 5,
        "goal": "show a similar business outcome",
    },
    {
        "seq": 4,
        "label": "risk_reversal",
        "days": 9,
        "goal": "offer a no-risk demo / trial",
    },
    {
        "seq": 5,
        "label": "breakup",
        "days": 14,
        "goal": "final breakup touch + reactivation CTA",
    },
]

REACTIVATE_DAYS = 21


class NurtureEngine:
    """Deterministic nurture CADENCE - returns plan + per-touch prompts."""

    def plan(self, lead_email: str, start_date: Optional[str] = None) -> Dict[str, Any]:
        return {
            "lead": lead_email,
            "total": 5,
            "touches": [dict(t) for t in NURTURE_TOUCHES],
            "reactivation_day": REACTIVATE_DAYS,
            "start_date": start_date or datetime.utcnow().isoformat(),
        }

    def advance(self, current_seq: int = 0) -> Dict[str, Any]:
        """Return the next touch in the cascade (and whether it's the last)."""
        for touch in NURTURE_TOUCHES:
            if touch["seq"] == current_seq + 1:
                return {"next": touch, "is_final": touch["label"] == "breakup"}
        return {"next": None, "is_final": True}

    def cadence_label(self, seq: int) -> str:
        for touch in NURTURE_TOUCHES:
            if touch["seq"] == seq:
                return touch["label"]
        return "outside_cadence"

    def should_reactivate(self, days_since_contact: int) -> bool:
        return days_since_contact >= REACTIVATE_DAYS

    def apply(self, reply: str) -> Dict[str, Any]:
        """Classify an inbound reply and decide the next action (deterministic)."""
        lower = (reply or "").lower()
        if any(k in lower for k in ("unsubscribe", "not interested", "stop", "remove me")):
            return {"intent": "unsubscribe", "action": "suppress"}
        if any(k in lower for k in ("yes", "book", "schedule", "call", "let's talk", "interested", "demo")):
            return {"intent": "positive", "action": "escalate_to_closer"}
        if any(k in lower for k in ("no thanks", "no,", "too expensive", "not now", "we're good")):
            return {"intent": "negative", "action": "winback_or_mark_lost"}
        if any(k in lower for k in ("?", "price", "pricing", "how much", "more info", "tell me")):
            return {"intent": "question", "action": "answer_and_offer_demo"}
        if not lower.strip():
            return {"intent": "no_reply", "action": "continue_cadence"}
        return {"intent": "ambiguous", "action": "human_review"}

    def status(self) -> Dict[str, Any]:
        return {
            "touches": len(NURTURE_TOUCHES),
            "reactivate_days": REACTIVATE_DAYS,
            "decisions": ["suppress", "escalate_human", "continue_cadence", "mark_lost", "human_review"],
        }


nurture_engine = NurtureEngine()
__all__ = ["NurtureEngine", "nurture_engine", "NURTURE_TOUCHES"]