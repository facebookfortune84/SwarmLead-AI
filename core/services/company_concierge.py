"""
Company Concierge - voice/text guided company creation, end to end.

Turns a founder's spoken answers into a *complete, buildable brief* for the
agent swarm. The concierge runs the journey step by step:

1. NAME   - brainstorm company names (checks against a known-taken set)
2. DOMAIN - suggest a domain for the chosen name (checks availability locally)
3. AUDIENCE - who the buyer is (description)
4. ROLES  - which agent roles to staff on the swarm
5. OFFER  - what is sold, price point, why-it-premium
6. READY  - synthesize everything into a refined, agent-ready company brief

The concierge is deterministic and scriptable: it never depends on the LLM to
advance a step (the LLM can enrich but the flow moves with or without it), so
the voice loop is always responsive. External "checks" (name/domain collisions)
run against local registries so the flow is honest and offline-safe.

Constitutional: this service *prepares* the brief. It never charges, never
sends, never provisions anything itself — delivery is a separate builder action
that stays behind the human approval gate.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------- registries

# A tiny, honest "taken" registry so name/domain checks return reproducible
# results offline. In production this would consult WHOIS/DNS + a real
# trademark DB; the deterministic registry keeps the demo/test surface stable.
TAKEN_NAMES = {
    "google", "facebook", "amazon", "apple", "microsoft", "meta", "tesla",
    "stripe", "openai", "anthropic", "genesis", "swarmos", "realms", "riches",
    "elevenlabs", "windsurf", "arcane", "claude",
}

TAKEN_DOMAINS = {
    "google.com", "facebook.com", "example.com", "test.com", "a.com", "b.com",
    "genesis.ai", "swarmos.com", "stripe.com", "openai.com", "apple.com",
    "microsoft.com", "meta.com", "tesla.com", "amazon.com",
}

RESERVED_TLDS = {"com", "net", "org", "io", "ai", "co", "app", "dev", "shop"}

# Swarm roles the founder can request to staff on their company.
AGENT_STAFFING = {
    "sdr_agent": "BANT-lite qualification, cadence, reactivation",
    "outreach_agent": "personalized outreach, follow-ups, messaging",
    "content_agent": "blog, landing copy, email/social templates",
    "seo_agent": "technical SEO, sitemap/robots/JSON-LD, programmatic pages",
    "growth_agent": "funnel health, experiments, LTV/CAC, churn",
    "closer_agent": "tiered offers, objection handling, closing",
    "voice_agent": "24/7 voice assistant, lead capture, voice onboarding",
    "landing_agent": "landing-flow qualification, voice-driven funnels",
}

DEFAULT_STAFF = ["sdr_agent", "outreach_agent", "content_agent"]

CHECKLIST = [
    "Create environment & tenant",
    "Provision voice agent with your greeting style",
    "Generate landing page + SEO assets (robots, sitemap, JSON-LD)",
    "Build 3+ prebuilt workflow templates",
    "Enqueue discovery + SDR qualification loop",
    "Set up referral + win-back monetization rails",
]


@dataclass
class ConciergePiece:
    """Single field collected during the guided flow."""

    name: str
    prompt: str
    required: bool = True


@dataclass
class ConciergeRow:
    """Mutable session state for one founder's creation journey."""

    session_id: str
    step_index: int = field(default=0)
    brief: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, str]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


FLOW: List[ConciergePiece] = [
    ConciergePiece(
        "company",
        "Let's find a great name for your business. One sentence: what do you "
        "(or will you) sell, and who's the customer? I'll brainstorm names that "
        "aren't taken and suggest a free domain.",
    ),
    ConciergePiece(
        "domain",
        "Here's a name that's free and a matching domain. Tell me a domain "
        "extension you'd like to check (.com, .io, .ai, .co, .app, .dev) or "
        "the domain you prefer.",
    ),
    ConciergePiece(
        "audience",
        "Describe your ideal customer - role, company size, and the job they "
        "hire you for. No marketing speak, just the real buyer.",
    ),
    ConciergePiece(
        "roles",
        "Which agent roles do you want on the swarm? I can staff SDR, outreach, "
        "content, SEO, growth, closer, voice and landing agents. List the ones "
        "that matter most.",
    ),
    ConciergePiece(
        "offer",
        "What exactly are you selling, at what price, and why would a customer "
        "pay for it over free alternatives?",
    ),
    ConciergePiece(
        "prompt",
        "Here's the brief the agents will use to build your company:\n{brief}\n\n"
        "Reply 'launch' to build all of it, or tell me what to change.",
    ),
]


class CompanyConcierge:
    """Deterministic, guided flow that collects a buildable company brief.

    Name/domain availability checks are local + deterministic so the flow is
    honest and offline-safe. Each ``advance()`` moves one step; the final
    ``brief`` is a single refined prompt the builder agents can consume.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, ConciergeRow] = {}

    # ------------------------------------------------------------ lifecycle

    def start(
        self, founder_name: str = "", opening_line: str = ""
    ) -> Dict[str, Any]:
        session_id = f"cc_{uuid.uuid4().hex[:10]}"
        row = ConciergeRow(
            session_id=session_id,
            brief={
                "founder_name": founder_name,
                "opening_line": opening_line,
                "company": "",
                "company_candidates": [],
                "domain": "",
                "domains": [],
                "audience": "",
                "roles": list(DEFAULT_STAFF),
                "offer": "",
                "product_tagline": "",
                "finished": False,
            },
        )
        self._sessions[session_id] = row
        return self._payload(row, prompt=self._prompt_for("company", row.brief), step="company")

    def get(self, session_id: str) -> Optional[ConciergeRow]:
        return self._sessions.get(session_id)

    def end(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def brief_for(self, session_id: str) -> Optional[Dict[str, Any]]:
        row = self.get(session_id)
        return dict(row.brief) if row else None

    # ------------------------------------------------------------- payload

    @staticmethod
    def _payload(
        row: ConciergeRow,
        prompt: str = "",
        step: Optional[str] = None,
        done: bool = False,
        brief: str = "",
        launch_signal: bool = False,
    ) -> Dict[str, Any]:
        """Shape a deterministic turn payload for the voice/UI layer."""
        return {
            "session_id": row.session_id,
            "step": step if step is not None else row.step(),
            "done": done or row.brief.get("finished", False),
            "prompt": prompt,
            "brief": brief or row.brief.get("brief_text", ""),
            "company": row.brief.get("company", ""),
            "domain": row.brief.get("domain", ""),
            "domains": row.brief.get("domains", []),
            "candidates": row.brief.get("company_candidates", []),
            "launch_signal": launch_signal,
            "history": list(row.history[-20:]),
        }

    def advance(self, session_id: str, user_text: str) -> Dict[str, Any]:
        """Advance one step based on the founder's answer (free text)."""
        row = self._sessions.get(session_id)
        if row is None:
            auto = self.start(opening_line=user_text)
            return auto

        row.history.append({"role": "user", "content": user_text})
        step = self._current_step(row)

        if step == "company":
            self._collect_company(row, user_text)
        elif step == "domain":
            self._collect_domain(row, user_text)
        elif step == "audience":
            row.brief["audience"] = user_text.strip()
        elif step == "roles":
            self._collect_roles(row, user_text)
        elif step == "offer":
            self._collect_offer(row, user_text)
        elif step == "prompt":
            if self._is_launch(user_text):
                row.step_index += 1
                row.brief["finished"] = True
                row.brief["brief_text"] = self._build_brief(row)
                return self._payload(
                    row,
                    step="done",
                    done=True,
                    brief=self._build_brief(row),
                    launch_signal=True,
                )
            # Refinement pass: overwrite whichever free-form field the founder
            # is correcting, then rebuild the final brief.
            self._apply_refinement(row, user_text)
            row.brief["brief_text"] = self._build_brief(row)
            return self._payload(
                row,
                step="prompt",
                prompt=self._prompt_for("prompt", row.brief),
            )

        row.step_index = min(row.step_index + 1, len(FLOW) - 1)
        next_step = self._current_step(row)
        return self._payload(row, step=next_step, prompt=self._prompt_for(next_step, row.brief))

    # ---------------------------------------------------------------- brief

    def _collect_company(self, row: ConciergeRow, text: str) -> None:
        """Brainstorm candidate names. Pick an available one as default."""
        candidates = self.brainstorm_names(text)
        row.brief["company_candidates"] = [
            {"name": n, "available": a} for n, a in candidates
        ]
        avail = [n for n, a in candidates if a]
        if avail and not row.brief.get("company"):
            row.brief["company"] = avail[0]
        elif not avail:
            row.brief["company"] = self._slugify(text) or "your-company"
        # Also keep the raw founder description for the final brief.
        row.brief["raw_company"] = text.strip()
        row.brief["product_tag"] = text.strip()[:160]

    def _collect_domain(self, row: ConciergeRow, text: str) -> None:
        name = row.brief.get("company") or self._slugify(text)
        tld = self._pick_tld(text)
        picked = self.domain_for(name, tld=tld)
        suggestions = self.domain_suggestions(name)
        row.brief["domains"] = suggestions
        row.brief["domain"] = picked["domain"]
        row.brief["domain_available"] = picked["available"]

    def _collect_roles(self, row: ConciergeRow, text: str) -> None:
        tokens = [t.strip() for t in re.split(r"[,;/]| and ", text.lower()) if t.strip()]
        roles = []
        for token in tokens:
            for key in AGENT_STAFFING:
                label = key.replace("_agent", "").replace("_", " ")
                if key.split("_")[0] in token or label in token:
                    roles.append(key)
        row.brief["roles"] = list(dict.fromkeys(roles)) or list(DEFAULT_STAFF)

    def _collect_offer(self, row: ConciergeRow, text: str) -> None:
        row.brief["offer"] = text.strip()

    def _is_launch(self, text: str) -> bool:
        return (
            "launch" in text.lower()
            or "build it" in text.lower()
            or text.strip().lower() == "go"
        )

    def _apply_refinement(self, row: ConciergeRow, text: str) -> None:
        """Best-effort: if the founder corrects a field, merge it; else keep the
        most recent text as the offer/audience tweak. Deterministic and cheap."""
        lower = text.lower()
        if any(k in lower for k in ("audience", "customer", "who")):
            row.brief["audience"] = text.strip()
        elif any(k in lower for k in ("offer", "price", "sell")):
            row.brief["offer"] = text.strip()
        elif any(k in lower for k in ("roles", "staff", "agents")):
            self._collect_roles(row, text)
        else:
            row.brief["audience"] = text.strip()

    # ------------------------------------------------------------- suggestions

    def brainstorm_names(self, idea: str) -> List[Tuple[str, bool]]:
        """Deterministic name brainstorm returning (name, available) pairs."""
        idea = re.sub(r"[^a-z0-9 ]", "", (idea or "").lower())
        words = [w for w in idea.split() if len(w) >= 2][:3]
        base = self._slugify(" ".join(words))
        suffixes = ["ly", "io", "a", "o", "hic", "app", "hub", "os", "x", "er"]
        prefixes = ["Nova", "Atlas", "Vertex", "Nucleus", "Zenith", "Pulse", "Orbit", "True"]
        candidates: List[str] = []
        for suf in suffixes:
            cand = base + suf if base else ""
            if cand and len(cand) <= 16 and cand not in candidates:
                candidates.append(cand)
        for pre in prefixes[:4]:
            for w in words[:1]:
                cand = (pre + w.capitalize()) if w else ""
                if cand and len(cand) <= 16 and cand not in candidates:
                    candidates.append(cand)
        for w in words[:2]:
            if w not in candidates:
                candidates.append(w)
        if base and base not in candidates:
            candidates.append(base)
        out = []
        seen = set()
        for name in candidates:
            if name in seen:
                continue
            seen.add(name)
            out.append((name, self.name_available(name)))
        return out

    def name_available(self, name: str) -> bool:
        slug = self._slugify(name)
        return bool(slug) and 3 <= len(slug) <= 18 and slug not in TAKEN_NAMES

    def domain_for(self, name: str, tld: str = "com") -> Dict[str, Any]:
        tld = (tld or "com").strip().lower().lstrip(".")
        full = f"{self._slugify(name)}.{tld if tld in RESERVED_TLDS else 'com'}"
        return {"domain": full, "available": self.domain_available(full)}

    def domain_suggestions(self, name: str) -> List[Dict[str, Any]]:
        slug = self._slugify(name)
        return [
            {"domain": f"{slug}.{tld}", "available": self.domain_available(f"{slug}.{tld}")}
            for tld in RESERVED_TLDS
        ]

    def domain_available(self, domain: str) -> bool:
        domain = (domain or "").strip().lower()
        if not re.match(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z]{2,})+$", domain):
            return False
        if domain in TAKEN_DOMAINS:
            return False
        tld = domain.rsplit(".", 1)[-1]
        return tld in RESERVED_TLDS

    @staticmethod
    def _pick_tld(text: str) -> str:
        match = re.search(r"\.([a-z]{2,4})", (text or "").lower())
        if match and match.group(1) in RESERVED_TLDS:
            return match.group(1)
        if len((text or "").strip()) <= 4 and (text or "").strip() in RESERVED_TLDS:
            return text.strip()
        return "com"

    @staticmethod
    def _slugify(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
        return slug[:63] or "acme"

    # ------------------------------------------------------------- brief

    def _current_step(self, row: ConciergeRow) -> str:
        if row.brief.get("finished"):
            return "done"
        idx = min(max(row.step_index, 0), len(FLOW) - 1)
        return FLOW[idx].name

    def _prompt_for(self, step: str, brief: Dict[str, Any]) -> str:
        for piece in FLOW:
            if piece.name == step:
                if step == "prompt":
                    return piece.prompt.format(brief=self._build_brief_from(brief))
                return piece.prompt
        return "What would you like to do next?"

    def _build_brief(self, row: ConciergeRow) -> str:
        return self._build_brief_from(row.brief)

    @staticmethod
    def _build_brief_from(brief: Dict[str, Any]) -> str:
        lines = [
            f"Company name: {brief.get('company') or 'unset'}",
            f"Company tagline/product idea: {brief.get('product_tag') or brief.get('opening_line') or ''}",
            f"Audience: {brief.get('audience') or 'to be defined'}",
            f"Offer: {brief.get('offer') or 'to be defined'}",
            f"Domain: {brief.get('domain') or 'to be claimed'}",
            f"Staff agents: {', '.join(brief.get('roles') or [])}",
        ]
        return "<br/>".join(line for line in lines if line.rsplit(": ", 1)[-1])

    # ------------------------------------------------------------- delivery

    def build_brief_props(self, session_id: str) -> Dict[str, Any]:
        """Flatten the session brief into the Company Builder input shape."""
        row = self.get(session_id)
        if row is None:
            return {}
        b = row.brief
        return {
            "business_name": b.get("company", ""),
            "business_description": " | ".join(
                p for p in [b.get("product_tag", ""), b.get("audience", ""), b.get("offer", "")] if p
            ),
            "founder_goal": b.get("audience", "") or "Launch and grow",
            "domain": b.get("domain", ""),
            "roles_staffed": b.get("roles", []),
            "brief": CompanyConcierge._build_brief_from(b),
        }

    # ------------------------------------------------------------- status

    def status(self) -> Dict[str, Any]:
        return {
            "sessions": len(self._sessions),
            "steps": [p.name for p in FLOW],
            "taken_names": len(TAKEN_NAMES),
            "tlds": sorted(RESERVED_TLDS),
        }


company_concierge = CompanyConcierge()
__all__ = ["CompanyConcierge", "company_concierge", "FLOW"]