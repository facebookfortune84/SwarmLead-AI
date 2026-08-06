import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

# Ensure repo root is on sys.path so `core` package can be imported in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
import yaml

from core.agents.governance.governance_agent import (
    AgentAction,
    ComplianceResult,
    ConstitutionEngine,
    FrictionTiers,
    GovernanceAgent,
    TemplateRegistry,
    TriggerEvaluator,
)
from core.auth.agent_identity import AgentIdentityRegistry

VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture(autouse=True)
def default_identities():
    from core.auth.agent_identity import DEFAULT_AGENT_CONFIG

    if not AgentIdentityRegistry._identities:
        AgentIdentityRegistry.load_from_config(DEFAULT_AGENT_CONFIG)
    yield


def make_action(**overrides):
    action = AgentAction(
        agent_id="strategy_agent",
        domain="product_code",
        trace_id=VALID_UUID,
        action_type="code_generation",
        tenant_scoped=True,
        accesses_data=False,
        agent_identity_valid=True,
    )
    for key, value in overrides.items():
        setattr(action, key, value)
    return action


def make_governance():
    return GovernanceAgent()


# ---------------------------------------------------------------------------
# ComplianceResult
# ---------------------------------------------------------------------------


def test_compliance_result_defaults():
    result = ComplianceResult(True, "Compliant")
    assert result.compliant is True
    assert result.violation == "Compliant"
    assert result.article == ""
    assert result.details == {}
    assert isinstance(result.timestamp, datetime)


def test_compliance_result_with_details():
    result = ComplianceResult(False, "bad", "§3", {"agent_id": "x"})
    assert result.compliant is False
    assert result.article == "§3"
    assert result.details == {"agent_id": "x"}


def test_compliance_result_to_dict():
    result = ComplianceResult(True, "ok", "§3", {"a": 1})
    data = result.to_dict()
    assert data["compliant"] is True
    assert data["violation"] == "ok"
    assert data["article"] == "§3"
    assert data["details"] == {"a": 1}
    assert data["timestamp"] == result.timestamp.isoformat()


# ---------------------------------------------------------------------------
# ConstitutionEngine
# ---------------------------------------------------------------------------


def test_engine_uses_default_rules_when_no_yaml(tmp_path):
    engine = ConstitutionEngine(str(tmp_path / "missing.yaml"))
    assert "sections" in engine.rules
    assert "12" in engine.rules["sections"]
    assert engine.rules["sections"]["12"]["no_standing_spend"] is True


def test_engine_loads_yaml(tmp_path):
    cfg = {"sections": {"1": {"custom_rule": True}}}
    path = tmp_path / "constitution.yaml"
    path.write_text(yaml.safe_dump(cfg))
    engine = ConstitutionEngine(str(path))
    assert engine.rules == cfg


def test_engine_default_rules_structure():
    engine = ConstitutionEngine()
    sections = engine.rules["sections"]
    assert sections["3"]["legible_authorship"] is True
    assert sections["4"]["4.4"]["friction_model"]["fast"] == ["routine"]
    assert sections["5"]["financial"] == "human_approval"
    assert sections["13"]["unique_nonshared_identity"] is True
    assert sections["14"]["fail_closed_financial_legal"] is True


def test_load_constitution_file_not_found():
    engine = ConstitutionEngine()
    rules = engine._load_constitution("does/not/exist.yaml")
    assert "sections" in rules


# ---------------------------------------------------------------------------
# ConstitutionEngine.check_action
# ---------------------------------------------------------------------------


def test_check_action_missing_agent_id():
    engine = ConstitutionEngine()
    result = engine.check_action(make_action(agent_id=""))
    assert result.compliant is False
    assert result.article == "§3"
    assert "Missing agent_id or trace_id" in result.violation


def test_check_action_missing_trace_id():
    engine = ConstitutionEngine()
    result = engine.check_action(make_action(trace_id=""))
    assert result.compliant is False
    assert result.article == "§3"


def test_check_action_cross_tenant_data_access():
    engine = ConstitutionEngine()
    result = engine.check_action(
        make_action(accesses_data=True, tenant_scoped=False)
    )
    assert result.compliant is False
    assert result.article == "§4.6"
    assert "Cross-tenant data access" in result.violation


def test_check_action_tenant_scoped_data_access_passes():
    engine = ConstitutionEngine()
    result = engine.check_action(make_action(accesses_data=True, tenant_scoped=True))
    assert result.compliant is True


def test_check_action_unauthorized_domain():
    engine = ConstitutionEngine()
    result = engine.check_action(
        make_action(agent_id="strategy_agent", domain="financial")
    )
    assert result.compliant is False
    assert result.article == "§5"
    assert "not allowed" in result.violation


def test_check_action_unknown_domain_string():
    engine = ConstitutionEngine()
    result = engine.check_action(make_action(domain="mystery_domain"))
    assert result.compliant is False
    assert result.article == "§5"


def test_check_action_unknown_agent_domain():
    engine = ConstitutionEngine()
    result = engine.check_action(make_action(agent_id="nobody"))
    assert result.compliant is False
    assert result.article == "§5"


def test_check_action_spend_without_monetary_rules():
    engine = ConstitutionEngine()
    result = engine.check_action(
        make_action(
            agent_id="payment_agent",
            domain="financial",
            spend_usd=100.0,
            counterparty="stripe",
        )
    )
    assert result.compliant is False
    assert result.article == "§12"
    assert "Monetary rule violation" in result.violation


def test_check_action_spend_denied_by_monetary_rules():
    engine = ConstitutionEngine()
    rules = Mock()
    rules.authorize_spend.return_value = False
    engine.monetary_rules = rules
    result = engine.check_action(
        make_action(
            agent_id="payment_agent",
            domain="financial",
            spend_usd=100.0,
            counterparty="stripe",
            rail_type="card",
        )
    )
    assert result.compliant is False
    assert result.article == "§12"
    rules.authorize_spend.assert_called_once_with(
        agent_id="payment_agent",
        amount_usd=100.0,
        counterparty="stripe",
        rail="card",
    )


def test_check_action_spend_approved():
    engine = ConstitutionEngine()
    rules = Mock()
    rules.authorize_spend.return_value = True
    engine.monetary_rules = rules
    result = engine.check_action(
        make_action(
            agent_id="payment_agent",
            domain="financial",
            spend_usd=100.0,
            counterparty="stripe",
        )
    )
    assert result.compliant is True


def test_check_action_invalid_agent_identity():
    engine = ConstitutionEngine()
    result = engine.check_action(make_action(agent_identity_valid=False))
    assert result.compliant is False
    assert result.article == "§13"


def test_check_action_fully_compliant():
    engine = ConstitutionEngine()
    result = engine.check_action(make_action())
    assert result.compliant is True
    assert result.violation == "Compliant"


# ---------------------------------------------------------------------------
# _check_domain_autonomy
# ---------------------------------------------------------------------------


def test_domain_autonomy_has_domain():
    engine = ConstitutionEngine()
    assert engine._check_domain_autonomy("strategy_agent", "product_code") is True


def test_domain_autonomy_identity_lacks_domain():
    engine = ConstitutionEngine()
    assert engine._check_domain_autonomy("outreach_agent", "product_code") is False


def test_domain_autonomy_unknown_agent():
    engine = ConstitutionEngine()
    assert engine._check_domain_autonomy("nobody", "product_code") is False


def test_domain_autonomy_unknown_domain():
    engine = ConstitutionEngine()
    assert engine._check_domain_autonomy("strategy_agent", "unknown_domain") is False


# ---------------------------------------------------------------------------
# _check_monetary_rules
# ---------------------------------------------------------------------------


def test_monetary_rules_none_denies():
    engine = ConstitutionEngine()
    assert engine._check_monetary_rules(make_action(spend_usd=5.0)) is False


def test_monetary_rules_authorize_true():
    engine = ConstitutionEngine()
    rules = Mock()
    rules.authorize_spend.return_value = True
    engine.monetary_rules = rules
    assert engine._check_monetary_rules(
        make_action(agent_id="payment_agent", spend_usd=5.0, counterparty="stripe")
    ) is True


def test_monetary_rules_authorize_false():
    engine = ConstitutionEngine()
    rules = Mock()
    rules.authorize_spend.return_value = False
    engine.monetary_rules = rules
    assert engine._check_monetary_rules(make_action(spend_usd=5.0)) is False


# ---------------------------------------------------------------------------
# TemplateRegistry
# ---------------------------------------------------------------------------


def test_template_registry_defaults():
    registry = TemplateRegistry()
    assert set(registry.templates) == {
        "ndas",
        "service_agreements",
        "employment_offers",
        "vendor_contracts",
        "press_releases",
    }


def test_get_template_found():
    registry = TemplateRegistry()
    assert registry.get_template("ndas") == "Standard NDA template..."


def test_get_template_missing():
    registry = TemplateRegistry()
    assert registry.get_template("bogus") is None


def test_validate_external_comms_uses_template():
    registry = TemplateRegistry()
    action = make_action(domain="external_comms", external_content="Standard NDA template... text")
    assert registry.validate_action_uses_template(action) is True


def test_validate_external_comms_without_template():
    registry = TemplateRegistry()
    action = make_action(domain="external_comms", external_content="completely custom text")
    assert registry.validate_action_uses_template(action) is False


def test_validate_non_external_domain():
    registry = TemplateRegistry()
    action = make_action(domain="product_code", external_content="anything")
    assert registry.validate_action_uses_template(action) is True


def test_validate_external_comms_no_content():
    registry = TemplateRegistry()
    action = make_action(domain="external_comms", external_content=None)
    assert registry.validate_action_uses_template(action) is True


# ---------------------------------------------------------------------------
# FrictionTiers
# ---------------------------------------------------------------------------


def test_friction_tier_genuine_action():
    friction = FrictionTiers()
    assert friction.get_tier("financial", "spending") == "genuine"
    assert friction.get_tier("legal_contracts", "contracts") == "genuine"
    assert friction.get_tier("security_secrets", "secrets_access") == "genuine"
    assert friction.get_tier("product_code", "legal_filings") == "genuine"


def test_friction_tier_fast_action():
    friction = FrictionTiers()
    assert friction.get_tier("product_code", "code_generation") == "fast"
    assert friction.get_tier("financial", "analysis") == "fast"


def test_friction_tier_fast_domain():
    friction = FrictionTiers()
    assert friction.get_tier("product_code", "execute") == "fast"
    assert friction.get_tier("simulation", "execute") == "fast"


def test_friction_tier_fallback():
    friction = FrictionTiers()
    assert friction.get_tier("external_comms", "send_email") == "fast"


# ---------------------------------------------------------------------------
# TriggerEvaluator
# ---------------------------------------------------------------------------


def test_evaluate_no_triggers():
    evaluator = TriggerEvaluator()
    assert evaluator.evaluate(make_action()) == []


def test_evaluate_dollar_value_threshold():
    evaluator = TriggerEvaluator()
    triggers = evaluator.evaluate(make_action(spend_usd=10000))
    assert triggers == ["dollar_value"]


def test_evaluate_dollar_value_below_threshold():
    evaluator = TriggerEvaluator()
    assert evaluator.evaluate(make_action(spend_usd=9999)) == []


def test_evaluate_cumulative_dollar_value():
    evaluator = TriggerEvaluator()
    triggers = evaluator.evaluate(make_action(spend_usd=100, cumulative_spend_usd=15000))
    assert "dollar_value_cumulative" in triggers


def test_evaluate_regulated_category():
    evaluator = TriggerEvaluator()
    triggers = evaluator.evaluate(make_action(category="healthcare"))
    assert triggers == ["regulated_category"]


def test_evaluate_irreversibility():
    evaluator = TriggerEvaluator()
    triggers = evaluator.evaluate(make_action(action_type="signed_contracts"))
    assert triggers == ["irreversibility"]


def test_evaluate_public_commitment():
    evaluator = TriggerEvaluator()
    triggers = evaluator.evaluate(make_action(action_type="launch_announcement"))
    assert triggers == ["public_commitment"]


def test_evaluate_multiple_triggers():
    evaluator = TriggerEvaluator()
    triggers = evaluator.evaluate(
        make_action(
            spend_usd=15000,
            cumulative_spend_usd=20000,
            category="finance",
            action_type="entity_registration",
        )
    )
    assert "dollar_value" in triggers
    assert "dollar_value_cumulative" in triggers
    assert "regulated_category" in triggers
    assert "irreversibility" in triggers


# ---------------------------------------------------------------------------
# GovernanceAgent
# ---------------------------------------------------------------------------


def test_init_components():
    governance = make_governance()
    assert isinstance(governance.constitution, ConstitutionEngine)
    assert isinstance(governance.templates, TemplateRegistry)
    assert isinstance(governance.friction, FrictionTiers)
    assert isinstance(governance.triggers, TriggerEvaluator)
    assert governance.monetary_rules is None


def test_init_loads_default_identities():
    make_governance()
    assert AgentIdentityRegistry.get("strategy_agent") is not None
    assert AgentIdentityRegistry.get("payment_agent") is not None


def test_init_loads_defaults_when_registry_empty():
    AgentIdentityRegistry._identities.clear()
    governance = GovernanceAgent()
    assert AgentIdentityRegistry.get("strategy_agent") is not None
    assert governance.constitution.rules["sections"]["12"]["no_standing_spend"] is True


def test_pre_check_compliant():
    governance = make_governance()
    result = governance.pre_check(make_action())
    assert result.compliant is True
    assert result.violation == "Pre-check passed"


def test_pre_check_constitutional_violation():
    governance = make_governance()
    result = governance.pre_check(make_action(agent_id=""))
    assert result.compliant is False
    assert result.article == "§3"


def test_pre_check_triggers_require_review():
    governance = make_governance()
    action = make_action(category="healthcare", human_review_completed=False)
    result = governance.pre_check(action)
    assert result.compliant is False
    assert result.article == "§5.1"
    assert "regulated_category" in result.details["triggers"]


def test_pre_check_triggers_reviewed_passes():
    governance = make_governance()
    action = make_action(category="healthcare", human_review_completed=True)
    result = governance.pre_check(action)
    assert result.compliant is True


def test_pre_check_genuine_tier_requires_review():
    governance = make_governance()
    action = make_action(
        agent_id="payment_agent",
        domain="financial",
        action_type="spending",
        human_review_completed=False,
    )
    result = governance.pre_check(action)
    assert result.compliant is False
    assert result.article == "§4.4"
    assert result.details == {"tier": "genuine"}


def test_pre_check_genuine_tier_reviewed_passes():
    governance = make_governance()
    action = make_action(
        agent_id="payment_agent",
        domain="financial",
        action_type="spending",
        human_review_completed=True,
    )
    result = governance.pre_check(action)
    assert result.compliant is True


def test_pre_check_external_comms():
    governance = make_governance()
    action = make_action(
        agent_id="outreach_agent",
        domain="external_comms",
        action_type="send_email",
    )
    result = governance.pre_check(action)
    assert result.compliant is True


def test_post_check_missing_spend_audit_log():
    governance = make_governance()
    rules = Mock()
    rules.verify_audit_log.return_value = False
    governance.register_monetary_rules(rules)
    action = make_action(spend_usd=10.0, audit_logged=True)
    result = governance.post_check(action, None)
    assert result.compliant is False
    assert result.article == "§12.5"


def test_post_check_spend_verified_but_not_logged():
    governance = make_governance()
    rules = Mock()
    rules.verify_audit_log.return_value = True
    governance.register_monetary_rules(rules)
    action = make_action(spend_usd=10.0, audit_logged=False)
    result = governance.post_check(action, None)
    assert result.compliant is False
    assert result.article == "§3"


def test_post_check_passes():
    governance = make_governance()
    rules = Mock()
    rules.verify_audit_log.return_value = True
    governance.register_monetary_rules(rules)
    action = make_action(spend_usd=10.0, audit_logged=True)
    result = governance.post_check(action, None)
    assert result.compliant is True
    assert result.violation == "Post-check passed"


def test_post_check_no_spend_no_log():
    governance = make_governance()
    action = make_action(spend_usd=None, audit_logged=False)
    result = governance.post_check(action, None)
    assert result.compliant is False
    assert result.article == "§3"


def test_post_check_monetary_rules_not_registered_raises():
    governance = make_governance()
    action = make_action(spend_usd=10.0, audit_logged=True)
    with pytest.raises(AttributeError):
        governance.post_check(action, None)


def test_register_monetary_rules_propagates():
    governance = make_governance()
    rules = Mock()
    governance.register_monetary_rules(rules)
    assert governance.monetary_rules is rules
    assert governance.constitution.monetary_rules is rules


@pytest.mark.asyncio
async def test_run_action_compliant():
    governance = make_governance()
    result = await governance.run(
        {
            "action": True,
            "agent_id": "strategy_agent",
            "domain": "product_code",
            "action_type": "code_generation",
            "accesses_data": True,
        },
        trace_id=VALID_UUID,
    )
    assert result["compliant"] is True
    assert result["article"] == ""


@pytest.mark.asyncio
async def test_run_action_violation():
    governance = make_governance()
    result = await governance.run({"action": True, "agent_id": ""})
    assert result["compliant"] is False
    assert result["article"] == "§3"


@pytest.mark.asyncio
async def test_run_summary():
    governance = make_governance()
    result = await governance.run()
    assert result["role"] == "Governance Agent"
    assert any("§3" in e for e in result["enforces"])
    assert "friction_tiers" in result
    assert "constitution as code" in result["summary"]
