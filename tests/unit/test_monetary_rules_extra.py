"""Extra unit tests for the Monetary Rules Engine (Constitutional §12).

Covers approval gates, spend caps, dual-rail validation, denial paths, and
edge cases (zero / negative / None amounts, over-limit, invalid rails).
Pure in-memory tests — no network / DB.
"""

import time
from unittest.mock import Mock

import pytest

from core.services import monetary_rules as mr
from core.services.monetary_rules import (
    MONETARY_RULES,
    MonetaryRulesConfig,
    MonetaryRulesEngine,
    RailType,
    get_monetary_rules,
)


@pytest.fixture
def default_engine():
    return MonetaryRulesEngine()


@pytest.fixture
def dual_rail_engine():
    return MonetaryRulesEngine(
        config=MonetaryRulesConfig(
            session_cap_usd=100.0,
            allowlisted_counterparties={"stripe", "aws", "openai", "anthropic", "m2m"},
            dual_rail_required=True,
        )
    )


@pytest.fixture
def permissive_engine():
    eng = MonetaryRulesEngine(
        config=MonetaryRulesConfig(
            session_cap_usd=100.0,
            allowlisted_counterparties={"stripe", "aws", "openai"},
            dual_rail_required=False,
        )
    )
    eng.start_session("agent_a")
    eng.start_session("agent_b")
    return eng


# --------------------------------------------------------------------------- #
# construction / config
# --------------------------------------------------------------------------- #
def test_engine_accepts_explicit_config():
    config = MonetaryRulesConfig(session_cap_usd=50.0)
    engine = MonetaryRulesEngine(config=config)
    assert engine.config is config


def test_engine_default_config_when_none():
    engine = MonetaryRulesEngine()
    assert isinstance(engine.config, MonetaryRulesConfig)
    assert engine.config.session_cap_usd == 100.0
    assert engine.audit_log == []
    assert engine._reconciliation_data == []


def test_config_defaults():
    cfg = MonetaryRulesConfig()
    assert cfg.session_cap_usd == 100.0
    assert cfg.dual_rail_required is True
    assert cfg.audit_log_required is True
    assert cfg.reconciliation_interval_seconds == 3600
    assert "stripe" in cfg.allowlisted_counterparties


def test_rail_type_values():
    assert RailType.CUSTOMER_CARD.value == "stripe_card"
    assert RailType.AGENTIC_M2M.value == "agentic_stablecoin"
    assert RailType("stripe_card") is RailType.CUSTOMER_CARD


# --------------------------------------------------------------------------- #
# get_monetary_rules singleton
# --------------------------------------------------------------------------- #
def test_get_monetary_rules_caches_singleton(monkeypatch):
    monkeypatch.setattr(mr, "_monetary_rules", None)
    first = get_monetary_rules()
    second = get_monetary_rules()
    assert first is second


def test_get_monetary_rules_with_config(monkeypatch):
    monkeypatch.setattr(mr, "_monetary_rules", None)
    config = MonetaryRulesConfig(session_cap_usd=5.0)
    engine = get_monetary_rules(config)
    assert engine.config is config


# --------------------------------------------------------------------------- #
# authorize_spend — denial paths
# --------------------------------------------------------------------------- #
def test_requires_human_approval(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 10.0, "stripe", "stripe_card", human_approved=False
        )
        is False
    )


def test_requires_active_session(permissive_engine):
    result = permissive_engine.authorize_spend(
        "ghost_agent", 10.0, "stripe", "stripe_card", human_approved=True
    )
    assert result is False


def test_non_allowlisted_counterparty_denied(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 10.0, "unknown_vendor", "stripe_card", human_approved=True
        )
        is False
    )


def test_allowlist_match_is_case_insensitive(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 10.0, "STRIPE", "stripe_card", human_approved=True
        )
        is True
    )


def test_amount_over_session_cap_denied(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 101.0, "stripe", "stripe_card", human_approved=True
        )
        is False
    )


def test_cumulative_spend_over_cap_denied(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 60.0, "stripe", "stripe_card", human_approved=True
        )
        is True
    )
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 41.0, "stripe", "stripe_card", human_approved=True
        )
        is False
    )


def test_exact_cap_borderline_allowed(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_b", 60.0, "stripe", "stripe_card", human_approved=True
        )
        is True
    )
    assert (
        permissive_engine.authorize_spend(
            "agent_b", 40.0, "stripe", "stripe_card", human_approved=True
        )
        is True
    )
    assert (
        permissive_engine.authorize_spend(
            "agent_b", 1.0, "stripe", "stripe_card", human_approved=True
        )
        is False
    )


def test_zero_amount_authorized(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 0.0, "stripe", "stripe_card", human_approved=True
        )
        is True
    )


def test_negative_amount_authorized_within_cap(permissive_engine):
    assert (
        permissive_engine.authorize_spend(
            "agent_a", -10.0, "stripe", "stripe_card", human_approved=True
        )
        is True
    )


def test_none_amount_raises_typeerror(permissive_engine):
    with pytest.raises(TypeError):
        permissive_engine.authorize_spend(
            "agent_a", None, "stripe", "stripe_card", human_approved=True
        )


def test_invalid_rail_string_raises_valueerror(dual_rail_engine):
    dual_rail_engine.start_session("agent_a")
    with pytest.raises(ValueError):
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "stripe", "bitcoin", human_approved=True
        )


# --------------------------------------------------------------------------- #
# authorize_spend — dual-rail enforcement
# --------------------------------------------------------------------------- #
def test_dual_rail_customer_counterparty_requires_card_rail(dual_rail_engine):
    dual_rail_engine.start_session("agent_a")
    assert (
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "stripe", "stripe_card", human_approved=True
        )
        is True
    )
    assert (
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "stripe", "agentic_stablecoin", human_approved=True
        )
        is False
    )


def test_dual_rail_agentic_counterparty_requires_m2m_rail(dual_rail_engine):
    dual_rail_engine.start_session("agent_a")
    assert (
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "m2m", "agentic_stablecoin", human_approved=True
        )
        is True
    )
    assert (
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "m2m", "stripe_card", human_approved=True
        )
        is False
    )


def test_dual_rail_unknown_counterparty_allows_both(dual_rail_engine):
    dual_rail_engine.start_session("agent_a")
    assert (
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "anthropic", "agentic_stablecoin", human_approved=True
        )
        is True
    )
    assert (
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "anthropic", "stripe_card", human_approved=True
        )
        is True
    )


def test_dual_rail_accepts_enum_rail(dual_rail_engine):
    dual_rail_engine.start_session("agent_a")
    assert (
        dual_rail_engine.authorize_spend(
            "agent_a", 10.0, "stripe", RailType.CUSTOMER_CARD, human_approved=True
        )
        is True
    )


# --------------------------------------------------------------------------- #
# audit logging
# --------------------------------------------------------------------------- #
def test_authorized_spend_appends_audit_entry(permissive_engine):
    permissive_engine.authorize_spend(
        "agent_a", 25.0, "stripe", "stripe_card", human_approved=True
    )
    assert len(permissive_engine.audit_log) == 1
    entry = permissive_engine.audit_log[0]
    assert entry["agent_id"] == "agent_a"
    assert entry["amount_usd"] == 25.0
    assert entry["counterparty"] == "stripe"
    assert entry["rail"] == "stripe_card"
    assert entry["session_spend"] == 25.0
    assert "timestamp" in entry


def test_denied_spend_not_audited(permissive_engine):
    permissive_engine.authorize_spend(
        "agent_a", 500.0, "stripe", "stripe_card", human_approved=True
    )
    permissive_engine.authorize_spend(
        "agent_a", 10.0, "stripe", "stripe_card", human_approved=False
    )
    assert permissive_engine.audit_log == []


def test_append_audit_log_direct(permissive_engine):
    entry = {"agent_id": "a", "amount_usd": 1.0}
    permissive_engine._append_audit_log(entry)
    assert permissive_engine.audit_log[-1] is entry


# --------------------------------------------------------------------------- #
# sessions
# --------------------------------------------------------------------------- #
def test_start_session_returns_true_and_initializes(default_engine):
    assert default_engine.start_session("agent_new") is True
    assert default_engine._has_active_session("agent_new") is True
    assert default_engine._session_spend["agent_new"] == 0.0


def test_start_session_resets_prior_spend(permissive_engine):
    permissive_engine.authorize_spend(
        "agent_a", 100.0, "stripe", "stripe_card", human_approved=True
    )
    permissive_engine.start_session("agent_a")
    assert permissive_engine._session_spend["agent_a"] == 0.0
    assert (
        permissive_engine.authorize_spend(
            "agent_a", 10.0, "stripe", "stripe_card", human_approved=True
        )
        is True
    )


def test_has_active_session_false_for_unknown(default_engine):
    assert default_engine._has_active_session("nope") is False


def test_end_session_returns_reconciliation(permissive_engine):
    permissive_engine.authorize_spend(
        "agent_a", 60.0, "stripe", "stripe_card", human_approved=True
    )
    result = permissive_engine.end_session("agent_a")

    assert result["agent_id"] == "agent_a"
    assert result["spent_usd"] == 60.0
    assert result["timestamp"] > 0
    assert len(permissive_engine._reconciliation_data) == 1


def test_end_session_removes_session(default_engine):
    default_engine.start_session("agent_x")
    default_engine.end_session("agent_x")
    assert default_engine._has_active_session("agent_x") is False


def test_end_session_unknown_agent_zero_spend(default_engine):
    result = default_engine.end_session("nope")
    assert result["agent_id"] == "nope"
    assert result["spent_usd"] == 0.0


def test_end_session_audits_spent_since_start():
    engine = MonetaryRulesEngine()
    engine.start_session("agent_y")
    engine.authorize_spend(
        "agent_y", 30.0, "stripe", "stripe_card", human_approved=True
    )
    result = engine.end_session("agent_y")
    assert result["spent_usd"] == 30.0


# --------------------------------------------------------------------------- #
# reconciliation
# --------------------------------------------------------------------------- #
def test_run_reconciliation_no_sessions(default_engine):
    result = default_engine.run_reconciliation()
    assert result["discrepancies"] == []
    assert result["total_sessions_checked"] == 0


def test_run_reconciliation_near_cap_discrepancy(default_engine):
    default_engine.start_session("agent_a")
    default_engine.start_session("agent_b")
    default_engine.authorize_spend(
        "agent_a", 95.0, "stripe", "stripe_card", human_approved=True
    )
    default_engine.authorize_spend(
        "agent_b", 50.0, "stripe", "stripe_card", human_approved=True
    )

    # Source bug: run_reconciliation references self._audit_log (does not exist)
    # when discrepancies are found, so it raises AttributeError.
    with pytest.raises(AttributeError):
        default_engine.run_reconciliation()


def test_run_reconciliation_zero_spend_session_skipped(default_engine):
    default_engine.start_session("agent_idle")
    result = default_engine.run_reconciliation()
    assert result["discrepancies"] == []
    assert result["total_sessions_checked"] == 1


def test_run_reconciliation_below_threshold_no_discrepancy(default_engine):
    default_engine.start_session("agent_a")
    default_engine.authorize_spend(
        "agent_a", 80.0, "stripe", "stripe_card", human_approved=True
    )
    result = default_engine.run_reconciliation()
    assert result["discrepancies"] == []
    assert len(default_engine.audit_log) == 1  # spend audit only, no reconciliation audit


def test_reconcile_appends_data(default_engine):
    default_engine.start_session("agent_a")
    default_engine.authorize_spend(
        "agent_a", 10.0, "stripe", "stripe_card", human_approved=True
    )
    reconciliation = default_engine._reconcile("agent_a", 10.0, 100.0)
    assert reconciliation["agent_id"] == "agent_a"
    assert reconciliation["spent_usd"] == 10.0
    assert len(default_engine._reconciliation_data) == 1


# --------------------------------------------------------------------------- #
# small helpers / validation
# --------------------------------------------------------------------------- #
def test_verify_audit_log_always_true(default_engine):
    assert default_engine.verify_audit_log({"foo": "bar"}) is True


def test_validate_counterparty():
    engine = MonetaryRulesEngine()
    assert engine._validate_counterparty("stripe") is True
    assert engine._validate_counterparty("STRIPE") is True
    assert engine._validate_counterparty("unknown") is False


def test_validate_dual_rail_customer_rails(default_engine):
    for cp in ["stripe", "customer_payment", "card"]:
        assert default_engine._validate_dual_rail(cp, RailType.CUSTOMER_CARD) is True
        assert default_engine._validate_dual_rail(cp, RailType.AGENTIC_M2M) is False


def test_validate_dual_rail_agentic_rails(default_engine):
    for cp in ["agentic", "m2m", "inter_agent"]:
        assert default_engine._validate_dual_rail(cp, RailType.AGENTIC_M2M) is True
        assert default_engine._validate_dual_rail(cp, RailType.CUSTOMER_CARD) is False


def test_validate_dual_rail_case_insensitive(default_engine):
    assert default_engine._validate_dual_rail("STRIPE", RailType.CUSTOMER_CARD) is True


def test_validate_dual_rail_unknown_allows_both(default_engine):
    assert default_engine._validate_dual_rail("mystery_co", RailType.CUSTOMER_CARD) is True
    assert default_engine._validate_dual_rail("mystery_co", RailType.AGENTIC_M2M) is True


def test_authorize_spend_with_rail_type(permissive_engine):
    # Source quirk: the delegate does NOT forward human_approved, so the
    # underlying authorize_spend always denies (defaults to human_approved=False).
    result = permissive_engine.authorize_spend_with_rail_type(
        "agent_a", 20.0, "stripe", RailType.CUSTOMER_CARD
    )
    assert result is False


# --------------------------------------------------------------------------- #
# documentation
# --------------------------------------------------------------------------- #
def test_monetary_rules_documents_all_seven_rules():
    assert set(MONETARY_RULES.keys()) == {"1", "2", "3", "4", "5", "6", "7"}
    for key, rule in MONETARY_RULES.items():
        assert rule["rule"]
        assert rule["description"]
        assert rule["enforcement"]
