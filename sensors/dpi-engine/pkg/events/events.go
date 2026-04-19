// Package events defines the canonical OT event types used by the DPI sensor.
// In production this package would be generated from proto/events.proto via protoc.
// For Phase 1 we define Go structs directly matching the proto schema.
package events

import "time"

// Protocol identifies the OT protocol of a captured event.
type Protocol int32

const (
	ProtocolUnspecified Protocol = 0
	ProtocolModbusTCP   Protocol = 1
	ProtocolDNP3        Protocol = 2
	ProtocolENIPCIP     Protocol = 3
	ProtocolBACnetIP    Protocol = 4
	ProtocolOPCUA       Protocol = 5
	ProtocolS7Comm      Protocol = 6
	ProtocolProfinet    Protocol = 7
)

func (p Protocol) String() string {
	switch p {
	case ProtocolModbusTCP:
		return "modbus"
	case ProtocolDNP3:
		return "dnp3"
	case ProtocolENIPCIP:
		return "enip"
	case ProtocolBACnetIP:
		return "bacnet"
	case ProtocolOPCUA:
		return "opcua"
	case ProtocolS7Comm:
		return "s7comm"
	case ProtocolProfinet:
		return "profinet"
	default:
		return "unknown"
	}
}

// Severity represents the assessed severity of an OT event.
type Severity int32

const (
	SeverityUnspecified Severity = 0
	SeverityInfo        Severity = 1
	SeverityLow         Severity = 2
	SeverityMedium      Severity = 3
	SeverityHigh        Severity = 4
	SeverityCritical    Severity = 5
)

func (s Severity) String() string {
	switch s {
	case SeverityInfo:
		return "info"
	case SeverityLow:
		return "low"
	case SeverityMedium:
		return "medium"
	case SeverityHigh:
		return "high"
	case SeverityCritical:
		return "critical"
	default:
		return "unspecified"
	}
}

// OTEvent is the canonical event emitted by the DPI sensor for every parsed OT packet.
type OTEvent struct {
	EventID    string    `json:"event_id"`
	Timestamp  time.Time `json:"ts"`
	SensorID   string    `json:"sensor_id"`
	SrcIP      string    `json:"src_ip"`
	DstIP      string    `json:"dst_ip"`
	SrcPort    uint16    `json:"src_port"`
	DstPort    uint16    `json:"dst_port"`
	Protocol   Protocol  `json:"protocol"`
	RawPayload []byte    `json:"raw_payload,omitempty"`

	// Only one of these will be non-nil per event.
	Modbus  *ModbusEvent  `json:"modbus,omitempty"`
	DNP3    *DNP3Event    `json:"dnp3,omitempty"`
	ENIP    *ENIPEvent    `json:"enip,omitempty"`
	BACnet  *BACnetEvent  `json:"bacnet,omitempty"`

	Fingerprint *AssetFingerprint `json:"fingerprint,omitempty"`
	Severity    Severity          `json:"severity"`
	Tags        []string          `json:"tags,omitempty"`
	Anomalies   []AnomalyFlag     `json:"anomalies,omitempty"`
}

// ModbusEvent contains parsed fields from a Modbus TCP packet.
type ModbusEvent struct {
	TransactionID uint16   `json:"transaction_id"`
	UnitID        uint8    `json:"unit_id"`
	FunctionCode  uint8    `json:"function_code"`
	Data          []byte   `json:"data,omitempty"`
	IsException   bool     `json:"is_exception,omitempty"`
	ExceptionCode uint8    `json:"exception_code,omitempty"`
	IsWrite       bool     `json:"is_write,omitempty"`
	StartAddress  uint16   `json:"start_address,omitempty"`
	Values        []uint16 `json:"values,omitempty"`
}

// DNP3Event contains parsed fields from a DNP3 packet.
type DNP3Event struct {
	SrcAddress      uint16 `json:"src_address"`
	DstAddress      uint16 `json:"dst_address"`
	FunctionCode    uint8  `json:"function_code"`
	IsUnsolicited   bool   `json:"is_unsolicited,omitempty"`
	IsBroadcast     bool   `json:"is_broadcast,omitempty"`
	ApplicationData []byte `json:"application_data,omitempty"`
}

// ENIPEvent contains parsed fields from an EtherNet/IP (CIP) packet.
type ENIPEvent struct {
	Command           uint16 `json:"command"`
	SessionHandle     uint32 `json:"session_handle"`
	EncapsulationData []byte `json:"encapsulation_data,omitempty"`
	CIPService        uint8  `json:"cip_service,omitempty"`
	CIPClassName      string `json:"cip_class_name,omitempty"`
	CIPInstance       uint16 `json:"cip_instance,omitempty"`
}

// BACnetEvent contains parsed fields from a BACnet/IP packet.
type BACnetEvent struct {
	ObjectType     uint16 `json:"object_type"`
	ObjectInstance uint32 `json:"object_instance"`
	PropertyID     uint32 `json:"property_id"`
	Value          []byte `json:"value,omitempty"`
	PDUType        uint8  `json:"pdu_type"`
}

// AssetFingerprint contains passive fingerprinting information about a device.
type AssetFingerprint struct {
	Vendor              string     `json:"vendor,omitempty"`
	Model               string     `json:"model,omitempty"`
	FirmwareVersion     string     `json:"firmware_version,omitempty"`
	MACOUI              string     `json:"mac_oui,omitempty"`
	ObservedProtocols   []Protocol `json:"observed_protocols,omitempty"`
	Hostname            string     `json:"hostname,omitempty"`
}

// AnomalyFlag represents a detected anomaly within a packet.
type AnomalyFlag struct {
	RuleID          string   `json:"rule_id"`
	Description     string   `json:"description"`
	Severity        Severity `json:"severity"`
	MITRETechnique  string   `json:"mitre_technique,omitempty"`
}

// NATSSubject returns the NATS JetStream subject for this event.
func (e *OTEvent) NATSSubject() string {
	return "ot.events." + e.Protocol.String() + "." + e.SensorID
}
