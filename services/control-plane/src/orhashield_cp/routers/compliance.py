"""Compliance router — regulatory framework status and evidence export."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/compliance/status")
async def compliance_status() -> dict:
    """Get current compliance posture across all supported frameworks."""
    return {
        "frameworks": {
            "nerc_cip_015": {"status": "partial", "coverage_pct": 60, "last_assessed": None},
            "iec_62443_3_3": {"status": "partial", "coverage_pct": 50, "last_assessed": None},
            "nis2": {"status": "partial", "coverage_pct": 40, "last_assessed": None},
            "epa_water": {"status": "partial", "coverage_pct": 70, "last_assessed": None},
        },
        "note": "Phase 1 coverage — see docs/compliance-mapping.md for full roadmap",
    }


@router.get("/compliance/export/{framework}")
async def export_compliance(framework: str) -> dict:
    """Generate a compliance evidence export for the specified framework."""
    return {
        "framework": framework,
        "status": "not_yet_implemented",
        "available_in": "Phase 2",
    }
