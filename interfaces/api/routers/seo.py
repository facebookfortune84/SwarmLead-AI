"""
SEO API — serves the crawler-facing assets.

- /sitemap.xml  (root, for search engines)
- /robots.txt   (root, for search engines)
- /api/seo/jsonld        (landing-page structured data)
- /api/seo/pages         (page inventory from the growth loop)
- /api/seo/pages/{url}   (per-page JSON-LD)
"""

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response

from core.services.seo_engine import seo_engine
from core.site import site_url

router = APIRouter(tags=["SEO"])


def _live_base_url() -> str:
    """Origin for this render: explicit override > current site URL.

    Resolved per request so dynamic tunnel mode (rotating daily URL) is
    always reflected without a rebuild or restart.
    """
    return os.getenv("SEO_BASE_URL") or site_url()


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml():
    return Response(
        content=seo_engine.build_sitemap(base_url=_live_base_url()),
        media_type="application/xml",
    )


@router.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    return PlainTextResponse(seo_engine.build_robots(base_url=_live_base_url()))


@router.get("/api/seo/jsonld")
async def jsonld():
    return Response(
        content=seo_engine.build_json_ld(base_url=_live_base_url()),
        media_type="application/ld+json",
    )


@router.get("/api/seo/pages")
async def pages():
    inventory = seo_engine.page_inventory(base_url=_live_base_url())
    return {"count": len(inventory), "pages": inventory}


@router.get("/api/seo/pages/{page_url:path}")
async def page_jsonld(page_url: str):
    base_url = _live_base_url().rstrip("/")
    full = page_url if page_url.startswith(("http://", "https://")) else f"{base_url}{page_url}"
    for page in seo_engine.seo_pages():
        if page["url"] == full or page["url"].endswith(page_url):
            return Response(
                content=seo_engine.build_page_json_ld(page),
                media_type="application/ld+json",
            )
    raise HTTPException(status_code=404, detail="Page not found")
