// Package capture — AF_XDP backend (Linux kernel ≥ 4.18 only).
// On kernels older than 4.18, the DPI engine automatically falls back
// to the PcapBackend. See main.go kernel version detection.
package capture

import (
	"context"
	"fmt"
	"sync/atomic"

	"go.uber.org/zap"
)

// AFXDPBackend implements Backend using AF_XDP for zero-copy kernel bypass.
// Requires CAP_NET_ADMIN, CAP_NET_RAW, CAP_SYS_ADMIN and Linux kernel ≥ 4.18.
// Full AF_XDP implementation requires github.com/cilium/ebpf XDP program loading.
// Phase 1: stub implementation that delegates to PcapBackend on unsupported kernels.
type AFXDPBackend struct {
	iface   string
	queueID int
	logger  *zap.Logger
	stats   struct {
		received atomic.Uint64
		dropped  atomic.Uint64
		bytes    atomic.Uint64
	}
	// fallback is used when AF_XDP setup fails or kernel is too old.
	fallback *PcapBackend
}

// NewAFXDPBackend creates an AFXDPBackend for the given network interface.
// If AF_XDP setup fails (e.g., unsupported NIC driver), it falls back to PcapBackend.
func NewAFXDPBackend(iface string, logger *zap.Logger) (*AFXDPBackend, error) {
	b := &AFXDPBackend{
		iface:   iface,
		queueID: 0,
		logger:  logger,
	}

	// Attempt AF_XDP socket setup.
	// Phase 1: AF_XDP socket creation requires eBPF program loading (XDP_FLAGS_SKB_MODE).
	// This is implemented in Phase 4 when edge appliances with AF_XDP-capable drivers are deployed.
	// For now, we attempt and fall back gracefully.
	if err := b.trySetupAFXDP(); err != nil {
		logger.Warn("af_xdp: setup failed, falling back to libpcap",
			zap.String("interface", iface),
			zap.Error(err),
		)
		fallback, err2 := NewPcapBackend(iface, logger)
		if err2 != nil {
			return nil, fmt.Errorf("af_xdp fallback to pcap failed: %w", err2)
		}
		b.fallback = fallback
	} else {
		logger.Info("af_xdp: kernel bypass enabled", zap.String("interface", iface))
	}

	return b, nil
}

func (b *AFXDPBackend) trySetupAFXDP() error {
	// Phase 4 implementation: load XDP program, create UMEM, create XSK socket.
	// For Phase 1, return an error to trigger graceful fallback.
	return fmt.Errorf("af_xdp: not yet implemented in Phase 1 — using libpcap fallback")
}

// Start begins packet capture using AF_XDP (or libpcap fallback).
func (b *AFXDPBackend) Start(ctx context.Context) (<-chan *RawPacket, error) {
	if b.fallback != nil {
		return b.fallback.Start(ctx)
	}
	// Phase 4: implement AF_XDP UMEM poll loop here.
	return nil, fmt.Errorf("af_xdp: Start() called without fallback — this is a bug")
}

// Stop closes the AF_XDP socket (or delegates to fallback).
func (b *AFXDPBackend) Stop() error {
	if b.fallback != nil {
		return b.fallback.Stop()
	}
	return nil
}

// Stats returns current capture statistics.
func (b *AFXDPBackend) Stats() CaptureStats {
	if b.fallback != nil {
		return b.fallback.Stats()
	}
	return CaptureStats{
		PacketsReceived: b.stats.received.Load(),
		PacketsDropped:  b.stats.dropped.Load(),
		BytesReceived:   b.stats.bytes.Load(),
	}
}
