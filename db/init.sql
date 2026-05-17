-- Schema for IoT Edge Device Monitoring Platform

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer', -- 'admin' | 'operator' | 'viewer'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    location VARCHAR(120),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    temperature DOUBLE PRECISION,
    load_pct DOUBLE PRECISION,
    position_x DOUBLE PRECISION,
    position_y DOUBLE PRECISION,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_device_time ON telemetry (device_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    metric VARCHAR(32) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    severity VARCHAR(16) NOT NULL DEFAULT 'warning',
    acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts (created_at DESC);

-- Default admin: username=admin password=admin123 (bcrypt hash). Change on first login.
INSERT INTO users (username, password_hash, role)
VALUES ('admin', '$2b$10$JDyYrsFNQagO69mg0ZsYnuAh1iE3njKzEuMwHMKFuZIn0Rq/d8TYe', 'admin')
ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, password_hash, role)
VALUES ('viewer', '$2b$10$q7fDltQE06I.bwh8eikkq./KRM5byz7jOeDngblXuVrpFtM30FIPO', 'viewer')
ON CONFLICT (username) DO NOTHING;

INSERT INTO devices (device_id, name, location) VALUES
    ('edge-001', 'Press Line A', 'Plant 1 / Bay 3'),
    ('edge-002', 'CNC Mill B', 'Plant 1 / Bay 5'),
    ('edge-003', 'Conveyor C', 'Plant 2 / Bay 1')
ON CONFLICT (device_id) DO NOTHING;
