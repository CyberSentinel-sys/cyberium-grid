from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SeverityEnum(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertCreate(BaseModel):
    asset_id: str
    severity: SeverityEnum
    description: str
    raw_event_id: str | None = None
    rule_id: str | None = None
    mitre_technique: str | None = None


class AlertResponse(BaseModel):
    alert_id: str
    asset_id: str
    severity: SeverityEnum
    description: str
    raw_event_id: str | None
    rule_id: str | None
    mitre_technique: str | None
    acknowledged: bool
    created_at: datetime

    model_config = {"from_attributes": True}
