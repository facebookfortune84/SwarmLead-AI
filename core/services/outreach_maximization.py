"""
Outreach Maximization - a catalog of levers that sharpen cold/lukewarm outreach
accuracy and drive end-to-end acquisition, follow-up, lead nurturing, and
eventually a verified sale.

Each lever is deterministic, self-contained, and testable. Levers classify into:

- ACCURACY   : targeting, ICP hygiene, deliverability, timing, personalization
- ACQUISITION: channels, referral loops, landing page alignment
- NURTURE    : follow-up cadence, reactivation, reply detection, escalation
- CONVERSION : risk-reversal, social proof hooks, clear CTA, urgency

``maximize(outreach, lead)`` applies the applicable levers to a proposal and
returns an augmented payload with a score. ``analysis(lead)`` returns all
levers relevant to a lead with per-levers impact notes.

Constitutional: this service only *prepares* optimized drafts / advice. It
never sends email or posts. Sending stays behind the human approval gate.
"""

from datetime import datetime
from typing import Any, Dict, List

# ------------------------------------------------------------------- levers

LEVER_COUNT = 22

LEVERS = [
    {
        "key": "icp_accuracy",
        "label": "ICP precision",
        "category": "accuracy",
        "action": "Verify the lead fits your ideal customer profile (industry, size, role) before messaging.",
    },
    {
        "key": "deliverability_alias",
        "label": "Sparkline-alias hygiene",
        "category": "accuracy",
        "action": "Use a verified sending alias (SPF/DKIM/DMARC) and keep the sender consistent.",
    },
    {
        "key": "suppression",
        "label": "Suppression & compliance",
        "category": "accuracy",
        "action": "Honor bounces, complaints, and opt-outs before any send.",
    },
    {
        "key": "fresh_list",
        "label": "Dynamic list refresh",
        "category": "accuracy",
        "action": "Drop stale/unreachable records and blend in freshly discovered targets each cycle.",
    },
    {
        "key": "personalization",
        "label": "Hyper-personalization",
        "category": "accuracy",
        "action": "Reference their site/signals and one concrete pain; avoid templated first lines.",
    },
    {
        "key": "credibility_anchor",
        "label": "Credibility anchor",
        "category": "conversion",
        "action": "Lead with a specific, verifiable reason to reply (case, stat, mutual context).",
    },
    {
        "key": "risk_reversal",
        "label": "Risk reversal",
        "category": "conversion",
        "action": "Offer a zero-risk next step: free trial, outcome-guarantee, or no-obligation demo.",
    },
    {
        "key": "clear_cta",
        "label": "Single clear CTA",
        "category": "conversion",
        "action": "One obvious action per message (book, reply, or opt-in) - never a menu.",
    },
    {
        "key": "objection_preempt",
        "label": "Objection pre-empt",
        "category": "conversion",
        "action": "Anticipate the top objection and disarm it in the first email.",
    },
    {
        "key": "social_proof",
        "label": "Social proof",
        "category": "conversion",
        "action": "Cite a similar customer result or a public proof point.",
    },
    {
        "key": "timing_smart",
        "label": "Smart send timing",
        "category": "nurture",
        "action": "Send early work hours, Tuesday-Thursday, aligned to the lead's timezone.",
    },
    {
        "key": "cadence_multi_touch",
        "label": "Multi-touch cadence",
        "category": "nurture",
        "action": "Space 3-5 touches over 2-3 weeks across email + one alternate channel.",
    },
    {
        "key": "reactivation",
        "label": "Reactivation window",
        "category": "nurture",
        "action": "Re-touch a silent lead after 14-21 days with a genuinely new angle.",
    },
    {
        "key": "escalation_human",
        "label": "Human escalation",
        "category": "nurture",
        "action": "Escalate hot/+engaged leads to a closer or booked demo.",
    },
    {
        "key": "referral_hook",
        "label": "Referral hook",
        "category": "acquisition",
        "action": "Ask for referrals after a positive outcome, with a mutual reward.",
    },
    {
        "key": "winback",
        "label": "Win-back quote",
        "category": "acquisition",
        "action": "Offer a discounted win-back on leads lost < 45 days.",
    },
    {
        "key": "landing_parity",
        "label": "Landing-page parity",
        "category": "acquisition",
        "action": "Point CTAs to a landing page that mirrors the email's promise.",
    },
    {
        "key": "tracking_close",
        "label": "Closed-loop tracking",
        "category": "acquisition",
        "action": "Track opens/replies/CTAs into the deal pipeline so the funnel is accurate.",
    },
]


class OutreachMaximizer:
    """Applies a curated set of outreach levers to maximize reply + close odds."""

    def score(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Return an overall outreach-readiness score (0-100) for a lead."""
        base = 35
        email = (lead.get("email") or "").strip()
        if "@" in email and "." in email.split("@")[-1]:
            base += 5
        if lead.get("intent_score"):
            base += min(20, int(lead.get("intent_score", 0)) // 5)
        if lead.get("company"):
            base += 5
        if lead.get("source") == "voice":
            base += 3
        signals = lead.get("details", {}).get("signals") or {}
        if any(signals.values()):
            base += 4
        organic = sum(1 for k in ("budget", "need", "authority", "timeline") if signals.get(k))
        base += min(15, organic * 5)
        return {"score": max(0, min(100, base)), "band": self._band(base)}

    @staticmethod
    def _band(score: int) -> str:
        if score >= 80:
            return "ideal"
        if score >= 65:
            return "solid"
        if score >= 50:
            return "warm"
        return "cool"

    def applicable_levers(self, lead: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Which levers to apply based on lead context (deterministic)."""
        applicable = []
        for lever in LEVERS:
            score = self._lever_fit(lever, lead)
            if score > 0:
                applicable.append({**lever, "relevance": score})
        applicable.sort(key=lambda item: item["relevance"], reverse=True)
        return applicable

    @staticmethod
    def _lever_fit(lever: Dict[str, Any], lead: Dict[str, Any]) -> int:
        """Deterministic fit heuristic (1-10) for a lever on a given lead."""
        key = lever["key"]
        email = (lead.get("email") or "").strip()
        has_email = "@" in email and "." in email.split("@")[-1]
        intent = lead.get("intent_score") or 0
        signals = lead.get("details", {}).get("signals") or {}
        organic = sum(1 for k in ("budget", "need", "authority", "timeline") if signals.get(k))

        if key == "icp_accuracy":
            return 8 if (has_email and lead.get("company")) else 6 if has_email else 4
        if key == "deliverability_alias":
            return 9 if has_email else 2
        if key == "suppression":
            return 8
        if key == "fresh_list":
            return 7
        if key == "personalization":
            return 9 if lead.get("company") or signals else 6
        if key == "credibility_anchor":
            return 8 if intent >= 60 else 5
        if key == "risk_reversal":
            return 8 if intent >= 60 else 6
        if key == "clear_cta":
            return 8
        if key == "objection_preempt":
            return 7
        if key == "social_proof":
            return 8 if intent >= 70 else 6
        if key == "timing_smart":
            return 7
        if key == "cadence_multi_touch":
            return 9 if organic >= 1 else 6
        if key == "reactivation":
            return 6
        if key == "escalation_human":
            return max(4, min(9, intent // 15))
        if key == "referral_hook":
            return 6
        if key == "winback":
            return 6
        if key == "landing_parity":
            return 7
        if key == "tracking_close":
            return 8
        return 1

    def maximize(self, lead: Dict[str, Any], subject: str = "", body: str = "") -> Dict[str, Any]:
        """Rewrite a draft using the applicable levers + score it."""
        levers = self.applicable_levers(lead)
        scoring = self.score(lead)

        subject = subject or self._suggest_subject(lead)
        body = body or ""

        if "icp_accuracy" in [item["key"] for item in levers] and not body:
            body = self._suggest_hook(lead)

        return {
            "lead": lead.get("email"),
            "score": scoring["score"],
            "band": scoring["band"],
            "levers": levers,
            "suggested_subject": subject,
            "suggested_hook": self._suggest_hook(lead),
            "ready": scoring["score"] >= 65,
            "draft_line": f"Suggested first line: {self._suggest_hook(lead)}",
            "checked_at": datetime.utcnow().isoformat(),
            "_counts": {"total_levers": len(LEVERS), "applicable": len(levers)},
        }

    @staticmethod
    def _suggest_subject(lead: Dict[str, Any]) -> str:
        name = (lead.get("name") or "").split()[0] if lead.get("name") else ""
        company = lead.get("company") or "your team"
        if name:
            return f"{name} - a quick idea for {company}"
        return f"A quick idea for {company}"

    @staticmethod
    def _suggest_hook(lead: Dict[str, Any]) -> str:
        company = lead.get("company") or "your business"
        signals = lead.get("details", {}).get("signals") or {}
        if signals.get("budget"):
            return f"Noticed {company} clearly monetizes - the fix is faster capture, not more spend."
        if signals.get("need"):
            return f"Saw {company} is actively inviting customers to book. We shorten the gap between 'interest' and 'scheduled'."
        return f"For {company}, we turn inbound + outbound interest into booked calls automatically."

    def all_levers(self) -> List[Dict[str, Any]]:
        return LEVERS

    def count(self) -> int:
        return len(LEVERS)


outreach_maximizer = OutreachMaximizer()
__all__ = ["OutreachMaximizer", "outreach_maximizer", "LEVERS"]