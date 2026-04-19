"""OrHaShield Blue-Team LangGraph — assembles the full multi-agent detection graph."""
from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from orhashield.agents.critic import critic_node
from orhashield.agents.human_gate import human_gate_node
from orhashield.agents.hypothesis_generator import hypothesis_generator_node
from orhashield.agents.protocol_expert import protocol_expert_node
from orhashield.agents.response_planner import response_planner_node
from orhashield.agents.state import OTState
from orhashield.agents.supervisor import route_from_supervisor, supervisor_node
from orhashield.agents.threat_intel import threat_intel_node
from orhashield.agents.twin_verifier import twin_verifier_node


def build_graph(checkpointer: object | None = None) -> CompiledStateGraph:
    """Assemble and compile the OrHaShield Blue-Team LangGraph.

    Node execution order (conditional on state):
      supervisor → threat_intel → supervisor
      supervisor → protocol_expert → hypothesis_generator → twin_verifier → response_planner → human_gate → critic → supervisor
      supervisor → END (on halt, error, or max iterations)

    interrupt_before=["human_gate"] causes the graph to pause before the human gate node,
    allowing the control-plane to inject HumanApproval records before resuming.
    """
    builder: StateGraph = StateGraph(OTState)  # type: ignore[type-arg]

    # Register all nodes.
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("threat_intel", threat_intel_node)
    builder.add_node("protocol_expert", protocol_expert_node)
    builder.add_node("hypothesis_generator", hypothesis_generator_node)
    builder.add_node("twin_verifier", twin_verifier_node)
    builder.add_node("response_planner", response_planner_node)
    builder.add_node("human_gate", human_gate_node)
    builder.add_node("critic", critic_node)

    # Entry point.
    builder.set_entry_point("supervisor")

    # Supervisor routes conditionally.
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "threat_intel": "threat_intel",
            "protocol_expert": "protocol_expert",
            "response_planner": "response_planner",
            "twin_verifier": "twin_verifier",
            "human_gate": "human_gate",
            "hypothesis_generator": "hypothesis_generator",
            END: END,
        },
    )

    # Linear edges for the main detection pipeline.
    builder.add_edge("threat_intel", "supervisor")
    builder.add_edge("protocol_expert", "hypothesis_generator")
    builder.add_edge("hypothesis_generator", "twin_verifier")
    builder.add_edge("twin_verifier", "response_planner")
    builder.add_edge("response_planner", "human_gate")
    builder.add_edge("human_gate", "critic")
    builder.add_edge("critic", "supervisor")

    compile_kwargs: dict[str, object] = {
        "interrupt_before": ["human_gate"],  # Pause for human approval.
    }
    if checkpointer is not None:
        compile_kwargs["checkpointer"] = checkpointer

    return builder.compile(**compile_kwargs)
