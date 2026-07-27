"""
Integration Test — Monetary Rules Engine

Verifies Constitutional §12 enforcement:
- Session spend caps
- Allowlisted counterparties
- Human approval requirements
- Audit logging
"""

import pytest

from core.services.monetary_rules import (
    MonetaryRulesEngine,
    MonetaryRulesConfig,
    RailType,
)


@pytest.fixture
def engine():
    config = MonetaryRulesConfig(
        session_cap_usd=100.0,
        allowlisted_counterparties={"stripe", "aws", "openai"},
        dual_rail_required=False,
    )
    eng = MonetaryRulesEngine(config=config)
    eng.start_session("agent_a")
    eng.start_session("agent_b")
    eng.start_session("agent_c")
    eng.start_session("agent_d")
    eng.start_session("agent_e")
    eng.start_session("agent_f")
    eng.start_session("agent_g")
    return eng


def test_allowlisted_counterparty_accepted(engine):
    result = engine.authorize_spend(
        agent_id="agent_a",
        amount_usd=50.0,
        counterparty="stripe",
        rail=RailType.CUSTOMER_CARD,
        human_approved=True,
    )
    assert result is True


def test_non_allowlisted_counterparty_rejected(engine):
    result = engine.authorize_spend(
        agent_id="agent_a",
        amount_usd=10.0,
        counterparty="unknown_vendor",
        rail=RailType.CUSTOMER_CARD,
        human_approved=True,
    )
    assert result is False


def test_session_cap_enforced(engine):
    ok = engine.authorize_spend("agent_b", 60.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True)
    assert ok is True

    ok = engine.authorize_spend("agent_b", 50.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True)
    assert ok is False


def test_session_cap_borderline(engine):
    assert engine.authorize_spend("agent_c", 50.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True) is True
    assert engine.authorize_spend("agent_c", 50.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True) is True
    assert engine.authorize_spend("agent_c", 1.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True) is False


def test_human_approval_required(engine):
    result = engine.authorize_spend(
        agent_id="agent_d",
        amount_usd=10.0,
        counterparty="stripe",
        rail=RailType.CUSTOMER_CARD,
        human_approved=False,
    )
    assert result is False


def test_audit_log_populated(engine):
    engine.authorize_spend("agent_e", 25.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True)
    engine.authorize_spend("agent_e", 30.0, "openai", RailType.AGENTIC_M2M, human_approved=True)

    assert len(engine.audit_log) >= 2


def test_different_agents_tracked_independently(engine):
    engine.authorize_spend("agent_f", 100.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True)
    r = engine.authorize_spend("agent_g", 100.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True)
    assert r is True
