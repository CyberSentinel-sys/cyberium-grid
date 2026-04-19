"""Threat intelligence node — enriches alerts with CVE and threat actor context via RAG."""
from __future__ import annotations

from typing import Any

import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import Asset, OTState

log = structlog.get_logger(__name__)


async def threat_intel_node(state: OTState, config: RunnableConfig) -> dict[str, Any]:
    """Enrich the current alert with CVE and threat-intel context from Qdrant RAG."""
    if not state.alerts:
        return {}

    alert = state.alerts[0] if not state.current_alert_id else next(
        (a for a in state.alerts if a.alert_id == state.current_alert_id), state.alerts[0]
    )

    asset = next((a for a in state.assets if a.asset_id == alert.asset_id), None)

    # Query Qdrant for relevant CVEs and threat actor TTPs.
    intel = await _query_threat_intel(alert.description, asset)

    if intel:
        log.info("threat_intel_enriched", alert_id=alert.alert_id, intel_hits=len(intel))
        enriched_description = alert.description + "\n\nThreat Intel Context:\n" + "\n".join(intel)
        updated_alerts = [
            a.model_copy(update={"description": enriched_description}) if a.alert_id == alert.alert_id else a
            for a in state.alerts
        ]
        return {"alerts": updated_alerts}

    return {}


async def _query_threat_intel(description: str, asset: Asset | None) -> list[str]:
    """Query Qdrant vector DB for relevant threat intelligence.

    In Phase 1 this returns static context for known high-profile TTPs.
    Phase 2: real Qdrant RAG over CISA advisories, Dragos YIR, vendor bulletins.
    """
    intel: list[str] = []

    desc_lower = description.lower()

    # Static TTP context for top OT threats (Phase 1 — replaced with Qdrant in Phase 2).
    if "modbus" in desc_lower and "write" in desc_lower:
        intel.append("FrostyGoop TTP: Modbus TCP writes to ENCO controller heating setpoints (Jan 2024, Lviv)")
        intel.append("CyberAv3ngers TTP: Unitronics Vision PLCs targeted via TCP/20256 with default creds")

    if "dnp3" in desc_lower and ("broadcast" in desc_lower or "direct operate" in desc_lower):
        intel.append("TRISIS/TRITON precedent: DNP3 direct-operate commands used to disable SIS")

    if "enumerate" in desc_lower or "scan" in desc_lower:
        intel.append("VOLTZITE TTP: Device enumeration preceding long-term OT persistence campaigns (300+ day dwell)")

    if asset and asset.vendor:
        vendor_lower = asset.vendor.lower()
        if "unitronics" in vendor_lower:
            intel.append("CISA AA23-335A: CyberAv3ngers specifically targeted Unitronics Vision Series PLCs")
        if "rockwell" in vendor_lower or "allen-bradley" in vendor_lower:
            intel.append("PIPEDREAM/INCONTROLLER: Modbus + CIP modules targeting Rockwell PLCs confirmed")
        if "schneider" in vendor_lower:
            intel.append("PIPEDREAM/INCONTROLLER: OPC UA + Modbus modules targeting Schneider M340/M580 confirmed")

    return intel
