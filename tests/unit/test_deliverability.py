"""Tests for the deliverability engine and suppression list."""

import pytest

from core.services.deliverability import DeliverabilityEngine, FREE_EMAIL_DOMAINS


@pytest.fixture
def de(tmp_path):
    return DeliverabilityEngine(suppression_path=tmp_path / "suppression.json")


def test_suppress_and_is_suppressed(de):
    assert de.suppress("a@b.com", "unsubscribe") is True
    assert de.is_suppressed("a@b.com") is True
    assert de.suppress("a@b.com", "unsubscribe") is False


def test_record_bounce_uses_marker(de):
    de.record_bounce("x@y.com", "550 5.1.1 user unknown")
    assert de.is_suppressed("x@y.com")
    stats = de.suppression_stats()
    assert stats.get("bounce", 0) >= 1


def test_filter_out_excludes_suppressed(de):
    de.suppress("blocked@x.com", "bounce")
    result = de.filter_out(["ok@x.com", "blocked@x.com"])
    assert result == ["ok@x.com"]


def test_recommended_records_shape(de):
    records = de.recommended_records("mail.example.com")
    assert "SPF (TXT)" in records
    assert records["SPF (TXT)"]["value"].startswith("v=spf1")
    assert records["DMARC (TXT)"]["value"].startswith("v=DMARC1")


def test_score_never_negative_or_over_100(de):
    score = de.score()
    assert 0 <= score["score"] <= 100
    assert score["grade"] in {"A", "B", "C", "D"}


def test_free_email_domains_defined():
    assert "gmail.com" in FREE_EMAIL_DOMAINS
