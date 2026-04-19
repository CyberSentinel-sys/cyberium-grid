// Package emit provides event emitters for the DPI sensor.
package emit

import (
	"context"
	"encoding/json"
	"fmt"
	"sync/atomic"

	"github.com/nats-io/nats.go"
	"github.com/orhashield/dpi-engine/pkg/events"
	"go.uber.org/zap"
)

// Emitter sends OTEvents to a destination.
type Emitter interface {
	Emit(ctx context.Context, event *events.OTEvent) error
	Close() error
}

// NATSEmitter publishes OTEvents to NATS JetStream.
// Subject routing: ot.events.{protocol}.{sensor_id}
// Payload: JSON-encoded OTEvent (protobuf in Phase 2).
type NATSEmitter struct {
	conn    *nats.Conn
	js      nats.JetStreamContext
	logger  *zap.Logger
	buffer  chan *events.OTEvent // back-pressure buffer
	metrics struct {
		success atomic.Uint64
		failure atomic.Uint64
	}
}

// NewNATSEmitter creates and returns a NATSEmitter connected to the given NATS URL.
// opts can include nats.UserInfo, nats.Secure, etc.
func NewNATSEmitter(url string, logger *zap.Logger, opts ...nats.Option) (*NATSEmitter, error) {
	conn, err := nats.Connect(url, opts...)
	if err != nil {
		return nil, fmt.Errorf("nats: connect to %q failed: %w", url, err)
	}

	js, err := conn.JetStream()
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("nats: JetStream context failed: %w", err)
	}

	// Ensure the OT events stream exists.
	if err := ensureStream(js); err != nil {
		logger.Warn("nats: stream setup failed, continuing without JetStream guarantees", zap.Error(err))
	}

	e := &NATSEmitter{
		conn:   conn,
		js:     js,
		logger: logger,
		buffer: make(chan *events.OTEvent, 10_000),
	}

	return e, nil
}

// ensureStream creates the OT events JetStream stream if it doesn't exist.
func ensureStream(js nats.JetStreamContext) error {
	_, err := js.StreamInfo("OT_EVENTS")
	if err == nats.ErrStreamNotFound {
		_, err = js.AddStream(&nats.StreamConfig{
			Name:        "OT_EVENTS",
			Subjects:    []string{"ot.events.>"},
			MaxAge:      86400 * 7, // 7 days
			Storage:     nats.FileStorage,
			MaxMsgs:     10_000_000,
			MaxMsgSize:  65536,
			Retention:   nats.LimitsPolicy,
			Replicas:    1,
		})
		if err != nil {
			return fmt.Errorf("create OT_EVENTS stream: %w", err)
		}
	}
	return err
}

// Emit publishes an OTEvent to NATS JetStream.
// If the NATS connection is unavailable, the event is dropped and the failure counter incremented.
func (e *NATSEmitter) Emit(_ context.Context, event *events.OTEvent) error {
	data, err := json.Marshal(event)
	if err != nil {
		e.metrics.failure.Add(1)
		return fmt.Errorf("nats: marshal event: %w", err)
	}

	subject := event.NATSSubject()
	if _, err := e.js.Publish(subject, data); err != nil {
		e.metrics.failure.Add(1)
		e.logger.Warn("nats: publish failed",
			zap.String("subject", subject),
			zap.String("event_id", event.EventID),
			zap.Error(err),
		)
		return err
	}

	e.metrics.success.Add(1)
	return nil
}

// Close drains and closes the NATS connection.
func (e *NATSEmitter) Close() error {
	e.conn.Drain()
	e.conn.Close()
	return nil
}

// Stats returns emit metrics.
func (e *NATSEmitter) Stats() (success, failure uint64) {
	return e.metrics.success.Load(), e.metrics.failure.Load()
}

// StdoutEmitter writes OTEvents as JSON to stdout. Used for debugging.
type StdoutEmitter struct {
	logger *zap.Logger
}

// NewStdoutEmitter creates a stdout emitter.
func NewStdoutEmitter(logger *zap.Logger) *StdoutEmitter {
	return &StdoutEmitter{logger: logger}
}

// Emit writes the event as JSON to stdout.
func (e *StdoutEmitter) Emit(_ context.Context, event *events.OTEvent) error {
	data, err := json.MarshalIndent(event, "", "  ")
	if err != nil {
		return err
	}
	e.logger.Info("event", zap.ByteString("json", data))
	return nil
}

// Close is a no-op for StdoutEmitter.
func (e *StdoutEmitter) Close() error { return nil }
