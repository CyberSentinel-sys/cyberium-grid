"""Protocol expert node — deep protocol-specific anomaly analysis."""
from __future__ import annotations

from typing import Any

import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import Alert, Asset, OTState, Severity

log = structlog.get_logger(__name__)


async def protocol_expert_node(state: OTState, config: RunnableConfig) -> dict[str, Any]:
    """Perform protocol-specific analysis on the current alert to surface additional context."""
    if not state.alerts:
        return {}

    alert = state.alerts[0] if not state.current_alert_id else next(
        (a for a in state.alerts if a.alert_id == state.current_alert_id), state.alerts[0]
    )
    asset = next((a for a in state.assets if a.asset_id == alert.asset_id), None)

    enrichments = _analyze(alert, asset)

    if enrichments:
        updated = alert.model_copy(update={
            "description": alert.description + "\n\nProtocol Analysis:\n" + "\n".join(enrichments)
        })
        return {"alerts": [
            updated if a.alert_id == alert.alert_id else a for a in state.alerts
        ]}

    return {}


def _analyze(alert: Alert, asset: Asset | None) -> list[str]:
    desc = alert.description.lower()
    findings: list[str] = []

    if "modbus-001" in desc or "modbus exception" in desc:
        findings.append("Modbus exception responses may indicate failed unauthorized write attempts or sensor manipulation")

    if "modbus-002" in desc or "broadcast" in desc:
        findings.append("Modbus broadcast writes can affect all devices on segment simultaneously — mass-disruption risk")
        findings.append("FrostyGoop attack used Modbus TCP broadcast writes to disable district heating controllers")

    if "modbus-003" in desc or "diagnostic" in desc:
        findings.append("Modbus diagnostic FC 8 is commonly used for device fingerprinting before targeted attacks")

    if "enip-001" in desc or "cip control" in desc:
        findings.append("CIP Reset/Stop commands can immediately halt PLC execution — critical disruption risk")

    if "dnp3-001" in desc or "dnp3 broadcast" in desc:
        findings.append("DNP3 broadcast direct-operate commands affect all outstation devices on the segment")

    if "bacnet-002" in desc or "bacnet write" in desc:
        findings.append("BACnet WriteProperty can modify setpoints, alarm thresholds, and control logic")

    if "device-enumeration" in desc or "enumerate" in desc:
        findings.append("Device enumeration is the first stage of VOLTZITE-class pre-positioning campaigns")
        findings.append("Monitor for subsequent engineering workstation logins within 24-48 hours post-enumeration")

    if asset and asset.purdue_level.value <= 1:
        findings.append(f"CRITICAL: This asset is at Purdue Level {asset.purdue_level.name} (field device) — any modification has immediate physical consequences")

    return findings
