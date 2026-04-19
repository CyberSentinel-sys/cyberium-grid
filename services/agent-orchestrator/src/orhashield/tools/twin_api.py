"""Digital twin API client."""
from __future__ import annotations

import os
from typing import Any

import httpx
import structlog

log = structlog.get_logger(__name__)

TWIN_API_URL = os.getenv("TWIN_API_URL", "http://digital-twin:8080")


async def simulate(action_dict: dict[str, Any]) -> dict[str, Any]:
    """Call the digital twin API to simulate an action.

    Returns: {"safe": bool|None, "reason": str}
    safe=None means the twin was unavailable — caller should escalate.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{TWIN_API_URL}/simulate", json=action_dict)
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]
    except Exception as exc:
        log.warning("twin_api_unavailable", error=str(exc))
        return {"safe": None, "reason": f"Twin API unavailable: {exc}"}
