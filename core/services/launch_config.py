"""
Launch campaign configuration and traffic-draft service.

Centralizes the Product Hunt launch metadata (dates, URLs, promo offer) and
composes share-ready social posts + Product Hunt engagement copy that the
growth loop drops into the approval queue. Every external action stays behind
the single human gate; this service only *prepares* drafts and share links.

Env overrides:
- ``LAUNCH_URL``        default https://realms2riches.com
- ``PRODUCT_HUNT_URL``  default https://www.producthunt.com/products/genesis-5
"""

import os
from datetime import datetime, timezone
from typing import Dict, List
from urllib.parse import quote

logger = None  # pragma: no cover - module import only

SITE_URL = os.getenv("LAUNCH_URL", "https://realms2riches.com")
PRODUCT_HUNT_URL = os.getenv(
    "PRODUCT_HUNT_URL", "https://www.producthunt.com/products/genesis-5"
)

LAUNCH_AT_ISO = "2026-08-03T00:01:00-04:00"
PROMO_CODE = "LAUNCH100"
PROMO_OFFER = "1 month free on any plan"
REFERRAL_CREDIT = "$50 credit"
REFERRAL_DISCOUNT = "20% off first month"

HASHTAGS = ["#AIBusiness", "#VoiceAI", "#ProductHunt", "#GenesisForge", "#LaunchDay"]

SOCIAL_POSTS = [
    {
        "network": "x",
        "text": (
            "Your business can now launch itself — by voice. We built an AI that "
            "answers your leads, qualifies them, and drafts every email. Live on "
            f"Product Hunt today! {PRODUCT_HUNT_URL} {HASHTAGS[0]} {HASHTAGS[2]}"
        ),
    },
    {
        "network": "linkedin",
        "text": (
            "I've spent months building an AI that runs a business end to end — "
            "from answering the phone in your voice to qualifying leads and "
            "drafting outreach. Genesis Forge is now live on Product Hunt. "
            f"Try it free: {SITE_URL} {HASHTAGS[0]} {HASHTAGS[3]}"
        ),
    },
    {
        "network": "facebook",
        "text": (
            "We just launched Genesis Forge — the first autonomous business "
            "launch platform powered by constitutional voice AI. Speak your "
            "vision, and a 19-agent workforce provisions, qualifies, and "
            "follows up for you. Launch week: 1 month free on any plan. "
            f"{SITE_URL} {HASHTAGS[3]}"
        ),
    },
    {
        "network": "reddit",
        "text": (
            "Built an AI that answers your business line in your voice, "
            "qualifies every lead, and drafts outreach. Full-duplex barge-in, "
            "RAG-grounded, 19 agents running the operation behind one human "
            f"approval gate. AMA / feedback welcome: {SITE_URL} {HASHTAGS[3]}"
        ),
    },
]

PH_COMMENTS = [
    (
        "What makes Genesis Forge different: full-duplex voice with real "
        "barge-in (interrupt it mid-sentence and it stops instantly), a "
        "constitutional 19-agent workforce, and every external action gated "
        "behind one human approval. Launching with a 19-agent workforce that "
        "provisions your business from a single spoken prompt."
    ),
    (
        "We've been running the autonomous growth loop for weeks — it "
        "discovers real businesses, drafts personalized outreach, and "
        "composes Stripe offers, all waiting for your single approval before "
        "anything goes out. That's the part we're most proud of: automation "
        "with a human in the loop, always."
    ),
]


def share_links() -> Dict[str, str]:
    """Pre-filled share URLs for X, Facebook, LinkedIn, WhatsApp."""
    text = quote(
        "Launch your business with your voice. Genesis Forge is live on "
        "Product Hunt — 15 AI agents run your whole operation behind one "
        "human approval gate."
    )
    ph = quote(PRODUCT_HUNT_URL, safe="")
    return {
        "x": f"https://twitter.com/intent/tweet?text={text}&url={ph}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={ph}",
        "linkedin": (
            f"https://www.linkedin.com/sharing/share-offsite/?url={ph}"
        ),
        "whatsapp": f"https://wa.me/?text={text}%20{ph}",
        "email": (
            f"mailto:?subject={quote('Launch your business with your voice')}"
            f"&body={text}%20{ph}"
        ),
    }
def status() -> Dict[str, object]:
    """Launch campaign status used by the API and landing page."""
    return {
        "launched": True,
        "product_hunt_url": PRODUCT_HUNT_URL,
        "site_url": SITE_URL,
        "launch_at_iso": LAUNCH_AT_ISO,
        "promo": {"code": PROMO_CODE, "offer": PROMO_OFFER},
        "referral": {
            "referrer_reward": REFERRAL_CREDIT,
            "referee_discount": REFERRAL_DISCOUNT,
        },
        "share": share_links(),
        "hashtags": HASHTAGS,
        "draft_count": len(SOCIAL_POSTS),
    }


def compose_traffic_drafts() -> List[Dict[str, str]]:
    """Compose ready-to-post launch traffic drafts for the approval queue."""
    drafts = [dict(post) for post in SOCIAL_POSTS]
    drafts.append(
        {
            "network": "product_hunt",
            "text": PH_COMMENTS[0],
            "kind": "ph_comment",
        }
    )
    drafts.append(
        {
            "network": "product_hunt",
            "text": PH_COMMENTS[1],
            "kind": "ph_comment",
        }
    )
    for draft in drafts:
        draft.setdefault("kind", "social_post")
    return drafts


def is_launch_week() -> bool:
    """True through the first 7 days after launch."""
    try:
        launch = datetime.fromisoformat(LAUNCH_AT_ISO)
        now = datetime.now(timezone.utc)
        if launch.tzinfo is None:
            launch = launch.replace(tzinfo=timezone.utc)
        delta = now - launch
        return 0 <= delta.total_seconds() <= 7 * 24 * 3600
    except ValueError:  # pragma: no cover - malformed constant
        return False


def activity() -> Dict[str, object]:
    """Real launch-week activity metrics for the landing ticker.

    Counts leads captured since launch (bucketed by source), high-intent
    leads, growth-loop cycles, and the approval queue. Never raises — if the
    DB is unreachable it returns zeroed stats so the landing page stays live.
    """
    launch = datetime.fromisoformat(LAUNCH_AT_ISO)
    if launch.tzinfo is None:
        launch = launch.replace(tzinfo=timezone.utc)
    since = launch.astimezone(timezone.utc).replace(tzinfo=None)

    leads_total = 0
    leads_by_source: Dict[str, int] = {}
    high_intent = 0
    try:
        import json as _json

        from core.models import Lead
        from core.persistence.session import SessionLocal

        db = SessionLocal()
        try:
            rows = (
                db.query(Lead)
                .filter(Lead.created_at >= since)
                .all()
            )
            for row in rows:
                leads_total += 1
                source = "voice"
                if row.metadata_json:
                    try:
                        meta = _json.loads(row.metadata_json)
                        source = meta.get("source") or "voice"
                    except ValueError:  # pragma: no cover - legacy row
                        pass
                leads_by_source[source] = leads_by_source.get(source, 0) + 1
                if (row.intent_score or 0) >= 70:
                    high_intent += 1
        finally:
            db.close()
    except Exception:  # pragma: no cover - DB down, keep page live
        leads_total = 0
        leads_by_source = {}
        high_intent = 0

    cycles = 0
    approval_pending = 0
    try:
        from core.services.growth_automation import growth_automation

        cycles = growth_automation.state.get("cycle_count", 0)
        approval_pending = len(growth_automation.pending_actions())
    except Exception:  # pragma: no cover - growth loop not wired
        pass

    return {
        "launch_week": is_launch_week(),
        "leads_since_launch": leads_total,
        "leads_by_source": leads_by_source,
        "high_intent_leads": high_intent,
        "growth_cycles": cycles,
        "approval_pending": approval_pending,
    }


__all__ = [
    "SITE_URL",
    "PRODUCT_HUNT_URL",
    "PROMO_CODE",
    "PROMO_OFFER",
    "SOCIAL_POSTS",
    "compose_traffic_drafts",
    "share_links",
    "status",
    "is_launch_week",
    "activity",
]
