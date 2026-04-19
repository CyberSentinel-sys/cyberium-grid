"""Alerts router — ingest and query security alerts."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from orhashield_cp.schemas.alert import AlertCreate, AlertResponse, SeverityEnum

router = APIRouter()


@router.post("/alerts", response_model=AlertResponse, status_code=201)
async def ingest_alert(alert: AlertCreate) -> AlertResponse:
    """Ingest a new security alert from the DPI sensor or agent orchestrator."""
    return AlertResponse(
        alert_id=str(uuid.uuid4()),
        asset_id=alert.asset_id,
        severity=alert.severity,
        description=alert.description,
        raw_event_id=alert.raw_event_id,
        rule_id=alert.rule_id,
        mitre_technique=alert.mitre_technique,
        acknowledged=False,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(
    severity: SeverityEnum | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[AlertResponse]:
    """List security alerts with optional severity filter."""
    return []


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(alert_id: str) -> AlertResponse:
    """Acknowledge an alert to remove it from the active queue."""
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
