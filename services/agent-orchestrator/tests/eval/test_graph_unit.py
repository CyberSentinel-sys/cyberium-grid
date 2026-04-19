"""Unit tests for LangGraph agent nodes using mocked LLM responses."""
from __future__ import annotations

import json
import uuid

import pytest

from orhashield.agents.state import (
    ActionClass,
    Alert,
    Asset,
    Hypothesis,
    OTState,
    PurdueLevel,
    Severity,
)
from orhashield.agents.supervisor import route_from_supervisor
from orhashield.agents.response_planner import _requires_human


class TestSupervisorRouting:
    def test_routes_to_threat_intel_when_no_assets(self) -> None:
        state = OTState(
            session_id=str(uuid.uuid4()),
            site_id="test",
            alerts=[_make_alert()],
        )
        assert route_from_supervisor(state) == "threat_intel"

    def test_routes_to_protocol_expert_when_alerts_no_hypotheses(self) -> None:
        state = OTState(
            session_id=str(uuid.uuid4()),
            site_id="test",
            assets=[_make_asset()],
            alerts=[_make_alert()],
        )
        assert route_from_supervisor(state) == "protocol_expert"

    def test_routes_to_end_on_halt(self) -> None:
        from langgraph.graph import END
        state = OTState(
            session_id=str(uuid.uuid4()),
            site_id="test",
            halt=True,
        )
        assert route_from_supervisor(state) == END

    def test_circuit_breaker_on_max_iterations(self) -> None:
        from langgraph.graph import END
        state = OTState(
            session_id=str(uuid.uuid4()),
            site_id="test",
            alerts=[_make_alert()],
            iteration_count=5,
            max_iterations=3,
        )
        assert route_from_supervisor(state) == END


class TestRequiresHuman:
    def test_observe_never_requires_human(self) -> None:
        assert _requires_human(ActionClass.OBSERVE, PurdueLevel.LEVEL_1) is False

    def test_alert_never_requires_human(self) -> None:
        assert _requires_human(ActionClass.ALERT, PurdueLevel.LEVEL_0) is False

    def test_isolate_level_2_requires_human(self) -> None:
        assert _requires_human(ActionClass.ISOLATE_NETWORK, PurdueLevel.LEVEL_2) is True

    def test_isolate_dmz_no_human_required(self) -> None:
        assert _requires_human(ActionClass.ISOLATE_NETWORK, PurdueLevel.LEVEL_3_5) is False

    def test_modify_setpoint_always_requires_human(self) -> None:
        for level in PurdueLevel:
            assert _requires_human(ActionClass.MODIFY_SETPOINT, level) is True

    def test_firmware_update_always_requires_human(self) -> None:
        for level in PurdueLevel:
            assert _requires_human(ActionClass.FIRMWARE_UPDATE, level) is True


def _make_alert() -> Alert:
    return Alert(
        alert_id=str(uuid.uuid4()),
        asset_id="asset-001",
        severity=Severity.HIGH,
        description="Test alert",
        raw_event_id=str(uuid.uuid4()),
        timestamp="2026-04-19T12:00:00Z",
    )


def _make_asset() -> Asset:
    return Asset(
        asset_id="asset-001",
        ip_address="192.168.1.1",
        purdue_level=PurdueLevel.LEVEL_2,
    )
