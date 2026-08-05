"""
Launch campaign API — status, share links, and traffic drafts.

Public endpoints (no auth): the landing page needs launch status and
share links client-side for the countdown and share buttons.
"""

from typing import Dict, List

from fastapi import APIRouter

from core.services import launch_config
from core.services.growth_automation import growth_automation

router = APIRouter(prefix="/api/launch", tags=["launch"])


@router.get("/status")
async def launch_status() -> Dict[str, object]:
    """Current launch campaign status for the landing page."""
    return launch_config.status()


@router.get("/activity")
async def launch_activity() -> Dict[str, object]:
    """Real launch-week activity metrics (leads, intent, growth cycles)."""
    return launch_config.activity()


@router.get("/share")
async def share() -> Dict[str, str]:
    """Pre-filled share links for X / Facebook / LinkedIn / WhatsApp / email."""
    return launch_config.share_links()


@router.get("/traffic/drafts")
async def traffic_drafts() -> List[Dict[str, str]]:
    """Ready-to-post launch traffic copy (drafts only — nothing is posted)."""
    return launch_config.compose_traffic_drafts()


@router.get("/traffic/queue")
async def traffic_queue() -> List[Dict]:
    """Pending traffic drafts awaiting the founder's approval."""
    return [
        a
        for a in growth_automation.pending_actions()
        if a["kind"] == "traffic_post"
    ]
