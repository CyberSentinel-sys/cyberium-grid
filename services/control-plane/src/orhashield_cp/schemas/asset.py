from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class PurdueLevel(int, Enum):
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_3_5 = 4
    LEVEL_4 = 5


class AssetCreate(BaseModel):
    ip_address: str
    mac_address: str | None = None
    vendor: str | None = None
    model: str | None = None
    purdue_level: PurdueLevel = PurdueLevel.LEVEL_3
    protocols: list[str] = []
    criticality: str = "medium"
    hostname: str | None = None


class AssetResponse(BaseModel):
    asset_id: str
    ip_address: str
    mac_address: str | None
    vendor: str | None
    model: str | None
    purdue_level: PurdueLevel
    protocols: list[str]
    criticality: str
    created_at: datetime

    model_config = {"from_attributes": True}
