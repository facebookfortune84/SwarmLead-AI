"""
Content Agent - BuilderAgent specialization for content generation.

Constitutional: Extends BuilderAgent with content-specific capabilities.
Reuses 75% of BuilderAgent codebase.
"""

from core.agents.content.content_agent import ContentAgent, ContentTemplate, ContentType

__all__ = ["ContentAgent", "ContentTemplate", "ContentType"]