"""
Default agent registration.

Registers the production agent implementations into the shared
``agent_manager`` singleton at startup so the Agent Center can
discover and execute them through the API.

Every identity in ``DEFAULT_AGENT_CONFIG`` gets a runnable handler, so the
Agent Center shows 15/15 active and functional agents.
"""

import logging

from core.orchestration.agent_manager import agent_manager

logger = logging.getLogger(__name__)

_registered = False


def register_default_agents() -> None:
    """Register all production agents into the agent manager."""
    global _registered
    if _registered:
        return

    # Self-heal identity registry: agent registration requires a valid
    # §13 identity for every name. Reload defaults when the registry is
    # empty (fresh process, test resets, or partial init failure).
    from core.auth.agent_identity import (
        DEFAULT_AGENT_CONFIG,
        AgentIdentityRegistry,
    )

    if not AgentIdentityRegistry._identities:
        AgentIdentityRegistry.load_from_config(DEFAULT_AGENT_CONFIG)

    from core.agents.audit.audit_agent import audit_agent
    from core.agents.builder.builder_agent import BuilderAgent
    from core.agents.content.content_agent import ContentAgent
    from core.agents.governance.governance_agent import governance_agent
    from core.agents.growth.growth_agent import GrowthAgent
    from core.agents.landing.landing_agent import LandingAgent
    from core.agents.monitoring.monitoring_agent import MonitoringAgent
    from core.agents.onboarding.onboarding_agent import OnboardingAgent
    from core.agents.outreach.outreach_agent import OutreachAgent
    from core.agents.payment.payment_agent import PaymentAgent
    from core.agents.repair.repair_agent import RepairAgent
    from core.agents.review.review_agent import ReviewAgent
    from core.agents.seo.seo_agent import SEOAgent
    from core.agents.strategy.strategy_agent import StrategyAgent
    from core.agents.voice.voice_agent import VoiceAgent
    from core.integrations.elevenlabs.elevenlabs_client import ElevenLabsClient
    from configs.config_loader import ConfigLoader

    config = ConfigLoader.load()

    agents = [
        ("strategy_agent", StrategyAgent("strategy_agent", config), ["market research", "positioning"]),
        ("outreach_agent", OutreachAgent("outreach_agent", config), ["email outreach", "messaging"]),
        ("builder_agent", BuilderAgent("builder_agent", config), ["provisioning", "build manifest"]),
        ("repair_agent", RepairAgent("repair_agent", config), ["diagnosis", "remediation"]),
        ("review_agent", ReviewAgent("review_agent", config), ["code review", "quality"]),
        (
            "voice_agent",
            VoiceAgent(
                "voice_agent",
                config,
                elevenlabs_client=ElevenLabsClient(),
            ),
            ["voice conversations", "tts", "stt"],
        ),
        ("governance_agent", governance_agent, ["constitution", "compliance", "friction"]),
        ("audit_agent", audit_agent, ["verification", "audit trails"]),
        ("monitoring_agent", MonitoringAgent(), ["health checks", "self-healing"]),
        ("payment_agent", PaymentAgent("payment_agent", config), ["billing", "quotes"]),
        (
            "landing_agent",
            LandingAgent(
                "landing_agent",
                config,
                voice_agent=None,
            ),
            ["landing conversations", "lead qualification"],
        ),
        (
            "onboarding_agent",
            OnboardingAgent("onboarding_agent", config),
            ["guided onboarding", "voice setup"],
        ),
        ("seo_agent", SEOAgent("seo_agent", config), ["seo analysis", "keywords"]),
        ("content_agent", ContentAgent("content_agent", config), ["content generation"]),
        ("growth_agent", GrowthAgent("growth_agent", config), ["growth analysis"]),
    ]

    for agent_id, handler, capabilities in agents:
        try:
            agent_manager.register_agent(
                name=agent_id,
                handler=handler,
                capabilities=capabilities,
                metadata={"implemented": True},
            )
            logger.info("Registered default agent: %s", agent_id)
        except Exception as exc:
            logger.warning("Skipping agent %s: %s", agent_id, exc)

    _registered = True


__all__ = ["register_default_agents"]
