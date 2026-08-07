"""Unit tests for default agent registration (core.orchestration.register_default_agents)."""

import pytest

from core.auth.agent_identity import AgentIdentityRegistry
from core.orchestration.agent_manager import agent_manager
from core.orchestration.register_default_agents import register_default_agents


@pytest.fixture(autouse=True)
def clean_registry():
    agent_manager.agents.clear()
    AgentIdentityRegistry._identities = {}
    AgentIdentityRegistry._allowlist_config = {}
    yield
    agent_manager.agents.clear()
    AgentIdentityRegistry._identities = {}


def test_register_default_agents_registers_nineteen(monkeypatch):
    monkeypatch.setattr(
        "core.orchestration.register_default_agents._registered", False
    )
    register_default_agents()
    assert len(agent_manager.agents) == 19


def test_register_default_agents_is_idempotent(monkeypatch):
    monkeypatch.setattr(
        "core.orchestration.register_default_agents._registered", False
    )
    register_default_agents()
    first_count = len(agent_manager.agents)
    register_default_agents()
    assert len(agent_manager.agents) == first_count


def test_register_default_agents_short_circuits_when_already_registered(monkeypatch):
    monkeypatch.setattr(
        "core.orchestration.register_default_agents._registered", True
    )
    before = dict(agent_manager.agents)
    register_default_agents()
    assert dict(agent_manager.agents) == before


def test_agent_ids_include_voice_and_landing(monkeypatch):
    monkeypatch.setattr(
        "core.orchestration.register_default_agents._registered", False
    )
    register_default_agents()
    agent_ids = set(agent_manager.agents)
    assert {"voice_agent", "landing_agent", "growth_agent", "seo_agent", "outreach_agent"} <= agent_ids
    assert {"sdr_agent", "closer_agent"} <= agent_ids
    assert {"concierge_agent", "nurture_agent"} <= agent_ids
