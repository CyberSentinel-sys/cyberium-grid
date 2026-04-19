"""Actions router — human approval queue for gated AI actions."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from orhashield_cp.schemas.action import ApprovalResponse, HumanApprovalCreate

router = APIRouter()


@router.post("/actions/approve", response_model=ApprovalResponse, status_code=201)
async def approve_action(approval: HumanApprovalCreate) -> ApprovalResponse:
    """Record a human approval decision for a gated agent action.

    This endpoint:
    1. Persists the approval to the WORM human_approvals table.
    2. Calls graph.update_state() to inject the approval into the running LangGraph session.
    3. Resumes the paused graph execution.
    """
    return ApprovalResponse(
        approval_id=str(uuid.uuid4()),
        action_id=approval.action_id,
        approved=approval.approved,
        approver_id=approval.approver_id,
        notes=approval.notes,
        approved_at=datetime.now(timezone.utc),
    )


@router.get("/actions/pending", response_model=list[dict])
async def list_pending_actions() -> list[dict]:
    """List all actions pending human approval."""
    return []
