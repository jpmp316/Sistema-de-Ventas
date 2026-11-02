import { useState } from "react";
import { ChevronDown } from "lucide-react";
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
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [loginError, setLoginError] = useState("");
  const [busy, setBusy] = useState(false);
  const isAdmin = session?.role === "admin";
  const currentView = !isAdmin && !["ventas", "inventario", "mi contraseña"].includes(vistaActual) ? "ventas" : vistaActual;

  async function closeSession() {
    setBusy(true);
    setProfileMenuOpen(false);
    await logout();
    setCredentials({ username: "", password: "" });
    setBusy(false);
  }

  async function login(event) {
    event.preventDefault(); setBusy(true); setLoginError("");
    try {
      const next = await authenticate(credentials.username, credentials.password);
      if (!["admin", "vendedor"].includes(next.role)) {
        await logout(next.token);
        setLoginError("Esta cuenta no tiene un rol habilitado.");
      } else {
        setVistaActual(next.role === "admin" ? "resumen" : "ventas");
        setCredentials({ username: "", password: "" });
      }
    } catch (error) { setLoginError(error.message); }
    finally { setBusy(false); }
  }

  if (!session) return <main className="auth-screen"><form className="panel new-product-form auth-card" onSubmit={login}>
    <div className="brand-mark">N</div><p className="eyebrow">NEXO · VENTAS E INVENTARIO</p><h1>Iniciar sesión</h1>
    <label className="new-product-field"><span>Usuario</span><input autoComplete="username" required value={credentials.username} onChange={e => setCredentials({...credentials, username:e.target.value})}/></label>
    <label className="new-product-field"><span>Contraseña</span><input type="password" autoComplete="current-password" required value={credentials.password} onChange={e => setCredentials({...credentials, password:e.target.value})}/></label>
    {loginError && <p className="new-product-error" role="alert">{loginError}</p>}
    <button className="primary-button" disabled={busy}>{busy ? "Validando…" : "Entrar"}</button>
  </form></main>;

  return <div className="app-layout"><Sidebar vistaActual={currentView} onCambiarVista={setVistaActual} role={session.role}/><main className="main-content">
    <header className="topbar"><div className="mobile-brand">Nexo</div><div className="topbar-spacer"/><div className="profile-menu"><button className="profile-button" aria-expanded={profileMenuOpen} onClick={() => setProfileMenuOpen((open) => !open)}><span className="avatar">{session.username.slice(0,1).toUpperCase()}</span><span>{session.username} · {isAdmin ? "Administrador" : "Vendedor"}</span><ChevronDown size={16}/></button>{profileMenuOpen && <div className="profile-menu-dropdown"><button type="button" disabled={busy} onClick={closeSession}>Cerrar sesión</button></div>}</div></header>
    {isAdmin && currentView === "resumen" && <Dashboard/>}{isAdmin && currentView === "estadísticas" && <Statistics/>}{isAdmin && currentView === "productos" && <Products/>}{currentView === "ventas" && <Sales/>}{currentView === "inventario" && <Inventory/>}{session.role === "vendedor" && currentView === "mi contraseña" && <ChangePassword/>}
    {isAdmin && currentView === "usuarios" && <Users/>}
  </main></div>;
}
export default function AppWithAuth() { return <AuthProvider><App /></AuthProvider>; }
