"""Assets router — OT device inventory management."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from orhashield_cp.schemas.asset import AssetCreate, AssetResponse, PurdueLevel

router = APIRouter()


@router.post("/assets", response_model=AssetResponse, status_code=201)
async def register_asset(asset: AssetCreate) -> AssetResponse:
    """Register a new OT asset in the inventory."""
    return AssetResponse(
        asset_id=str(uuid.uuid4()),
        ip_address=asset.ip_address,
        mac_address=asset.mac_address,
        vendor=asset.vendor,
        model=asset.model,
        purdue_level=asset.purdue_level,
        protocols=asset.protocols,
        criticality=asset.criticality,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/assets", response_model=list[AssetResponse])
async def list_assets(
    purdue_level: PurdueLevel | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AssetResponse]:
    """List OT assets with optional Purdue level filter."""
    return []


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str) -> AssetResponse:
    """Get a specific OT asset by ID."""
    raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
