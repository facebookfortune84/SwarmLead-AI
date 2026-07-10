import pytest
import asyncio

# Import fixtures so pytest registers them
from tests.fixtures.agent_fixtures import *
from tests.fixtures.data_fixtures import *

from core.orchestration.agent_manager import AgentManager
from core.orchestration.task_router import TaskRouter


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def agent_manager():
    return AgentManager()


@pytest.fixture
def router(agent_manager):
    return TaskRouter(agent_manager)