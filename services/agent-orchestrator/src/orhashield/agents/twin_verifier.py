"""Twin verifier node — simulates proposed actions in the digital twin sandbox."""
from __future__ import annotations

from typing import Any

import httpx
import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import ActionClass, ActionRequest, OTState

log = structlog.get_logger(__name__)

TWIN_API_URL = "http://digital-twin:8080"  # Override via TWIN_API_URL env var.


async def twin_verifier_node(state: OTState, config: RunnableConfig) -> dict[str, Any]:
    """Simulate each queued action in the digital twin before allowing it to proceed."""
    import os

    twin_url = os.getenv("TWIN_API_URL", TWIN_API_URL)
    verified: list[ActionRequest] = []

    for action in state.actions_queue:
        if action.twin_verified:
            verified.append(action)
            continue

        if action.action_class in (ActionClass.OBSERVE, ActionClass.ALERT):
            # Read-only actions need no twin simulation.
            verified.append(action.model_copy(update={"twin_verified": True}))
            continue

        result = await _simulate(twin_url, action)
        if result["safe"]:
            verified.append(action.model_copy(update={"twin_verified": True}))
            log.info("twin_verified_safe", action_id=action.action_id)
        else:
            log.warning(
                "twin_simulation_unsafe",
                action_id=action.action_id,
                reason=result.get("reason", "unknown"),
            )
            # Keep in queue but mark requires_human=True with twin failure note.
            updated = action.model_copy(update={
                "twin_verified": False,
                "requires_human": True,
                "description": action.description + f"\n[TWIN SIMULATION UNSAFE: {result.get('reason', '')}]",
            })
            verified.append(updated)

    return {"actions_queue": verified}


async def _simulate(twin_url: str, action: ActionRequest) -> dict[str, Any]:
    """Call the digital twin API to simulate an action."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{twin_url}/simulate",
                json={
                    "action_id": action.action_id,
                    "action_class": action.action_class.value,
                    "asset_id": action.asset_id,
                    "parameters": action.parameters,
                },
            )
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]
    except Exception as exc:
        log.warning("twin_api_unavailable", error=str(exc))
        # When twin is unavailable, return safe=None which triggers escalation.
        return {"safe": None, "reason": f"Twin API unavailable: {exc}"}
