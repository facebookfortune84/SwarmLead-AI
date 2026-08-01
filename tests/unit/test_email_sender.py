"""Tests for the SMTP email sender used by the growth loop."""

import pytest

from core.services.email_sender import EmailSender


@pytest.fixture
def sender(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test.local")
    monkeypatch.setenv("SMTP_USER", "test@example.com")
    monkeypatch.setenv("SMTP_PASS", "secret")
    return EmailSender()


def test_unconfigured_reports_unconfigured(monkeypatch):
    for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS"):
        monkeypatch.delenv(key, raising=False)
    s = EmailSender()
    result = asyncio_run(s.send("a@b.com", "s", "b"))
    assert result["status"] == "unconfigured"


def test_dry_run_never_sends(monkeypatch, sender):
    monkeypatch.setenv("OUTREACH_DRY_RUN", "1")
    s = EmailSender()
    assert s.dry_run is True
    result = asyncio_run(s.send("a@b.com", "Subject", "Body"))
    assert result["status"] == "dry_run"


def test_rate_limit_blocks(monkeypatch, sender):
    monkeypatch.setenv("OUTREACH_DRY_RUN", "0")
    sender.rate_limit_per_hour = 2
    for _ in range(2):
        asyncio_run(sender.send("a@b.com", "s", "b"))
    result = asyncio_run(sender.send("a@b.com", "s", "b"))
    assert result["status"] == "rate_limited"


def asyncio_run(coro):
    import asyncio

    return asyncio.run(coro)
