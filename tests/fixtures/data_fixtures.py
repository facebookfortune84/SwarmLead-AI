import pytest


@pytest.fixture
def sample_input():
    return {
        "audience": "SaaS founders",
        "goal": "Generate leads"
    }


@pytest.fixture
def empty_input():
    return {}