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

router = APIRouter(tags=["SEO"])


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml():
    return Response(
        content=seo_engine.build_sitemap(),
        media_type="application/xml",
    )


@router.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    return PlainTextResponse(seo_engine.build_robots())


@router.get("/api/seo/jsonld")
async def jsonld():
    return Response(content=seo_engine.build_json_ld(), media_type="application/ld+json")


@router.get("/api/seo/pages")
async def pages():
    inventory = seo_engine.page_inventory()
    return {"count": len(inventory), "pages": inventory}


@router.get("/api/seo/pages/{page_url:path}")
async def page_jsonld(page_url: str):
    base_url = os.getenv("SEO_BASE_URL", seo_engine.base_url).rstrip("/")
    full = page_url if page_url.startswith(("http://", "https://")) else f"{base_url}{page_url}"
    for page in seo_engine.seo_pages():
        if page["url"] == full or page["url"].endswith(page_url):
            return Response(
                content=seo_engine.build_page_json_ld(page),
                media_type="application/ld+json",
            )
    raise HTTPException(status_code=404, detail="Page not found")
