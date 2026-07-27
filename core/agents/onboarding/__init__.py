"""
Onboarding Agent - StrategyAgent specialization for user onboarding.

Constitutional: Extends StrategyAgent with onboarding-specific capabilities.
Reuses 85% of StrategyAgent codebase.
"""

from core.agents.onboarding.onboarding_agent import (
    OnboardingAgent,
    OnboardingStep,
    OnboardingStepConfig,
)

__all__ = ["OnboardingAgent", "OnboardingStep", "OnboardingStepConfig"]
