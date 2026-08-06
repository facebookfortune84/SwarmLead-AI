"""Unit tests for the SEO asset engine (core.services.seo_engine)."""

import json

import pytest

from core.services.seo_engine import (
    STATIC_URLS,
    SEOEngine,
    _strip_protocol,
)


@pytest.fixture
def engine(tmp_path):
    state = tmp_path / "growth_state.json"
    state.write_text(
        json.dumps(
            {
                "artifacts": {
                    "seo_pages": [
                        {
                            "url": "https://realms2riches.com/industries/legal-practices",
                            "title": "Legal Practices Lead Generation",
                            "status": "draft",
                            "priority": 0.8,
                            "changefreq": "weekly",
                            "generated_at": "2026-08-01T00:00:00Z",
                            "schema": {
                                "@context": "https://schema.org",
                                "@type": "SoftwareApplication",
                                "name": "Legal Practices Edition",
                            },
                        },
                        {"url": "https://realms2riches.com/industries/dup", "priority": 0.8},
                        {
                            "url": "/home-services",
                            "title": "Home Services",
                            "status": "draft",
                            "priority": 0.7,
                            "generated_at": "2026-08-01T00:00:00Z",
                        },
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    return SEOEngine(
        base_url="https://realms2riches.com", growth_state_path=state
    )


def test_static_urls_always_included(engine):
    inventory = engine.page_inventory()
    urls = [e["url"] for e in inventory]
    for static in STATIC_URLS:
        assert f"https://realms2riches.com{static['url']}" in urls


def test_programmatic_pages_included(engine):
    urls = [e["url"] for e in engine.page_inventory()]
    assert "https://realms2riches.com/industries/legal-practices" in urls
    assert "https://realms2riches.com/home-services" in urls


def test_duplicates_deduplicated(engine):
    urls = [e["url"] for e in engine.page_inventory()]
    assert len(urls) == len(set(urls))


def test_sitemap_renders(engine):
    xml = engine.build_sitemap()
    assert "<urlset" in xml
    assert xml.count("<url>") >= len(STATIC_URLS)
    assert "https://realms2riches.com/industries/legal-practices" in xml
    assert xml.rstrip().endswith("</urlset>")


def test_robots_mentions_sitemap(engine):
    robots = engine.build_robots()
    assert robots.startswith("User-agent: *")
    assert "https://realms2riches.com/sitemap.xml" in robots
    assert "Disallow: /admin/" in robots


def test_json_ld_org_and_website(engine):
    data = json.loads(engine.build_json_ld())
    types = {item["@type"] for item in data}
    assert types == {"Organization", "WebSite"}
    assert data[0]["url"] == "https://realms2riches.com"


def test_page_json_ld(engine):
    page = {"title": "X", "schema": {"@type": "Article", "headline": "X"}}
    rendered = json.loads(engine.build_page_json_ld(page))
    assert rendered["@context"] == "https://schema.org"
    assert rendered["headline"] == "X"


def test_engine_missing_state(tmp_path):
    empty = SEOEngine(
        base_url="https://x.com", growth_state_path=tmp_path / "nope.json"
    )
    assert empty.seo_pages() == []
    xml = empty.build_sitemap()
    assert "<urlset" in xml


def test_strip_protocol():
    assert _strip_protocol("https://realms2riches.com/x/y") == "/x/y"
    assert _strip_protocol("/x/y") == "/x/y"
    assert _strip_protocol("x/y") == "/x/y"