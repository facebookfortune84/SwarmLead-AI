"""Tests for the voice-learning hooks in the product knowledge base."""

from core.services.product_knowledge import ProductKnowledgeBase


def _kb() -> ProductKnowledgeBase:
    kb = ProductKnowledgeBase(repo_root=".")
    kb._keyword_boosts = {}
    kb._retrieval_stats = {}
    return kb


def test_retrieval_records_intent_stats():
    kb = _kb()
    kb.retrieve("what does the growth plan cost")
    snapshot = kb.analytics_snapshot()
    assert "monetization" in snapshot
    assert snapshot["monetization"]["count"] >= 1


def test_learn_applies_keyword_boost():
    kb = _kb()
    kb.learn({"pricing": 0.5})
    assert kb._keyword_boosts["pricing"] == 0.5
    kb.learn({"pricing": 0.25})
    assert kb._keyword_boosts["pricing"] == 0.75


def test_retrieval_prefers_boosted_chunks():
    kb = _kb()
    plain = kb.retrieve("plan")
    kb.learn({"pricing": 10.0})
    boosted = kb.retrieve("plan")
    assert len(boosted) <= len(plain) + 1
