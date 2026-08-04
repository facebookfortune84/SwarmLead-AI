"""Unit tests for the content models (core.models.content)."""

from datetime import datetime

from core.models.content import Content, ContentStatus, ContentTemplate, ContentType


def test_content_type_enum_values():
    assert ContentType.BLOG.value == "blog"
    assert ContentType.LANDING.value == "landing"
    assert ContentType.EMAIL.value == "email"
    assert ContentType.SOCIAL.value == "social"
    assert ContentType.CASE_STUDY.value == "case_study"
    assert ContentType.WHITEPAPER.value == "whitepaper"
    assert ContentType.NEWSLETTER.value == "newsletter"
    assert ContentType.HELP_ARTICLE.value == "help_article"


def test_content_status_enum_values():
    assert ContentStatus.DRAFT.value == "draft"
    assert ContentStatus.REVIEW.value == "review"
    assert ContentStatus.PUBLISHED.value == "published"
    assert ContentStatus.ARCHIVED.value == "archived"


def test_content_defaults():
    c = Content(id="c1", content_type=ContentType.BLOG, title="Hello", content="Body")
    assert c.status == ContentStatus.DRAFT
    assert c.word_count == 0
    assert c.seo_keywords == []
    assert c.meta_description is None
    assert c.canonical_url is None
    assert c.author_id is None
    assert c.tenant_id is None
    assert c.published_at is None
    assert c.metadata == {}
    assert isinstance(c.created_at, datetime)
    assert isinstance(c.updated_at, datetime)


def test_content_roundtrip_with_all_fields():
    when = datetime(2026, 8, 1)
    c = Content(
        id="c2",
        content_type=ContentType.WHITEPAPER,
        title="Deep dive",
        content="Long form",
        status=ContentStatus.PUBLISHED,
        word_count=1200,
        seo_keywords=["ai", "agents"],
        meta_description="meta",
        meta_title="title",
        canonical_url="https://realms2riches.com/dive",
        author_id="u1",
        tenant_id="t1",
        created_at=when,
        updated_at=when,
        published_at=when,
        metadata={"source": "test"},
    )
    assert c.id == "c2"
    assert c.content_type == ContentType.WHITEPAPER
    assert c.status == ContentStatus.PUBLISHED
    assert c.word_count == 1200
    assert c.seo_keywords == ["ai", "agents"]
    assert c.meta_title == "title"
    assert c.canonical_url == "https://realms2riches.com/dive"
    assert c.tenant_id == "t1"
    assert c.metadata == {"source": "test"}


def test_content_fields_are_mutable():
    c = Content(id="c3", content_type=ContentType.EMAIL, title="t", content="b")
    c.status = ContentStatus.REVIEW
    c.word_count = 50
    c.seo_keywords.append("outreach")
    assert c.status == ContentStatus.REVIEW
    assert c.word_count == 50
    assert c.seo_keywords == ["outreach"]


def test_content_template_defaults():
    t = ContentTemplate(
        id="t1",
        name="Blog template",
        content_type="blog",
        structure=["intro", "body", "cta"],
        variables=["company", "industry"],
        word_count_target=800,
        tone="professional",
        target_audience="founders",
        seo_keywords=["launch"],
        required_sections=["intro"],
        optional_sections=["faq"],
    )
    assert t.id == "t1"
    assert t.name == "Blog template"
    assert t.content_type == "blog"
    assert t.structure == ["intro", "body", "cta"]
    assert t.variables == ["company", "industry"]
    assert t.word_count_target == 800
    assert t.tone == "professional"
    assert t.required_sections == ["intro"]
    assert t.optional_sections == ["faq"]
