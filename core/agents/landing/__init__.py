"""
Landing Page Agent - Proactive voice agent for landing page.

StrategyAgent specialization for landing page interactions.
"""

from core.agents.landing.landing_agent import LandingAgent
from core.agents.landing.landing_agent import VisitorContext, LandingFlow

__all__ = ["LandingAgent", "VisitorContext", "LandingFlow"]