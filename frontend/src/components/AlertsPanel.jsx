import React, { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function AlertsPanel() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [showAck, setShowAck] = useState(false);

  async function load() {
    try {
      const { data } = await api.get(`/alerts/?acknowledged=${showAck}`);
      setAlerts(data);
    } catch {}
  }

  useEffect(() => {
    load();
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, [showAck]);

  async function ack(id) {
    await api.post(`/alerts/${id}/ack`);
    load();
  }

  const canAck = user && (user.role === "admin" || user.role === "operator");

  return (
    <div className="dash" data-testid="alerts-page">
      <header className="dash-head">
        <div>
          <h1>Alerts</h1>
          <p className="muted">Threshold breaches from telemetry pipeline</p>
        </div>
        <label className="switch">
          <input
            type="checkbox"
            data-testid="show-ack-toggle"
            checked={showAck}
            onChange={(e) => setShowAck(e.target.checked)}
          />
          <span>Show acknowledged</span>
        </label>
      </header>
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Device</th>
              <th>Metric</th>
              <th>Value</th>
              <th>Threshold</th>
              <th>Severity</th>
              <th>Time</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 && (
              <tr><td colSpan={7} className="muted center">No active alerts</td></tr>
            )}
            {alerts.map((a) => (
              <tr key={a.id} data-testid={`alert-row-${a.id}`}>
                <td>{a.device_id}</td>
                <td>{a.metric}</td>
                <td>{a.value?.toFixed(2)}</td>
                <td>{a.threshold}</td>
                <td>
                  <span className={`pill ${a.severity}`}>{a.severity}</span>
                </td>
                <td>{new Date(a.created_at).toLocaleString()}</td>
                <td>
                  {!a.acknowledged && canAck && (
                    <button
                      className="link"
                      data-testid={`ack-button-${a.id}`}
                      onClick={() => ack(a.id)}
                    >
                      Acknowledge
                    </button>
                  )}
                  {a.acknowledged && <span className="muted">acked</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
