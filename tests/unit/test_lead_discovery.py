"""Tests for the lead-discovery engine (accuracy-first lead sourcing)."""

import pytest

from core.services import lead_discovery as mod


def test_reserved_and_disposable_domains_flagged():
    assert mod._reserved("test@example.com".split("@")[-1])
    assert mod._reserved("buyer@test.co".split("@")[-1])
    assert mod._reserved("foo@mailinator.com".split("@")[-1])
    assert not mod._reserved("realbusiness.com")


def test_email_extraction_skips_role_and_junk():
    html = """
    <a href="mailto:owner@smithplumbing.com">Owner</a>
    <a href="mailto:info@smithplumbing.com">info</a>
    <p>Reach us at john.smith@gmail.com or noreply@site.com</p>
    <p>contact@example.com should never appear</p>
    """
    emails = mod._extract_emails(html)
    assert "owner@smithplumbing.com" in emails
    assert "info@smithplumbing.com" not in emails  # role inbox
    assert "john.smith@gmail.com" in emails
    assert "noreply@site.com" not in emails
    assert "contact@example.com" not in emails  # reserved domain


def test_email_extraction_handles_obfuscation():
    html = '<p>Email us: sarah at brightlaw dot com</p>'
    emails = mod._extract_emails(html)
    assert any("sarah@brightlaw.com" in e for e in emails)


def test_mx_check_accepts_real_domain_and_rejects_impossible():
    ok, host = mod._mx_ok("gmail.com")
    assert ok is True and host
    # A guaranteed-nonexistent TLD should fail cleanly (no exception).
    ok, host = mod._mx_ok("definitely-not-a-real-domain-xyz")
    assert ok is False


def test_score_prefers_business_domain():
    assert mod._score_lead("smithplumbing.com", "mx.smithplumbing.com") > mod._score_lead(
        "gmail.com", "mx.gmail.com"
    )


def test_blocked_maildomains():
    assert mod._blocked_maildomain("realmadrid.com") is True
    assert mod._blocked_maildomain("eonline.com") is True
    assert mod._blocked_maildomain("cnn.com") is True
    assert mod._blocked_maildomain("smithplumbing.com") is False


def test_big_brand_detection():
    assert mod._looks_big_brand("realmadrid.com", "Real Madrid CF", "realmadrid.com") is True
    assert mod._looks_big_brand("eonline.com", "E! Online", "eentertainment.com") is True
    assert mod._looks_big_brand("smithplumbing.com", "Smith Plumbing LLC", "smithplumbing.com") is False
    assert mod._looks_big_brand("dcummingslaw.com", "DCummings Law LLC", "dcummingslaw.com") is False


def test_clean_vertical_strips_quotes():
    assert mod._clean_vertical('"dental clinic" site owner contact') == "Dental"
    assert mod._clean_vertical("law firm official website") == "Law"


@pytest.mark.asyncio
async def test_discover_end_to_end_with_stubbed_search(tmp_path, monkeypatch):
    findings = tmp_path / "findings.json"

    async def fake_crawl(self, url):
        return (
            "<html><title>Smith Plumbing</title>"
            '<a href="mailto:owner@smithplumbing.com">Owner</a>'
            "</html>",
            {
                "title": "Smith Plumbing | Home",
                "final_url": url,
                "homepage_emails": ["owner@smithplumbing.com"],
                "contact_emails": [],
            },
        )

    async def fake_find(self, query):
        return ["https://smithplumbing.com"]

    monkeypatch.setattr(mod.LeadDiscoveryEngine, "_crawl", fake_crawl)
    monkeypatch.setattr(mod.LeadDiscoveryEngine, "_find_urls", fake_find)
    monkeypatch.setattr(mod, "FINDINGS_PATH", findings)

    engine = mod.LeadDiscoveryEngine(findings_path=str(findings))
    leads = await engine.discover(verticals=["plumber"], max_targets=1)
    assert leads, "expected at least one discovered lead"
    assert leads[0].email == "owner@smithplumbing.com"
    assert leads[0].intent_score >= 70
    assert engine._known("owner@smithplumbing.com")

    # Second pass must not re-emit the same lead (dedup).
    again = await engine.discover(verticals=["plumber"], max_targets=1)
    assert all(l.email != "owner@smithplumbing.com" for l in again)
