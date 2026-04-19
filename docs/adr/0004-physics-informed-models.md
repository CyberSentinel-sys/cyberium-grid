# ADR 0004 — Physics-Informed ML for Anomaly Detection

**Status:** Accepted  
**Date:** 2026-04-19  
**Author:** CyberSentinel Systems Engineering

## Context

OT anomaly detection with pure data-driven ML suffers from:

1. **High false-positive rate**: industrial processes have complex operating modes (startup, shutdown, maintenance, seasonal variation) that pure statistical models flag as anomalies.
2. **Training data scarcity**: public OT intrusion datasets (SWaT, WADI, HAI, Gas Pipeline, Power System) are small and lab-synthetic.
3. **Air-gap training constraint**: customers cannot send raw PLC telemetry to a cloud for model training.
4. **Physical constraint blindness**: an ML model predicting a pressure value of -50 PSI for a sealed tank is physically impossible, but the model doesn't know this.

## Decision

Use **physics-informed neural networks (PINNs)** and **statistical process control (SPC)** combined:

1. **SPC baseline (immediate value)**: on-device Shewhart control charts and CUSUM for each measured variable. Uses known engineering limits (operating range, safety setpoints) as bounds. Zero training data required. High explainability.

2. **PINN layer (medium term)**: embed known physical equations as soft constraints in the loss function during training. Example: for a water tank system, the mass-balance equation `dV/dt = Q_in - Q_out` is enforced. The model learns residuals from physical expectations, not absolute values.

3. **LSTM/Transformer temporal model (long term)**: trained on site-specific telemetry after a 30-day baselining period. Physics constraints applied as post-hoc filters: predictions that violate hard physical limits are clamped and flagged.

4. **Federated learning**: model updates computed on-site (preserving air-gap); deltas aggregated via secure aggregation with differential privacy (Phase 4).

## Training Datasets

| Dataset | Source | Use |
|---|---|---|
| SWaT (Secure Water Treatment) | iTrust, SUTD | Water treatment baseline |
| WADI | iTrust, SUTD | Water distribution |
| HAI (HIL-based Augmented ICS) | KAIST | Power/water combined |
| Gas Pipeline Dataset | Mississippi State Uni | Gas control anomaly |
| Power System Dataset | Mississippi State Uni | Power system anomaly |

All datasets used under academic license for research/training; not redistributed.

## Alternatives Rejected

| Alternative | Rejection Reason |
|---|---|
| Pure anomaly detection (autoencoder only) | High FP rate in real OT; no physical constraint awareness |
| Pure rule engine | Cannot detect novel attacks; requires manual rule authoring per site |
| LLM-only reasoning | Hallucination risk for physical process limits; latency too high for real-time |
| LSTM only | Learns correlations without physical constraints; physically impossible predictions |

## Consequences

- SPC baselines are computed on-site during initial deployment (no training data needed to start).
- PINN training requires site-specific P&ID information to encode physical equations; this is part of the deployment process.
- Physics constraint violations are themselves an alert class (e.g., sensor reading beyond physical range may indicate sensor manipulation).
- Model artifacts stored in ONNX format for portability across Python/Go/Rust inference environments.
