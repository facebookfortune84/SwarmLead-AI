"""Tests for the acquisition lead-magnet API."""

import pytest

from interfaces.api.routers.acquisition import SkeletonRequest, business_skeleton


@pytest.mark.asyncio
async def test_skeleton_generates_manifest():
    result = await business_skeleton(
        SkeletonRequest(idea="An AI coach for real estate agents", email="skeleton@test.com")
    )
    assert result["manifest"]["status"] == "manifest_ready"
    assert "skeleton" in result["manifest"]
    assert result["manifest"]["skeleton"]["project_slug"]


@pytest.mark.asyncio
async def test_skeleton_no_email_still_returns_manifest():
    result = await business_skeleton(SkeletonRequest(idea="A newsletter tool"))
    assert result["manifest"]["skeleton"]["reversible"] is True
