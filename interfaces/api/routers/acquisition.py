"""
Acquisition API — Product Hunt launch kit, directory tracker, and the
Business Skeleton Generator lead magnet (PLG email capture).

The skeleton generator is deterministic (no LLM) so it answers instantly.
When a visitor submits an email, they become a HIGH-INTENT lead
(intent_score 70), which the growth loop then drafts a checkout offer for
— always behind the human gate.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger("Acquisition")

DIRECTORIES_PATH = Path(__file__).resolve().parents[3] / "data" / "acquisition_directories.json"

router = APIRouter(prefix="/api/acquisition", tags=["Acquisition"])


def _load_directories() -> dict:
    if DIRECTORIES_PATH.exists():
        try:
            return json.loads(DIRECTORIES_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    return {"items": []}


class SkeletonRequest(BaseModel):
    """Business Skeleton Generator payload."""

    idea: str
    email: Optional[str] = None
    name: Optional[str] = None


@router.post("/skeleton")
async def business_skeleton(payload: SkeletonRequest):
    """Generate a business skeleton manifest; capture email as a high-intent lead."""
    from core.agents.builder.builder_agent import BuilderAgent

    agent = BuilderAgent("builder_agent", None)
    manifest = await agent.execute(
        input_data={"text": payload.idea, "product": payload.idea, "audience": "founders"},
        context={},
        trace_id=None,
    )

    lead_id = None
    if payload.email and "@" in payload.email:
        try:
            from core.persistence.session import SessionLocal

            db = SessionLocal()
            try:
                from core.models import Lead

                lead = Lead(
                    email=payload.email,
                    name=payload.name or "Business Skeleton Lead",
                    intent_score=70,
                    metadata_json=json.dumps(
                        {
                            "source": "business_skeleton_generator",
                            "idea": payload.idea,
                        }
                    ),
                )
                db.add(lead)
                db.commit()
                lead_id = lead.id
            finally:
                db.close()
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not capture lead: %s", exc)

    return {
        "manifest": manifest,
        "lead_captured": lead_id is not None,
        "lead_id": lead_id,
        "next_step": manifest["next_step"],
    }


@router.get("/ph-launch")
async def ph_launch_kit():
    """Return the Product Hunt launch kit (copy + schedule)."""
    doc = Path(__file__).resolve().parents[3] / "docs" / "ph_launch_plan.md"
    summary = ""
    if doc.exists():
        try:
            summary = doc.read_text(encoding="utf-8")[:2000]
        except OSError:
            summary = ""
    return {
        "kit": "docs/ph_launch_plan.md",
        "preview": summary,
        "launch_day": "Monday 00:01 PST",
    }


@router.get("/directories")
async def directories():
    """Return the AI directory submission tracker."""
    return _load_directories()
