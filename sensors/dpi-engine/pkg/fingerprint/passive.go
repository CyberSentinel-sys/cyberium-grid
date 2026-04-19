// Package fingerprint provides passive asset fingerprinting for the DPI sensor.
package fingerprint

import (
	"strings"
	"sync"

	"github.com/orhashield/dpi-engine/pkg/events"
)

// Fingerprinter builds AssetFingerprint records from observed OT traffic.
// It is safe for concurrent use.
type Fingerprinter struct {
	mu      sync.RWMutex
	assets  map[string]*events.AssetFingerprint // key: src_ip
}

// NewFingerprinter creates a new passive fingerprinter.
func NewFingerprinter() *Fingerprinter {
	return &Fingerprinter{
		assets: make(map[string]*events.AssetFingerprint),
	}
}

// Update incorporates a new OTEvent into the fingerprint database.
// Returns the updated fingerprint for the source IP.
func (f *Fingerprinter) Update(ev *events.OTEvent) *events.AssetFingerprint {
	if ev.SrcIP == "" {
		return nil
	}

	f.mu.Lock()
	defer f.mu.Unlock()

	fp, ok := f.assets[ev.SrcIP]
	if !ok {
		fp = &events.AssetFingerprint{}
		f.assets[ev.SrcIP] = fp
	}

	// Add observed protocol if not already recorded.
	if !containsProtocol(fp.ObservedProtocols, ev.Protocol) {
		fp.ObservedProtocols = append(fp.ObservedProtocols, ev.Protocol)
	}

	// Extract vendor/model from protocol-specific identity responses.
	f.extractIdentity(fp, ev)

	return fp
}

// Get returns the current fingerprint for an IP, or nil if unknown.
func (f *Fingerprinter) Get(ip string) *events.AssetFingerprint {
	f.mu.RLock()
	defer f.mu.RUnlock()
	return f.assets[ip]
}

// All returns a snapshot of all fingerprints.
func (f *Fingerprinter) All() map[string]*events.AssetFingerprint {
	f.mu.RLock()
	defer f.mu.RUnlock()
	out := make(map[string]*events.AssetFingerprint, len(f.assets))
	for k, v := range f.assets {
		cp := *v
		out[k] = &cp
	}
	return out
}

func (f *Fingerprinter) extractIdentity(fp *events.AssetFingerprint, ev *events.OTEvent) {
	switch ev.Protocol {
	case events.ProtocolModbusTCP:
		// Modbus Device Identification (FC 43/14) response contains vendor + model.
		if ev.Modbus != nil && ev.Modbus.FunctionCode == 0x2B && len(ev.Modbus.Data) > 2 {
			data := ev.Modbus.Data
			// Parse MEI Type 14 (Device Identification): object 0=VendorName, 1=ProductCode, 2=MajorMinorRevision
			parseModbusDeviceID(fp, data)
		}

	case events.ProtocolENIPCIP:
		// EtherNet/IP ListIdentity response contains vendor, product name, firmware revision.
		if ev.ENIP != nil && ev.ENIP.Command == 0x0063 && len(ev.ENIP.EncapsulationData) > 10 {
			parseENIPIdentity(fp, ev.ENIP.EncapsulationData)
		}

	case events.ProtocolBACnetIP:
		// BACnet IAm response contains device ID and vendor.
		if ev.BACnet != nil && ev.BACnet.PDUType == 1 { // UnconfirmedRequest
			// Vendor extraction from BACnet IAm requires deeper parsing (Phase 2).
		}
	}

	// Vendor lookup from OUI (first 3 bytes of MAC — not available from pure IP capture;
	// would require ARP/neighbor discovery integration in Phase 2).
}

func parseModbusDeviceID(fp *events.AssetFingerprint, data []byte) {
	if len(data) < 4 {
		return
	}
	// Skip MEI type(1), Read Device ID code(1), Conformity level(1), More/Next(1), Number of objects(1)
	offset := 2
	if offset >= len(data) {
		return
	}
	numObjects := int(data[offset])
	offset++

	for i := 0; i < numObjects && offset+2 < len(data); i++ {
		objID := data[offset]
		objLen := int(data[offset+1])
		offset += 2
		if offset+objLen > len(data) {
			break
		}
		value := string(data[offset : offset+objLen])
		offset += objLen

		switch objID {
		case 0x00:
			fp.Vendor = cleanString(value)
		case 0x01:
			fp.Model = cleanString(value)
		case 0x02:
			fp.FirmwareVersion = cleanString(value)
		}
	}
}

func parseENIPIdentity(fp *events.AssetFingerprint, data []byte) {
	// EtherNet/IP Identity Object response parsing.
	// Item type 0x000C = Identity Object. Vendor ID at offset varies.
	// Phase 1: simple heuristic from known Rockwell/Schneider/Siemens responses.
	if len(data) < 20 {
		return
	}

	// Known vendor ID patterns (EtherNet/IP vendor IDs from ODVA registry).
	// This will be replaced with full ODVA vendor table in Phase 2.
	knownVendors := map[uint16]string{
		1:   "Rockwell Automation",
		9:   "Schneider Electric",
		10:  "Siemens",
		278: "Omron",
		886: "Mitsubishi Electric",
	}

	if len(data) >= 22 {
		// vendorID is at a variable offset after CPF items; Phase 1 heuristic.
		vendorID := uint16(data[20]) | uint16(data[21])<<8
		if name, ok := knownVendors[vendorID]; ok {
			fp.Vendor = name
		}
	}
}

func cleanString(s string) string {
	return strings.TrimSpace(strings.Map(func(r rune) rune {
		if r < 32 || r > 126 {
			return -1
		}
		return r
	}, s))
}

func containsProtocol(protos []events.Protocol, p events.Protocol) bool {
	for _, x := range protos {
		if x == p {
			return true
		}
	}
	return false
}
