import React, { useEffect, useState } from "react";
import { api } from "../api";
import SensorCard from "./SensorCard";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";

export default function Dashboard() {
  const [latest, setLatest] = useState([]);
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState(null);

  async function fetchLatest() {
    try {
      const { data } = await api.get("/telemetry/latest");
      setLatest(data);
      if (!selected && data.length) setSelected(data[0].device_id);
    } catch {}
  }

  async function fetchHistory(device_id) {
    if (!device_id) return;
    try {
      const { data } = await api.get(`/telemetry/?device_id=${device_id}&limit=60`);
      setHistory(
        data
          .slice()
          .reverse()
          .map((r) => ({
            t: new Date(r.recorded_at).toLocaleTimeString(),
            temperature: r.temperature,
            load_pct: r.load_pct,
          }))
      );
    } catch {}
  }

  useEffect(() => {
    fetchLatest();
    const id = setInterval(fetchLatest, 3000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!selected) return;
    fetchHistory(selected);
    const id = setInterval(() => fetchHistory(selected), 3000);
    return () => clearInterval(id);
  }, [selected]);

  return (
    <div className="dash" data-testid="dashboard">
      <header className="dash-head">
        <div>
          <h1>Live Telemetry</h1>
          <p className="muted">Real-time edge device monitoring · auto refresh 3s</p>
        </div>
      </header>

      <section className="card-grid">
        {latest.length === 0 && <div className="muted">Waiting for telemetry…</div>}
        {latest.map((t) => (
          <SensorCard
            key={t.device_id}
            telemetry={t}
            active={selected === t.device_id}
            onClick={() => setSelected(t.device_id)}
          />
        ))}
      </section>

      <section className="panel">
        <header className="panel-head">
          <h2>{selected ? `History · ${selected}` : "Select a device"}</h2>
        </header>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="t" stroke="var(--muted)" />
              <YAxis stroke="var(--muted)" />
              <Tooltip
                contentStyle={{
                  background: "var(--panel)",
                  border: "1px solid var(--border)",
                  color: "var(--text)",
                }}
              />
              <Line type="monotone" dataKey="temperature" stroke="#ff7849" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="load_pct" stroke="#3ec1a3" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
