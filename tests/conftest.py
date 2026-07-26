import pytest
import asyncio

from tests.fixtures.agent_fixtures import *
from tests.fixtures.data_fixtures import *

from core.auth.agent_identity import AgentIdentityRegistry, AgentIdentity, AgentDomain
from core.orchestration.agent_manager import AgentManager
from core.orchestration.task_router import TaskRouter


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_identity_registry():
    AgentIdentityRegistry._identities = {}
    AgentIdentityRegistry._allowlist_config = {}
    yield


def _register_test_identities():
    test_identities = [
        ("test_agent", "TestAgent", "Test Agent"),
        ("echo", "EchoAgent", "Echo Agent"),
        ("fail_agent", "FailAgent", "Fail Agent"),
        ("slow", "SlowAgent", "Slow Agent"),
        ("dup", "DupAgent", "Dup Agent"),
        ("sync_agent", "SyncAgent", "Sync Agent"),
        ("a1", "Agent1", "Agent 1"),
        ("a2", "Agent2", "Agent 2"),
        ("agent1", "Agent1", "Agent 1"),
    ]
    for agent_id, agent_type, display_name in test_identities:
        AgentIdentityRegistry.register(
            AgentIdentity(
                agent_id=agent_id,
                agent_type=agent_type,
                display_name=display_name,
                domains={AgentDomain.SIMULATION},
                tool_allowlist={"*"},
                data_allowlist={"*"},
            )
        )


@pytest.fixture
def agent_manager(reset_identity_registry):
    mgr = AgentManager()
    _register_test_identities()
    return mgr


@pytest.fixture
def router(agent_manager):
    return agent_manager.task_router
