"""
Lead management API endpoints.

This module provides CRUD-style operations for creating leads,
listing leads, retrieving individual leads, and generating follow-up
tickets for a given lead.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.persistence.linear_engine import get_swarm_db

router = APIRouter(prefix="/api/leads", tags=["Leads"])


class LeadCreate(BaseModel):
    """Payload for creating a new lead."""

    email: str
    name: str | None = None
    company: str | None = None
    metadata: dict | None = None


@router.post("")
async def create_lead(payload: LeadCreate):
    """
    Create a new lead in the database.

    Args:
        payload (LeadCreate): Lead details including email, name, and metadata.

    Returns:
        dict: The ID of the newly created lead.
    """
    db = get_swarm_db()
    lead_id = db.create_lead(
        payload.email,
        name=payload.name,
        company=payload.company,
        metadata=payload.metadata,
    )
    return {"lead_id": lead_id}


@router.get("")
async def list_leads(limit: int = 100):
    """
    List leads stored in the database.

    Args:
        limit (int): Maximum number of leads to return.

    Returns:
        dict: A list of lead records.
    """
    db = get_swarm_db()
    leads = db.list_leads(limit=limit)
    return {"leads": leads}


@router.get("/{lead_id}")
async def get_lead(lead_id: str):
    """
    Retrieve a single lead by ID.

    Args:
        lead_id (str): The lead identifier.

    Raises:
        HTTPException: If the lead does not exist.

    Returns:
        dict: Lead record.
    """
    db = get_swarm_db()
    lead = db.get_lead(lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead


@router.post("/{lead_id}/ticket")
async def create_ticket_for_lead(
    lead_id: str,
    department: str = "sales",
    title: str = "Follow-up",
    instruction: str = "Contact lead",
):
    """
    Create a follow-up ticket for a specific lead.

    Args:
        lead_id (str): The lead identifier.
        department (str): Department responsible for the ticket.
        title (str): Ticket title.
        instruction (str): Ticket instructions.

    Raises:
        HTTPException: If the lead does not exist.

    Returns:
        dict: Status of ticket creation.
    """
    db = get_swarm_db()
    lead = db.get_lead(lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    ticket_id = db.create_ticket(
        lead_id=lead_id,
        department=department,
        title=title,
        instruction=instruction,
    )

    ticket = {
        "ticket_id": ticket_id,
        "lead_id": lead_id,
        "department": department,
        "title": title,
        "instruction": instruction,
        "status": "open",
    }

    return {
        "status": "ticket_created",
        "ticket": ticket,
    }


@router.get("/{lead_id}/ticket")
async def get_tickets_for_lead(lead_id: str):
    """
    Retrieve all tickets associated with a specific lead.

    Args:
        lead_id (str): The lead identifier.

    Raises:
        HTTPException: If the lead does not exist.

    Returns:
        dict: List of ticket records for the lead.
    """
    db = get_swarm_db()
    lead = db.get_lead(lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    tickets = db.list_tickets(limit=1000)
    lead_tickets = [
        t for t in tickets if t["project_id"] == lead_id
    ]

    return {"tickets": lead_tickets}


@router.get("/tickets/all")
async def list_all_tickets(limit: int = 100):
    """List all tickets across leads (most recent first)."""
    db = get_swarm_db()
    tickets = db.list_tickets(limit=limit)
    return {"tickets": tickets}
