"""Unit tests for the GrowthAgent (core.agents.growth.growth_agent)."""

import pytest

from core.agents.growth.growth_agent import (
    FunnelStage,
    GrowthAgent,
    GrowthExperiment,
    GrowthMetric,
)
from configs.config_loader import ConfigLoader


@pytest.fixture
def agent():
    return GrowthAgent("growth_agent", ConfigLoader.load())


def test_default_funnel_has_five_stages(agent):
    assert len(agent.funnel_stages) == 5
    names = [s.name for s in agent.funnel_stages]
    assert names == ["Acquisition", "Activation", "Retention", "Revenue", "Referral"]


@pytest.mark.asyncio
async def test_analyze_funnel_healthy(agent):
    result = await agent.analyze_funnel(
        {
            "visitors": 0.2,
            "activation_rate": 0.3,
            "retention_rate": 0.5,
            "conversion_rate": 0.2,
            "referral_rate": 0.3,
        }
    )
    assert result["overall_health"] == "healthy"
    assert result["bottlenecks"] == []


@pytest.mark.asyncio
async def test_analyze_funnel_finds_bottlenecks(agent):
    result = await agent.analyze_funnel(
        {
            "visitors": 0.2,
            "activation_rate": 0.05,
            "retention_rate": 0.5,
            "conversion_rate": 0.3,
            "referral_rate": 0.3,
        }
    )
    assert result["overall_health"] == "needs_attention"
    stages = [b["stage"] for b in result["bottlenecks"]]
    assert "Activation" in stages
    bottleneck = next(b for b in result["bottlenecks"] if b["stage"] == "Activation")
    assert bottleneck["priority"] == "high"
    assert any("onboarding" in r for r in result["recommendations"])


@pytest.mark.asyncio
async def test_analyze_funnel_medium_priority(agent):
    result = await agent.analyze_funnel(
        {
            "visitors": 0.10,
            "activation_rate": 0.25,
            "retention_rate": 0.4,
            "conversion_rate": 0.1,
            "referral_rate": 0.2,
        }
    )
    bottleneck = next(b for b in result["bottlenecks"] if b["stage"] == "Acquisition")
    assert bottleneck["priority"] == "medium"


@pytest.mark.asyncio
async def test_recommendations_for_each_stage(agent):
    recs = agent._generate_recommendations(
        [
            {"stage": "Activation", "actual": 0, "target": 0.25},
            {"stage": "Retention", "actual": 0, "target": 0.4},
            {"stage": "Revenue", "actual": 0, "target": 0.1},
            {"stage": "Referral", "actual": 0, "target": 0.2},
            {"stage": "Other", "actual": 0, "target": 0.5},
        ]
    )
    joined = " ".join(recs)
    assert "voice-guided setup" in joined
    assert "re-engagement" in joined
    assert "pricing" in joined
    assert "referral program" in joined


@pytest.mark.asyncio
async def test_create_and_analyze_experiment(agent):
    exp = GrowthExperiment(
        name="new-pricing",
        hypothesis="Annual pricing lifts conversion",
        metric=GrowthMetric.REVENUE,
        control_variant="monthly",
        treatment_variant="annual",
        minimum_detectable_effect=0.02,
        sample_size=1000,
        duration_days=30,
    )
    name = await agent.create_experiment(exp)
    assert name == "new-pricing"
    result = await agent.analyze_experiment("new-pricing")
    assert result["experiment"] == "new-pricing"
    assert result["status"] == "draft"
    assert result["recommendation"] == "continue"


@pytest.mark.asyncio
async def test_analyze_missing_experiment(agent):
    result = await agent.analyze_experiment("nope")
    assert result == {"error": "Experiment not found"}


@pytest.mark.asyncio
async def test_design_referral_program_defaults(agent):
    result = await agent.design_referral_program({})
    assert result["program_name"] == "Genesis Referral Program"
    assert result["incentive_structure"]["referrer_reward"] == "$50 credit"
    assert result["tracking"]["attribution_window_days"] == 30
    assert result["voice_integration"]["share_via_voice"] is True


@pytest.mark.asyncio
async def test_design_referral_program_custom(agent):
    result = await agent.design_referral_program(
        {"name": "My Program", "referrer_reward": "$100", "referee_discount": "10%"}
    )
    assert result["program_name"] == "My Program"
    assert result["incentive_structure"]["referrer_reward"] == "$100"


@pytest.mark.asyncio
async def test_calculate_ltv_cac_healthy(agent):
    result = await agent.calculate_ltv_cac({"ltv": 300, "cac": 100})
    assert result["ratio"] == 3.0
    assert result["healthy"] is True
    assert result["payback_months"] == 4.0


@pytest.mark.asyncio
async def test_calculate_ltv_cac_zero_cac(agent):
    result = await agent.calculate_ltv_cac({"ltv": 100, "cac": 0})
    assert result["ratio"] == 0
    assert result["healthy"] is False


@pytest.mark.asyncio
async def test_predict_churn_high_risk(agent):
    result = await agent.predict_churn(
        {"days_since_login": 20, "feature_usage_count": 1, "support_tickets": 5}
    )
    assert result["risk_level"] == "high"
    assert len(result["risk_factors"]) == 3
    assert "re-engagement email" in " ".join(result["recommended_actions"])


@pytest.mark.asyncio
async def test_predict_churn_low_risk(agent):
    result = await agent.predict_churn({"days_since_login": 2, "feature_usage_count": 9})
    assert result["risk_level"] == "low"
    assert result["recommended_actions"] == ["Monitor"]


@pytest.mark.asyncio
async def test_predict_churn_medium_risk(agent):
    result = await agent.predict_churn(
        {"days_since_login": 20, "feature_usage_count": 1, "support_tickets": 1}
    )
    assert result["risk_level"] == "medium"


@pytest.mark.asyncio
async def test_recommend_expansion(agent):
    result = await agent.recommend_expansion({"team_size": 6})
    assert result["estimated_expansion_revenue"] == 700
    assert len(result["upsell_opportunities"]) == 2
    assert result["confidence"] == 0.75


def test_growth_metric_values():
    assert GrowthMetric.ACQUISITION.value == "acquisition"
    assert GrowthMetric.ACTIVATION.value == "activation"
    assert GrowthMetric.RETENTION.value == "retention"
    assert GrowthMetric.REVENUE.value == "revenue"
    assert GrowthMetric.REFERRAL.value == "referral"


def test_funnel_stage_default_conversion():
    stage = FunnelStage("Test", "desc", "metric", 0.5)
    assert stage.current_conversion == 0.0
