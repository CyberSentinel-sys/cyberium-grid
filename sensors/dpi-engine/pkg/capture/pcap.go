// Package capture provides packet capture backends for the DPI sensor.
package capture

import (
	"context"
	"fmt"
	"sync/atomic"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/pcap"
	"go.uber.org/zap"
)

// RawPacket holds a captured network packet with metadata.
type RawPacket struct {
	Data      []byte
	Timestamp time.Time
	IfIndex   int
}

// CaptureStats holds packet capture statistics.
type CaptureStats struct {
	PacketsReceived uint64
	PacketsDropped  uint64
	BytesReceived   uint64
}

// Backend is the interface for packet capture backends.
type Backend interface {
	Start(ctx context.Context) (<-chan *RawPacket, error)
	Stop() error
	Stats() CaptureStats
}

// OTPortBPFFilter is the BPF filter that restricts capture to known OT protocol ports.
// This reduces CPU load and limits the attack surface of the parser.
const OTPortBPFFilter = "port 502 or port 20000 or port 44818 or port 47808 or port 102 or port 4840"

// PcapBackend implements Backend using gopacket/pcap (libpcap or PCAP file replay).
type PcapBackend struct {
	source  string // network interface name or PCAP file path
	handle  *pcap.Handle
	logger  *zap.Logger
	stats   struct {
		received atomic.Uint64
		dropped  atomic.Uint64
		bytes    atomic.Uint64
	}
}

// NewPcapBackend creates a PcapBackend for the given interface name or PCAP file path.
func NewPcapBackend(source string, logger *zap.Logger) (*PcapBackend, error) {
	return &PcapBackend{source: source, logger: logger}, nil
}

// Start opens the capture handle and begins emitting packets to the returned channel.
// The channel is closed when the context is cancelled or the PCAP source is exhausted.
func (b *PcapBackend) Start(ctx context.Context) (<-chan *RawPacket, error) {
	var (
		handle *pcap.Handle
		err    error
	)

	// Attempt to open as live interface first; fall back to file.
	handle, err = pcap.OpenLive(b.source, 65535, true, pcap.BlockForever)
	if err != nil {
		// Try as PCAP file for offline replay / testing.
		handle, err = pcap.OpenOffline(b.source)
		if err != nil {
			return nil, fmt.Errorf("pcap: cannot open %q as interface or file: %w", b.source, err)
		}
		b.logger.Info("pcap: opened file for offline replay", zap.String("source", b.source))
	} else {
		b.logger.Info("pcap: live capture started", zap.String("interface", b.source))
	}

	if err = handle.SetBPFFilter(OTPortBPFFilter); err != nil {
		b.logger.Warn("pcap: failed to set BPF filter, capturing all traffic", zap.Error(err))
	}

	b.handle = handle
	out := make(chan *RawPacket, 1024)

	go func() {
		defer close(out)
		defer handle.Close()

		src := gopacket.NewPacketSource(handle, handle.LinkType())
		src.NoCopy = true

		for {
			select {
			case <-ctx.Done():
				b.logger.Info("pcap: capture stopping (context cancelled)")
				return
			case pkt, ok := <-src.Packets():
				if !ok {
					return
				}
				data := pkt.Data()
				b.stats.received.Add(1)
				b.stats.bytes.Add(uint64(len(data)))

				cp := make([]byte, len(data))
				copy(cp, data)

				select {
				case out <- &RawPacket{
					Data:      cp,
					Timestamp: pkt.Metadata().Timestamp,
				}:
				default:
					// Channel full — drop packet and record.
					b.stats.dropped.Add(1)
				}
			}
		}
	}()

	return out, nil
}

// Stop closes the capture handle.
func (b *PcapBackend) Stop() error {
	if b.handle != nil {
		b.handle.Close()
	}
	return nil
}

// Stats returns current capture statistics.
func (b *PcapBackend) Stats() CaptureStats {
	return CaptureStats{
		PacketsReceived: b.stats.received.Load(),
		PacketsDropped:  b.stats.dropped.Load(),
		BytesReceived:   b.stats.bytes.Load(),
	}
}
