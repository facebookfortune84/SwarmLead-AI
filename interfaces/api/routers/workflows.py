"""# noqa: E501
Workflows API — create, inspect, and control multi-step workflows.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.models.workflow import Workflow
from core.persistence.session import get_db
from core.services.workflow_service import WorkflowService
from interfaces.api.auth.middleware import get_current_active_user

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────


class StepDefinition(BaseModel):
    step_name: str
    step_type: str  # ticket/notification/approval/condition
    input: Optional[dict] = None


class WorkflowCreate(BaseModel):
    name: str
    steps: List[StepDefinition]
    company_id: Optional[str] = None


class WorkflowFromTemplate(BaseModel):
    template_id: str
    company_id: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Prebuilt workflow templates
# ─────────────────────────────────────────────────────────────────────────────

WORKFLOW_TEMPLATES = [
    {
        "id": "email-follow-up",
        "name": "Email Follow-Up",
        "category": "Email",
        "description": "Convert inbound leads with a multi-touch nurture email sequence.",
        "icon": "mail",
        "steps": [
            {"step_name": "Capture Lead", "step_type": "notification", "input": {}},
            {"step_name": "Send Intro Email", "step_type": "notification", "input": {"channel": "email"}},
            {"step_name": "Send Value Email", "step_type": "notification", "input": {"channel": "email"}},
            {"step_name": "Send Offer Email", "step_type": "notification", "input": {"channel": "email"}},
            {"step_name": "Handoff to Sales", "step_type": "ticket", "input": {"department": "sales"}},
        ],
    },
    {
        "id": "voice-outreach",
        "name": "Voice Agent Outreach",
        "category": "Voice",
        "description": "Qualify callers with the AI voice agent and route hot leads to your team.",
        "icon": "mic",
        "steps": [
            {"step_name": "Answer Call", "step_type": "notification", "input": {"channel": "voice"}},
            {"step_name": "Qualify Caller", "step_type": "condition", "input": {"intent": "qualify"}},
            {"step_name": "Capture Lead", "step_type": "notification", "input": {"channel": "voice"}},
            {"step_name": "Book Call", "step_type": "ticket", "input": {"department": "sales"}},
        ],
    },
    {
        "id": "seo-ranking",
        "name": "SEO Content Engine",
        "category": "SEO",
        "description": "Publish and rank SEO content on a weekly cadence using the SEO agent.",
        "icon": "search",
        "steps": [
            {"step_name": "Keyword Research", "step_type": "notification", "input": {"channel": "seo"}},
            {"step_name": "Draft Article", "step_type": "notification", "input": {"channel": "seo"}},
            {"step_name": "Review Draft", "step_type": "condition", "input": {}},
            {"step_name": "Publish & Index", "step_type": "notification", "input": {"channel": "seo"}},
        ],
    },
    {
        "id": "traffic-boost",
        "name": "Traffic Boost",
        "category": "Traffic",
        "description": "Drive inbound traffic through outreach, social content, and campaigns.",
        "icon": "zap",
        "steps": [
            {"step_name": "Build Audience", "step_type": "notification", "input": {"channel": "outreach"}},
            {"step_name": "Launch Campaign", "step_type": "notification", "input": {"channel": "campaign"}},
            {"step_name": "Run Referral Loop", "step_type": "notification", "input": {"channel": "growth"}},
        ],
    },
    {
        "id": "lead-nurture",
        "name": "Lead Nurture Sequence",
        "category": "Follow-Up",
        "description": "Automatically nurture every inbound lead until they book or opt out.",
        "icon": "repeat",
        "steps": [
            {"step_name": "Segment Lead", "step_type": "condition", "input": {}},
            {"step_name": "Send Nurture Email", "step_type": "notification", "input": {"channel": "email"}},
            {"step_name": "Call With Voice Agent", "step_type": "notification", "input": {"channel": "voice"}},
            {"step_name": "Escalate Hot Lead", "step_type": "ticket", "input": {"department": "sales"}},
        ],
    },
]


@router.get("/templates")
async def list_workflow_templates(
    current_user: dict = Depends(get_current_active_user),
):
    """List prebuilt workflow templates for one-click creation."""
    return {"templates": WORKFLOW_TEMPLATES}


@router.post("/from-template")
async def create_workflow_from_template(
    body: WorkflowFromTemplate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a workflow from a named prebuilt template."""
    template = next((t for t in WORKFLOW_TEMPLATES if t["id"] == body.template_id), None)
    if template is None:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    svc = WorkflowService(db)
    wf = svc.create_workflow(
        name=template["name"],
        steps=template["steps"],
        company_id=body.company_id or "",
    )
    if wf is None or not hasattr(wf, "id"):
        raise HTTPException(status_code=400, detail="Unable to create workflow")
    return svc.get_status(str(wf.id))


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: WorkflowCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new workflow definition."""
    svc = WorkflowService(db)
    wf = svc.create_workflow(
        name=body.name,
        steps=[s.model_dump() for s in body.steps],
        company_id=body.company_id or "",
    )
    if wf is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to create workflow"
        )
    if hasattr(wf, "id"):
        workflow_id = wf.id
    elif isinstance(wf, str):
        workflow_id = wf
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected workflow creation result",
        )
    # normalize id to string for the status lookup
    return svc.get_status(str(workflow_id))


@router.get("")
async def list_workflows(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all workflows (most recent first)."""
    limit = min(max(limit, 1), 200)
    rows = db.query(Workflow).order_by(Workflow.created_at.desc()).offset(skip).limit(limit).all()
    svc = WorkflowService(db)
    return {
        "skip": skip,
        "limit": limit,
        "items": [svc.get_status(str(w.id)) for w in rows],
    }


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the current status and step details of a workflow."""
    svc = WorkflowService(db)
    result = svc.get_status(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result


@router.post("/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Start a pending workflow."""
    svc = WorkflowService(db)
    wf = svc.start_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return svc.get_status(str(workflow_id))


@router.post("/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Pause a running workflow."""
    svc = WorkflowService(db)
    wf = svc.pause_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return svc.get_status(str(workflow_id))


@router.post("/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Resume a paused workflow."""
    svc = WorkflowService(db)
    wf = svc.resume_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return svc.get_status(str(workflow_id))


@router.post("/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Cancel a workflow (marks as failed)."""
    svc = WorkflowService(db)
    wf = svc.cancel_workflow(workflow_id, user_id=current_user["id"])
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return svc.get_status(str(workflow_id))
