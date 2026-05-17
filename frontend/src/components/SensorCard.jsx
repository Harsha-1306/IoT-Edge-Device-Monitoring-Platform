import React from "react";

export default function SensorCard({ telemetry, active, onClick }) {
  const t = telemetry;
  const tempHot = t.temperature > 75;
  const loadHigh = t.load_pct > 90;
  return (
    <button
      onClick={onClick}
      className={`sensor-card ${active ? "active" : ""}`}
      data-testid={`sensor-card-${t.device_id}`}
    >
      <header className="sc-head">
        <div className="sc-id">{t.device_id}</div>
        <div className={`sc-dot ${tempHot || loadHigh ? "warn" : "ok"}`} />
      </header>
      <div className="sc-row">
        <div className="metric">
          <span className="m-label">Temp</span>
          <span className={`m-value ${tempHot ? "hot" : ""}`}>
            {t.temperature?.toFixed(1)}°C
          </span>
        </div>
        <div className="metric">
          <span className="m-label">Load</span>
          <span className={`m-value ${loadHigh ? "hot" : ""}`}>
            {t.load_pct?.toFixed(1)}%
          </span>
        </div>
      </div>
      <div className="sc-row">
        <div className="metric">
          <span className="m-label">Pos X</span>
          <span className="m-value sub">{t.position_x?.toFixed(1)}</span>
        </div>
        <div className="metric">
          <span className="m-label">Pos Y</span>
          <span className="m-value sub">{t.position_y?.toFixed(1)}</span>
        </div>
      </div>
      <footer className="sc-foot">
        Updated {new Date(t.recorded_at).toLocaleTimeString()}
      </footer>
    </button>
  );
}
