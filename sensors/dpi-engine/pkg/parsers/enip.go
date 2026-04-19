package parsers

import (
	"encoding/binary"
	"fmt"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/uuid"
	"github.com/orhashield/dpi-engine/pkg/events"
)

// EtherNet/IP uses port 44818 (TCP) and 2222 (UDP).
const (
	ENIPTCPPort = 44818
	ENIPUDPPort = 2222
)

// EtherNet/IP encapsulation commands.
const (
	ENIPCmdNOP              = 0x0000
	ENIPCmdListServices     = 0x0004
	ENIPCmdListIdentity     = 0x0063
	ENIPCmdListInterfaces   = 0x0064
	ENIPCmdRegisterSession  = 0x0065
	ENIPCmdUnregisterSession = 0x0066
	ENIPCmdSendRRData       = 0x006F
	ENIPCmdSendUnitData     = 0x0070
)

// CIP service codes of interest.
const (
	CIPServiceGetAttrAll  = 0x01
	CIPServiceSetAttrAll  = 0x02
	CIPServiceGetAttrList = 0x03
	CIPServiceSetAttrList = 0x04
	CIPServiceReset       = 0x05
	CIPServiceStart       = 0x06
	CIPServiceStop        = 0x07
	CIPServiceCreate      = 0x08
	CIPServiceDelete      = 0x09
)

// cipClassNames maps common CIP class IDs to human-readable names.
var cipClassNames = map[uint16]string{
	0x01: "Identity",
	0x02: "Message Router",
	0x06: "Connection Manager",
	0x29: "Parameter",
	0x2A: "Parameter Group",
	0x37: "File",
	0x64: "ControlLogix Diagnostics",
	0x70: "ControlLogix Explicit Message",
}

// ENIPParser parses EtherNet/IP (CIP over TCP) packets.
type ENIPParser struct{}

// NewENIPParser creates a new EtherNet/IP parser.
func NewENIPParser() *ENIPParser { return &ENIPParser{} }

// Protocol returns ProtocolENIPCIP.
func (p *ENIPParser) Protocol() events.Protocol { return events.ProtocolENIPCIP }

// Parse decodes an EtherNet/IP packet.
func (p *ENIPParser) Parse(sensorID string, pkt gopacket.Packet) (*events.OTEvent, error) {
	tcpLayer := pkt.Layer(layers.LayerTypeTCP)
	if tcpLayer == nil {
		return nil, nil
	}
	tcp := tcpLayer.(*layers.TCP)
	if tcp.DstPort != ENIPTCPPort && tcp.SrcPort != ENIPTCPPort {
		return nil, nil
	}

	payload := tcp.Payload
	// EtherNet/IP encapsulation header: command(2) + length(2) + session(4) + status(4) + sender_context(8) + options(4) = 24 bytes
	if len(payload) < 24 {
		return nil, nil
	}

	cmd := binary.LittleEndian.Uint16(payload[0:2])
	sessionHandle := binary.LittleEndian.Uint32(payload[4:8])

	ev := &events.OTEvent{
		EventID:    uuid.New().String(),
		Timestamp:  pkt.Metadata().Timestamp,
		SensorID:   sensorID,
		Protocol:   events.ProtocolENIPCIP,
		RawPayload: payload,
		SrcPort:    uint16(tcp.SrcPort),
		DstPort:    uint16(tcp.DstPort),
		Severity:   events.SeverityInfo,
	}

	if ipLayer := pkt.Layer(layers.LayerTypeIPv4); ipLayer != nil {
		ip := ipLayer.(*layers.IPv4)
		ev.SrcIP = ip.SrcIP.String()
		ev.DstIP = ip.DstIP.String()
	}

	enipEv := &events.ENIPEvent{
		Command:           uint16(cmd),
		SessionHandle:     sessionHandle,
		EncapsulationData: payload[24:],
	}

	// Parse CIP from SendRRData / SendUnitData payloads.
	if (cmd == ENIPCmdSendRRData || cmd == ENIPCmdSendUnitData) && len(payload) > 40 {
		cipData := payload[40:] // skip encap header + CPF header (varies; approximate)
		if len(cipData) > 0 {
			enipEv.CIPService = cipData[0] & 0x7F
			if len(cipData) > 2 {
				classID := uint16(cipData[2])
				enipEv.CIPClassName = cipClassName(classID)
				if len(cipData) > 4 {
					enipEv.CIPInstance = binary.LittleEndian.Uint16(cipData[4:6])
				}
			}
		}

		// Anomaly: CIP Reset, Stop — potential disruption commands.
		if enipEv.CIPService == CIPServiceReset || enipEv.CIPService == CIPServiceStop {
			ev.Severity = events.SeverityHigh
			ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
				RuleID:         "ENIP-001",
				Description:    fmt.Sprintf("CIP control command: service=0x%02X on %s", enipEv.CIPService, enipEv.CIPClassName),
				Severity:       events.SeverityHigh,
				MITRETechnique: "T0855",
			})
			ev.Tags = append(ev.Tags, "cip-control-command")
		}
	}

	// Anomaly: device identity enumeration.
	if cmd == ENIPCmdListIdentity {
		ev.Tags = append(ev.Tags, "device-enumeration")
		ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
			RuleID:         "ENIP-002",
			Description:    "EtherNet/IP identity enumeration (ListIdentity) — potential reconnaissance",
			Severity:       events.SeverityLow,
			MITRETechnique: "T0846",
		})
	}

	ev.ENIP = enipEv
	return ev, nil
}

func cipClassName(classID uint16) string {
	if name, ok := cipClassNames[classID]; ok {
		return name
	}
	return fmt.Sprintf("Unknown(0x%04X)", classID)
}

var _ Parser = (*ENIPParser)(nil)
