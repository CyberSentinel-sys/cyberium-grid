# OrHaShield — Compliance Framework Mapping

**Version:** 0.1.0  
**Date:** 2026-04-19

This document maps OrHaShield platform capabilities to the key regulatory and standards requirements customers must meet.

## NERC CIP-015 — Internal Network Security Monitoring (INSM)

Effective: First Mandatory Compliance Date TBD post-FERC order approval

| CIP-015 Requirement | OrHaShield Capability | Component | Status |
|---|---|---|---|
| R1.1: Document assets requiring INSM | Asset inventory with Purdue level classification | control-plane, dpi-engine | Phase 1 |
| R1.2: Monitor for malicious communications | Passive DPI on all OT protocol traffic | dpi-engine + agent-orchestrator | Phase 1 |
| R1.3: Log and retain INSM data (90 days min) | TimescaleDB hypertables with configurable retention | infra/db | Phase 1 |
| R2: Implement INSM capabilities | Full DPI sensor + behavioral detection | dpi-engine + ml/anomaly | Phase 1-2 |
| R3: Protect INSM system from compromise | WORM audit log, Rust safety gate, mTLS | safety-gate, infra | Phase 1 |
| R4: Incident response integration | SOAR bridge, SIEM integration | services/control-plane | Phase 2 |

**Compliance evidence export**: `compliance/nerc-cip-015/` module generates audit-ready CSV + PDF reports.

---

## IEC 62443-3-3 — System Security Requirements

| SR Requirement | OrHaShield Capability | Component | Status |
|---|---|---|---|
| SR 1.1: Human user identification & authentication | JWT + API-key auth, RBAC roles | control-plane/auth | Phase 1 |
| SR 1.3: Account management | User management API, audit trail | control-plane | Phase 1 |
| SR 2.1: Authorization enforcement | OPA/Rego policy gate, Purdue action matrix | safety-gate | Phase 1 |
| SR 3.1: Communication integrity | TLS on all service-to-service connections | infra | Phase 1-2 |
| SR 3.3: Security functionality verification | Property-based tests + Kani formal verification | services/safety-gate/tests | Phase 1 |
| SR 6.1: Audit log accessibility | WORM audit log, compliance export API | control-plane, infra/db | Phase 1 |
| SR 6.2: Continuous monitoring | Real-time DPI + agent detection | dpi-engine + orchestrator | Phase 1 |
| SR 7.1: Denial of service protection | NATS rate limiting, circuit breaker, BPF filter | infra, agent-orchestrator | Phase 1 |

---

## NIS2 Directive (EU 2022/2555) — Article 21 Security Measures

| Article 21 Requirement | OrHaShield Capability | Component | Status |
|---|---|---|---|
| 21(2)(a): Risk analysis policies | Continuous asset risk scoring, CVSS-adjusted scoring | control-plane | Phase 1-2 |
| 21(2)(b): Incident handling | Alert workflow, SOAR integration, IR runbooks | agent-orchestrator, control-plane | Phase 1-2 |
| 21(2)(c): Business continuity / backup | Backup asset configuration export | control-plane | Phase 2 |
| 21(2)(d): Supply chain security | SBOM tracking, firmware integrity | services/firmware-integrity | Phase 4 |
| 21(2)(e): Acquisition / development security | SDLC controls documented in CLAUDE.md, CI/CD SAST | .github/workflows | Phase 1 |
| 21(2)(f): Effectiveness assessment | Compliance dashboard, control effectiveness scoring | ui/dashboard | Phase 2 |
| 21(2)(g): Cyber hygiene | Asset patching guidance, vulnerability correlation | control-plane | Phase 2 |
| 21(2)(h): Cryptography policy | TLS everywhere, documented key rotation policy | infra | Phase 1 |
| 21(2)(i): HR security | User lifecycle API (manual process, not automated) | control-plane | Phase 1 |
| 21(2)(j): MFA | Dashboard MFA (TOTP) | control-plane/auth | Phase 2 |

**Incident reporting**: OrHaShield generates NIS2-compliant incident reports (72-hour initial + 1-month final) as PDF exports from the control plane.

---

## EPA SDWA §1433 + Emergency Response Plan (ERP) Requirements

Relevant to US community water systems (our primary SMB wedge target).

| EPA Requirement | OrHaShield Capability | Notes |
|---|---|---|
| Risk and Resilience Assessment (RRA) | Asset inventory + threat landscape + vulnerability assessment export | Supports RRA documentation |
| Emergency Response Plan (ERP) | IR runbook generation, escalation procedures | Supports ERP documentation |
| Cyberattack detection | Real-time DPI + anomaly detection | Core platform capability |
| Access control | Asset-level access tracking | Phase 2 |
| Network security | Segmentation recommendations, anomaly detection | Phase 1-2 |

**Pricing for water utilities**: Community tier (free, ≤50 assets) designed specifically to meet EPA §1433 documentation requirements at zero cost for rural/small utilities.

---

## NCA OTCC-1:2022 (Saudi Arabia OT Cybersecurity Controls)

| OTCC Domain | OrHaShield Capability | Status |
|---|---|---|
| OT-1: Governance | Policy framework documentation, compliance dashboard | Phase 2 |
| OT-2: Defense — Asset Management | Passive asset discovery + fingerprinting | Phase 1 |
| OT-2: Defense — Threat Detection | Real-time DPI + multi-agent detection | Phase 1 |
| OT-2: Defense — Incident Response | Alert workflow + SOAR bridge | Phase 1-2 |
| OT-2: Defense — Vulnerability Management | CVE correlation + patch guidance | Phase 2 |
| OT-3: Resilience | Backup configuration export, recovery guidance | Phase 2 |
| OT-4: Third-Party | Vendor risk questionnaire integration | Phase 3 |

OTCC compliance pack: `compliance/nca-otcc/` — Arabic-language report generation included.

---

## Australia SOCI + Cyber Security Act 2024

| Requirement | OrHaShield Capability | Notes |
|---|---|---|
| Critical Infrastructure Risk Management Program (CIRMP) | Risk assessment framework, compliance export | Phase 2 |
| Incident reporting (≤12 hours for Category 1) | Real-time alert + one-click incident report generation | Phase 1 |
| Ransomware payment reporting (AUD $3M+ entities) | Incident classification + reporting workflow | Phase 2 |

---

## Singapore CCoP 2.0 (Cybersecurity Code of Practice for CII)

| Requirement | OrHaShield Capability | Notes |
|---|---|---|
| OT addendum: continuous monitoring | Real-time DPI + anomaly detection | Phase 1 |
| OT addendum: threat hunting | Manual threat-hunt playbooks + agent-assisted | Phase 2 |
| OT addendum: red/purple teaming | OrHaShield Sentinel (Phase 3) | Phase 3 |
| Biennial audit support | Compliance evidence export + audit trail | Phase 1-2 |

---

## Coverage Summary

| Framework | Phase 1 Coverage | Phase 2 Coverage | Full Coverage |
|---|---|---|---|
| NERC CIP-015 | ~60% | ~90% | Phase 2 |
| IEC 62443-3-3 | ~50% | ~80% | Phase 3 |
| NIS2 Article 21 | ~40% | ~75% | Phase 3 |
| EPA SDWA §1433 | ~70% | ~90% | Phase 2 |
| NCA OTCC-1:2022 | ~30% | ~65% | Phase 3 |
| SOCI + CSA 2024 | ~35% | ~70% | Phase 3 |
| CCoP 2.0 | ~30% | ~60% | Phase 3 |
