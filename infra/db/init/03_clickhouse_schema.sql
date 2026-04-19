-- OrHaShield ClickHouse Analytics Schema
-- Used for high-throughput analytics queries over OT event data.

CREATE DATABASE IF NOT EXISTS orhashield;

-- ── Packet analytics (high-volume DPI sensor output) ─────────────────────────
CREATE TABLE IF NOT EXISTS orhashield.packet_stats (
    event_date  Date MATERIALIZED toDate(timestamp),
    timestamp   DateTime64(3) NOT NULL,
    sensor_id   LowCardinality(String) NOT NULL,
    src_ip      IPv4,
    dst_ip      IPv4,
    protocol    LowCardinality(String) NOT NULL,
    bytes       UInt32 DEFAULT 0,
    severity    LowCardinality(String) DEFAULT 'info'
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (sensor_id, protocol, timestamp)
TTL event_date + INTERVAL 90 DAY;

-- ── Anomaly analytics ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orhashield.anomalies (
    event_date  Date MATERIALIZED toDate(detected_at),
    detected_at DateTime64(3) NOT NULL,
    rule_id     LowCardinality(String) NOT NULL,
    severity    LowCardinality(String) NOT NULL,
    protocol    LowCardinality(String) NOT NULL,
    src_ip      IPv4,
    mitre_technique LowCardinality(String) DEFAULT ''
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (rule_id, severity, detected_at)
TTL event_date + INTERVAL 180 DAY;

-- ── Materialized views for dashboard KPIs ────────────────────────────────────
CREATE MATERIALIZED VIEW IF NOT EXISTS orhashield.anomalies_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, rule_id, severity)
AS SELECT
    toStartOfHour(detected_at) AS hour,
    rule_id,
    severity,
    count() AS count
FROM orhashield.anomalies
GROUP BY hour, rule_id, severity;
