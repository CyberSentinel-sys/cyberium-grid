"""OrHaShield Control Plane — FastAPI application entry point."""
from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from orhashield_cp.routers import actions, alerts, assets, compliance
from orhashield_cp.ws.realtime import websocket_router

log = structlog.get_logger(__name__)

app = FastAPI(
    title="OrHaShield Control Plane",
    description="AI-native SCADA/ICS/OT security platform — control plane API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://dashboard:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(assets.router, prefix="/api/v1", tags=["assets"])
app.include_router(actions.router, prefix="/api/v1", tags=["actions"])
app.include_router(compliance.router, prefix="/api/v1", tags=["compliance"])
app.include_router(websocket_router, prefix="/ws", tags=["realtime"])


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    """Health check endpoint for load balancer and Kubernetes probes."""
    return {"status": "ok", "version": "0.1.0"}


@app.on_event("startup")
async def startup() -> None:
    log.info("OrHaShield Control Plane started")


@app.on_event("shutdown")
async def shutdown() -> None:
    log.info("OrHaShield Control Plane shutting down")
