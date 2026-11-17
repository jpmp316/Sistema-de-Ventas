import { useState } from "react";
import {
  ArrowUpRight,
  Boxes,
  ChevronDown,
  LockKeyhole,
  LogOut,
  ShoppingBag,
  ChartNoAxesCombined,
} from "lucide-react";
import Sidebar from "./components/Sidebar";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import Sales from "./pages/Sales";
import Inventory from "./pages/Inventory";
import Statistics from "./pages/Statistics";
import ChangePassword from "./pages/ChangePassword";
import Users from "./pages/Users";
import { AuthProvider, useAuth } from "./auth/AuthContext";

function App() {
  const { session, login: authenticate, logout } = useAuth();
  const [vistaActual, setVistaActual] = useState("resumen");
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [credentials, setCredentials] = useState({
    username: "",
    password: "",
  });
  const [loginError, setLoginError] = useState("");
  const [busy, setBusy] = useState(false);
  const isAdmin = session?.role === "admin";
  const currentView =
    !isAdmin && !["ventas", "inventario", "mi contraseña"].includes(vistaActual)
      ? "ventas"
      : vistaActual;

  async function closeSession() {
    setBusy(true);
    setProfileMenuOpen(false);
    await logout();
    setCredentials({ username: "", password: "" });
    setBusy(false);
  }

  async function login(event) {
    event.preventDefault();
    setBusy(true);
    setLoginError("");
    try {
      const next = await authenticate(
        credentials.username,
        credentials.password,
      );
      if (!["admin", "vendedor"].includes(next.role)) {
        await logout(next.token);
        setLoginError("Esta cuenta no tiene un rol habilitado.");
      } else {
        setVistaActual(next.role === "admin" ? "resumen" : "ventas");
        setCredentials({ username: "", password: "" });
      }
    } catch (error) {
      setLoginError(error.message);
    } finally {
      setBusy(false);
    }
  }

  if (!session)
    return (
      <main className="auth-screen">
        <section className="auth-story" aria-label="Nexo, ventas e inventario">
          <div className="brand">
            <div className="brand-mark">N</div>
            <div>
              <h2>
                Nexo<span className="brand-period">.</span>
              </h2>
              <span>VENTAS E INVENTARIO</span>
            </div>
          </div>
          <div className="auth-story-content">
            <p className="auth-kicker">MENOS FRICCIÓN. MÁS CONTROL.</p>
            <h2>
              Todo tu negocio.
              <br />
              <em>En el mismo lugar.</em>
            </h2>
            <p>
              Conecta tus ventas, tu inventario y tu equipo. Una visión clara
              para cada decisión.
            </p>
            <div className="auth-illustration" aria-hidden="true">
              <div className="auth-orbit" />
              <div className="auth-hub">
                N<span>nexo</span>
              </div>
              <div className="auth-node auth-node-sales">
                <ShoppingBag size={22} />
                <span>Ventas</span>
              </div>
              <div className="auth-node auth-node-stock">
                <Boxes size={22} />
                <span>Inventario</span>
              </div>
              <div className="auth-node auth-node-reports">
                <ChartNoAxesCombined size={22} />
                <span>Reportes</span>
              </div>
            </div>
          </div>
          <p className="auth-story-footer">
            Un espacio para hacer crecer tu negocio.
            <ArrowUpRight size={18} />
          </p>
        </section>
        <section className="auth-form-side">
          <form className="panel new-product-form auth-card" onSubmit={login}>
            <div className="auth-welcome-icon">
              <LockKeyhole size={23} />
            </div>
            <div>
              <p className="eyebrow">BIENVENIDO A NEXO</p>
              <h1>Inicia sesión</h1>
              <p className="page-subtitle">
                Ingresa tus credenciales para continuar.
              </p>
            </div>
            <label className="new-product-field">
              <span>Usuario</span>
              <input
                autoComplete="username"
                required
                value={credentials.username}
                onChange={(e) =>
                  setCredentials({ ...credentials, username: e.target.value })
                }
              />
            </label>
            <label className="new-product-field">
              <span>Contraseña</span>
              <input
                type="password"
                autoComplete="current-password"
                required
                value={credentials.password}
                onChange={(e) =>
                  setCredentials({ ...credentials, password: e.target.value })
                }
              />
            </label>
            {loginError && (
              <p className="new-product-error" role="alert">
                {loginError}
              </p>
            )}
            <button className="primary-button" disabled={busy}>
              {busy ? "Validando…" : "Entrar a mi espacio"}
              <ArrowUpRight size={18} />
            </button>
            <p className="auth-footnote">
              <LockKeyhole size={14} /> Acceso exclusivo para tu equipo
            </p>
          </form>
          <p className="auth-bottom-note">
            Nexo · Gestión de ventas e inventario
          </p>
        </section>
      </main>
    );

  return (
    <div className="app-layout">
      <Sidebar
        vistaActual={currentView}
        onCambiarVista={setVistaActual}
        role={session.role}
      />
      <main className="main-content">
        <header className="topbar">
          <div className="workspace-breadcrumb">
            <span>Nexo</span>
            <span aria-hidden="true">/</span>
            <strong>{currentView}</strong>
          </div>
          <div className="topbar-spacer" />
          <div className="profile-menu">
            <button
              className="profile-button"
              aria-expanded={profileMenuOpen}
              onClick={() => setProfileMenuOpen((open) => !open)}
            >
              <span className="avatar">
                {session.username.slice(0, 1).toUpperCase()}
              </span>
              <span className="profile-identity">
                <strong>{session.username}</strong>
                <small>{isAdmin ? "Administrador" : "Vendedor"}</small>
              </span>
              <ChevronDown size={16} />
            </button>
            {profileMenuOpen && (
              <div className="profile-menu-dropdown">
                <button type="button" disabled={busy} onClick={closeSession}>
                  <LogOut size={16} />
                  Cerrar sesión
                </button>
              </div>
            )}
          </div>
        </header>
        {isAdmin && currentView === "resumen" && <Dashboard />}
        {isAdmin && currentView === "estadísticas" && <Statistics />}
        {isAdmin && currentView === "productos" && <Products />}
        {currentView === "ventas" && <Sales />}
        {currentView === "inventario" && <Inventory />}
        {session.role === "vendedor" && currentView === "mi contraseña" && (
          <ChangePassword />
        )}
        {isAdmin && currentView === "usuarios" && <Users />}
      </main>
    </div>
  );
}
export default function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}
