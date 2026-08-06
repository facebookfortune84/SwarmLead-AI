"""Unit tests for the SEO router (interfaces.api.routers.seo)."""

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.services.seo_engine import SEOEngine
from interfaces.api.routers.seo import router


@pytest.fixture
def client(tmp_path, monkeypatch):
    import core.services.seo_engine as seo_module
    import interfaces.api.routers.seo as router_module

    engine = SEOEngine(
        base_url="https://realms2riches.com",
        growth_state_path=tmp_path / "empty.json",
    )
    monkeypatch.setattr(seo_module, "seo_engine", engine)
    monkeypatch.setattr(router_module, "seo_engine", engine)

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_sitemap_xml(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "<urlset" in response.text


def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.text.startswith("User-agent: *")
    assert "Sitemap:" in response.text


def test_jsonld_endpoint(client):
    response = client.get("/api/seo/jsonld")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/ld+json")
    types = {item["@type"] for item in json.loads(response.text)}
    assert "Organization" in types


def test_pages_endpoint(client):
    from core.services.seo_engine import STATIC_URLS

    response = client.get("/api/seo/pages")
    body = response.json()
    assert body["count"] == len(STATIC_URLS)
    assert body["pages"][0]["url"].startswith("https://")


def test_page_jsonld_404(client):
    assert client.get("/api/seo/pages/nope").status_code == 404
