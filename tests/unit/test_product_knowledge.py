"""Tests for the product knowledge base (voice agent doc grounding)."""

from core.services.product_knowledge import ProductKnowledgeBase


def _kb() -> ProductKnowledgeBase:
    return ProductKnowledgeBase(repo_root=".")


def test_loads_docs():
    kb = _kb()
    assert len(kb._chunks) > 50


def test_retrieve_returns_bounded_results():
    kb = _kb()
    results = kb.retrieve("how do I create an outreach campaign")
    assert len(results) <= 4
    total = sum(len(c["text"]) for c in results)
    assert total <= 1600


def test_format_context_empty_for_blank_query():
    kb = _kb()
    assert kb.format_context("") == ""


def test_retrieve_ranked_by_query_terms():
    kb = _kb()
    results = kb.retrieve("outreach campaign leads", top_k=2, max_chars=900)
    assert len(results) <= 2
    assert all("text" in c and "title" in c for c in results)
