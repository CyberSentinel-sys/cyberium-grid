"""Human gate node — handles human approval of gated actions.

This node is interrupted by LangGraph before execution (via interrupt_before=["human_gate"]).
The graph is resumed by the control-plane POST /api/v1/actions/approve endpoint,
which calls graph.update_state() to inject the HumanApproval records.
"""
from __future__ import annotations

from typing import Any

import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import ActionRequest, OTState

log = structlog.get_logger(__name__)


async def human_gate_node(state: OTState, config: RunnableConfig) -> dict[str, Any]:
    """Process human approval decisions for queued actions.

    When this node executes (after interrupt is resumed), human_approvals contains
    the operator's decisions. Route approved actions to NATS; record denials.
    """
    from orhashield.tools.nats_consumer import publish_approved_action

    pending = [a for a in state.actions_queue if a.requires_human]
    approved: list[ActionRequest] = list(state.approved_actions)
    denied: list[ActionRequest] = list(state.denied_actions)

    for action in pending:
        approval = next(
            (ap for ap in state.human_approvals if ap.action_id == action.action_id),
            None,
        )

        if approval is None:
            # Should not happen after interrupt is properly resumed; halt for safety.
            log.error("missing_human_approval", action_id=action.action_id)
            return {
                "halt": True,
                "error": f"Human gate: missing approval for action {action.action_id}",
            }

        if approval.approved:
            try:
                await publish_approved_action(action)
                approved.append(action)
                log.info(
                    "action_approved",
                    action_id=action.action_id,
                    approver=approval.approver_id,
                    action_class=action.action_class.value,
                )
            except Exception as exc:
                log.error("publish_approved_action_failed", action_id=action.action_id, error=str(exc))
                # Don't halt — record as denied with error note.
                denied.append(action)
        else:
            denied.append(action)
            log.info(
                "action_denied",
                action_id=action.action_id,
                approver=approval.approver_id,
                notes=approval.notes,
            )

    return {
        "approved_actions": approved,
        "denied_actions": denied,
    }
