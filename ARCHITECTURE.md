# OrHaShield — Architecture

## System Context

OrHaShield is an AI-native SCADA/ICS/OT protection platform. It monitors every device in an OT network passively (and optionally actively), correlates events using a multi-agent LangGraph graph, gates every proposed response action through a deterministic Rust safety gate, and surfaces actionable intelligence through a real-time dashboard.

```
┌─────────────────────────────────────────────────────────────┐
│                    OT NETWORK (Purdue L0-L3)                │
│  PLCs · RTUs · HMIs · IEDs · Historians · Eng Workstations  │
└────────────────────────────┬────────────────────────────────┘
                             │  Mirrored traffic (SPAN/TAP)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│               SENSOR PLANE  (sensors/dpi-engine)             │
│  Go · gopacket · AF_XDP(≥4.18)/libpcap fallback             │
│  Parsers: Modbus · DNP3 · EtherNet/IP · BACnet · ...        │
│  Passive fingerprinting → Asset inventory                    │
└────────────────────────────┬────────────────────────────────┘
                             │  OTEvent protobuf → NATS JetStream
                             │  Subject: ot.events.{protocol}.{sensor_id}
                             ▼
┌─────────────────────────────────────────────────────────────┐
│           AGENT ORCHESTRATOR  (services/agent-orchestrator)  │
│  Python 3.11 · LangGraph StateGraph · Anthropic Claude API   │
│                                                              │
│  Supervisor → ProtocolExpert → HypothesisGenerator          │
│            → TwinVerifier → ResponsePlanner                  │
│            → HumanGate [INTERRUPT] → Critic → Supervisor    │
│                                                              │
│  State: OTState (Pydantic) · Checkpoint: Postgres            │
│  Tracing: LangSmith · Workflows: Temporal                    │
└──────────┬──────────────────────────────┬───────────────────┘
           │ ot.actions.proposed          │ ot.alerts.{severity}
           ▼                              ▼
┌──────────────────────┐     ┌───────────────────────────────┐
│  SAFETY GATE          │     │  CONTROL PLANE                 │
│  (services/safety-gate)│    │  (services/control-plane)      │
│  Rust · tokio         │     │  Python · FastAPI · Pydantic   │
│  regorus (Rego/OPA)   │     │                               │
│  Purdue action matrix │     │  REST API + WebSocket          │
│  Property-tested      │     │  JWT + API-key auth            │
│  Formal: Kani harness │     │  Human approval queue          │
└──────┬───────────────┘     └──────────────┬────────────────┘
       │ ot.actions.approved/denied/escalate │
       └──────────────────────┬─────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  DASHBOARD                 │
              │  (ui/dashboard)            │
              │  Next.js 14 · TypeScript   │
              │  Tailwind · shadcn/ui      │
              │  react-flow asset graph    │
              │  Real-time WebSocket feed  │
              │  Human approval queue UI   │
              └───────────────────────────┘
```

## Data Flow

1. **Capture**: DPI engine captures OT traffic via SPAN/TAP. AF_XDP for kernel bypass (Linux ≥4.18); libpcap fallback for older kernels and VMs.
2. **Parse**: Protocol parsers decode Modbus/DNP3/EtherNet-IP/BACnet packets into canonical `OTEvent` protobufs.
3. **Emit**: Events published to NATS JetStream `ot.events.{protocol}.{sensor_id}`.
4. **Detect**: Agent orchestrator consumes events, runs anomaly detection, generates hypotheses using Claude claude-sonnet-4-6.
5. **Verify**: `TwinVerifier` node simulates every proposed action in the digital twin sandbox before forwarding.
6. **Gate**: `HumanGate` node interrupts the LangGraph for human approval of gated actions. On approval, `ActionRequest` is published to `ot.actions.proposed`.
7. **Policy**: Rust safety gate evaluates every action against OPA/Rego policy. Outputs to `ot.actions.approved`, `ot.actions.denied`, or `ot.actions.escalate`.
8. **Execute** (Phase 2+): Response executor calls firewall/NAC/SRA APIs for approved actions.
9. **Audit**: Every decision written to WORM `agent_decisions` table. No DELETE/UPDATE ever.
10. **Dashboard**: Control plane fans NATS events to dashboard via WebSocket.

## Service Mesh (Docker Compose — Development)

```
┌────────────────────────────────────────────────────────────┐
│  Docker bridge network: orhashield_net                      │
│                                                            │
│  nats:4222          postgres:5432      clickhouse:9000      │
│  qdrant:6333        neo4j:7687         (all data services)  │
│                                                            │
│  dpi-engine         agent-orchestrator  safety-gate         │
│  control-plane:8000 dashboard:3000                          │
└────────────────────────────────────────────────────────────┘
```

dpi-engine runs with `network_mode: host` and `CAP_NET_RAW` to access raw sockets. All other services on the bridge network.

## Purdue Model Network Segmentation (Production)

| Component | Purdue Level | Network Zone | Connectivity |
|---|---|---|---|
| dpi-engine | Level 3 / DMZ | OT-DMZ | SPAN port in, NATS out |
| agent-orchestrator | Level 3.5 / DMZ | Security DMZ | NATS in/out, DB, LLM API |
| safety-gate | Level 3.5 / DMZ | Security DMZ | NATS in/out, DB |
| control-plane | Level 4 | IT Network | NATS in, DB, WebSocket out |
| dashboard | Level 4 | IT Network | HTTPS/WSS in, REST out |

## LLM Serving Strategy

| Deployment Mode | LLM Backend | Notes |
|---|---|---|
| Cloud tier | Anthropic API (`claude-sonnet-4-6`, `claude-haiku-4-5-20251001`) | Requires internet egress |
| On-prem / air-gap | Ollama + vLLM (local model) | Zero egress; reduced capability |
| Edge (Phase 4+) | ONNX quantized models (Hailo/NVIDIA Jetson) | Anomaly scoring only |

The `ANTHROPIC_API_KEY` env var being unset switches the orchestrator to the local Ollama backend automatically.

## Secret Management

- **Development**: `.env` file, never committed (`.gitignore` entry required)
- **Production**: HashiCorp Vault sidecar injection; secrets mounted as environment variables at container start
- **Required secrets**: See `.env.example` at repo root

## NATS Subject Hierarchy

```
ot.events.modbus.{sensor_id}     # Raw Modbus events from DPI
ot.events.dnp3.{sensor_id}       # Raw DNP3 events
ot.events.enip.{sensor_id}       # EtherNet/IP events
ot.events.bacnet.{sensor_id}     # BACnet events
ot.alerts.info                   # Processed info alerts
ot.alerts.low
ot.alerts.medium
ot.alerts.high
ot.alerts.critical
ot.actions.proposed              # Agent-proposed actions → safety gate
ot.actions.approved              # Gate-approved → response executor
ot.actions.denied                # Gate-denied → audit
ot.actions.escalate              # Requires elevated human review
ot.audit                         # WORM append-only audit stream
```

## Key Architectural Decisions

See `docs/adr/` for full ADR documents.

| ADR | Decision |
|---|---|
| 0001 | LangGraph as agent orchestration framework |
| 0002 | Rust + regorus for safety gate (memory safety + embedded Rego) |
| 0003 | Go for DPI sensor (performance + gopacket ecosystem) |
| 0004 | Physics-informed ML for anomaly detection (reduces false positives) |

## Phase Roadmap

| Phase | Timeline | Key Deliverables |
|---|---|---|
| 0 | Week 1 | Foundation docs, CI/CD, directory scaffold |
| 1 | Months 1-3 | MVP: DPI sensor, LangGraph agents, safety gate, control plane, dashboard |
| 2 | Months 4-6 | OPC UA + S7 parsers, full response automation, compliance module |
| 3 | Months 7-9 | OrHaShield Sentinel (autonomous red team), digital twin, IEC 61850 |
| 4 | Months 10-12 | Federated learning, edge appliance, firmware integrity |
| 5 | Year 2 | Medical OT, EV/DER, maritime, rail, MSSP multi-tenant |
