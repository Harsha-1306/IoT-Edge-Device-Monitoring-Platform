IoT Edge Device Monitoring Platform

**Tech stack:** Python · Flask · MQTT (Eclipse Mosquitto) · PostgreSQL · Docker Compose · React · REST APIs

A cloud-native real-time monitoring platform that ingests IoT sensor telemetry (temperature, load,
position) into PostgreSQL via an MQTT broker, exposes a Flask REST API with JWT-based
role-based access control, raises threshold alerts, and visualises everything in a React dashboard
with a dark/light theme.

## Architecture

```
+----------------+      MQTT       +-------------+      SQL       +--------------+
|  Edge devices  |  ── publish ──▶ |  Mosquitto  | ── subscribe ─▶|  Flask API   |
|  (simulator)   |   iot/<id>/...  |   broker    |                |  + workers    |
+----------------+                 +-------------+                +-------┬------+
                                                                          ▼
                                                                  +---------------+
                                                                  |  PostgreSQL   |
                                                                  +---------------+
                                                                          ▲
                                                                          │ REST /api
                                                                  +---------------+
                                                                  | React frontend|
                                                                  +---------------+
```

## Services

| Service     | Image / Build           | Port (host) | Purpose                                       |
|-------------|-------------------------|-------------|-----------------------------------------------|
| `postgres`  | `postgres:16-alpine`    | 5432        | Telemetry datastore                           |
| `mosquitto` | `eclipse-mosquitto:2`   | 1883 / 9001 | MQTT broker (TCP + WebSockets)                |
| `backend`   | `./backend` (Flask)     | 5001 → 5000 | REST API + MQTT subscriber + alerting         |
| `simulator` | `./simulator`           | —           | Publishes synthetic telemetry for N devices   |
| `frontend`  | `./frontend` (React)    | 3000 → 80   | Dashboard, alerts, devices, RBAC-aware UI     |

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Dashboard: <http://localhost:3000>
- REST API:  <http://localhost:5001/api/health>
- MQTT:      `mqtt://localhost:1883`  (topic pattern `iot/+/telemetry`)

## Default users (seeded)

| Username | Password   | Role     |
|----------|------------|----------|
| `admin`  | `admin123` | admin    |
| `viewer` | `viewer123`| viewer   |

> Created on first run via `db/init.sql`. Change them after first login. Admins can create more
> users via `POST /api/auth/register`.

## REST API

All endpoints are JSON; protected endpoints require `Authorization: Bearer <token>`.

| Method | Path                          | Role           | Description                          |
|--------|-------------------------------|----------------|--------------------------------------|
| POST   | `/api/auth/login`             | public         | Returns JWT                          |
| POST   | `/api/auth/register`          | admin          | Create a new user                    |
| GET    | `/api/auth/me`                | any            | Current user                         |
| GET    | `/api/devices/`               | any            | List devices                         |
| POST   | `/api/devices/`               | admin          | Register a device                    |
| GET    | `/api/telemetry/`             | any            | Recent telemetry (filter `device_id`)|
| GET    | `/api/telemetry/latest`       | any            | Latest reading per device            |
| POST   | `/api/telemetry/`             | admin/operator | Ingest via HTTP                      |
| GET    | `/api/alerts/`                | any            | Open or all alerts                   |
| POST   | `/api/alerts/<id>/ack`        | admin/operator | Acknowledge an alert                 |

### Example: log in and read telemetry

```bash
TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

curl -s http://localhost:5001/api/telemetry/latest \
  -H "Authorization: Bearer $TOKEN" | jq
```

## MQTT contract

Topic: `iot/<device_id>/telemetry`

Payload:

```json
{
  "device_id": "edge-001",
  "temperature": 68.4,
  "load_pct": 72.1,
  "position_x": 51.2,
  "position_y": 49.8,
  "ts": 1714659300
}
```

## Thresholds

Configured via `TEMP_THRESHOLD` and `LOAD_THRESHOLD` env vars. The Flask MQTT subscriber writes
breaches to the `alerts` table. The dashboard polls `/api/alerts/` every 3 seconds.

## RBAC

| Role     | Read telemetry | Acknowledge alerts | Ingest via HTTP | Manage devices/users |
|----------|----------------|--------------------|-----------------|----------------------|
| viewer   | ✅              | ❌                 | ❌              | ❌                   |
| operator | ✅              | ✅                 | ✅              | ❌                   |
| admin    | ✅              | ✅                 | ✅              | ✅                   |

## Development

Run services individually (Postgres + Mosquitto via Compose, app locally):

```bash
docker compose up -d postgres mosquitto
cd backend && pip install -r requirements.txt && DATABASE_URL=postgresql://iot:iotpass@localhost:5432/iot_telemetry MQTT_HOST=localhost python app.py
cd ../frontend && yarn && yarn start
```

## Cloud migration

Because every service is a container with explicit env-var configuration, the same `docker-compose.yml`
can be lifted to ECS, GKE Autopilot, or a single VM. PostgreSQL can be swapped for a managed DB by
changing `DATABASE_URL`; MQTT can be swapped for HiveMQ Cloud / AWS IoT Core by changing
`MQTT_HOST`/`MQTT_PORT` (and adding TLS).
"# IoT-Edge-Device-Monitoring-Platform" 
