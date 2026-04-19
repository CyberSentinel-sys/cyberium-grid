-- OrHaShield PostgreSQL Schema
-- Version: 0.1.0
-- Run by docker-entrypoint-initdb.d on first start.

-- ── Extensions ───────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "citext";    -- case-insensitive text for emails

-- ── Assets (OT device inventory) ─────────────────────────────────────────────
CREATE TABLE assets (
    asset_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_address      INET NOT NULL,
    mac_address     MACADDR,
    vendor          VARCHAR(255),
    model           VARCHAR(255),
    hostname        VARCHAR(255),
    -- Purdue level: 0=field, 1=basic control, 2=area supervisory, 3=site ops, 4=DMZ (3.5), 5=enterprise
    purdue_level    SMALLINT NOT NULL DEFAULT 3 CHECK (purdue_level BETWEEN 0 AND 5),
    criticality     VARCHAR(20) NOT NULL DEFAULT 'medium'
                    CHECK (criticality IN ('info', 'low', 'medium', 'high', 'critical')),
    protocols       TEXT[] NOT NULL DEFAULT '{}',
    firmware_version VARCHAR(100),
    site_id         VARCHAR(100) NOT NULL DEFAULT 'default',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assets_ip ON assets (ip_address);
CREATE INDEX idx_assets_site ON assets (site_id);
CREATE INDEX idx_assets_purdue ON assets (purdue_level);

-- ── Alerts (security events) ──────────────────────────────────────────────────
CREATE TABLE alerts (
    alert_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID REFERENCES assets (asset_id) ON DELETE SET NULL,
    severity        VARCHAR(20) NOT NULL
                    CHECK (severity IN ('info', 'low', 'medium', 'high', 'critical')),
    description     TEXT NOT NULL,
    raw_event_id    VARCHAR(255),
    rule_id         VARCHAR(100),
    mitre_technique VARCHAR(20),
    acknowledged    BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMPTZ,
    session_id      UUID,  -- links to the LangGraph session that processed this alert
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_severity ON alerts (severity);
CREATE INDEX idx_alerts_asset ON alerts (asset_id);
CREATE INDEX idx_alerts_created ON alerts (created_at DESC);
CREATE INDEX idx_alerts_unacked ON alerts (acknowledged) WHERE NOT acknowledged;

-- ── Agent Decisions (WORM — never UPDATE or DELETE) ───────────────────────────
CREATE TABLE agent_decisions (
    decision_id     BIGSERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    action_id       UUID NOT NULL,
    action_class    VARCHAR(50) NOT NULL,
    asset_id        UUID,
    purdue_level    SMALLINT,
    decision        VARCHAR(20) NOT NULL CHECK (decision IN ('allow', 'deny', 'escalate')),
    reason          TEXT NOT NULL,
    confidence      FLOAT,
    severity        VARCHAR(20),
    model_used      VARCHAR(100),
    policy_version  VARCHAR(50),
    twin_verified   BOOLEAN NOT NULL DEFAULT FALSE,
    proposed_by     VARCHAR(100),
    decided_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- NO updated_at. This table is append-only (WORM semantics enforced below).
);

CREATE INDEX idx_decisions_session ON agent_decisions (session_id);
CREATE INDEX idx_decisions_decided ON agent_decisions (decided_at DESC);
CREATE INDEX idx_decisions_decision ON agent_decisions (decision);

-- ── Human Approvals (WORM) ────────────────────────────────────────────────────
CREATE TABLE human_approvals (
    approval_id     BIGSERIAL PRIMARY KEY,
    action_id       UUID NOT NULL,
    approved        BOOLEAN NOT NULL,
    approver_id     VARCHAR(255) NOT NULL,
    notes           TEXT NOT NULL DEFAULT '',
    approved_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- Append-only: no UPDATE, no DELETE.
);

CREATE INDEX idx_approvals_action ON human_approvals (action_id);
CREATE INDEX idx_approvals_approver ON human_approvals (approver_id);

-- ── Audit Log (WORM — all system events) ─────────────────────────────────────
CREATE TABLE audit_log (
    log_id          BIGSERIAL PRIMARY KEY,
    event_type      VARCHAR(100) NOT NULL,
    actor_id        VARCHAR(255),
    resource_type   VARCHAR(100),
    resource_id     VARCHAR(255),
    details         JSONB,
    logged_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_type ON audit_log (event_type);
CREATE INDEX idx_audit_logged ON audit_log (logged_at DESC);

-- ── Site Policies (operator-configured relaxations) ───────────────────────────
CREATE TABLE site_policies (
    policy_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id         VARCHAR(100) NOT NULL,
    action_class    VARCHAR(50) NOT NULL,
    purdue_level    SMALLINT NOT NULL,
    allow_autonomous BOOLEAN NOT NULL DEFAULT FALSE,
    requires_dual_approval BOOLEAN NOT NULL DEFAULT TRUE,
    justification   TEXT NOT NULL,
    created_by      VARCHAR(255) NOT NULL,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── WORM Enforcement via Row-Level Security ───────────────────────────────────
-- The application role (orhashield_app) can only INSERT, never UPDATE or DELETE.

CREATE ROLE orhashield_app;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO orhashield_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO orhashield_app;

-- Revoke dangerous privileges on WORM tables.
REVOKE UPDATE, DELETE ON agent_decisions FROM orhashield_app;
REVOKE UPDATE, DELETE ON human_approvals FROM orhashield_app;
REVOKE UPDATE, DELETE ON audit_log FROM orhashield_app;

-- Row-level security as defense-in-depth.
ALTER TABLE agent_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY worm_insert_only ON agent_decisions FOR INSERT TO orhashield_app WITH CHECK (true);
CREATE POLICY worm_select_only ON agent_decisions FOR SELECT TO orhashield_app USING (true);

CREATE POLICY worm_insert_only ON human_approvals FOR INSERT TO orhashield_app WITH CHECK (true);
CREATE POLICY worm_select_only ON human_approvals FOR SELECT TO orhashield_app USING (true);

CREATE POLICY worm_insert_only ON audit_log FOR INSERT TO orhashield_app WITH CHECK (true);
CREATE POLICY worm_select_only ON audit_log FOR SELECT TO orhashield_app USING (true);

-- Grant superuser access to the orhashield user (dev convenience; restrict in prod).
GRANT ALL ON ALL TABLES IN SCHEMA public TO orhashield;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO orhashield;
