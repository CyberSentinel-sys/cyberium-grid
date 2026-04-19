"""Real-time WebSocket endpoint — fans NATS events to connected dashboard clients."""
from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

log = structlog.get_logger(__name__)

websocket_router = APIRouter()

# In-memory connection registry (replaced with Redis pub/sub in Phase 2 multi-instance).
_connections: set[WebSocket] = set()


@websocket_router.websocket("/realtime")
async def realtime_ws(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time OT event streaming to the dashboard."""
    await websocket.accept()
    _connections.add(websocket)
    log.info("ws_client_connected", total_connections=len(_connections))

    try:
        # Send connection confirmation.
        await websocket.send_json({"type": "connected", "message": "OrHaShield real-time stream active"})

        # Heartbeat loop — keep connection alive.
        while True:
            try:
                # Wait for client message or send heartbeat every 30s.
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back any ping messages.
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        log.info("ws_client_disconnected")
    finally:
        _connections.discard(websocket)


async def broadcast(event: dict[str, Any]) -> None:
    """Broadcast an event to all connected WebSocket clients."""
    if not _connections:
        return
    dead: set[WebSocket] = set()
    payload = json.dumps(event)
    for ws in _connections:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    _connections.difference_update(dead)
