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


def test_security_modes_select_transport(monkeypatch):
    monkeypatch.setenv("OUTREACH_DRY_RUN", "0")
    monkeypatch.setenv("SMTP_HOST", "smtp.test.local")
    monkeypatch.setenv("SMTP_USER", "test@example.com")
    monkeypatch.setenv("SMTP_PASS", "secret")
    monkeypatch.setenv("SMTP_SECURITY", "ssl")
    ssl_sender = EmailSender()
    assert ssl_sender.security == "ssl"

    monkeypatch.setenv("SMTP_SECURITY", "none")
    plain_sender = EmailSender()
    assert plain_sender.security == "none"

    monkeypatch.setenv("SMTP_SECURITY", "tls")
    tls_sender = EmailSender()
    assert tls_sender.security == "tls"


def test_send_sync_ssl_uses_smtp_ssl(monkeypatch):
    import smtplib

    monkeypatch.setenv("SMTP_HOST", "smtp.test.local")
    monkeypatch.setenv("SMTP_USER", "test@example.com")
    monkeypatch.setenv("SMTP_PASS", "secret")
    monkeypatch.setenv("SMTP_SECURITY", "ssl")
    s = EmailSender()

    class FakeSmtp:
        instance = None

        def __init__(self, host, port, context=None, timeout=None):
            self.sent = False
            self.logged_in = False
            FakeSmtp.instance = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def login(self, user, password):
            self.logged_in = True

        def send_message(self, msg):
            self.sent = True

    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSmtp)
    monkeypatch.setattr(smtplib, "SMTP", FakeSmtp)
    s._send_sync("a@b.com", "Subject", "Body")
    assert FakeSmtp.instance.sent is True


def asyncio_run(coro):
    import asyncio

    return asyncio.run(coro)
