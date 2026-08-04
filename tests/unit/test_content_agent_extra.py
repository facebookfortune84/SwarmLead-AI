import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Ensure repo root is on sys.path so `core` package can be imported in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core.agents.content.content_agent import (
    ContentAgent,
    ContentBrief,
    ContentTemplate,
    ContentType,
)


@pytest.fixture
def config():
    return {}


@pytest.fixture
def agent(config):
    return ContentAgent(
        name="content",
        config=config,
    )


# ---------------------------------------------------------------------------
# Construction / templates
# ---------------------------------------------------------------------------


def test_init_sets_up_default_templates(agent):
    assert set(agent.templates) == {
        "blog",
        "landing",
        "email",
        "case_study",
        "social",
        "whitepaper",
    }
    assert agent.templates["blog"].content_type == ContentType.BLOG
    assert agent.templates["landing"].content_type == ContentType.LANDING
    assert agent.templates["email"].content_type == ContentType.EMAIL
    assert agent.templates["case_study"].content_type == ContentType.CASE_STUDY
    assert agent.templates["social"].content_type == ContentType.SOCIAL
    assert agent.templates["whitepaper"].content_type == ContentType.WHITEPAPER


def test_content_type_enum_values():
    assert ContentType.BLOG.value == "blog"
    assert ContentType.LANDING.value == "landing"
    assert ContentType.EMAIL.value == "email"
    assert ContentType.SOCIAL.value == "social"
    assert ContentType.CASE_STUDY.value == "case_study"
    assert ContentType.WHITEPAPER.value == "whitepaper"
    assert ContentType.NEWSLETTER.value == "newsletter"
    assert ContentType.HELP_ARTICLE.value == "help_article"


def test_content_template_defaults():
    template = ContentTemplate(
        name="T", content_type=ContentType.BLOG, structure=["a"], word_count_target=100
    )
    assert template.tone == "professional"
    assert template.target_audience == "business"
    assert template.seo_keywords == []
    assert template.required_sections == []
    assert template.optional_sections == []


def test_content_brief_defaults():
    brief = ContentBrief(
        topic="t",
        content_type=ContentType.BLOG,
        target_audience="a",
        key_messages=[],
        keywords=[],
    )
    assert brief.tone == "professional"
    assert brief.word_count is None
    assert brief.include_examples is True
    assert brief.include_cta is True
    assert brief.cta_text is None


# ---------------------------------------------------------------------------
# execute
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_success_with_template(agent):
    agent.call_llm = AsyncMock(return_value="A great blog post about lead gen.")
    result = await agent.execute({"template": "blog", "seo_keywords": ["lead", "gen"]}, {}, "trace-1")
    assert result["success"] is True
    assert result["result"]["template"] == "blog"
    assert "content" in result["result"]
    agent.call_llm.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_routes_on_content_type(agent):
    agent.call_llm = AsyncMock(return_value="Landing page copy here.")
    result = await agent.execute({"content_type": "landing"}, {})
    assert result["success"] is True
    assert result["result"]["template"] == "landing"


@pytest.mark.asyncio
async def test_execute_defaults_to_blog(agent):
    agent.call_llm = AsyncMock(return_value="Default blog content.")
    result = await agent.execute({}, {})
    assert result["success"] is True
    assert result["result"]["template"] == "blog"


@pytest.mark.asyncio
async def test_execute_returns_error_dict(agent):
    result = await agent.execute({"template": "missing"}, {})
    assert result == {"success": False, "error": "Template not found: missing"}


@pytest.mark.asyncio
async def test_execute_without_seo_keywords(agent):
    agent.call_llm = AsyncMock(return_value="Some content here.")
    result = await agent.execute({"template": "email"}, {})
    assert result["success"] is True
    assert result["result"]["seo_score"] == 50.0


# ---------------------------------------------------------------------------
# generate_content
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_content_returns_metrics(agent):
    agent.call_llm = AsyncMock(return_value="Intro body conclusion.")
    result = await agent.generate_content("blog", {"topic": "T"}, seo_keywords=["intro"])
    assert result["content"] == "Intro body conclusion."
    assert result["template"] == "blog"
    assert result["word_count"] == 3
    assert result["seo_score"] == 100.0
    assert isinstance(result["readability_score"], float)
    assert result["metadata"]["template"] == "blog"
    assert result["metadata"]["word_count"] == 3
    assert "generated_at" in result["metadata"]


@pytest.mark.asyncio
async def test_generate_content_template_not_found(agent):
    result = await agent.generate_content("nope", {})
    assert result == {"error": "Template not found: nope"}


@pytest.mark.asyncio
async def test_generate_content_without_seo_keywords(agent):
    agent.call_llm = AsyncMock(return_value="Plain content here.")
    result = await agent.generate_content("social", {})
    assert result["template"] == "social"
    assert result["seo_score"] == 50.0


@pytest.mark.asyncio
async def test_generate_content_empty_llm_response(agent):
    agent.call_llm = AsyncMock(return_value="")
    result = await agent.generate_content("social", {})
    assert result["content"] == ""
    assert result["word_count"] == 0
    assert result["seo_score"] == 50.0
    assert result["readability_score"] == 0


# ---------------------------------------------------------------------------
# _build_prompt
# ---------------------------------------------------------------------------


def test_build_prompt_with_keywords(agent):
    template = agent.templates["blog"]
    prompt = agent._build_prompt(template, {"topic": "SEO"}, ["seo", "content"])
    assert "blog" in prompt
    assert "seo, content" in prompt
    assert "conversational" in prompt
    assert json.dumps({"topic": "SEO"}, indent=2) in prompt
    assert "1. hook" in prompt
    assert "5. cta" in prompt


def test_build_prompt_empty_keywords_uses_auto(agent):
    template = agent.templates["email"]
    prompt = agent._build_prompt(template, {}, [])
    assert "auto" in prompt


def test_build_prompt_required_sections(agent):
    template = ContentTemplate(
        name="Custom",
        content_type=ContentType.BLOG,
        structure=["section_a"],
        word_count_target=100,
        required_sections=["section_a", "section_b"],
    )
    prompt = agent._build_prompt(template, {}, [])
    assert "section_a, section_b" in prompt


# ---------------------------------------------------------------------------
# _generate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_returns_llm_response(agent):
    agent.call_llm = AsyncMock(return_value="generated text")
    result = await agent._generate("prompt", agent.templates["blog"])
    assert result == "generated text"
    agent.call_llm.assert_awaited_once_with("prompt")


@pytest.mark.asyncio
async def test_generate_fallback_on_llm_error(agent):
    agent.call_llm = AsyncMock(side_effect=RuntimeError("boom"))
    template = agent.templates["blog"]
    result = await agent._generate("prompt", template)
    assert result.startswith("# Blog Post")
    assert "[Generated content pending LLM availability]" in result
    assert "- hook" in result
    assert "- cta" in result


# ---------------------------------------------------------------------------
# _calculate_seo_score
# ---------------------------------------------------------------------------


def test_seo_score_no_keywords(agent):
    assert agent._calculate_seo_score("anything here", []) == 50.0


def test_seo_score_all_keywords(agent):
    assert agent._calculate_seo_score("SEO content rocks", ["seo", "content"]) == 100.0


def test_seo_score_partial_keywords(agent):
    assert agent._calculate_seo_score("seo only", ["seo", "missing"]) == 50.0


def test_seo_score_case_insensitive(agent):
    assert agent._calculate_seo_score("SEO CONTENT ROCKS", ["seo", "content"]) == 100.0


def test_seo_score_no_keywords_found(agent):
    assert agent._calculate_seo_score("nothing relevant", ["zzz"]) == 0.0


# ---------------------------------------------------------------------------
# _calculate_readability
# ---------------------------------------------------------------------------


def test_readability_empty_content(agent):
    assert agent._calculate_readability("") == 0


def test_readability_no_sentences(agent):
    assert agent._calculate_readability("no punctuation here") == 0


def test_readability_clamps_to_100(agent):
    assert agent._calculate_readability("a.") == 100


def test_readability_clamps_to_0(agent):
    long_text = " ".join(["babababa"] * 20) + "."
    assert agent._calculate_readability(long_text) == 0


# ---------------------------------------------------------------------------
# _count_syllables
# ---------------------------------------------------------------------------


def test_count_syllables_simple(agent):
    assert agent._count_syllables("hello") == 2


def test_count_syllables_vowel_cluster(agent):
    assert agent._count_syllables("aeiou") == 1


def test_count_syllables_no_vowels(agent):
    assert agent._count_syllables("bcdfg") == 1


def test_count_syllables_uppercase(agent):
    assert agent._count_syllables("HELLO") == 2


# ---------------------------------------------------------------------------
# generate_* convenience methods
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_blog_post(agent):
    agent.call_llm = AsyncMock(return_value="Blog content")
    result = await agent.generate_blog_post("topic", ["kw"], {"extra": 1})
    assert result["template"] == "blog"
    prompt = agent.call_llm.await_args.args[0]
    assert "topic" in prompt
    assert "kw" in prompt


@pytest.mark.asyncio
async def test_generate_landing_page(agent):
    agent.call_llm = AsyncMock(return_value="Landing copy")
    result = await agent.generate_landing_page("Product", ["f1"], ["b1"])
    assert result["template"] == "landing"


@pytest.mark.asyncio
async def test_generate_email_sequence(agent):
    agent.call_llm = AsyncMock(return_value="Email content")
    result = await agent.generate_email_sequence("welcome", 3, "SMB", "signup")
    assert len(result) == 3
    assert agent.call_llm.await_count == 3


@pytest.mark.asyncio
async def test_generate_email_sequence_zero_steps(agent):
    agent.call_llm = AsyncMock(return_value="Email content")
    result = await agent.generate_email_sequence("welcome", 0, "SMB", "signup")
    assert result == []
    agent.call_llm.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_social_posts(agent):
    agent.call_llm = AsyncMock(return_value="Post")
    result = await agent.generate_social_posts("topic", 2, "twitter")
    assert len(result) == 2
    assert agent.call_llm.await_count == 2


@pytest.mark.asyncio
async def test_generate_social_posts_zero(agent):
    agent.call_llm = AsyncMock(return_value="Post")
    result = await agent.generate_social_posts("topic", 0, "twitter")
    assert result == []
    agent.call_llm.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_case_study(agent):
    agent.call_llm = AsyncMock(return_value="Case study")
    result = await agent.generate_case_study("Acme", "challenge", "solution", {"roi": "200%"})
    assert result["template"] == "case_study"


# ---------------------------------------------------------------------------
# generate_batch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_batch_parallel(agent):
    agent.call_llm = AsyncMock(return_value="Batch content")
    results = await agent.generate_batch("blog", [{"topic": "a"}, {"topic": "b"}], parallel=True)
    assert len(results) == 2
    assert all(r["template"] == "blog" for r in results)


@pytest.mark.asyncio
async def test_generate_batch_sequential(agent):
    agent.call_llm = AsyncMock(return_value="Batch content")
    results = await agent.generate_batch(
        "email", [{"topic": "a"}, {"topic": "b"}], parallel=False
    )
    assert len(results) == 2
    assert agent.call_llm.await_count == 2


@pytest.mark.asyncio
async def test_generate_batch_empty(agent):
    agent.call_llm = AsyncMock(return_value="x")
    results = await agent.generate_batch("blog", [], parallel=True)
    assert results == []
    agent.call_llm.assert_not_awaited()
