"""
Company Builder API.

Endpoints for building complete, provisionable company packages using
the Genesis agent swarm:
- POST /api/company/build         -> build a company from a description
- GET  /api/company/{company_id}  -> get build status + package
- GET  /api/company/{company_id}/download -> download the ZIP artifact
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.services.company_builder import company_builder
from core.storage.file_manager import FileManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/company", tags=["Company"])


class BuildRequest(BaseModel):
    business_name: str
    business_description: str
    founder_goal: Optional[str] = None


@router.post("/build")
async def build_company(payload: BuildRequest):
    """Build a complete company package with the agent swarm."""
    try:
        result = await company_builder.build_company(
            payload.business_name,
            payload.business_description,
            payload.founder_goal,
        )
        return result
    except Exception as exc:
        logger.exception("Company build failed")
        raise HTTPException(status_code=500, detail=f"Company build failed: {exc}")


@router.get("/{company_id}")
async def get_company_build(company_id: str):
    """Get the build result for a company."""
    fm = FileManager()
    exists = fm.company_exists(company_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Company build not found")
    return {
        "company_id": company_id,
        "status": "built",
        "download_url": f"/api/company/{company_id}/download",
        "exists": True,
    }


@router.get("/{company_id}/download")
async def download_company_build(company_id: str):
    """Download the company package ZIP artifact."""
    fm = FileManager()
    if not fm.company_exists(company_id):
        raise HTTPException(status_code=404, detail="Company build not found")

    import os
    import tempfile

    from fastapi.responses import FileResponse

    tmp_dir = tempfile.mkdtemp(prefix="genesis_company_")
    download_path = os.path.join(tmp_dir, f"{company_id}-company-package.zip")
    ok = fm.retrieve_company(company_id, download_path)
    if not ok:
        raise HTTPException(status_code=500, detail="Company artifact unavailable")

    return FileResponse(
        download_path,
        media_type="application/zip",
        filename=f"{company_id}-company-package.zip",
    )
