"""
SEO asset engine — deterministic sitemap / robots.txt / JSON-LD generation.

Consumes the growth loop's accumulated ``artifacts.seo_pages`` (programmatic
industry pages) plus a fixed set of canonical routes, and renders the three
standard crawler-facing assets. All logic is pure string composition, so it
is fully testable without any network or LLM calls.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from core.site import site_url

logger = logging.getLogger("SEOEngine")

GROWTH_STATE_PATH = Path(__file__).resolve().parents[2] / "data" / "growth_state.json"

DEFAULT_BASE_URL = site_url()

# Canonical routes that always exist regardless of the growth-loop artifacts.
STATIC_URLS = [
    {"url": "/", "changefreq": "weekly", "priority": 1.0},
    {"url": "/industries", "changefreq": "weekly", "priority": 0.9},
    {"url": "/tools/business-skeleton", "changefreq": "weekly", "priority": 0.8},
    {"url": "/onboarding", "changefreq": "monthly", "priority": 0.7},
    {"url": "/demo", "changefreq": "monthly", "priority": 0.7},
]

_CANONICAL_PATH_RE = re.compile(r"^https?://[^/]+(?=/|$)")


def _strip_protocol(url: str) -> str:
    """Normalize a URL to a root-relative path (or keep absolute paths)."""
    if not url:
        return url
    if url.startswith("http://") or url.startswith("https://"):
        match = _CANONICAL_PATH_RE.match(url)
        trimmed = url[match.end():] if match else url
        return trimmed or "/"
    if not url.startswith("/"):
        return "/" + url
    return url


class SEOEngine:
    """Builds crawler-facing assets from live + static page inventory."""

    def __init__(self, base_url: str | None = None, growth_state_path: Path | None = None):
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.growth_state_path = growth_state_path or GROWTH_STATE_PATH

    # ---------------------------------------------------------------- source
    def seo_pages(self) -> List[Dict[str, Any]]:
        """Read programmatic page specs from the growth loop's state file."""
        try:
            with open(self.growth_state_path, encoding="utf-8") as fh:
                state = json.load(fh)
            pages = state.get("artifacts", {}).get("seo_pages", []) or []
            return [
                p for p in pages if p.get("url") and p.get("status") in {"draft", "published"}
            ]
        except (OSError, ValueError):
            return []

    def page_inventory(self) -> List[Dict[str, Any]]:
        """Full URL inventory: growth-loop programmatic pages + static routes."""
        seen = set()
        inventory = []
        for static in STATIC_URLS:
            url = static["url"]
            if url in seen:
                continue
            seen.add(url)
            inventory.append(
                {
                    "url": self.base_url + url,
                    "changefreq": static["changefreq"],
                    "priority": static["priority"],
                    "lastmod": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
            )
        for page in self.seo_pages():
            url = _strip_protocol(page.get("url", ""))
            if not url or url in seen:
                continue
            seen.add(url)
            inventory.append(
                {
                    "url": self.base_url + url,
                    "changefreq": page.get("changefreq", "weekly"),
                    "priority": float(page.get("priority", 0.8)),
                    "lastmod": page.get("generated_at", "")[:10]
                    or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
            )
        return inventory

    # ---------------------------------------------------------------- assets
    def build_sitemap(self) -> str:
        """Render a standard sitemap.xml from the page inventory."""
        urls = "\n".join(
            f"    <url>\n"
            f"      <loc>{entry['url']}</loc>\n"
            f"      <lastmod>{entry['lastmod']}</lastmod>\n"
            f"      <changefreq>{entry['changefreq']}</changefreq>\n"
            f"      <priority>{entry['priority']:.1f}</priority>\n"
            f"    </url>"
            for entry in self.page_inventory()
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n"
            "</urlset>\n"
        )

    def build_robots(self) -> str:
        """Render robots.txt referencing the sitemap."""
        return (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /admin/\n"
            "Disallow: /api/\n"
            f"\nSitemap: {self.base_url}/sitemap.xml\n"
        )

    def build_json_ld(self) -> str:
        """JSON-LD structured data for the landing page (Organization + WebSite)."""
        schema = [
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Realm & Riches",
                "url": self.base_url,
                "sameAs": [],
            },
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "SwarmLead AI",
                "url": self.base_url,
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": f"{self.base_url}/?q={{search_term_string}}",
                    "query-input": "required name=search_term_string",
                },
            },
        ]
        return json.dumps(schema, indent=2)

    @staticmethod
    def build_page_json_ld(page: Dict[str, Any]) -> str:
        """JSON-LD for a single programmatic page from its schema spec."""
        schema = page.get("schema") or {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page.get("title", ""),
            "description": page.get("description", ""),
        }
        schema.setdefault("@context", "https://schema.org")
        return json.dumps(schema)


seo_engine = SEOEngine()

__all__ = ["SEOEngine", "seo_engine", "STATIC_URLS", "DEFAULT_BASE_URL"]