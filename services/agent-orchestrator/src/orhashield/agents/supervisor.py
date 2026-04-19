"""Supervisor node — routes the LangGraph to the appropriate next node."""
from __future__ import annotations

import structlog
from langchain_core.runnables import RunnableConfig

from orhashield.agents.state import OTState

log = structlog.get_logger(__name__)


def route_from_supervisor(state: OTState) -> str:
    """Determine which node the supervisor should route to next."""
    from langgraph.graph import END

    if state.halt or state.error:
        return END

    if state.iteration_count >= state.max_iterations:
        log.warning("circuit_breaker_fired", iterations=state.iteration_count)
        return END

    # Need more threat intel before hypothesis generation.
    if not state.assets and state.alerts:
        return "threat_intel"

    # Have alerts but no hypotheses yet — run protocol expert + hypothesis generation.
    if state.alerts and not state.hypotheses:
        return "protocol_expert"

    # Have hypotheses but no actions — plan a response.
    if state.hypotheses and not state.actions_queue:
        return "response_planner"

    # Have actions queued waiting for twin verification — verify them.
    if state.actions_queue and not all(a.twin_verified or a.action_class.value in ("observe", "alert") for a in state.actions_queue):
        return "twin_verifier"

    # Have verified actions waiting for human gate.
    if state.actions_queue and any(a.requires_human for a in state.actions_queue):
        return "human_gate"

    # Critic feedback available — run another iteration.
    if state.critic_feedback and state.iteration_count < state.max_iterations:
        return "hypothesis_generator"

    return END


async def supervisor_node(state: OTState, config: RunnableConfig) -> dict:  # type: ignore[type-arg]
    """Supervisor node: logs the current routing decision and increments iteration count."""
    next_node = route_from_supervisor(state)
    log.info(
        "supervisor_routing",
        session_id=state.session_id,
        iteration=state.iteration_count,
        next_node=next_node,
        alert_count=len(state.alerts),
        hypothesis_count=len(state.hypotheses),
        action_count=len(state.actions_queue),
    )
    return {"iteration_count": state.iteration_count + 1}
