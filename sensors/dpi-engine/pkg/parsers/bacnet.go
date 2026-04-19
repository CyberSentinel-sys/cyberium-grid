package parsers

import (
	"encoding/binary"
	"fmt"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/uuid"
	"github.com/orhashield/dpi-engine/pkg/events"
)

// BACnet/IP uses UDP port 47808 (0xBAC0).
const BACnetPort = 47808

// BACnet APDU types (PDU types).
const (
	BACnetPDUConfirmedRequest   = 0x00
	BACnetPDUUnconfirmedRequest = 0x10
	BACnetPDUSimpleACK          = 0x20
	BACnetPDUComplexACK         = 0x30
	BACnetPDUSegmentACK         = 0x40
	BACnetPDUError              = 0x50
	BACnetPDUReject             = 0x60
	BACnetPDUAbort              = 0x70
)

// BACnet confirmed service codes (relevant for writes).
const (
	BACnetSvcAcknowledgeAlarm     = 0x00
	BACnetSvcConfirmedCOVNotif    = 0x01
	BACnetSvcConfirmedEventNotif  = 0x02
	BACnetSvcGetAlarmSummary      = 0x03
	BACnetSvcReadProperty         = 0x0C
	BACnetSvcReadPropertyMultiple = 0x0E
	BACnetSvcWriteProperty        = 0x0F
	BACnetSvcWritePropMultiple    = 0x10
	BACnetSvcDeviceCommunCtrl     = 0x11
	BACnetSvcReinitializeDevice   = 0x14
)

// BACnet unconfirmed service codes.
const (
	BACnetUSvcIAm           = 0x00
	BACnetUSvcIHave         = 0x01
	BACnetUSvcCOVNotif      = 0x02
	BACnetUSvcEventNotif    = 0x03
	BACnetUSvcPrivateTransfer = 0x04
	BACnetUSvcTextMessage   = 0x05
	BACnetUSvcTimeSynchron  = 0x06
	BACnetUSvcWhoHas        = 0x07
	BACnetUSvcWhoIs         = 0x08
	BACnetUSvcUTCSynchron   = 0x09
)

// BACnetParser parses BACnet/IP (UDP) packets.
type BACnetParser struct{}

// NewBACnetParser creates a new BACnet/IP parser.
func NewBACnetParser() *BACnetParser { return &BACnetParser{} }

// Protocol returns ProtocolBACnetIP.
func (p *BACnetParser) Protocol() events.Protocol { return events.ProtocolBACnetIP }

// Parse decodes a BACnet/IP packet.
func (p *BACnetParser) Parse(sensorID string, pkt gopacket.Packet) (*events.OTEvent, error) {
	udpLayer := pkt.Layer(layers.LayerTypeUDP)
	if udpLayer == nil {
		return nil, nil
	}
	udp := udpLayer.(*layers.UDP)
	if udp.DstPort != BACnetPort && udp.SrcPort != BACnetPort {
		return nil, nil
	}

	payload := udp.Payload
	// BACnet/IP: BVLC header (4 bytes) + NPDU (variable) + APDU
	if len(payload) < 6 {
		return nil, nil
	}

	// BVLC header: type(1) + func(1) + length(2)
	bvlcFunc := payload[1]
	_ = binary.BigEndian.Uint16(payload[2:4]) // bvlcLen

	ev := &events.OTEvent{
		EventID:    uuid.New().String(),
		Timestamp:  pkt.Metadata().Timestamp,
		SensorID:   sensorID,
		Protocol:   events.ProtocolBACnetIP,
		RawPayload: payload,
		SrcPort:    uint16(udp.SrcPort),
		DstPort:    uint16(udp.DstPort),
		Severity:   events.SeverityInfo,
	}

	if ipLayer := pkt.Layer(layers.LayerTypeIPv4); ipLayer != nil {
		ip := ipLayer.(*layers.IPv4)
		ev.SrcIP = ip.SrcIP.String()
		ev.DstIP = ip.DstIP.String()
	}

	bacnetEv := &events.BACnetEvent{}

	// BVLC function 0x0B = Original-Broadcast-NPDU (global broadcast to all BACnet devices).
	if bvlcFunc == 0x0B {
		ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
			RuleID:         "BACNET-001",
			Description:    "BACnet global broadcast — potential WhoIs/device enumeration",
			Severity:       events.SeverityLow,
			MITRETechnique: "T0846",
		})
		ev.Tags = append(ev.Tags, "bacnet-broadcast")
	}

	// Parse NPDU (starts at offset 4).
	if len(payload) < 7 {
		ev.BACnet = bacnetEv
		return ev, nil
	}

	npduCtrl := payload[5]
	apduOffset := 6
	if npduCtrl&0x20 != 0 { // DNET present
		apduOffset += 3 // DNET(2) + DLEN(1)
		if apduOffset < len(payload) && payload[apduOffset-1] > 0 {
			apduOffset += int(payload[apduOffset-1]) // DADR
		}
	}
	if npduCtrl&0x08 != 0 { // SNET present
		apduOffset += 3
		if apduOffset < len(payload) && payload[apduOffset-1] > 0 {
			apduOffset += int(payload[apduOffset-1])
		}
	}
	if npduCtrl&0x04 != 0 { // Hop count present
		apduOffset++
	}

	if apduOffset >= len(payload) {
		ev.BACnet = bacnetEv
		return ev, nil
	}

	apdu := payload[apduOffset:]
	if len(apdu) == 0 {
		ev.BACnet = bacnetEv
		return ev, nil
	}

	pduType := apdu[0] & 0xF0
	bacnetEv.PDUType = uint8(pduType >> 4)

	if pduType == BACnetPDUConfirmedRequest && len(apdu) >= 4 {
		svc := apdu[3]
		// WriteProperty, WritePropertyMultiple, ReinitializeDevice, DeviceCommunicationControl.
		if svc == BACnetSvcWriteProperty || svc == BACnetSvcWritePropMultiple {
			ev.Severity = events.SeverityMedium
			ev.Tags = append(ev.Tags, "bacnet-write")
			ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
				RuleID:         "BACNET-002",
				Description:    fmt.Sprintf("BACnet WriteProperty service (0x%02X) — potential unauthorized modification", svc),
				Severity:       events.SeverityMedium,
				MITRETechnique: "T0831",
			})
		}
		if svc == BACnetSvcReinitializeDevice || svc == BACnetSvcDeviceCommunCtrl {
			ev.Severity = events.SeverityHigh
			ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
				RuleID:         "BACNET-003",
				Description:    fmt.Sprintf("BACnet critical control service (0x%02X): ReinitializeDevice or DeviceCommunicationControl", svc),
				Severity:       events.SeverityHigh,
				MITRETechnique: "T0855",
			})
		}
	}

	ev.BACnet = bacnetEv
	return ev, nil
}

var _ Parser = (*BACnetParser)(nil)
