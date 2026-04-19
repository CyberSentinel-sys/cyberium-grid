# ADR 0001 — LangGraph as Agent Orchestration Framework

**Status:** Accepted  
**Date:** 2026-04-19  
**Author:** CyberSentinel Systems Engineering

## Context

OrHaShield requires a multi-agent AI system to coordinate detection, hypothesis generation, twin verification, human approval, and response planning. The system must support:

- Durable state across agent steps (survive restarts without losing in-progress detection sessions)
- Human-in-the-loop interrupts (pause graph execution for human approval, resume on response)
- Reflexion loops (critic node evaluates and re-triggers hypothesis generation)
- Time-travel replay (re-run a historical detection session with updated models)
- Fine-grained tracing of every LLM call, tool invocation, and state transition
- On-prem/air-gap compatibility (no mandatory cloud dependency)

## Decision

Use **LangGraph** (`langchain-ai/langgraph`, MIT license) as the agent orchestration framework with:

- `StateGraph` as the graph type (OTState as the typed state model)
- `AsyncPostgresSaver` (from `langgraph-checkpoint-postgres`) as the checkpointer for durable sessions
- **LangSmith** for tracing in environments with internet egress; disabled in air-gap deployments
- **Temporal** (`temporalio/temporal`) for durable long-running workflows that outlive the agent process (e.g., 30-day threat-hunt missions)

## Alternatives Rejected

| Alternative | Rejection Reason |
|---|---|
| CrewAI | No durable checkpointing; human-in-loop interrupts not native |
| AutoGen (Microsoft) | Tight Azure lock-in; less mature checkpoint/interrupt support |
| Custom FSM (Python) | Too much maintenance burden; re-implementing LangGraph features |
| OpenAI Agents SDK | Proprietary; OpenAI API dependency; no Anthropic-native support |
| PydanticAI | Excellent for single-agent typed I/O but not designed for multi-node graphs |

## Consequences

- LangGraph version must be pinned in `pyproject.toml`; checkpoint API changes between minor versions.
- Postgres must always be available for the checkpointer; the orchestrator has a hard dependency on `asyncpg`.
- LangGraph interrupt semantics require the control plane to call `graph.update_state()` to inject human approval and resume execution.
- Air-gap deployments: set `LANGCHAIN_TRACING_V2=false` to disable LangSmith.

## Version Pin

```
langgraph==0.2.x  # Pin minor version; test before upgrading
langgraph-checkpoint-postgres==0.1.x
```

Review this ADR before any LangGraph major version upgrade.
