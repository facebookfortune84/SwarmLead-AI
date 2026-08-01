"""
Growth Autonomy API — control surface for the autonomous growth loop and
the single human-in-the-loop approval gate.

Endpoints:
- GET  /api/growth/status        loop state, funnel, queue counts
- GET  /api/growth/queue         pending human approvals
- POST /api/growth/approve/{id}  THE human gate — approve a queued action
- POST /api/growth/reject/{id}   reject a queued action
- POST /api/growth/run-now       trigger a cycle immediately
- POST /api/growth/toggle        pause/resume auto mode
"""

from fastapi import APIRouter, Depends, HTTPException

from interfaces.api.auth.middleware import get_current_active_user

from core.services.growth_automation import growth_automation

router = APIRouter(
    prefix="/api/growth",
    tags=["Growth Autonomy"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/status")
async def growth_status(_=Depends(get_current_active_user)):
    return growth_automation.status()


@router.get("/queue")
async def growth_queue(_=Depends(get_current_active_user)):
    return {"items": growth_automation.pending_actions()}


@router.post("/approve/{action_id}")
async def approve_action(action_id: str, _=Depends(get_current_active_user)):
    result = await growth_automation.approve(action_id)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@router.post("/reject/{action_id}")
async def reject_action(action_id: str, _=Depends(get_current_active_user)):
    result = growth_automation.reject(action_id)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@router.post("/purge/{action_id}")
async def purge_action(action_id: str, _=Depends(get_current_active_user)):
    result = growth_automation.purge(action_id)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@router.post("/purge-all")
async def purge_all(_=Depends(get_current_active_user)):
    return growth_automation.purge_all_pending()


@router.post("/discover")
async def discover(_=Depends(get_current_active_user)):
    from core.services.lead_discovery import lead_discovery

    return {
        "findings": len(lead_discovery.findings()),
        "recent": lead_discovery.findings()[:10],
    }


@router.post("/run-now")
async def run_now(_=Depends(get_current_active_user)):
    return await growth_automation.run_now()


@router.post("/toggle")
async def toggle(enabled: bool, _=Depends(get_current_active_user)):
    growth_automation.set_enabled(enabled)
    return {"enabled": enabled}
