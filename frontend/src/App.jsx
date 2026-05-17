import React from "react";
import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import AlertsPanel from "./components/AlertsPanel";
import DeviceList from "./components/DeviceList";

function Layout({ children }) {
  const { user, logout, theme, setTheme } = useAuth();
  const nav = useNavigate();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" />
          <div>
            <div className="brand-title">EdgeWatch</div>
            <div className="brand-sub">IoT Telemetry</div>
          </div>
        </div>
        <nav className="nav">
          <Link to="/" data-testid="nav-dashboard">Dashboard</Link>
          <Link to="/alerts" data-testid="nav-alerts">Alerts</Link>
          <Link to="/devices" data-testid="nav-devices">Devices</Link>
        </nav>
        <div className="sidebar-footer">
          <button
            className="theme-toggle"
            data-testid="theme-toggle"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </button>
          {user && (
            <div className="user-box">
              <div className="user-info">
                <div className="user-name">{user.username}</div>
                <div className="user-role">{user.role}</div>
              </div>
              <button
                className="logout"
                data-testid="logout-button"
                onClick={() => { logout(); nav("/login"); }}
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

function RequireAuth({ children }) {
  const { user } = useAuth();
  const hasToken = !!localStorage.getItem("token");
  if (!hasToken) return <Navigate to="/login" replace />;
  if (!user) return <div className="loading">Loading…</div>;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={<RequireAuth><Layout><Dashboard /></Layout></RequireAuth>}
      />
      <Route
        path="/alerts"
        element={<RequireAuth><Layout><AlertsPanel /></Layout></RequireAuth>}
      />
      <Route
        path="/devices"
        element={<RequireAuth><Layout><DeviceList /></Layout></RequireAuth>}
      />
    </Routes>
  );
}
