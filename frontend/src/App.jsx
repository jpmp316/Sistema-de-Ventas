import { useState } from "react";
import { Bell, ChevronDown, Search, UserPlus } from "lucide-react";
import Sidebar from "./components/Sidebar";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import { apiRequest } from "./api";
import { AuthProvider, useAuth } from "./auth/AuthContext";

function App() {
  const { session, login: authenticate, logout } = useAuth();
  const [vistaActual, setVistaActual] = useState("resumen");
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [loginError, setLoginError] = useState("");
  const [userForm, setUserForm] = useState({ username: "", password: "" });
  const [userMessage, setUserMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function login(event) {
    event.preventDefault(); setBusy(true); setLoginError("");
    try {
      const next = await authenticate(credentials.username, credentials.password);
      if (next.role !== "admin") { logout(); setLoginError("La cuenta de vendedor está preparada; su acceso estará disponible en una siguiente etapa."); }
    } catch (error) { setLoginError(error.message); }
    finally { setBusy(false); }
  }

  async function createSeller(event) {
    event.preventDefault(); setBusy(true); setUserMessage("");
    try {
      await apiRequest("/users/", { method: "POST", token: session.token, body: JSON.stringify(userForm) });
      setUserForm({ username: "", password: "" }); setUserMessage("Cuenta de vendedor creada.");
    } catch (error) { setUserMessage(error.message); }
    finally { setBusy(false); }
  }

  if (!session) return <main className="auth-screen"><form className="panel new-product-form auth-card" onSubmit={login}>
    <div className="brand-mark">N</div><p className="eyebrow">NEXO · VENTAS E INVENTARIO</p><h1>Iniciar sesión</h1>
    <label className="new-product-field"><span>Usuario</span><input autoComplete="username" required value={credentials.username} onChange={e => setCredentials({...credentials, username:e.target.value})}/></label>
    <label className="new-product-field"><span>Contraseña</span><input type="password" autoComplete="current-password" required value={credentials.password} onChange={e => setCredentials({...credentials, password:e.target.value})}/></label>
    {loginError && <p className="new-product-error" role="alert">{loginError}</p>}
    <button className="primary-button" disabled={busy}>{busy ? "Validando…" : "Entrar"}</button>
  </form></main>;

  return <div className="app-layout"><Sidebar vistaActual={vistaActual} onCambiarVista={setVistaActual}/><main className="main-content">
    <header className="topbar"><div className="mobile-brand">Nexo</div><div className="topbar-spacer"/><label className="search-box"><Search size={18}/><input type="search" placeholder="Buscar..."/></label><button className="icon-button" aria-label="Notificaciones"><Bell size={20}/><span className="notification-dot"/></button><div className="profile-menu"><button className="profile-button" aria-expanded={profileMenuOpen} onClick={() => setProfileMenuOpen((open) => !open)}><span className="avatar">{session.username.slice(0,1).toUpperCase()}</span><span>{session.username} · Administrador</span><ChevronDown size={16}/></button>{profileMenuOpen && <div className="profile-menu-dropdown"><button type="button" onClick={logout}>Cerrar sesión</button></div>}</div></header>
    {vistaActual === "resumen" && <Dashboard/>}{vistaActual === "productos" && <Products/>}
    {vistaActual === "usuarios" && <section className="panel new-product-form"><h1>Crear vendedor</h1><p>La contraseña inicial se guardará usando hash seguro en el backend.</p><form onSubmit={createSeller} className="new-product-fields"><label className="new-product-field"><span>Usuario</span><input required minLength="3" maxLength="50" value={userForm.username} onChange={e=>setUserForm({...userForm,username:e.target.value})}/></label><label className="new-product-field"><span>Contraseña inicial</span><input type="password" required minLength="6" value={userForm.password} onChange={e=>setUserForm({...userForm,password:e.target.value})}/></label><button className="primary-button" disabled={busy}><UserPlus size={17}/> Crear vendedor</button></form>{userMessage&&<p role="status">{userMessage}</p>}</section>}
  </main></div>;
}
export default function AppWithAuth() { return <AuthProvider><App /></AuthProvider>; }
