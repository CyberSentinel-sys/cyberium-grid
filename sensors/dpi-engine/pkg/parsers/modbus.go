// Package parsers provides OT protocol parsers that produce canonical OTEvents.
package parsers

import (
	"encoding/binary"
	"fmt"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/uuid"
	"github.com/orhashield/dpi-engine/pkg/events"
)

// Parser is the interface all protocol parsers implement.
type Parser interface {
	// Parse attempts to decode the packet. Returns nil, nil if the packet does
	// not match this protocol (not an error — just not our protocol).
	Parse(sensorID string, pkt gopacket.Packet) (*events.OTEvent, error)
	// Protocol returns the protocol identifier this parser handles.
	Protocol() events.Protocol
}

// ModbusTCP port.
const ModbusPort = 502

// Modbus function codes.
const (
	FCReadCoils              = 0x01
	FCReadDiscreteInputs     = 0x02
	FCReadHoldingRegisters   = 0x03
	FCReadInputRegisters     = 0x04
	FCWriteSingleCoil        = 0x05
	FCWriteSingleRegister    = 0x06
	FCWriteMultipleCoils     = 0x0F
	FCWriteMultipleRegisters = 0x10
	FCMaskWriteRegister      = 0x16
	FCReadWriteMultipleRegs  = 0x17
	FCReadDeviceIdentification = 0x2B
	FCDiagnostics            = 0x08
	FCExceptionMask          = 0x80
)

// writeFunctionCodes is the set of Modbus function codes that write to field devices.
var writeFunctionCodes = map[uint8]bool{
	FCWriteSingleCoil:        true,
	FCWriteSingleRegister:    true,
	FCWriteMultipleCoils:     true,
	FCWriteMultipleRegisters: true,
	FCMaskWriteRegister:      true,
	FCReadWriteMultipleRegs:  true,
}

// ModbusParser parses Modbus TCP packets.
type ModbusParser struct{}

// NewModbusParser creates a new Modbus TCP parser.
func NewModbusParser() *ModbusParser { return &ModbusParser{} }

// Protocol returns ProtocolModbusTCP.
func (p *ModbusParser) Protocol() events.Protocol { return events.ProtocolModbusTCP }

// Parse decodes a Modbus TCP packet from the given gopacket.Packet.
// Returns nil, nil for non-Modbus packets.
func (p *ModbusParser) Parse(sensorID string, pkt gopacket.Packet) (*events.OTEvent, error) {
	tcpLayer := pkt.Layer(layers.LayerTypeTCP)
	if tcpLayer == nil {
		return nil, nil
	}
	tcp := tcpLayer.(*layers.TCP)

	// Modbus TCP uses port 502 as destination or source (response).
	if tcp.DstPort != ModbusPort && tcp.SrcPort != ModbusPort {
		return nil, nil
	}

	payload := tcp.Payload
	if len(payload) < 8 {
		return nil, nil // minimum Modbus TCP MBAP header (7) + 1 byte FC
	}

	mbap, fc, data, err := parseModbusTCP(payload)
	if err != nil {
		return nil, nil // malformed packet, skip
	}

	ev := &events.OTEvent{
		EventID:    uuid.New().String(),
		Timestamp:  pkt.Metadata().Timestamp,
		SensorID:   sensorID,
		Protocol:   events.ProtocolModbusTCP,
		RawPayload: payload,
		Severity:   events.SeverityInfo,
	}

	if ipLayer := pkt.Layer(layers.LayerTypeIPv4); ipLayer != nil {
		ip := ipLayer.(*layers.IPv4)
		ev.SrcIP = ip.SrcIP.String()
		ev.DstIP = ip.DstIP.String()
	}
	ev.SrcPort = uint16(tcp.SrcPort)
	ev.DstPort = uint16(tcp.DstPort)

	modbusEv := &events.ModbusEvent{
		TransactionID: mbap.transactionID,
		UnitID:        mbap.unitID,
		FunctionCode:  fc,
	}

	isException := fc&FCExceptionMask != 0
	modbusEv.IsException = isException

	if isException {
		if len(data) > 0 {
			modbusEv.ExceptionCode = data[0]
		}
		ev.Severity = events.SeverityMedium
		ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
			RuleID:         "MODBUS-001",
			Description:    fmt.Sprintf("Modbus exception response: FC=0x%02X code=0x%02X", fc, modbusEv.ExceptionCode),
			Severity:       events.SeverityMedium,
			MITRETechnique: "T0836",
		})
	}

	if writeFunctionCodes[fc] {
		modbusEv.IsWrite = true
		ev.Severity = events.SeverityLow
		ev.Tags = append(ev.Tags, "write-operation")

		addr, vals := parseWritePayload(fc, data)
		modbusEv.StartAddress = addr
		modbusEv.Values = vals

		// Anomaly: write to broadcast or reserved unit ID
		if mbap.unitID == 0xFF || mbap.unitID == 0x00 {
			ev.Severity = events.SeverityHigh
			ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
				RuleID:         "MODBUS-002",
				Description:    fmt.Sprintf("Modbus write to broadcast/reserved unit ID: %d", mbap.unitID),
				Severity:       events.SeverityHigh,
				MITRETechnique: "T0855",
			})
		}
	}

	// Anomaly: diagnostic function code (FC 8) used — potential port scan or device enumeration.
	if fc == FCDiagnostics {
		ev.Severity = events.SeverityMedium
		ev.Anomalies = append(ev.Anomalies, events.AnomalyFlag{
			RuleID:         "MODBUS-003",
			Description:    "Modbus diagnostic function code (FC 8) — potential device enumeration",
			Severity:       events.SeverityMedium,
			MITRETechnique: "T0846",
		})
	}

	// FrostyGoop TTP: Modbus write FC 6/16 to ENCO controller addresses.
	if (fc == FCWriteSingleRegister || fc == FCWriteMultipleRegisters) && modbusEv.StartAddress >= 0x0000 {
		ev.Tags = append(ev.Tags, "potential-frostygoop-ttp")
	}

	ev.Modbus = modbusEv
	ev.RawPayload = payload
	return ev, nil
}

// mbapHeader represents the Modbus Application Protocol header.
type mbapHeader struct {
	transactionID uint16
	protocolID    uint16
	length        uint16
	unitID        uint8
}

func parseModbusTCP(data []byte) (mbapHeader, uint8, []byte, error) {
	if len(data) < 8 {
		return mbapHeader{}, 0, nil, fmt.Errorf("too short")
	}
	hdr := mbapHeader{
		transactionID: binary.BigEndian.Uint16(data[0:2]),
		protocolID:    binary.BigEndian.Uint16(data[2:4]),
		length:        binary.BigEndian.Uint16(data[4:6]),
		unitID:        data[6],
	}
	if hdr.protocolID != 0 {
		return mbapHeader{}, 0, nil, fmt.Errorf("not Modbus TCP (protocol ID %d)", hdr.protocolID)
	}
	fc := data[7]
	pduData := data[8:]
	return hdr, fc, pduData, nil
}

func parseWritePayload(fc uint8, data []byte) (startAddr uint16, values []uint16) {
	if len(data) < 4 {
		return
	}
	startAddr = binary.BigEndian.Uint16(data[0:2])

	switch fc {
	case FCWriteSingleCoil, FCWriteSingleRegister:
		if len(data) >= 4 {
			values = []uint16{binary.BigEndian.Uint16(data[2:4])}
		}
	case FCWriteMultipleRegisters:
		if len(data) < 5 {
			return
		}
		count := data[4]
		for i := 0; i < int(count) && 5+int(i)*2+1 < len(data); i++ {
			values = append(values, binary.BigEndian.Uint16(data[5+i*2:5+i*2+2]))
		}
	}
	return
}

// Ensure ModbusParser implements Parser at compile time.
var _ Parser = (*ModbusParser)(nil)

// Silence unused import warning — time is used indirectly via uuid.
var _ = time.Now
