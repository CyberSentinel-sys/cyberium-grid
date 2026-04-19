# OrHaShield — CLAUDE.md

You are the principal engineer for **OrHaShield**, an AI-native SCADA/ICS/OT protection platform built by CyberSentinel Systems. This file is your operating constitution. Read it before every session.

---

## Project Mission

Build the autonomous AI defender for every SCADA device on earth — from a PLC at a village water plant to an IED in a national grid — with the safety-first, air-gap-respecting, multi-agent brain that incumbent vendors (Claroty, Dragos, Nozomi, Armis) are too afraid to build.

---

## Repository Layout

```
cyberium-grid/
├── CLAUDE.md              ← you are here
├── ARCHITECTURE.md        ← read this next
├── SAFETY.md              ← non-negotiable safety rules
├── docs/
│   ├── adr/               ← Architecture Decision Records
│   ├── threat-model.md
│   ├── purdue-action-matrix.md
│   └── compliance-mapping.md
├── sensors/
│   └── dpi-engine/        ← Go: packet capture + protocol parsing
├── services/
│   ├── agent-orchestrator/ ← Python/LangGraph: multi-agent Blue-Team AI
│   ├── control-plane/      ← Python/FastAPI: REST + WebSocket API
│   ├── safety-gate/        ← Rust: OPA policy engine, action gating
│   ├── response-executor/  ← Rust: firewall/NAC/SRA action executor
│   └── firmware-integrity/ ← Rust: edge-device firmware verification
├── ml/
│   ├── anomaly/            ← autoencoder, LSTM, TCN, physics-informed
│   ├── gnn/                ← asset-relationship graph neural network
│   └── federated/          ← federated learning with secure aggregation
├── digital-twin/
│   ├── grfics-harness/     ← GRFICSv2 + OpenPLC docker compose
│   ├── minicps-scenarios/  ← MiniCPS Python scenarios
│   └── scenarios/          ← attack simulation scripts
├── sentinel/               ← autonomous red-team (RTAI-derived)
├── compliance/
│   ├── iec62443/
│   ├── nerc-cip-015/
│   ├── nis2/
│   ├── epa-water/
│   ├── nca-otcc/
│   └── soci/
├── policy/                 ← OPA Rego bundles
├── infra/
│   ├── docker-compose.yml  ← local dev stack
│   ├── k8s/                ← Kubernetes manifests
│   └── db/                 ← migrations
├── ui/
│   └── dashboard/          ← Next.js 14 + TypeScript + Tailwind
└── .github/
    └── workflows/          ← CI/CD pipelines
```

---

## Hard Rules — Never Violate

### 1. SAFETY FIRST
Any code path that can affect a real OT asset (PLC write, firewall rule, NAC quarantine, SRA session) **must** pass through the Rust `safety-gate` service with OPA policy evaluation. No exceptions. No bypasses. No TODO comments left open.

### 2. Deterministic before probabilistic
When ML model confidence < 0.80 **or** asset Purdue level ≤ 2 **or** asset criticality = `CRITICAL`: fall back to deterministic rules. Never auto-act on low-confidence ML output in safety-critical context.

### 3. Air-gap first
Every component must have a fully functional on-prem / offline mode. Never assume internet connectivity. Cloud features are additive, not required.

### 4. Human-in-the-loop by default (MVP)
Any action that touches a real asset requires explicit human approval in the MVP phase. The `HumanGate` LangGraph node must be in the happy path. Relax per action class only after digital-twin validation + customer sign-off.

### 5. Two-model verification for HIGH severity
Actions classified `severity=HIGH` must be proposed by one LLM and independently verified by a second before entering the safety gate. Use `claude-sonnet-4-6` to propose, `claude-haiku-4-5-20251001` to verify (or swap).

### 6. Digital-twin pre-flight
Every proposed write/execute action must be simulated in the digital twin sandbox before being queued for human approval or autonomous execution. The `TwinVerifier` LangGraph node is mandatory for any `ActionRequest`.

### 7. WORM audit log
Every agent decision, prompt, tool call, and output is written to an append-only audit table. No DELETE or UPDATE on `audit_log`. Use Postgres row-level security if needed. Archive to S3 Glacier equivalent.

### 8. Purdue model awareness
```
Level 0-1 (field devices)   → NEVER autonomous, NEVER agent-touch without explicit human override
Level 2 (control systems)   → human-gated always
Level 3 (site ops)          → policy-gated, twin-verified, high-confidence only
Level 3.5 (DMZ)             → can be automated within tight policy bounds
Level 4-5 (enterprise/cloud)→ standard IT security automation rules apply
```

### 9. No fabricated protocol semantics
When implementing parsers: cite CISA ICSNPP source, vendor documentation, or NIST SP 800-82r3. Do not guess at byte offsets or field meanings. Reference tests against known-good PCAP files.

### 10. Test in twin before integration
No code touches a real OT asset integration test until it passes the digital twin integration suite. Write twin scenarios before writing executor code.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | Python 3.12, LangGraph (MIT), LangSmith tracing |
| LLM (cloud) | Anthropic Claude (`claude-sonnet-4-6`, `claude-haiku-4-5-20251001`) via `anthropic` SDK |
| LLM (on-prem/air-gap) | Ollama + vLLM, ONNX edge inference |
| Sensor / DPI | Go 1.23+, gopacket, AF_XDP, libpcap |
| Safety gate | Rust (edition 2021), tokio, OPA/Rego via regor or opa-wasm |
| Response executor | Rust, async |
| Control plane | Python, FastAPI, Pydantic v2, Alembic |
| Time-series DB | PostgreSQL 16 + TimescaleDB |
| Analytics DB | ClickHouse |
| Asset graph | Neo4j Community or Kuzu |
| Vector DB (RAG) | Qdrant |
| Eventing | NATS JetStream |
| Workflow durability | Temporal |
| Policy engine | OPA/Rego |
| Dashboard | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Container | Docker, Kubernetes (Helm charts) |
| CI/CD | GitHub Actions: lint, unit, integration, twin-integration, SAST (Semgrep), SBOM (Syft), container scan (Trivy) |
| SBOM | Syft + CycloneDX |
| IDS rules | Sigma + Suricata |
| Threat intel | MISP + OpenCTI |
| Endpoint telemetry | OSQuery + Velociraptor extension |

---

## Agent Architecture (LangGraph)

```
Supervisor
├── ProtocolExpertModbus
├── ProtocolExpertDNP3
├── ProtocolExpertOPCUA
├── ProtocolExpertS7
├── ProtocolExpertEtherNetIP
├── ThreatIntel          (CVE/advisory RAG over Qdrant)
├── HypothesisGenerator  (LLM — Claude claude-sonnet-4-6)
├── TwinVerifier         (calls digital-twin API)
├── ResponsePlanner      (generates OT-safe playbook)
├── SafetyGate           (calls Rust safety-gate service)
├── HumanGate            (NATS interrupt + approval)
├── Executor             (calls response-executor via safety-gated RPC)
└── Critic               (Reflexion loop over past decisions)
```

All state: `OTState` Pydantic model. All tool calls: typed with Pydantic. All traces: LangSmith.

---

## Compliance North Stars

- IEC 62443-3-3 (system security requirements)
- IEC 62443-4-1 / 4-2 (product development / component requirements)
- NERC CIP-015 (Internal Network Security Monitoring — INSM)
- NIST SP 800-82r3 (Guide to OT Security)
- NIS2 Directive (EU)
- EPA SDWA §1433 + ERP requirements (US water)
- NCA OTCC-1:2022 (Saudi Arabia)
- Australia SOCI + Cyber Security Act 2024
- Singapore CCoP 2.0
- FDA 524B (medical devices — MedShield AI integration)
- ISO/IEC 42001 (AI management system)
- OWASP Top 10 for Agentic Applications 2026

---

## Protocol Coverage Roadmap

**MVP (Phase 1):** Modbus TCP, DNP3, EtherNet/IP (CIP), BACnet/IP
**Phase 2:** OPC UA, S7Comm/S7Comm+, Profinet IO/CM
**Phase 3:** IEC 61850 (GOOSE/SV/MMS), HART-IP, Foundation Fieldbus H1, PROFIBUS DP
**Phase 4:** Mitsubishi SLMP, Schneider UMAS, Yokogawa Vnet/IP, Emerson DeltaV, ABB 800xA
**Phase 5:** DICOM, HL7, IEEE 11073 (medical OT — MedShield); OCPP/ISO 15118 (EV charging); IEC 61968/61970 (DER)

---

## Key Open-Source Dependencies

- `github.com/cisagov/ICSNPP` — ICS Zeek parsers (baseline for all protocol work)
- `zeek/zeek` — network monitoring core
- `OISF/suricata` — signature IDS
- `djformby/GRFICS-v2` — ICS cyber range (digital twin)
- `scy-phy/minicps` — CPS simulation
- `open-policy-agent/opa` — policy engine
- `temporalio/temporal` — workflow durability
- `qdrant/qdrant` — vector DB
- `langchain-ai/langgraph` — agent orchestration
- `anchore/syft` — SBOM
- `e-m-b-a/emba` + Firmadyne — firmware analysis

---

## What We Do NOT Do

- No autonomous actions on Level 0-2 assets without explicit written customer authorization
- No cloud-only deployments for customers with air-gap requirements
- No storing raw PLC telemetry in a third-party cloud without explicit DPA
- No skipping the digital-twin pre-flight test
- No removing items from the audit log
- No "AI washing" — if a feature uses rules, say so; ML claims must be backed by eval metrics
