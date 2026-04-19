-- OrHaShield TimescaleDB Hypertable Setup
-- Requires TimescaleDB extension (timescale/timescaledb Docker image).

-- ── Telemetry (OT sensor measurements — time-series) ─────────────────────────
CREATE TABLE telemetry (
    time        TIMESTAMPTZ NOT NULL,
    asset_id    UUID NOT NULL,
    metric      VARCHAR(100) NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    unit        VARCHAR(50),
    quality     SMALLINT DEFAULT 192,  -- OPC UA quality: 192=Good, 0=Bad
    tags        JSONB NOT NULL DEFAULT '{}'
);

-- Convert to TimescaleDB hypertable partitioned by time.
SELECT create_hypertable('telemetry', 'time',
    chunk_time_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Composite index for asset + time queries (most common access pattern).
CREATE INDEX ON telemetry (asset_id, time DESC);
-- Index for metric queries (e.g., "show me all flow_rate readings").
CREATE INDEX ON telemetry (metric, time DESC);

-- Continuous aggregate: 5-minute rollup for dashboard visualization.
CREATE MATERIALIZED VIEW telemetry_5m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    asset_id,
    metric,
    avg(value) AS avg_value,
    min(value) AS min_value,
    max(value) AS max_value,
    count(*) AS sample_count
FROM telemetry
GROUP BY bucket, asset_id, metric
WITH NO DATA;

-- Refresh policy: keep 5-minute rollups up to date.
SELECT add_continuous_aggregate_policy('telemetry_5m',
    start_offset => INTERVAL '1 hour',
    end_offset   => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes',
    if_not_exists => TRUE
);

-- Retention policy: keep raw telemetry for 90 days.
SELECT add_retention_policy('telemetry', INTERVAL '90 days', if_not_exists => TRUE);

-- ── Network Events (raw OT events from DPI sensor) ────────────────────────────
CREATE TABLE ot_events (
    time        TIMESTAMPTZ NOT NULL,
    event_id    VARCHAR(36) NOT NULL,
    sensor_id   VARCHAR(100) NOT NULL,
    src_ip      INET,
    dst_ip      INET,
    protocol    VARCHAR(50) NOT NULL,
    severity    VARCHAR(20) NOT NULL,
    event_data  JSONB NOT NULL,
    anomalies   JSONB NOT NULL DEFAULT '[]'
);

SELECT create_hypertable('ot_events', 'time',
    chunk_time_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

CREATE INDEX ON ot_events (protocol, time DESC);
CREATE INDEX ON ot_events (src_ip, time DESC);
CREATE INDEX ON ot_events (sensor_id, time DESC);
CREATE INDEX ON ot_events (severity, time DESC) WHERE severity IN ('high', 'critical');

-- Retention: keep raw OT events for 30 days (NERC CIP-015 minimum).
SELECT add_retention_policy('ot_events', INTERVAL '30 days', if_not_exists => TRUE);

GRANT SELECT, INSERT ON telemetry TO orhashield;
GRANT SELECT, INSERT ON ot_events TO orhashield;
GRANT SELECT ON telemetry_5m TO orhashield;
