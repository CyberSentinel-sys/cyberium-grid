"""NATS consumer and publisher tools for the agent orchestrator."""
from __future__ import annotations

import json
import os
from typing import Any

import nats
import structlog

from orhashield.agents.state import ActionRequest

log = structlog.get_logger(__name__)

_nc: Any = None  # Global NATS connection (lazy-initialized).


async def get_nats() -> Any:
    global _nc
    if _nc is None or not _nc.is_connected:
        url = os.getenv("NATS_URL", "nats://localhost:4222")
        user = os.getenv("NATS_USER", "")
        password = os.getenv("NATS_PASSWORD", "")
        opts: dict[str, Any] = {}
        if user and password:
            opts["user"] = user
            opts["password"] = password
        _nc = await nats.connect(url, **opts)
        log.info("nats_connected", url=url)
    return _nc


async def publish_approved_action(action: ActionRequest) -> None:
    """Publish an approved ActionRequest to NATS for the safety gate."""
    nc = await get_nats()
    js = await nc.jetstream()
    payload = action.model_dump_json().encode()
    await js.publish("ot.actions.proposed", payload)
    log.info("published_proposed_action", action_id=action.action_id)


async def subscribe_ot_events(subject: str, handler: Any) -> None:
    """Subscribe to OT events from the DPI sensor via NATS JetStream."""
    nc = await get_nats()
    js = await nc.jetstream()
    await js.subscribe(subject, cb=handler, durable="agent-orchestrator")
    log.info("subscribed", subject=subject)
