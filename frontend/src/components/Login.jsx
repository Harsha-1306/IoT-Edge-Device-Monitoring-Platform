import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [username, setU] = useState("admin");
  const [password, setP] = useState("admin123");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setErr("");
    try {
      await login(username, password);
      nav("/");
    } catch (e) {
      setErr(e.response?.data?.error || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={submit} data-testid="login-form">
        <div className="login-brand">
          <span className="brand-mark big" />
          <div>
            <h1>EdgeWatch</h1>
            <p>IoT Edge Device Monitoring</p>
          </div>
        </div>
        <label>Username</label>
        <input
          data-testid="login-username"
          value={username}
          onChange={(e) => setU(e.target.value)}
          autoComplete="username"
        />
        <label>Password</label>
        <input
          data-testid="login-password"
          type="password"
          value={password}
          onChange={(e) => setP(e.target.value)}
          autoComplete="current-password"
        />
        {err && <div className="error" data-testid="login-error">{err}</div>}
        <button type="submit" disabled={busy} data-testid="login-submit">
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <div className="login-hint">Default: admin / admin123 — viewer / viewer123</div>
      </form>
    </div>
  );
}
