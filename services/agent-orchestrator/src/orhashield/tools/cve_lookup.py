"""CVE and vulnerability lookup tool using Qdrant RAG."""
from __future__ import annotations

import os
from typing import Any

import structlog

log = structlog.get_logger(__name__)


async def lookup_cves(vendor: str | None, model: str | None, protocol: str | None = None) -> list[dict[str, Any]]:
    """Look up relevant CVEs from the Qdrant vector database.

    Phase 1: returns static high-signal CVEs for known vendors.
    Phase 2: real Qdrant semantic search over NVD + CISA ICS advisories.
    """
    results: list[dict[str, Any]] = []

    if not vendor and not model and not protocol:
        return results

    key = (vendor or "").lower()

    # Static high-signal CVE database for MVP (Phase 1).
    static_cves: dict[str, list[dict[str, Any]]] = {
        "unitronics": [
            {"cve_id": "CVE-2023-6448", "cvss": 9.8, "description": "Unitronics Vision PLCs exposed on TCP/20256 with default password '1111' — exploited by CyberAv3ngers (IRGC-CEC) Nov 2023"},
        ],
        "siemens": [
            {"cve_id": "CVE-2022-38773", "cvss": 8.4, "description": "Siemens SIPROTEC 5 devices: unauthenticated access to engineering interface"},
            {"cve_id": "CVE-2023-44317", "cvss": 9.3, "description": "Siemens SIMATIC S7-1500: OPC UA stack vulnerability allowing remote code execution"},
        ],
        "rockwell": [
            {"cve_id": "CVE-2012-6435", "cvss": 10.0, "description": "Rockwell ControlLogix 1756-ENxT: unauthenticated ENIP commands allow PLC stop — still unpatched in many deployments"},
            {"cve_id": "CVE-2022-1159", "cvss": 7.7, "description": "Rockwell Studio 5000: DLL hijacking during project file open"},
        ],
        "schneider": [
            {"cve_id": "CVE-2022-37301", "cvss": 9.8, "description": "Schneider Electric Modicon M340: authentication bypass in UMAS protocol"},
        ],
    }

    for key_part in [vendor, model]:
        if not key_part:
            continue
        for vendor_key, cves in static_cves.items():
            if vendor_key in key_part.lower():
                results.extend(cves)

    return results
