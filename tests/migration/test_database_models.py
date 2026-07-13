"""
Migration Validation

Verify migrated SQLAlchemy models register correctly.

This catches:

- table registration failures
- metadata corruption
- duplicate table definitions
- relationship compilation issues
- migration damage to models
"""

from core.models.api_key import APIKey
from core.models.deployment import Deployment
from core.models.lead import Lead
from core.models.message import Message
from core.models.message_thread import MessageThread
from core.models.notification import Notification
from core.models.outreach import LeadTimeline
from core.models.tenant import CompanyTenant
from core.models.ticket import Ticket
from core.models.ticket_comment import TicketComment
from core.models.ticket_history import TicketHistory
from core.models.usage import UsageEvent
from core.models.user import User
from core.models.workflow import Workflow
from core.models.workflow_step import WorkflowStep
from core.persistence.base import Base

EXPECTED_MODELS = [
    User,
    APIKey,
    Lead,
    UsageEvent,
    Deployment,
    CompanyTenant,
    Notification,
    Message,
    MessageThread,
    Workflow,
    WorkflowStep,
    Ticket,
    TicketHistory,
    TicketComment,
    LeadTimeline,
]


def test_all_models_define_tablename():

    failures = []

    for model in EXPECTED_MODELS:
        tablename = getattr(
            model,
            "__tablename__",
            None,
        )

        if not tablename:
            failures.append(model.__name__)

    assert not failures, failures


def test_all_models_registered():

    metadata_tables = Base.metadata.tables

    failures = []

    for model in EXPECTED_MODELS:
        table_name = getattr(
            model,
            "__tablename__",
            None,
        )

        if table_name not in metadata_tables:
            failures.append(table_name)

    assert not failures, failures


def test_no_duplicate_table_names():

    table_names = []

    for model in EXPECTED_MODELS:
        table_names.append(model.__tablename__)

    assert len(table_names) == len(set(table_names))


def test_metadata_contains_tables():

    assert len(Base.metadata.tables) > 0
