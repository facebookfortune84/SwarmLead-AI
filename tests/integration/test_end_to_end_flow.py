"""
End-to-End Integration Test

Verifies the core SwarmLead v3 business flow.

Flow:

    Lead
      ↓
    Usage
      ↓
    Ticket
      ↓
    Workflow
      ↓
    Tenant
"""

from core.persistence.linear_engine import (
    get_swarm_db,
)
from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.tenant_service import (
    TenantService,
)
from core.services.ticket_service import (
    TicketService,
)
from core.services.workflow_service import (
    WorkflowService,
)


def test_end_to_end_business_flow():

    init_db()

    #
    # STEP 1
    # Lead Creation
    #
    swarm_db = get_swarm_db()

    lead_id = swarm_db.create_lead(
        email="integration@example.com",
        name="Integration User",
        company="Integration Co",
    )

    assert lead_id

    #
    # STEP 2
    # Usage Tracking
    #
    usage_id = swarm_db.record_usage(
        project_id=str(lead_id),
        event_type="integration_test",
        amount="1",
    )

    assert usage_id

    #
    # STEP 3
    # Ticket Creation
    #
    db = SessionLocal()

    try:
        ticket_service = TicketService(db)

        ticket = ticket_service.create_ticket(
            title="Integration Ticket",
            instruction="Created from E2E test",
            priority="medium",
        )

        assert ticket is not None

        #
        # STEP 4
        # Workflow Creation
        #
        workflow_service = WorkflowService(db)

        workflow = workflow_service.create_workflow(
            name="Integration Workflow",
            steps=[
                {
                    "step_name": "Test Step",
                    "step_type": "ticket",
                }
            ],
        )

        assert workflow is not None

        #
        # STEP 5
        # Tenant Creation
        #
        tenant_service = TenantService(db)

        tenant = tenant_service.register(name="Integration Tenant")

        assert tenant is not None

    finally:
        db.close()
