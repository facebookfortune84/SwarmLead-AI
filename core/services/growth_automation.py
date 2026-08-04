"""
Autonomous Growth Loop — full-auto marketing / outreach / SEO / voice tuning
with a single human-in-the-loop gate.

The loop runs as a background task inside the API process (env-gated by
GROWTH_AUTO_MODE). On every cycle it:

1. SEO       — generates programmatic SEO page specs + technical SEO drafts
               (asset generation, no human gate).
2. Content   — drafts blog/social/email assets from the GTM task array
               (drafts, no human gate; publishing is the founder's job).
3. Outreach  — drafts personalized outreach for qualified leads and places
               each send in the APPROVAL QUEUE (human gate). Never sends
               without approval.
4. Voice     — reads knowledge-retrieval analytics, learns keyword boosts
               so the voice agent answers better over time (no human gate).
5. Monetize  — scores the funnel, composes Stripe checkout offers for
               high-intent leads, and places each quote in the APPROVAL
               QUEUE (human gate). Never charges without approval.

External actions (email sends, payment links) always land behind the one
human gate; the loop only ever *prepares*. This honors the constitution's
``ai_drafted_human_reviewed`` rule (docs/governance/ENFORCEMENT.md §4.4).
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("GrowthAutomation")

STATE_PATH = Path(__file__).resolve().parents[2] / "data" / "growth_state.json"

DEFAULT_CYCLE_HOURS = 6
OUTREACH_LIMIT_PER_CYCLE = 8
QUOTE_LIMIT_PER_CYCLE = 3
INTENT_QUOTE_THRESHOLD = 60

OUTREACH_ANGLES = [
    "full-duplex voice agent answers your business line in real time",
    "zero-to-provisioned: your business scaffolded from one prompt",
    "15 agent workforce runs outreach, SEO and follow-ups for you",
]

SEO_INDUSTRIES = [
    {"name": "E-Commerce", "slug": "e-commerce", "industry": "E-Commerce"},
    {"name": "Real Estate", "slug": "real-estate", "industry": "Real Estate"},
    {"name": "Home Services", "slug": "home-services", "industry": "Home Services"},
    {"name": "Dental Clinics", "slug": "dental-clinics", "industry": "Dental Clinics"},
    {"name": "Fitness Coaching", "slug": "fitness-coaching", "industry": "Fitness Coaching"},
    {"name": "Legal Practices", "slug": "legal-practices", "industry": "Legal Practices"},
    {"name": "E-Commerce Fulfillment", "slug": "e-commerce-fulfillment", "industry": "E-Commerce Fulfillment"},
    {"name": "Boutique Agencies", "slug": "boutique-agencies", "industry": "Boutique Agencies"},
    {"name": "Property Management", "slug": "property-management", "industry": "Property Management"},
    {"name": "Auto Dealerships", "slug": "auto-dealerships", "industry": "Auto Dealerships"},
    {"name": "MedSpas", "slug": "med-spas", "industry": "MedSpas"},
    {"name": "Contractors", "slug": "contractors", "industry": "Contractors"},
]

GTM_TASKS = [
    {
        "phase": "Content Marketing",
        "task": "Draft_BargeIn_Feature_Post",
        "details": "500-word technical post: Half-Duplex vs Full-Duplex AI voice agents.",
        "keywords": ["VAD", "AEC", "Latency", "Human-grade AI"],
    },
    {
        "phase": "GEO Optimization",
        "task": "Create_FAQ_for_AI_Answer_Engines",
        "details": "10 Q&As: 'How to launch a business in 5 minutes', 'What is an agentic OS'.",
        "keywords": ["agentic OS", "business launch", "provisioning"],
    },
    {
        "phase": "Product-Led Growth",
        "task": "Generate_Provisioning_Demo_Scripts",
        "details": "5 launch scenarios (E-commerce, Newsletter, SaaS, Agency, Local Service).",
        "keywords": ["e-commerce", "newsletter", "saas", "agency", "local service"],
    },
]


class ApprovalAction:
    """One pending external action awaiting the single human gate."""

    def __init__(self, kind: str, payload: Dict[str, Any]) -> None:
        self.id = uuid.uuid4().hex[:12].upper()
        self.kind = kind  # "outreach_send" | "quote_send"
        self.payload = payload
        self.status = "pending"  # pending | approved | rejected
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.reviewed_at: Optional[str] = None
        self.result: Optional[Dict] = None


class GrowthAutomation:
    """Orchestrates the autonomous growth cycle and the approval queue."""

    def __init__(self, state_path: Optional[Path] = None) -> None:
        self.state_path = state_path or STATE_PATH
        self.enabled = os.getenv("GROWTH_AUTO_MODE", "1") == "1"
        self.use_llm = os.getenv("GROWTH_USE_LLM", "0") == "1"
        self.cycle_hours = float(os.getenv("GROWTH_CYCLE_HOURS", DEFAULT_CYCLE_HOURS))
        self.state: Dict[str, Any] = self._load_state()
        self._loop_task: Optional[asyncio.Task] = None
        self._lock: Optional[asyncio.Lock] = None

    def _cycle_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    # ------------------------------------------------------------------ state
    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                logger.warning("Growth state unreadable; starting fresh")
        return self._empty_state()

    @staticmethod
    def _empty_state() -> Dict[str, Any]:
        return {
            "enabled": True,
            "cycle_count": 0,
            "last_run": None,
            "next_run": None,
            "last_errors": [],
            "funnel": {},
            "learned_keyword_boosts": {},
            "artifacts": {"seo_pages": [], "content_drafts": []},
            "approval_queue": [],
        }

    def _save_state(self) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(
                json.dumps(self.state, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.warning("Could not persist growth state: %s", exc)

    # ------------------------------------------------------------- run cycle
    async def run_cycle(self, reason: str = "scheduled") -> Dict[str, Any]:
        """Run one full growth cycle across all phases (serialized by a lock)."""
        lock = self._cycle_lock()
        if lock.locked():
            return {"status": "already_running", "reason": reason}
        async with lock:
            return await self._run_cycle_unlocked(reason)

    async def _run_cycle_unlocked(self, reason: str) -> Dict[str, Any]:
        started = datetime.now(timezone.utc).isoformat()
        cycle = {"started_at": started, "reason": reason, "phases": {}}

        phases = {
            "discovery": self._phase_discovery,
            "seo": self._phase_seo,
            "content": self._phase_content,
            "outreach": self._phase_outreach,
            "traffic": self._phase_traffic,
            "voice": self._phase_voice,
            "monetize": self._phase_monetize,
        }
        for name, phase in phases.items():
            try:
                cycle["phases"][name] = await phase()
            except Exception as exc:  # one phase must not kill the cycle
                logger.exception("Phase %s failed", name)
                cycle["phases"][name] = {"status": "error", "error": str(exc)}
                self.state["last_errors"] = (
                    self.state.get("last_errors", [])[-9:] + [f"{name}: {exc}"]
                )

        self.state["cycle_count"] += 1
        self.state["last_run"] = started
        self.state["next_run"] = (
            datetime.now(timezone.utc).timestamp() + self.cycle_hours * 3600
        )
        self._save_state()
        return cycle

    # ------------------------------------------------------------------ seo
    async def _phase_seo(self) -> Dict[str, Any]:
        from core.agents.seo.seo_agent import SEOAgent

        agent = SEOAgent("seo_agent", None)
        batch = 3
        start = (self.state.get("cycle_count", 0) * batch) % len(SEO_INDUSTRIES)
        sample = [
            SEO_INDUSTRIES[(start + i) % len(SEO_INDUSTRIES)] for i in range(batch)
        ]
        pages = await agent.generate_programmatic_pages("industries", sample)

        # Merge into the cumulative artifact set (dedupe by URL, keep latest).
        merged: Dict[str, dict] = {}
        for existing in self.state.get("artifacts", {}).get("seo_pages", []):
            merged[existing["url"]] = existing
        for page in pages:
            page["status"] = "draft"
            page["generated_at"] = self.state.get("last_run") or datetime.now(timezone.utc).isoformat()
            merged[page["url"]] = page
        self.state["artifacts"]["seo_pages"] = list(merged.values())

        tech = await agent.generate_technical_seo("landing", {})
        return {
            "status": "ok",
            "pages_generated": len(pages),
            "cumulative_pages": len(merged),
            "sample_slugs": [p["url"] for p in pages],
            "technical": tech["meta_tags"]["title"],
        }

    # --------------------------------------------------------------- content
    async def _phase_content(self) -> Dict[str, Any]:
        from core.agents.content.content_agent import ContentAgent

        agent = ContentAgent("content_agent", None)
        cycle = self.state.get("cycle_count", 0)
        drafts = []
        for idx, task in enumerate(GTM_TASKS):
            if not self.use_llm:
                drafts.append(
                    {
                        "task": task["task"],
                        "phase": task["phase"],
                        "variant": (cycle * len(GTM_TASKS)) + idx,
                        "content": self._content_scaffold(task),
                        "seo_score": None,
                    }
                )
                continue
            try:
                result = await asyncio.wait_for(
                    agent.generate_content(
                        "blog",
                        {"topic": task["task"], "keywords": task["keywords"]},
                        seo_keywords=task["keywords"],
                    ),
                    timeout=15,
                )
                if "error" in result:
                    raise RuntimeError(result["error"])
                drafts.append(
                    {
                        "task": task["task"],
                        "phase": task["phase"],
                        "variant": (cycle * len(GTM_TASKS)) + idx,
                        "content": result["content"],
                        "seo_score": result.get("seo_score"),
                    }
                )
            except asyncio.TimeoutError:
                drafts.append(
                    {
                        "task": task["task"],
                        "phase": task["phase"],
                        "variant": (cycle * len(GTM_TASKS)) + idx,
                        "content": f"[Draft scaffold for {task['task']} — LLM timed out]",
                        "seo_score": None,
                    }
                )
        # Merge into cumulative set keyed by task (latest variant wins).
        merged: Dict[str, dict] = {}
        for existing in self.state.get("artifacts", {}).get("content_drafts", []):
            merged[existing["task"]] = existing
        for draft in drafts:
            merged[draft["task"]] = draft
        self.state["artifacts"]["content_drafts"] = list(merged.values())
        return {
            "status": "ok",
            "drafts_ready": len(drafts),
            "cumulative_drafts": len(merged),
        }

    @staticmethod
    def _content_scaffold(task: Dict[str, Any]) -> str:
        return (
            f"# {task['task'].replace('_', ' ').title()}\n\n"
            f"## Why it matters\n"
            f"{task['details']}\n\n"
            f"## Target keywords\n"
            + ", ".join(task.get("keywords", []))
            + "\n\n"
            "## Body\n"
            "[Expand with the voice-agent differentiator: full-duplex barge-in, "
            "zero-to-provisioned launch OS, 15-agent workforce.]\n\n"
            "## CTA\n"
            "Try the live voice agent on the landing page — it answers in seconds."
        )

    # --------------------------------------------------------------- discovery
    async def _phase_discovery(self) -> Dict[str, Any]:
        """Find real businesses that publish a contact email on their site.

        Discovery is internal prep (DB rows only) — it never sends email.
        Drafted outreach still lands behind the founder's approve gate.
        Gated by GROWTH_DISCOVERY=1 so tests and CPU-only setups stay fast.
        """
        if os.getenv("GROWTH_DISCOVERY", "1") != "1":
            return {"status": "ok", "discovered": 0, "written": 0, "verticals": []}
        from core.services.lead_discovery import lead_discovery

        found = await lead_discovery.discover(max_targets=6)
        written = 0
        for lead in found:
            try:
                from core.models import Lead
                from core.persistence.session import SessionLocal

                db = SessionLocal()
                try:
                    existing = (
                        db.query(Lead).filter(Lead.email == lead.email).first()
                    )
                    if existing:
                        continue
                    db.add(
                        Lead(
                            email=lead.email,
                            name=lead.name or lead.company,
                            company=lead.company,
                            status="NEW",
                            website=lead.website,
                            intent_score=lead.intent_score,
                            metadata_json=json.dumps(
                                {
                                    "source": lead.source,
                                    "vertical": lead.vertical,
                                    "confidence": lead.confidence,
                                    "details": lead.details,
                                }
                            ),
                        )
                    )
                    db.commit()
                    written += 1
                finally:
                    db.close()
            except Exception as exc:  # pragma: no cover
                logger.info("Could not persist discovered lead: %s", exc)
        return {
            "status": "ok",
            "discovered": len(found),
            "written": written,
            "verticals": sorted({ld.vertical for ld in found}),
        }

    # --------------------------------------------------------------- outreach
    async def _phase_outreach(self) -> Dict[str, Any]:
        leads = self._qualified_leads(limit=OUTREACH_LIMIT_PER_CYCLE)
        drafted = 0
        domain_counts: Dict[str, int] = {}
        for lead in leads:
            if self._pending_count("outreach_send") >= OUTREACH_LIMIT_PER_CYCLE:
                break
            if self._already_contacted(lead["email"]):
                continue
            if self._suppressed(lead["email"]):
                continue
            domain = lead["email"].split("@")[-1].lower()
            if domain_counts.get(domain, 0) >= 2:
                continue
            message = self._draft_outreach(lead)
            self._enqueue(
                "outreach_send",
                {
                    "to_email": lead["email"],
                    "lead_name": lead.get("name") or lead["email"],
                    "subject": message["subject"],
                    "body": message["body"],
                },
            )
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            drafted += 1
        return {"status": "ok", "leads_qualified": len(leads), "drafted": drafted}

    # ---------------------------------------------------------------- traffic
    async def _phase_traffic(self) -> Dict[str, Any]:
        """Compose launch-traffic drafts (social posts + PH comments).

        Only runs during launch week, caps at 2 drafts per cycle, and never
        duplicates a pending/approved post. Posts are *drafts for the human
        gate* — the system never posts to social networks on its own.
        """
        from core.services.launch_config import compose_traffic_drafts, is_launch_week

        if not is_launch_week():
            return {"status": "skipped", "reason": "outside launch week"}

        drafts = compose_traffic_drafts()
        queued = 0
        for draft in drafts:
            if self._pending_count("traffic_post") >= 2:
                break
            fingerprint = (draft.get("network"), draft.get("kind", "social_post"))
            if self._traffic_drafted(fingerprint):
                continue
            self._enqueue(
                "traffic_post",
                {
                    "network": draft["network"],
                    "kind": draft.get("kind", "social_post"),
                    "text": draft["text"],
                    "note": (
                        "Copy-paste this post to the network, or use the "
                        "share links from /api/launch/status."
                    ),
                },
            )
            queued += 1
        return {"status": "ok", "drafts_queued": queued, "total_available": len(drafts)}

    def _traffic_drafted(self, fingerprint: tuple) -> bool:
        return any(
            a["kind"] == "traffic_post"
            and (a["payload"].get("network"), a["payload"].get("kind")) == fingerprint
            and a["status"] in {"pending", "approved"}
            for a in self.state.get("approval_queue", [])
        )

    def _suppressed(self, email: str) -> bool:
        from core.services.deliverability import deliverability

        return deliverability.is_suppressed(email)

    def _qualified_leads(self, limit: int) -> List[Dict]:
        from core.services.lead_discovery import DISPOSABLE_DOMAINS, RESERVED_DOMAINS

        try:
            from core.models import Lead
            from core.persistence.session import SessionLocal

            db = SessionLocal()
            try:
                rows = (
                    db.query(Lead)
                    .filter(Lead.email_invalid.isnot(True))
                    .filter(Lead.status == "NEW")
                    .order_by(Lead.intent_score.desc(), Lead.created_at.desc())
                    .limit(limit * 3)
                    .all()
                )
                out = []
                for r in rows:
                    if not r.email or "@" not in r.email:
                        continue
                    domain = r.email.split("@")[-1].lower()
                    # Accuracy gate: never draft to reserved / disposable /
                    # free-email test artifacts. Business-domain only.
                    if domain in RESERVED_DOMAINS or domain in DISPOSABLE_DOMAINS:
                        continue
                    if self._suppressed(r.email):
                        continue
                    out.append(
                        {
                            "email": r.email,
                            "name": r.name,
                            "company": r.company,
                            "intent_score": r.intent_score or 0,
                            "website": r.website,
                        }
                    )
                    if len(out) >= limit:
                        break
                return out
            finally:
                db.close()
        except Exception as exc:  # DB unavailable in some test contexts
            logger.info("Lead query unavailable (%s); using fixture list", exc)
            return [
                {
                    "email": "owner@smithplumbing.com",
                    "name": "Example Lead",
                    "company": "Smith Plumbing",
                    "intent_score": 80,
                }
            ]

    def _draft_outreach(self, lead: Dict) -> Dict[str, str]:
        angle = OUTREACH_ANGLES[(lead["intent_score"] or 0) % len(OUTREACH_ANGLES)]
        name = lead.get("name") or "there"
        company = lead.get("company") or "your company"
        subject = f"Meet the AI that answers for {company}"
        body = (
            f"Hi {name},\n\n"
            f"SwarmOS just shipped a full-duplex voice agent and a 15-agent "
            f"workforce that runs outreach, SEO and follow-ups automatically. "
            f"The headline: {angle}.\n\n"
            f"Want a 5-minute, zero-setup demo for {company}? Book a slot here and "
            f"we'll provision your workspace live.\n\n"
            f"Best,\nThe SwarmOS Team"
        )
        return {"subject": subject, "body": body}

    # ---------------------------------------------------------------- voice
    async def _phase_voice(self) -> Dict[str, Any]:
        from core.services.product_knowledge import product_knowledge

        snapshot = product_knowledge.analytics_snapshot()
        boosts: Dict[str, float] = {}

        monet = snapshot.get("monetization")
        if monet and monet["count"] >= 2:
            for term in monet["terms"]:
                if term in {"price", "pricing", "cost", "plan", "subscribe", "buy", "trial"}:
                    boosts[term] = 0.4
        support = snapshot.get("support")
        if support and support["count"] >= 3:
            for term in support["terms"]:
                if term in {"ticket", "support", "issue"}:
                    boosts[term] = 0.3

        if boosts:
            product_knowledge.learn(boosts)
            for kw, w in boosts.items():
                self.state["learned_keyword_boosts"][kw] = (
                    self.state["learned_keyword_boosts"].get(kw, 0.0) + w
                )

        return {
            "status": "ok",
            "intents": {k: v["count"] for k, v in snapshot.items() if isinstance(v, dict) and "count" in v and not k.startswith("chunk:")},
            "boosts_applied": boosts,
        }

    # ---------------------------------------------------------------- monetize
    async def _phase_monetize(self) -> Dict[str, Any]:
        funnel = self._funnel_snapshot()
        self.state["funnel"] = funnel

        from core.agents.growth.growth_agent import GrowthAgent

        growth = GrowthAgent("growth_agent", None)
        analysis = await growth.analyze_funnel(
            {
                "visitors": funnel.get("visitors", 0),
                "activation_rate": funnel.get("activation_rate", 0),
                "retention_rate": funnel.get("retention_rate", 0),
                "conversion_rate": funnel.get("conversion_rate", 0),
                "referral_rate": 0.0,
            }
        )

        quoted = 0
        for lead in self._high_intent_leads(limit=QUOTE_LIMIT_PER_CYCLE):
            if self._already_quoted(lead["email"]):
                continue
            if self._pending_count("quote_send") >= QUOTE_LIMIT_PER_CYCLE:
                break
            offer = self._compose_offer(lead)
            if not offer.get("checkout_url"):
                continue
            self._enqueue(
                "quote_send",
                {
                    "to_email": lead["email"],
                    "lead_name": lead.get("name") or lead["email"],
                    "subject": f"Your {offer['tier'].title()} workspace is ready",
                    "body": (
                        f"Hi {lead.get('name') or 'there'},\n\n{offer['message']}\n\n"
                        f"Start here: {offer['checkout_url']}\n\nSwarmOS"
                    ),
                    "tier": offer["tier"],
                    "checkout_url": offer["checkout_url"],
                },
            )
            quoted += 1

        return {
            "status": "ok",
            "funnel_health": analysis.get("overall_health"),
            "bottlenecks": [b["stage"] for b in analysis.get("bottlenecks", [])],
            "quotes_prepared": quoted,
        }

    def _compose_offer(self, lead: Dict) -> Dict:
        from core.services.monetization import monetization

        return monetization.offer_for(lead)

    def _funnel_snapshot(self) -> Dict[str, Any]:
        try:
            from core.models import Lead, Ticket, User
            from core.persistence.session import SessionLocal

            db = SessionLocal()
            try:
                leads_total = db.query(Lead).count()
                leads_new = db.query(Lead).filter(Lead.status == "NEW").count()
                users = db.query(User).count()
                tickets = db.query(Ticket).count()
            finally:
                db.close()
            return {
                "visitors": leads_total * 3 + 100,
                "leads": leads_total,
                "leads_new": leads_new,
                "users": users,
                "tickets": tickets,
                "activation_rate": min(0.9, users / max(leads_total, 1)),
                "conversion_rate": min(0.5, tickets / max(users, 1) * 0.1),
            }
        except Exception as exc:
            logger.info("Funnel query unavailable: %s", exc)
            return {
                "visitors": 0,
                "leads": 0,
                "users": 0,
                "tickets": 0,
                "activation_rate": 0.0,
                "conversion_rate": 0.0,
            }

    def _high_intent_leads(self, limit: int) -> List[Dict]:
        return [
            lead
            for lead in self._qualified_leads(limit=100)
            if (lead.get("intent_score") or 0) >= INTENT_QUOTE_THRESHOLD
        ][:limit]

    # ---------------------------------------------------------- approval gate
    def _enqueue(self, kind: str, payload: Dict[str, Any]) -> None:
        action = ApprovalAction(kind, payload)
        self.state.setdefault("approval_queue", []).append(
            {
                "id": action.id,
                "kind": kind,
                "payload": payload,
                "status": "pending",
                "created_at": action.created_at,
                "reviewed_at": None,
                "result": None,
            }
        )
        self._save_state()

    def _pending_count(self, kind: str) -> int:
        return sum(
            1
            for a in self.state.get("approval_queue", [])
            if a["status"] == "pending" and a["kind"] == kind
        )

    def _already_contacted(self, email: str) -> bool:
        return any(
            a["kind"] == "outreach_send"
            and a["payload"].get("to_email") == email
            and a["status"] in {"pending", "approved"}
            for a in self.state.get("approval_queue", [])
        )

    def _already_quoted(self, email: str) -> bool:
        return any(
            a["kind"] == "quote_send"
            and a["payload"].get("to_email") == email
            and a["status"] in {"pending", "approved"}
            for a in self.state.get("approval_queue", [])
        )

    def pending_actions(self) -> List[Dict]:
        return [a for a in self.state.get("approval_queue", []) if a["status"] == "pending"]

    async def approve(self, action_id: str) -> Dict[str, Any]:
        """THE human gate: review + approve one queued external action."""
        action = self._find_action(action_id)
        if not action:
            return {"status": "not_found"}
        if action["status"] != "pending":
            return {"status": "already_reviewed", "current": action["status"]}

        if action["kind"] == "outreach_send":
            result = await self._dispatch_outreach(action)
        elif action["kind"] == "quote_send":
            result = await self._dispatch_quote(action)
        elif action["kind"] == "traffic_post":
            from core.services.launch_config import share_links

            result = {
                "status": "approved_for_manual_post",
                "note": (
                    "Approved copy. Post it on the target network and record "
                    "the URL in the payload when done."
                ),
                "share_links": share_links(),
            }
        else:
            result = {"status": "unknown_kind"}

        if result.get("status") == "failed":
            self._record_failure(action, result)
        elif action["kind"] == "quote_send" and result.get("status") == "sent":
            self._record_quote(action)

        approved_statuses = {"sent", "dry_run", "approved_for_manual_post"}
        action["status"] = "approved" if result.get("status") in approved_statuses else "failed"
        action["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        action["result"] = result
        self._save_state()
        return {"status": action["status"], "result": result}

    def _record_failure(self, action: Dict, result: Dict) -> None:
        """Auto-suppress bounced / failed sends so we never retry a dead address."""
        try:
            from core.services.deliverability import deliverability

            email = action["payload"].get("to_email", "")
            error = str(result.get("error", ""))
            if any(m in error.lower() for m in ("bounce", "550", "5.1.1", "undeliverable", "blocked")):
                deliverability.record_bounce(email, error)
            elif any(m in error.lower() for m in ("unsubscribe", "complaint", "spam")):
                deliverability.record_complaint(email)
            else:
                deliverability.suppress(email, f"failed_send:{error[:60]}")
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not record suppression: %s", exc)

    def _record_quote(self, action: Dict) -> None:
        """Track approved/paid quotes for MRR projection."""
        tier = action["payload"].get("tier", "growth")
        monthly = {"starter": 29, "growth": 99, "enterprise": 299}.get(tier, 99)
        rev = self.state.setdefault("revenue", {"quotes_approved": 0, "projected_mrr": 0})
        rev["quotes_approved"] = rev.get("quotes_approved", 0) + 1
        rev["projected_mrr"] = rev.get("projected_mrr", 0) + monthly
        self._save_state()

    def reject(self, action_id: str, note: str = "") -> Dict[str, Any]:
        action = self._find_action(action_id)
        if not action:
            return {"status": "not_found"}
        action["status"] = "rejected"
        action["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        action["result"] = {"note": note}
        self._save_state()
        return {"status": "rejected"}

    def purge(self, action_id: str) -> Dict[str, Any]:
        """Remove a queued action AND suppress its email so it never re-drafts."""
        action = self._find_action(action_id)
        if not action:
            return {"status": "not_found"}
        email = action.get("payload", {}).get("to_email", "")
        if email:
            try:
                from core.services.deliverability import deliverability

                deliverability.suppress(email, "purged_test_lead")
                # Durable: mark the Lead row invalid so purge survives container
                # recreates (the file-based suppression list does not).
                try:
                    from core.models import Lead
                    from core.persistence.session import SessionLocal

                    db = SessionLocal()
                    try:
                        rows = db.query(Lead).filter(Lead.email == email).all()
                        for row in rows:
                            row.email_invalid = True
                            row.status = "PURGED"
                        db.commit()
                    finally:
                        db.close()
                except Exception as exc:  # pragma: no cover
                    logger.warning("Could not mark lead purged: %s", exc)
            except Exception as exc:  # pragma: no cover
                logger.warning("Could not suppress purged lead: %s", exc)
        self.state["approval_queue"] = [
            a for a in self.state.get("approval_queue", []) if a["id"] != action_id
        ]
        self._save_state()
        return {"status": "purged", "email": email}

    def purge_all_pending(self) -> Dict[str, Any]:
        """Purge every pending action in the queue (bulk cleanup)."""
        removed = []
        for action in list(self.state.get("approval_queue", [])):
            if action["status"] == "pending":
                self.purge(action["id"])
                removed.append(action["id"])
        return {"status": "purged", "removed": len(removed)}

    def _find_action(self, action_id: str) -> Optional[Dict]:
        for a in self.state.get("approval_queue", []):
            if a["id"] == action_id:
                return a
        return None

    async def _dispatch_outreach(self, action: Dict) -> Dict:
        from core.services.email_sender import email_sender

        payload = action["payload"]
        return await email_sender.send(
            payload["to_email"],
            payload["subject"],
            payload["body"],
        )

    async def _dispatch_quote(self, action: Dict) -> Dict:
        from core.services.email_sender import email_sender

        payload = action["payload"]
        return await email_sender.send(
            payload["to_email"],
            payload["subject"],
            payload["body"],
        )

    # -------------------------------------------------------------- lifecycle
    async def start_loop(self) -> None:
        """Background loop: run a cycle now, then every cycle_hours."""
        if self._loop_task and not self._loop_task.done():
            return
        if not self.enabled:
            logger.info("Growth auto mode disabled (GROWTH_AUTO_MODE=0)")
            return

        async def _loop():
            logger.info("Growth loop started; cycle every %.1fh", self.cycle_hours)
            while True:
                try:
                    await self.run_cycle()
                except Exception as exc:  # never kill the loop
                    logger.exception("Growth cycle crashed: %s", exc)
                await asyncio.sleep(self.cycle_hours * 3600)

        self._loop_task = asyncio.create_task(_loop())

    async def run_now(self) -> Dict[str, Any]:
        return await self.run_cycle(reason="manual")

    def status(self) -> Dict[str, Any]:
        from core.services.deliverability import deliverability

        return {
            "enabled": self.enabled,
            "cycle_hours": self.cycle_hours,
            "cycle_count": self.state.get("cycle_count", 0),
            "last_run": self.state.get("last_run"),
            "next_run": self.state.get("next_run"),
            "funnel": self.state.get("funnel", {}),
            "revenue": self.state.get("revenue", {"quotes_approved": 0, "projected_mrr": 0}),
            "deliverability": deliverability.score(),
            "learned_keyword_boosts": self.state.get("learned_keyword_boosts", {}),
            "discovery": {
                "findings": self._discovery_count(),
                "recent": self._recent_discoveries(5),
            },
            "artifacts": {
                "seo_pages": len(self.state.get("artifacts", {}).get("seo_pages", [])),
                "content_drafts": len(self.state.get("artifacts", {}).get("content_drafts", [])),
            },
            "approval_queue": {
                "total": len(self.state.get("approval_queue", [])),
                "pending": len(self.pending_actions()),
                "pending_outreach": self._pending_count("outreach_send"),
                "pending_quotes": self._pending_count("quote_send"),
            },
        }

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self.state["enabled"] = enabled
        self._save_state()

    def _discovery_count(self) -> int:
        try:
            from core.services.lead_discovery import lead_discovery

            return len(lead_discovery.findings())
        except Exception:
            return 0

    def _recent_discoveries(self, n: int) -> List[Dict]:
        try:
            from core.services.lead_discovery import lead_discovery

            return lead_discovery.findings()[:n]
        except Exception:
            return []


growth_automation = GrowthAutomation()

__all__ = ["GrowthAutomation", "growth_automation", "ApprovalAction"]
