"""
Integration Test

Workflow service integration tests.
"""

from core.persistence.session import (
    SessionLocal,
    init_db,
)
from core.services.workflow_service import (
    WorkflowService,
)


def test_workflow_service_constructs():

    init_db()

    db = SessionLocal()

    try:
        service = WorkflowService(db)

        assert service is not None

    finally:
        db.close()


def test_workflow_creation():

    init_db()

    db = SessionLocal()

    try:
        service = WorkflowService(db)

        workflow = service.create_workflow(
            name="Integration Workflow",
            steps=[
                {
                    "step_name": "Create Ticket",
                    "step_type": "ticket",
                }
            ],
        )

        assert workflow is not None

        assert workflow.name == "Integration Workflow"

    finally:
        db.close()
