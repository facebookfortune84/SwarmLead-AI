"""
Voice Agent Module

Voice-enabled agents for customer acquisition and onboarding.
"""

from core.agents.voice.voice_agent import VoiceAgent
from core.agents.voice.voice_analytics import VoiceAnalytics, VoiceSessionMetrics, voice_analytics

__all__ = [
    "VoiceAgent",
    "VoiceAnalytics",
    "VoiceSessionMetrics",
    "voice_analytics",
]
