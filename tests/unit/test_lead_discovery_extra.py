"""Extra tests for the lead-discovery engine (uncovered branches, hermetic HTTP)."""

import json
import logging

import httpx
import pytest

from core.services import lead_discovery as mod


def _fake_client(handler):
    """Return an httpx.AsyncClient stand-in wired to a MockTransport handler.

    The engine constructs ``httpx.AsyncClient(timeout=..., headers=...,
    follow_redirects=True)`` internally; this factory returns a class that
    accepts those kwargs and routes every ``get`` through ``handler``.
    """

    transport = httpx.MockTransport(handler)
    real_async_client = httpx.AsyncClient

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            self._inner = real_async_client(transport=transport)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            await self._inner.aclose()
            return False

        async def get(self, url, **kwargs):
            return await self._inner.get(url, **kwargs)

    return FakeAsyncClient


def _patched_engine(tmp_path, monkeypatch, handler, mx=(True, "mx.smithplumbing.com")):
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(handler))
    monkeypatch.setattr(mod, "_mx_ok", lambda domain, _mx=mx: _mx)
    return mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "findings.json"))


# ---------------------------------------------------------------- pure helpers
def test_blocked_maildomain_segment_markers():
    assert mod._blocked_maildomain("mail.deltadentalofca.com") is True
    assert mod._blocked_maildomain("northwesternmutual.com") is True
    assert mod._blocked_maildomain("agent.stateinsurance.com") is True
    assert mod._blocked_maildomain("plumbingco.net") is False


def test_extract_emails_empty_html():
    assert mod._extract_emails("") == []
    assert mod._extract_emails(None) == []


def test_extract_emails_skips_overlong_email():
    html = f"{'a' * 110}@{'b' * 6}.com"
    assert mod._extract_emails(html) == []


def test_extract_emails_skips_stripped_empty_local():
    assert mod._extract_emails(".@b.com") == []
    assert mod._extract_emails("...@bar.co") == []


def test_extract_emails_multiple_and_dedup():
    html = (
        '<a href="mailto:bob@acmeplumbing.com">Bob</a>'
        "<p>write to bob@acmeplumbing.com or alice@acmeplumbing.com</p>"
        "<p>again bob@acmeplumbing.com</p>"
        "<p>support@acmeplumbing.com is a role inbox</p>"
        "<p>help@acmeplumbing.com too</p>"
    )
    assert mod._extract_emails(html) == ["bob@acmeplumbing.com", "alice@acmeplumbing.com"]


def test_extract_emails_skips_reserved_and_disposable():
    html = (
        "<p>contact@example.com reserved</p>"
        "<p>joe@mailinator.com disposable</p>"
        "<p>owner@smithplumbing.com real</p>"
    )
    assert mod._extract_emails(html) == ["owner@smithplumbing.com"]


def test_extract_emails_obfuscation_variants():
    html = (
        "<p>a) maria at brightlaw dot com</p>"
        "<p>b) maria [at] brightlaw [dot] com</p>"
        "<p>c) maria@brightlaw.com</p>"
    )
    assert mod._extract_emails(html) == ["maria@brightlaw.com"]


def test_title_from_html():
    assert mod._title_from_html("<html><title>  Acme   Plumbing | Home  </title></html>") == (
        "Acme Plumbing | Home"
    )
    assert mod._title_from_html("<html><body>no title</body></html>") == ""
    assert mod._title_from_html("<title>   </title>") == ""
    long_title = "x" * 200
    assert len(mod._title_from_html(f"<title>{long_title}</title>")) == 120


def test_score_lead_personal_mailbox_penalty():
    assert mod._score_lead("gmail.com", "mx.gmail.com") == 60
    assert mod._score_lead("business.com", "mx.business.com") == 90
    assert mod._score_lead("business.com", "implicit-A") == 80
    assert mod._score_lead("gmail.com", None) == 50


def test_mx_ok_success(monkeypatch):
    import dns.resolver

    class FakeExchange:
        exchange = "mx.acmeplumbing.com."

    class FakeAnswers:
        def __bool__(self):
            return True

        def __getitem__(self, i):
            return FakeExchange()

    monkeypatch.setattr(
        dns.resolver, "resolve", lambda domain, rtype, lifetime=None: FakeAnswers()
    )
    ok, host = mod._mx_ok("acmeplumbing.com")
    assert ok is True
    assert host == "mx.acmeplumbing.com"


def test_mx_ok_implicit_a_fallback(monkeypatch):
    import dns.resolver

    def fake(domain, rtype, lifetime=None):
        if rtype == "MX":
            raise Exception("no MX")
        return []

    monkeypatch.setattr(dns.resolver, "resolve", fake)
    ok, host = mod._mx_ok("smallbiz.com")
    assert ok is True
    assert host == "implicit-A"


def test_mx_ok_failure(monkeypatch):
    import dns.resolver

    def fake(domain, rtype, lifetime=None):
        raise Exception("timeout")

    monkeypatch.setattr(dns.resolver, "resolve", fake)
    ok, host = mod._mx_ok("dead-domain-xyz")
    assert ok is False
    assert host is None


def test_name_from_email():
    assert mod._name_from_email("john.doe") == "John Doe"
    assert mod._name_from_email("jdoe") == "Jdoe"
    assert mod._name_from_email("john") == "John"
    assert mod._name_from_email(".") == ""


def test_looks_generic_company():
    assert mod._looks_generic_company("") is True
    assert mod._looks_generic_company("ab") is True
    assert mod._looks_generic_company("Just a moment") is True
    assert mod._looks_generic_company("Acme Plumbing LLC") is False


# ------------------------------------------------------------ findings storage
def test_load_findings_reads_json(tmp_path):
    p = tmp_path / "findings.json"
    p.write_text(json.dumps({"a@b.com": {"company": "X"}}), encoding="utf-8")
    engine = mod.LeadDiscoveryEngine(findings_path=str(p))
    assert engine._load_findings() == {"a@b.com": {"company": "X"}}


def test_load_findings_missing(tmp_path):
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "nope.json"))
    assert engine._load_findings() == {}


def test_load_findings_corrupt_json(tmp_path):
    p = tmp_path / "findings.json"
    p.write_text("{not json", encoding="utf-8")
    engine = mod.LeadDiscoveryEngine(findings_path=str(p))
    assert engine._load_findings() == {}


def test_save_findings_oserror_logged(tmp_path, caplog):
    blocker = tmp_path / "blocker"
    blocker.write_text("a regular file", encoding="utf-8")
    engine = mod.LeadDiscoveryEngine(findings_path=str(blocker / "sub" / "f.json"))
    engine._seen = {"a@b.com": {"company": "X"}}
    with caplog.at_level(logging.WARNING, logger="LeadDiscovery"):
        engine._save_findings()
    assert "Could not persist discovery findings" in caplog.text


def test_record_and_known(tmp_path):
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    lead = mod.DiscoveredLead(email="Owner@ACME.com", company="Acme", vertical="Dental")
    engine._record(lead)
    assert engine._known("owner@acme.com")
    assert not engine._known("other@acme.com")
    findings = engine.findings()
    assert len(findings) == 1
    assert findings[0]["email"] == "owner@acme.com"
    assert findings[0]["company"] == "Acme"


# --------------------------------------------------------------- search paths
@pytest.mark.asyncio
async def test_search_ddg_parses_uddg(tmp_path, monkeypatch):
    html = (
        '<a class="result__a" href="uddg=https%3A%2F%2Facmeplumbing.com%2F&rut=1">Acme</a>'
        '<a class="result__a" href="https://direct.com">Direct</a>'
        '<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fother.com%2F&rut=2">Other</a>'
    )
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(lambda r: httpx.Response(200, text=html)))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    urls = await engine._search_ddg("plumber")
    assert "https://acmeplumbing.com/" in urls
    assert "https://direct.com" in urls
    assert "//duckduckgo.com/l/?uddg=https%3A%2F%2Fother.com%2F&rut=2" in urls


@pytest.mark.asyncio
async def test_search_ddg_non_200(tmp_path, monkeypatch):
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(lambda r: httpx.Response(500)))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    assert await engine._search_ddg("plumber") == []


@pytest.mark.asyncio
async def test_search_ddg_exception(tmp_path, monkeypatch):
    def boom(r):
        raise httpx.ConnectError("network down")

    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(boom))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    assert await engine._search_ddg("plumber") == []


@pytest.mark.asyncio
async def test_search_bing_rss_parses_items(tmp_path, monkeypatch):
    rss = (
        "<item><title>Acme Plumbing</title><link>https://acmeplumbing.com/</link></item>"
        "<item><title>B</title><link>https://b.com</link></item>"
    )
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(lambda r: httpx.Response(200, text=rss)))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    assert await engine._search_bing_rss("plumber") == [
        "https://acmeplumbing.com/",
        "https://b.com",
    ]


@pytest.mark.asyncio
async def test_search_bing_rss_non_200(tmp_path, monkeypatch):
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(lambda r: httpx.Response(503)))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    assert await engine._search_bing_rss("plumber") == []


@pytest.mark.asyncio
async def test_search_bing_rss_exception(tmp_path, monkeypatch):
    def boom(r):
        raise httpx.ConnectError("network down")

    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(boom))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    assert await engine._search_bing_rss("plumber") == []


@pytest.mark.asyncio
async def test_search_bing_parses_h2_links(tmp_path, monkeypatch):
    html = '<h2><a href="https://acmeplumbing.com">Acme</a></h2><a href="https://other.com"><h2>Other</h2></a>'
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(lambda r: httpx.Response(200, text=html)))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    urls = await engine._search_bing("plumber")
    assert urls == ["https://other.com", "https://acmeplumbing.com"]


@pytest.mark.asyncio
async def test_search_bing_non_200(tmp_path, monkeypatch):
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(lambda r: httpx.Response(500)))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    assert await engine._search_bing("plumber") == []


@pytest.mark.asyncio
async def test_search_bing_exception(tmp_path, monkeypatch):
    def boom(r):
        raise httpx.ConnectError("network down")

    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(boom))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    assert await engine._search_bing("plumber") == []


# ------------------------------------------------------------------ find_urls
@pytest.mark.asyncio
async def test_find_urls_cleans_and_dedups(tmp_path, monkeypatch):
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))

    async def fake_rss(query):
        return [
            "https://www.acmeplumbing.com/about",
            "https://www.facebook.com/acme",
            "ftp://files.acmeplumbing.com",
            "https://site.edu",
            "https://agency.gov",
            "https://charity.org",
            "https://www.manta.com/listing",
            "https://wiki.wikimedia.org/x",
            "http://barehost",
            "https:///nopath",
            "https://[::1",
            "https://www.acmeplumbing.com/about",
            "https://acmeplumbing.com",
        ]

    monkeypatch.setattr(engine, "_search_bing_rss", fake_rss)
    urls = await engine._find_urls("plumber")
    assert urls == ["https://www.acmeplumbing.com", "http://barehost", "https://acmeplumbing.com"]


@pytest.mark.asyncio
async def test_find_urls_falls_back_when_rss_empty(tmp_path, monkeypatch):
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))

    async def fake_rss(query):
        return []

    async def fake_ddg(query):
        return ["https://ddgco.com"]

    async def fake_bing(query):
        raise RuntimeError("bing broke")

    monkeypatch.setattr(engine, "_search_bing_rss", fake_rss)
    monkeypatch.setattr(engine, "_search_ddg", fake_ddg)
    monkeypatch.setattr(engine, "_search_bing", fake_bing)
    urls = await engine._find_urls("plumber")
    assert urls == ["https://ddgco.com"]


# --------------------------------------------------------------------- crawl
@pytest.mark.asyncio
async def test_crawl_homepage_and_contact(tmp_path, monkeypatch):
    def handler(request):
        if request.url.path == "/contact":
            return httpx.Response(200, text='<p>Jane: <a href="mailto:jane@acmeplumbing.com">jane</a></p>')
        return httpx.Response(
            200,
            text=(
                "<html><head><title>Acme Plumbing | Home</title></head>"
                '<a href="mailto:bob@acmeplumbing.com">Bob</a>'
            ),
        )

    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(handler))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    html, meta = await engine._crawl("https://acmeplumbing.com")
    assert meta["homepage_emails"] == ["bob@acmeplumbing.com"]
    assert "jane@acmeplumbing.com" in meta["contact_emails"]
    assert meta["title"] == "Acme Plumbing | Home"
    assert meta["final_url"] == "https://acmeplumbing.com"
    assert "mailto:bob@acmeplumbing.com" in html


@pytest.mark.asyncio
async def test_crawl_skips_failing_contact_pages(tmp_path, monkeypatch):
    def handler(request):
        if request.url.path == "/contact":
            return httpx.Response(404)
        if request.url.path == "/contact-us":
            raise httpx.ConnectError("boom")
        if request.url.path == "/about":
            return httpx.Response(200, text="<p>jane@acmeplumbing.com</p>")
        return httpx.Response(200, text="<html><title>Acme</title></html>")

    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(handler))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    _, meta = await engine._crawl("https://acmeplumbing.com")
    assert meta["contact_emails"] == ["jane@acmeplumbing.com"]


@pytest.mark.asyncio
async def test_crawl_homepage_404(tmp_path, monkeypatch):
    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(lambda r: httpx.Response(404)))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    html, meta = await engine._crawl("https://acmeplumbing.com")
    assert html == ""
    assert meta == {}


@pytest.mark.asyncio
async def test_crawl_homepage_exception(tmp_path, monkeypatch):
    def boom(r):
        raise httpx.ConnectError("timeout")

    monkeypatch.setattr(mod.httpx, "AsyncClient", _fake_client(boom))
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    html, meta = await engine._crawl("https://acmeplumbing.com")
    assert html == ""
    assert meta == {}


@pytest.mark.asyncio
async def test_crawl_no_emails(tmp_path, monkeypatch):
    monkeypatch.setattr(
        mod.httpx,
        "AsyncClient",
        _fake_client(lambda r: httpx.Response(200, text="<html><title>Acme</title></html>")),
    )
    engine = mod.LeadDiscoveryEngine(findings_path=str(tmp_path / "f.json"))
    _, meta = await engine._crawl("https://acmeplumbing.com")
    assert "homepage_emails" not in meta
    assert meta["title"] == "Acme"


# ------------------------------------------------------------------- discover
@pytest.mark.asyncio
async def test_discover_full_e2e_persists_and_dedups(tmp_path, monkeypatch):
    def handler(request):
        if b"format=rss" in request.url.query:
            return httpx.Response(
                200,
                text=(
                    "<item><title>Acme Plumbing</title>"
                    "<link>https://acmeplumbing.com</link></item>"
                ),
            )
        if request.url.path == "/contact":
            return httpx.Response(200, text='<p>Jane Doe: <a href="mailto:jane@acmeplumbing.com">jane</a></p>')
        return httpx.Response(
            200,
            text=(
                "<html><head><title>Acme Plumbing LLC | Home</title></head>"
                '<body><a href="mailto:bob@acmeplumbing.com">Bob</a>'
                "<p>info@acmeplumbing.com (role, ignored)</p>"
                "</body></html>"
            ),
        )

    engine = _patched_engine(tmp_path, monkeypatch, handler, mx=(True, "mx.acmeplumbing.com"))
    leads = await engine.discover(verticals=["plumber"], max_targets=1)
    emails = {lead.email for lead in leads}
    assert emails == {"bob@acmeplumbing.com", "jane@acmeplumbing.com"}

    bob = [lead for lead in leads if lead.email == "bob@acmeplumbing.com"][0]
    assert bob.name == "Bob"
    assert bob.company == "Acme Plumbing LLC"
    assert bob.vertical.strip('"') == "Plumber"
    assert bob.website == "https://acmeplumbing.com"
    assert bob.intent_score == 94
    assert bob.confidence == "high"
    assert bob.details["mx"] == "mx.acmeplumbing.com"
    assert bob.details["title"] == "Acme Plumbing LLC | Home"
    assert bob.details["signals"]["authority"] is True
    assert bob.details["maildomain"] == "acmeplumbing.com"

    assert engine._known("bob@acmeplumbing.com")
    assert engine._known("jane@acmeplumbing.com")
    findings = engine.findings()
    assert len(findings) == 2
    assert {f["email"] for f in findings} == emails

    again = await engine.discover(verticals=["plumber"], max_targets=1)
    assert again == []


@pytest.mark.asyncio
async def test_discover_search_failure_fallback(tmp_path, monkeypatch):
    def handler(request):
        if b"format=rss" in request.url.query:
            return httpx.Response(500)
        return httpx.Response(200, text="no results at all")

    engine = _patched_engine(tmp_path, monkeypatch, handler)
    leads = await engine.discover(verticals=["plumber"], max_targets=1)
    assert leads == []
    assert engine.findings() == []


@pytest.mark.asyncio
async def test_discover_skips_blocked_maildomain(tmp_path, monkeypatch):
    def handler(request):
        if b"format=rss" in request.url.query:
            return httpx.Response(
                200,
                text="<item><title>News</title><link>https://newsaggregator.com</link></item>",
            )
        return httpx.Response(
            200,
            text="<html><title>News Aggregator</title><p>newsdesk@cnn.com</p></html>",
        )

    engine = _patched_engine(tmp_path, monkeypatch, handler)
    leads = await engine.discover(verticals=["news"], max_targets=1)
    assert leads == []
    assert engine.findings() == []


@pytest.mark.asyncio
async def test_discover_skips_no_mx(tmp_path, monkeypatch):
    def handler(request):
        if b"format=rss" in request.url.query:
            return httpx.Response(
                200,
                text="<item><title>X</title><link>https://acmeplumbing.com</link></item>",
            )
        return httpx.Response(
            200,
            text="<html><title>Acme Plumbing</title><p>bob@acmeplumbing.com</p></html>",
        )

    engine = _patched_engine(tmp_path, monkeypatch, handler, mx=(False, None))
    leads = await engine.discover(verticals=["plumber"], max_targets=1)
    assert leads == []


@pytest.mark.asyncio
async def test_discover_skips_generic_company(tmp_path, monkeypatch):
    def handler(request):
        if b"format=rss" in request.url.query:
            return httpx.Response(
                200,
                text="<item><title>X</title><link>https://acmeplumbing.com</link></item>",
            )
        return httpx.Response(
            200,
            text="<html><title>Just a moment</title><p>bob@acmeplumbing.com</p></html>",
        )

    engine = _patched_engine(tmp_path, monkeypatch, handler)
    leads = await engine.discover(verticals=["plumber"], max_targets=1)
    assert leads == []


@pytest.mark.asyncio
async def test_discover_skips_big_brand(tmp_path, monkeypatch):
    def handler(request):
        if b"format=rss" in request.url.query:
            return httpx.Response(
                200,
                text="<item><title>X</title><link>https://coffeeroasters.com</link></item>",
            )
        return httpx.Response(
            200,
            text="<html><title>Starbucks Coffee</title><p>careers@starbucks.com</p></html>",
        )

    engine = _patched_engine(tmp_path, monkeypatch, handler)
    leads = await engine.discover(verticals=["coffee"], max_targets=1)
    assert leads == []


@pytest.mark.asyncio
async def test_discover_personal_email_medium_confidence(tmp_path, monkeypatch):
    def handler(request):
        if b"format=rss" in request.url.query:
            return httpx.Response(
                200,
                text="<item><title>X</title><link>https://bakeshop.com</link></item>",
            )
        return httpx.Response(
            200,
            text="<html><title>Bakeshop Co</title><p>maria.doe@proton.me</p></html>",
        )

    engine = _patched_engine(tmp_path, monkeypatch, handler, mx=(True, "implicit-A"))
    leads = await engine.discover(verticals=["bakery"], max_targets=1)
    assert len(leads) == 1
    assert leads[0].email == "maria.doe@proton.me"
    assert leads[0].name == "Maria Doe"
    assert leads[0].intent_score == 64
    assert leads[0].confidence == "medium"
