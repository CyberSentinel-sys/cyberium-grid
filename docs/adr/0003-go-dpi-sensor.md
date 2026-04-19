# ADR 0003 — Go for DPI Sensor Data Plane

**Status:** Accepted  
**Date:** 2026-04-19  
**Author:** CyberSentinel Systems Engineering

## Context

The DPI sensor must parse raw OT network traffic at line rate, emit canonical events, and run on constrained industrial hardware (Intel Atom-class embedded controllers, 4 cores, 8GB RAM). Requirements:

- High throughput: 1Gbps line rate target on 4-core embedded controller
- Kernel bypass: AF_XDP for zero-copy packet capture on Linux ≥4.18 (libpcap fallback for older kernels including 4.4.x which is our current dev environment)
- Rich protocol parsing: Modbus TCP, DNP3, EtherNet/IP, BACnet, and 20+ OT protocols across the roadmap
- Canonical event schema: protobuf for binary efficiency
- Low memory: sensor must not accumulate unbounded memory on burst traffic
- Cross-compile to ARM for edge appliance (Phase 4)

## Decision

Use **Go 1.23+** with:

- `google/gopacket` for libpcap-based packet capture and initial protocol layer parsing
- `cilium/ebpf` for AF_XDP kernel bypass (auto-detected at runtime; graceful fallback to libpcap on kernels <4.18)
- `google/protobuf` (`google.golang.org/protobuf`) for canonical `OTEvent` schema
- `nats-io/nats.go` for event emission to NATS JetStream
- `spf13/cobra` for CLI interface
- `go.uber.org/zap` for structured logging
- `prometheus/client_golang` for metrics exposition

Protocol parsers written as `Parser` interface implementations, one file per protocol, table-driven tests against PCAP fixtures.

## AF_XDP Kernel Compatibility

The development environment runs Linux 4.4.0 (AF_XDP requires ≥4.18). The `main.go` detects the kernel version at startup:

```go
if kernelMajorMinor() < [2]int{4, 18} {
    logger.Warn("AF_XDP unavailable (kernel <4.18), using libpcap fallback")
    backend = NewPcapBackend(cfg.Interface)
} else {
    backend = NewAFXDPBackend(cfg.Interface)
}
```

Production edge appliances will run a current kernel with AF_XDP support.

## ICSNPP Reference

Protocol parser correctness is validated against CISA ICSNPP Zeek scripts (`github.com/cisagov/ICSNPP`). Parser tests load the ICSNPP test PCAPs and verify our output matches known-good field values.

## Alternatives Rejected

| Alternative | Rejection Reason |
|---|---|
| Python (Scapy) | Too slow for line-rate capture; GIL limits multi-core |
| Zeek (standalone) | Good for analysis but harder to embed; Turing-complete scripting adds attack surface |
| Rust | Excellent memory safety; but slower development iteration for parser-heavy work; gopacket ecosystem has better OT protocol coverage |
| C/C++ | Memory safety concerns; cross-compilation more complex |

## Consequences

- `go.mod` must pin major versions; gopacket v1.x API is stable.
- AF_XDP requires `CAP_NET_ADMIN`, `CAP_NET_RAW`, `CAP_SYS_ADMIN` in Docker; documented in `docker-compose.yml`.
- Protobuf schema changes require regenerating `pkg/events/events.pb.go` and bumping the schema version.
- Performance benchmark (`BenchmarkModbusParse`) must remain >100k packets/sec or a regression issue is filed.
