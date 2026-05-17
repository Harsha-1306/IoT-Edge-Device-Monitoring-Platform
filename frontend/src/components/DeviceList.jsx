import React, { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function DeviceList() {
  const { user } = useAuth();
  const [devices, setDevices] = useState([]);
  const [form, setForm] = useState({ device_id: "", name: "", location: "" });
  const [err, setErr] = useState("");

  async function load() {
    const { data } = await api.get("/devices/");
    setDevices(data);
  }
  useEffect(() => { load(); }, []);

  async function submit(e) {
    e.preventDefault();
    setErr("");
    try {
      await api.post("/devices/", form);
      setForm({ device_id: "", name: "", location: "" });
      load();
    } catch (e) {
      setErr(e.response?.data?.error || "Failed");
    }
  }

  return (
    <div className="dash" data-testid="devices-page">
      <header className="dash-head">
        <div>
          <h1>Devices</h1>
          <p className="muted">Registered edge endpoints</p>
        </div>
      </header>
      <div className="panel">
        <table className="table">
          <thead>
            <tr><th>Device ID</th><th>Name</th><th>Location</th></tr>
          </thead>
          <tbody>
            {devices.map((d) => (
              <tr key={d.id} data-testid={`device-row-${d.device_id}`}>
                <td className="mono">{d.device_id}</td>
                <td>{d.name}</td>
                <td>{d.location || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {user?.role === "admin" && (
        <div className="panel">
          <header className="panel-head"><h2>Register device</h2></header>
          <form className="form-row" onSubmit={submit}>
            <input
              data-testid="device-id-input"
              placeholder="device_id"
              value={form.device_id}
              onChange={(e) => setForm({ ...form, device_id: e.target.value })}
              required
            />
            <input
              data-testid="device-name-input"
              placeholder="Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
            <input
              data-testid="device-location-input"
              placeholder="Location"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
            />
            <button data-testid="device-create-button" type="submit">Add device</button>
            {err && <span className="error">{err}</span>}
          </form>
        </div>
      )}
    </div>
  );
}
