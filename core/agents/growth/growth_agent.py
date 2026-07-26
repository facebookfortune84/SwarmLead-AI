"""
Growth Agent - Funnel optimization, referral loops, expansion revenue.

StrategyAgent specialization for growth.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from core.agents.strategy.strategy_agent import StrategyAgent


class GrowthMetric(str, Enum):
    ACQUISITION = "acquisition"
    ACTIVATION = "activation"
    RETENTION = "retention"
    REVENUE = "revenue"
    REFERRAL = "referral"


@dataclass
class GrowthExperiment:
    """Growth experiment configuration."""
    name: str
    hypothesis: str
    metric: GrowthMetric
    control_variant: str
    treatment_variant: str
    minimum_detectable_effect: float
    sample_size: int
    duration_days: int
    status: str = "draft"


@dataclass
class FunnelStage:
    """Funnel stage definition."""
    name: str
    description: str
    metric: str
    target_conversion: float
    current_conversion: float = 0.0


class GrowthAgent(StrategyAgent):
    """
    Growth Agent - Funnel optimization, referral loops, expansion revenue.
    
    Extends StrategyAgent for growth-specific workflows.
    """
    
    def __init__(self, name: str, config):
        super().__init__(name, config)
        self.experiments: Dict[str, GrowthExperiment] = {}
        self.funnel_stages: List[FunnelStage] = []
        self._initialize_default_funnel()
    
    def _initialize_default_funnel(self):
        """Initialize default AAARRR funnel."""
        self.funnel_stages = [
            FunnelStage("Acquisition", "New visitors", "visitors", 0.15),
            FunnelStage("Activation", "First value moment", "activation_rate", 0.25),
            FunnelStage("Retention", "Repeat usage", "retention_rate", 0.40),
            FunnelStage("Revenue", "Monetization", "conversion_rate", 0.10),
            FunnelStage("Referral", "Viral growth", "referral_rate", 0.20)
        ]
    
    async def analyze_funnel(self, funnel_data: Dict) -> Dict:
        """Analyze funnel and identify bottlenecks."""
        bottlenecks = []
        
        for stage in self.funnel_stages:
            actual = funnel_data.get(stage.metric, 0)
            if actual < stage.target_conversion * 0.8:  # 20% below target
                bottlenecks.append({
                    "stage": stage.name,
                    "metric": stage.metric,
                    "actual": actual,
                    "target": stage.target_conversion,
                    "gap": stage.target_conversion - actual,
                    "priority": "high" if actual < stage.target_conversion * 0.5 else "medium"
                })
        
        return {
            "bottlenecks": bottlenecks,
            "overall_health": "healthy" if not bottlenecks else "needs_attention",
            "recommendations": self._generate_recommendations(bottlenecks)
        }
    
    def _generate_recommendations(self, bottlenecks: List[Dict]) -> List[str]:
        recommendations = []
        for b in bottlenecks:
            if b["stage"] == "Activation":
                recommendations.append("Improve onboarding flow with voice-guided setup")
                recommendations.append("Add interactive product tour")
            elif b["stage"] == "Retention":
                recommendations.append("Implement email re-engagement campaigns")
                recommendations.append("Add in-app notifications for key features")
            elif b["stage"] == "Revenue":
                recommendations.append("Optimize pricing page with voice FAQ")
                recommendations.append("Add usage-based pricing calculator")
            elif b["stage"] == "Referral":
                recommendations.append("Launch referral program with voice-sharing")
                recommendations.append("Add social sharing to voice sessions")
        return recommendations
    
    async def create_experiment(self, experiment: GrowthExperiment) -> str:
        """Create growth experiment."""
        self.experiments[experiment.name] = experiment
        return experiment.name
    
    async def analyze_experiment(self, experiment_name: str) -> Dict:
        """Analyze experiment results."""
        exp = self.experiments.get(experiment_name)
        if not exp:
            return {"error": "Experiment not found"}
        
        # Would analyze actual experiment data
        return {
            "experiment": exp.name,
            "status": exp.status,
            "recommendation": "continue"  # or "stop", "iterate"
        }
    
    async def design_referral_program(self, config: Dict) -> Dict:
        """Design referral program."""
        return {
            "program_name": config.get("name", "Genesis Referral Program"),
            "incentive_structure": {
                "referrer_reward": config.get("referrer_reward", "$50 credit"),
                "referee_discount": config.get("referee_discount", "20% off first month"),
                "tiered_rewards": [
                    {"referrals": 1, "reward": "$50"},
                    {"referrals": 5, "reward": "$250"},
                    {"referrals": 10, "reward": "$500 + premium features"}
                ]
            },
            "tracking": {
                "method": "unique_referral_links",
                "attribution_window_days": 30
            },
            "voice_integration": {
                "share_via_voice": True,
                "voice_share_prompt": "Share Genesis with a friend using your voice",
                "voice_referral_link": "Share via voice command"
            },
            "compliance": {
                "terms_link": "/terms/referral",
                "privacy_link": "/privacy"
            }
        }
    
    async def calculate_ltv_cac(self, cohort_data: Dict) -> Dict:
        """Calculate LTV/CAC ratio for cohort."""
        ltv = cohort_data.get("ltv", 0)
        cac = cohort_data.get("cac", 1)
        
        return {
            "ltv": ltv,
            "cac": cac,
            "ratio": ltv / cac if cac > 0 else 0,
            "payback_months": cac / (ltv / 12) if ltv > 0 else 0,
            "healthy": ltv / cac >= 3 if cac > 0 else False
        }
    
    async def predict_churn(self, user_data: Dict) -> Dict:
        """Predict churn risk for user."""
        # Simplified churn prediction
        risk_factors = []
        risk_score = 0.0
        
        if user_data.get("days_since_login", 999) > 14:
            risk_factors.append("Inactive > 14 days")
            risk_score += 0.3
        
        if user_data.get("feature_usage_count", 0) < 3:
            risk_factors.append("Low feature adoption")
            risk_score += 0.2
        
        if user_data.get("support_tickets", 0) > 3:
            risk_factors.append("High support burden")
            risk_score += 0.2
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
            "risk_factors": risk_factors,
            "recommended_actions": [
                "Trigger re-engagement email",
                "Offer 1-on-1 onboarding call",
                "Provide feature discovery guide"
            ] if risk_score > 0.4 else ["Monitor"]
        }
    
    async def recommend_expansion(self, account_data: Dict) -> Dict:
        """Recommend expansion opportunities."""
        return {
            "upsell_opportunities": [
                {
                    "feature": "Advanced Analytics",
                    "reason": "High usage of basic reports",
                    "estimated_value": 200
                },
                {
                    "feature": "Team Collaboration",
                    "reason": "Team size > 5",
                    "estimated_value": 500
                }
            ],
            "cross_sell_opportunities": [],
            "estimated_expansion_revenue": 700,
            "confidence": 0.75
        }


__all__ = ["GrowthAgent", "GrowthExperiment", "FunnelStage", "GrowthMetric"]