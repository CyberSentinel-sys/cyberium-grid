package parsers

import (
	"encoding/binary"
	"fmt"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/uuid"
	"github.com/orhashield/dpi-engine/pkg/events"
)

const DNP3Port = 20000

// DNP3 function codes (Application layer).
const (
	DNP3FCConfirm           = 0x00
	DNP3FCRead              = 0x01
	DNP3FCWrite             = 0x02
	DNP3FCSelectOperate     = 0x03
	DNP3FCDirectOperate     = 0x04
	DNP3FCDirectOperateNoAck = 0x05
	DNP3FCImmediateFreeze   = 0x07
	DNP3FCInitializeData    = 0x0A
	DNP3FCEnableUnsolicited = 0x14
	DNP3FCDisableUnsolicited = 0x15
	DNP3FCAuthentication    = 0x20
	DNP3FCResponse          = 0x81
	DNP3FCUnsolicitedResponse = 0x82
)

// criticalFunctionCodes are DNP3 function codes that can affect physical output.
var criticalFunctionCodes = map[uint8]bool{
	DNP3FCWrite:              true,
	DNP3FCSelectOperate:      true,
	DNP3FCDirectOperate:      true,
	DNP3FCDirectOperateNoAck: true,
	DNP3FCImmediateFreeze:    true,
	DNP3FCInitializeData:     true,
}

// DNP3Parser parses DNP3 TCP packets.
type DNP3Parser struct{}

// NewDNP3Parser creates a new DNP3 parser.
func NewDNP3Parser() *DNP3Parser { return &DNP3Parser{} }

// Protocol returns ProtocolDNP3.
func (p *DNP3Parser) Protocol() events.Protocol { return events.ProtocolDNP3 }

// Parse decodes a DNP3 TCP packet.
// Returns nil, nil for non-DNP3 packets.
func (p *DNP3Parser) Parse(sensorID string, pkt gopacket.Packet) (*events.OTEvent, error) {
	tcpLayer := pkt.Layer(layers.LayerTypeTCP)
	if tcpLayer == nil {
		// DNP3 also runs over UDP — check that too.
		udpLayer := pkt.Layer(layers.LayerTypeUDP)
		if udpLayer == nil {
			return nil, nil
		}
		udp := udpLayer.(*layers.UDP)
		if udp.DstPort != DNP3Port && udp.SrcPort != DNP3Port {
			return nil, nil
		}
		return p.parsePayload(sensorID, pkt, udp.Payload, 0, uint16(udp.SrcPort), uint16(udp.DstPort))
	}

	tcp := tcpLayer.(*layers.TCP)
	if tcp.DstPort != DNP3Port && tcp.SrcPort != DNP3Port {
		return nil, nil
	}
	return p.parsePayload(sensorID, pkt, tcp.Payload, 0, uint16(tcp.SrcPort), uint16(tcp.DstPort))
}

func (p *DNP3Parser) parsePayload(
	sensorID string,
	pkt gopacket.Packet,
	payload []byte,
	_ int,
	srcPort, dstPort uint16,
) (*events.OTEvent, error) {
	// DNP3 Data Link Layer frame: 0x05 0x64 + length(1) + ctrl(1) + dst(2) + src(2) + CRC(2)
	if len(payload) < 10 {
		return nil, nil
	}
	if payload[0] != 0x05 || payload[1] != 0x64 {
		return nil, nil // not a DNP3 frame
	}

	dstAddr := binary.LittleEndian.Uint16(payload[4:6])
	srcAddr := binary.LittleEndian.Uint16(payload[6:8])

	ctrl := payload[3]
	isMaster := ctrl&0x40 != 0
	isBroadcast := dstAddr >= 0xFFF0 && dstAddr <= 0xFFFF

	ev := &events.OTEvent{
		EventID:    uuid.New().String(),
		Timestamp:  pkt.Metadata().Timestamp,
		SensorID:   sensorID,
		Protocol:   events.ProtocolDNP3,
		RawPayload: payload,
		SrcPort:    srcPort,
		DstPort:    dstPort,
		Severity:   events.SeverityInfo,
	}

	if ipLayer := pkt.Layer(layers.LayerTypeIPv4); ipLayer != nil {
		ip := ipLayer.(*layers.IPv4)
		ev.SrcIP = ip.SrcIP.String()
		ev.DstIP = ip.DstIP.String()
	}

	dnp3Ev := &events.DNP3Event{
		SrcAddress:  srcAddr,
		DstAddress:  dstAddr,
		IsBroadcast: isBroadcast,
	}

	// Parse Application Layer (starts after transport header, offset varies).
	// Full DNP3 framing with CRC extraction is complex; this parses the basic FC.
	if len(payload) >= 14 {
		appCtrl := payload[10]
		dnp3Ev.IsUnsolicited = appCtrl&0x20 != 0
		if len(payload) > 11 {
			dnp3Ev.FunctionCode = payload[11]
			dnp3Ev.ApplicationData = payload[12:]
		}
	}

	if isBroadcast {
		ev.Severity = events.SeverityHigh
		ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
			RuleID:         "DNP3-001",
			Description:    fmt.Sprintf("DNP3 broadcast to address 0x%04X — potential command injection", dstAddr),
			Severity:       events.SeverityHigh,
			MITRETechnique: "T0855",
		})
	}

	if criticalFunctionCodes[dnp3Ev.FunctionCode] {
		ev.Severity = maxSeverity(ev.Severity, events.SeverityMedium)
		ev.Tags = append(ev.Tags, "dnp3-control-operation")
	}

	if dnp3Ev.IsUnsolicited && !isMaster {
		ev.Tags = append(ev.Tags, "dnp3-unsolicited-response")
	}

	ev.DNP3 = dnp3Ev
	return ev, nil
}

func maxSeverity(a, b events.Severity) events.Severity {
	if a > b {
		return a
	}
	return b
}

var _ Parser = (*DNP3Parser)(nil)
