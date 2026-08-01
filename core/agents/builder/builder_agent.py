"""
Builder Agent — Provisions business artifacts from a founder's intent.

Constitutional §5: product_code is autonomous & reversible.
Produces a reversible build manifest (files, config, checklist) without
performing irreversible external actions.
"""

import json
import uuid
from typing import Any, Dict, Optional

from core.agents.base_agent import BaseAgent


class BuilderAgent(BaseAgent):
    """Turns a founder prompt into a buildable business artifact manifest."""

    def __init__(self, name, config):
        super().__init__(name, config)
        self._builds: Dict[str, Dict] = {}

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: Optional[str],
    ) -> Dict[str, Any]:
        product = input_data.get("product", "")
        audience = input_data.get("audience", "")
        goal = input_data.get("goal", "")
        text = input_data.get("text", "")

        intent = text or goal or f"Launch a {product} business for {audience}"

        build_id = f"build_{uuid.uuid4().hex[:8]}"

        # Deterministic skeleton — always available, never blocks on the LLM.
        skeleton = self._build_skeleton(intent, product, audience)

        # Optional LLM enrichment of the landing copy (fast path skips if empty).
        copy = ""
        if input_data.get("generate_copy"):
            try:
                copy = await self.call_llm(
                    f"You are a launch builder. Write 120 words of landing-page hero + subhead copy for this business intent. "
                    f"Intent: {intent}. Audience: {audience}. Return only the copy.",
                    trace_id=trace_id,
                )
            except Exception:
                copy = ""

        manifest = {
            "build_id": build_id,
            "intent": intent,
            "product": product,
            "audience": audience,
            "skeleton": skeleton,
            "generated_copy": copy,
            "status": "manifest_ready",
            "next_step": "Run the launch workflow to provision this build.",
        }

        self._builds[build_id] = manifest
        return manifest

    def _build_skeleton(self, intent: str, product: str, audience: str) -> Dict[str, Any]:
        slug = (
            "".join(c for c in (product or intent).lower() if c.isalnum() or c in "-_ ")
            .strip()
            .replace(" ", "-")[:32]
        ) or "business"

        return {
            "project_slug": slug,
            "files": {
                "landing/index.html": f"Landing page for {product or intent}",
                "landing/copy.md": "Hero + subhead + CTA copy",
                "config/provision.json": json.dumps(
                    {"business": slug, "audience": audience}, indent=2
                ),
                "launch/checklist.md": "1. Verify copy  2. Provision infra  3. Go live",
            },
            "infra_plan": {
                "db": "postgres",
                "hosting": "container",
                "domain": f"{slug}.example.com",
            },
            "reversible": True,
        }
