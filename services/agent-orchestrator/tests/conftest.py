"""Shared pytest fixtures for the agent orchestrator test suite."""
from __future__ import annotations

import uuid
from typing import AsyncGenerator

import pytest

from orhashield.agents.state import Alert, Asset, OTState, PurdueLevel, Severity


@pytest.fixture
def sample_asset() -> Asset:
    return Asset(
        asset_id=str(uuid.uuid4()),
        ip_address="192.168.10.101",
        vendor="Unitronics",
        model="Vision 430",
        purdue_level=PurdueLevel.LEVEL_1,
        protocols=["modbus_tcp"],
        criticality=Severity.HIGH,
    )


@pytest.fixture
def sample_alert(sample_asset: Asset) -> Alert:
    return Alert(
        alert_id=str(uuid.uuid4()),
        asset_id=sample_asset.asset_id,
        severity=Severity.HIGH,
        description="Modbus write to broadcast unit ID (0xFF) detected on port 502",
        raw_event_id=str(uuid.uuid4()),
        timestamp="2026-04-19T12:00:00Z",
        rule_id="MODBUS-002",
        mitre_technique="T0855",
    )


@pytest.fixture
def initial_state(sample_asset: Asset, sample_alert: Alert) -> OTState:
    return OTState(
        session_id=str(uuid.uuid4()),
        site_id="site-001",
        assets=[sample_asset],
        alerts=[sample_alert],
        current_alert_id=sample_alert.alert_id,
    )
