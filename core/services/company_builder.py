"""
Company Builder - multi-agent company generation.

Runs the Genesis agent swarm (Strategy, Content, SEO, Growth) to build a
complete, provisionable company package for a business the user describes,
then produces a downloadable ZIP artifact.

The pipeline is resilient: each agent stage runs independently and the
package is always assembled with whatever stages succeed.
"""

import asyncio
import json
import logging
import re
import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.orchestration.agent_manager import agent_manager
from core.orchestration.register_default_agents import register_default_agents
from core.storage.file_manager import FileManager

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output/companies")


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or f"company-{uuid.uuid4().hex[:8]}"


class CompanyBuilder:
    """Builds a complete company package from a business description."""

    def __init__(self) -> None:
        self.file_manager = FileManager()
        register_default_agents()

    # ------------------------------------------------------------------
    # Build pipeline
    # ------------------------------------------------------------------

    async def build_company(
        self,
        business_name: str,
        business_description: str,
        founder_goal: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a full company package using the agent swarm."""
        company_id = uuid.uuid4().hex[:12]
        slug = _slugify(business_name)
        goal = founder_goal or f"Launch and grow {business_name}"

        base_input = {
            "product": business_name,
            "audience": "prospective customers of " + business_name,
            "goal": goal,
        }
        context = {"domain": "simulation", "trace_id": company_id}

        stages = {
            "strategy": self._run_stage(
                "strategy_agent",
                {**base_input, "text": f"Build a marketing strategy for {business_description}"},
                context,
            ),
            "content": self._run_stage(
                "content_agent",
                {
                    **base_input,
                    "template": "landing",
                    "text": f"Create landing page content for {business_description}",
                },
                context,
            ),
            "seo": self._run_stage(
                "seo_agent",
                {**base_input, "text": f"Create technical SEO for {business_description}"},
                context,
            ),
            "growth": self._run_stage(
                "growth_agent",
                {
                    **base_input,
                    "text": f"Create a growth plan for {business_description}",
                },
                context,
            ),
        }

        results: Dict[str, Any] = {}
        for name, coro in stages.items():
            try:
                results[name] = await asyncio.wait_for(coro, timeout=180)
            except Exception as exc:
                logger.warning("Company build stage %s failed: %s", name, exc)
                results[name] = {"success": False, "error": str(exc)}

        package = self._assemble_package(company_id, slug, business_name, business_description, results)

        company_dir, zip_path = self._write_artifacts(slug, package)

        archive_key = self.file_manager.store_company(company_id, str(zip_path), metadata={"slug": slug})
        if archive_key:
            logger.info("Stored company archive %s at %s", company_id, archive_key)

        self._persist_tenant(company_id, slug, business_name, package, zip_path)

        return {
            "company_id": company_id,
            "slug": slug,
            "name": business_name,
            "status": "built",
            "created_at": datetime.utcnow().isoformat(),
            "summary": package["summary"],
            "stages": {k: bool(v.get("success")) for k, v in results.items()},
            "documents": [p.name for p in company_dir.glob("*.md")],
            "artifact": "company-package.zip",
            "download_available": True,
            "download_path": f"/api/company/{company_id}/download",
        }

    async def _run_stage(self, agent_id: str, input_data: Dict[str, Any], context: Dict) -> Dict[str, Any]:
        return await agent_manager.execute_agent(agent_id, input_data, context=context)

    # ------------------------------------------------------------------
    # Package assembly
    # ------------------------------------------------------------------

    def _assemble_package(
        self,
        company_id: str,
        slug: str,
        name: str,
        description: str,
        results: Dict[str, Any],
    ) -> Dict[str, Any]:
        strategy = self._extract_result(results.get("strategy", {}))
        content = self._extract_result(results.get("content", {}))
        seo = self._extract_result(results.get("seo", {}))
        growth = self._extract_result(results.get("growth", {}))

        angles = strategy.get("angles") or self._fallback_lines(description, "marketing angle")
        hooks = strategy.get("hooks") or self._fallback_lines(description, "hook")
        strategy_summary = strategy.get("summary") or f"Launch and scale {name} with a focused go-to-market strategy."

        content_text = (
            content.get("content")
            or content.get("result", {}).get("content")
            or self._fallback_content(name, description)
        )
        if isinstance(content_text, dict):
            content_text = content_text.get("content") or json.dumps(content_text)

        seo_text = seo.get("summary") or json.dumps(seo.get("meta_tags", {}), indent=2)
        growth_text = growth.get("summary") or self._fallback_growth(name)

        return {
            "company_id": company_id,
            "slug": slug,
            "name": name,
            "description": description,
            "summary": strategy_summary,
            "strategy": {"angles": angles, "hooks": hooks, "summary": strategy_summary},
            "content": {"landing_copy": str(content_text)[:4000]},
            "seo": {"summary": str(seo_text)[:3000]},
            "growth": {"summary": str(growth_text)[:3000]},
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _extract_result(self, stage: Dict) -> Dict[str, Any]:
        if not stage.get("success"):
            return {}
        result = stage.get("result", {})
        if isinstance(result, dict) and isinstance(result.get("result"), dict):
            result = result["result"]
        if isinstance(result, dict) and isinstance(result.get("result"), dict):
            result = result["result"]
        return result if isinstance(result, dict) else {}

    # ------------------------------------------------------------------
    # Artifact writing
    # ------------------------------------------------------------------

    def _write_artifacts(self, slug: str, package: Dict[str, Any]) -> tuple:
        company_dir = OUTPUT_DIR / slug
        if company_dir.exists():
            shutil.rmtree(company_dir)
        company_dir.mkdir(parents=True, exist_ok=True)

        docs = {
            "README.md": self._render_readme(package),
            "business-plan.md": self._render_markdown("Business Plan", package["description"], package["summary"]),
            "marketing-strategy.md": self._render_strategy(package),
            "landing-content.md": package["content"]["landing_copy"],
            "seo-plan.md": package["seo"]["summary"],
            "growth-plan.md": package["growth"]["summary"],
            "company-package.json": json.dumps(package, indent=2),
        }
        for filename, body in docs.items():
            (company_dir / filename).write_text(body, encoding="utf-8")

        zip_path = company_dir / "company-package.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename in docs:
                zf.write(company_dir / filename, arcname=filename)

        return company_dir, zip_path

    def _render_readme(self, package: Dict) -> str:
        return f"""# {package['name']} — Company Package

Generated by Genesis on {package['generated_at']}

## Summary
{package['summary']}

## Contents
- `business-plan.md` — business overview and go-to-market summary
- `marketing-strategy.md` — marketing angles and hooks
- `landing-content.md` — landing page copy
- `seo-plan.md` — technical SEO recommendations
- `growth-plan.md` — growth recommendations
- `company-package.json` — full machine-readable package

## Provisioning
Import `company-package.json` into the Genesis platform to provision a live
tenant, AI voice agent, and lead workflows for {package['name']}.
"""

    def _render_markdown(self, title: str, description: str, summary: str) -> str:
        return f"# {title}\n\n## Business\n{description}\n\n## Strategy Summary\n{summary}\n"

    def _render_strategy(self, package: Dict) -> str:
        strategy = package["strategy"]
        lines = ["# Marketing Strategy\n"]
        lines.append("## Angles\n")
        lines.extend(f"- {a}" for a in strategy["angles"])
        lines.append("\n## Hooks\n")
        lines.extend(f"- {h}" for h in strategy["hooks"])
        lines.append("\n## Summary\n")
        lines.append(strategy["summary"])
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # Fallbacks (graceful degradation)
    # ------------------------------------------------------------------

    def _fallback_lines(self, description: str, kind: str) -> List[str]:
        return [
            f"{kind} 1: Position {description} around a clear, memorable promise.",
            f"{kind} 2: Differentiate with proof, ease of use, and founder-led service.",
            f"{kind} 3: Convert with a low-friction first step and fast time-to-value.",
        ]

    def _fallback_content(self, name: str, description: str) -> str:
        return (
            f"# {name}\n\n{description}\n\n"
            "## Get Started\n"
            "Request a free walkthrough and see how we deliver results in your first 30 days.\n"
            "## Why {name}\n"
            "Focused, transparent, and measurable. We make it simple to get started."
        )

    def _fallback_growth(self, name: str) -> str:
        return (
            f"# Growth Plan for {name}\n\n"
            "1. Launch a referral program rewarding existing customers.\n"
            "2. Publish weekly SEO content targeting high-intent keywords.\n"
            "3. Automate follow-up sequences for every inbound lead.\n"
            "4. Add a voice agent to qualify and book calls 24/7."
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist_tenant(self, company_id: str, slug: str, name: str, package: Dict, zip_path: Path) -> None:
        try:
            from core.models.tenant import CompanyTenant
            from core.persistence.session import SessionLocal

            session = SessionLocal()
            try:
                tenant = CompanyTenant(
                    id=company_id,
                    slug=slug,
                    name=name,
                    subdomain=f"{slug}.genesis.local",
                    status="built",
                    metadata_json=json.dumps(
                        {
                            "package": package,
                            "artifact": "company-package.zip",
                            "artifact_path": str(zip_path),
                        },
                        default=str,
                    ),
                )
                session.add(tenant)
                session.commit()
            finally:
                session.close()
        except Exception as exc:
            logger.warning("Failed to persist company tenant: %s", exc)


company_builder = CompanyBuilder()
__all__ = ["CompanyBuilder", "company_builder"]
