"""
Content Models

Data models for content generation and management.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum


class ContentType(str, Enum):
    BLOG = "blog"
    LANDING = "landing"
    EMAIL = "email"
    SOCIAL = "social"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    NEWSLETTER = "newsletter"
    HELP_ARTICLE = "help_article"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Content:
    """Content model for generated content."""
    id: str
    content_type: ContentType
    title: str
    content: str
    status: ContentStatus = ContentStatus.DRAFT
    word_count: int = 0
    seo_keywords: List[str] = field(default_factory=list)
    meta_description: Optional[str] = None
    meta_title: Optional[str] = None
    canonical_url: Optional[str] = None
    author_id: Optional[str] = None
    tenant_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentTemplate:
    """Template for content generation."""
    id: str
    name: str
    content_type: str
    structure: List[str]
    variables: List[str]
    word_count_target: int
    tone: str
    target_audience: str
    seo_keywords: List[str]
    required_sections: List[str]
    optional_sections: List[str]


__all__ = [
    "Content",
    "ContentType",
    "ContentStatus",
    "ContentTemplate",
]