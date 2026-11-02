import { useEffect, useState } from "react";
import { UserPlus } from "lucide-react";
import { createSeller, deleteUser, getUsers, updateUser } from "../api";
import { useAuth } from "../auth/AuthContext";
import { isSecurePassword, PASSWORD_HELP } from "../passwordPolicy";

const emptyForm = { username: "", password: "" };
const roleName = role => ({ admin: "Administrador", vendedor: "Vendedor" }[role] ?? role);

export default function Users() {
  const { token, session } = useAuth();
  const [result, setResult] = useState({ items: [], total: 0, total_pages: 0 });
  const [page, setPage] = useState(1);
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [removing, setRemoving] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;
    getUsers(token, page).then(data => {
      if (!active) return;
      if (page > Math.max(1, data.total_pages)) { setPage(Math.max(1, data.total_pages)); return; }
      setResult(data);
    }).catch(err => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [token, page, revision]);

  function resetForm() { setEditing(null); setForm(emptyForm); }
  function refresh() { setLoading(true); setRevision(value => value + 1); }
  function edit(user) {
    setEditing(user); setForm({ username: user.username, password: "" });
    setRemoving(null); setError(""); setMessage("");
    document.getElementById("managed-username")?.focus();
  }
  async function save(event) {
    event.preventDefault();
    if (busy) return;
    setError(""); setMessage("");
    if ((!editing || form.password) && !isSecurePassword(form.password)) { setError(PASSWORD_HELP); return; }
    setBusy(true);
    try {
      const data = { username: form.username.trim() };
      if (form.password) data.password = form.password;
      if (editing) {
        const saved = await updateUser(token, editing.id, data);
        setResult(current => ({ ...current, items: current.items.map(user => user.id === saved.id ? saved : user) }));
        setMessage("Usuario actualizado.");
      } else {
        await createSeller(token, data);
        setMessage("Cuenta de vendedor creada."); setPage(1); refresh();
      }
      resetForm();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  async function remove() {
    if (busy || !removing) return;
    setBusy(true); setError(""); setMessage("");
    try {
      await deleteUser(token, removing.id);
      setRemoving(null); setMessage("Usuario eliminado."); refresh();
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <>
    <section className="page-heading"><div><p className="eyebrow">ADMINISTRACIÓN</p><h1>Usuarios</h1><p className="page-subtitle">Consulta los roles y gestiona las cuentas del negocio.</p></div></section>
    <section className="panel new-product-form">
      <h2>{editing ? `Editar usuario · ${roleName(editing.role)}` : "Crear vendedor"}</h2>
      <form onSubmit={save}>
        <div className="new-product-fields">
          <label className="new-product-field"><span>Usuario</span><input id="managed-username" required minLength={3} maxLength={50} pattern="[\p{L}\p{N}_\-]+" title="Letras, números, guion y guion bajo" disabled={busy} value={form.username} onChange={event=>setForm({...form,username:event.target.value})}/></label>
          <label className="new-product-field"><span>{editing ? "Nueva contraseña (opcional)" : "Contraseña inicial"}</span><input type="password" autoComplete="new-password" required={!editing} minLength={8} maxLength={128} disabled={busy} aria-describedby="managed-password-help" value={form.password} onChange={event=>setForm({...form,password:event.target.value})}/><small id="managed-password-help">{PASSWORD_HELP} {editing && "Déjala vacía para conservar la actual."}</small></label>
        </div>
        <div className="new-product-form-actions users-form-actions">
          {editing && <button type="button" className="subtle-button" disabled={busy} onClick={resetForm}>Cancelar edición</button>}
          <button className="primary-button" disabled={busy}>{!editing && <UserPlus size={17}/>} {busy ? "Guardando…" : editing ? "Guardar cambios" : "Crear vendedor"}</button>
        </div>
      </form>
    </section>
    {error && <p className="new-product-error" role="alert">{error}</p>}
    {message && <p role="status">{message}</p>}
    {removing && <section className="panel new-product-form" aria-label="Confirmar eliminación"><p>¿Eliminar la cuenta <strong>{removing.username}</strong>? Esta acción es permanente. Las cuentas con ventas o movimientos se conservan.</p><div className="new-product-form-actions"><button type="button" className="subtle-button" disabled={busy} onClick={()=>setRemoving(null)}>Cancelar</button><button type="button" className="primary-button" disabled={busy} onClick={remove}>{busy ? "Eliminando…" : "Confirmar eliminación"}</button></div></section>}
    <section className="panel recent-panel" aria-labelledby="users-table-title">
      <div className="panel-heading"><h2 id="users-table-title">Cuentas del negocio</h2><button className="subtle-button" disabled={loading||busy} onClick={()=>{setError("");refresh();}}>Actualizar lista</button></div>
      <div className="table-wrapper"><table className="sales-table"><thead><tr><th scope="col">Usuario</th><th scope="col">Rol</th><th scope="col">Creado el</th><th scope="col">Acciones</th></tr></thead><tbody>
        {loading ? <tr><td colSpan={4}>Cargando usuarios…</td></tr> : result.items.map(user=><tr key={user.id}>
          <td><strong>{user.username}</strong></td><td><span className="sale-status">{roleName(user.role)}</span></td><td>{new Date(user.created_at).toLocaleDateString("es-CO")}</td>
          <td>{user.username === session.username ? <span>Tu cuenta</span> : <div className="users-row-actions"><button type="button" className="text-button" disabled={busy} onClick={()=>edit(user)}>Editar</button><button type="button" className="text-button" disabled={busy} onClick={()=>{setRemoving(user);resetForm();setError("");setMessage("");}}>Eliminar</button></div>}</td>
        </tr>)}
        {!loading&&!result.items.length&&<tr><td colSpan={4}>No hay usuarios registrados.</td></tr>}
      </tbody></table></div>
      <nav className="pagination-bar" aria-label="Paginación de usuarios"><span>{result.total} usuarios · página {page} de {Math.max(1,result.total_pages)}</span><div><button type="button" className="subtle-button" disabled={busy||loading||page<=1} onClick={()=>{setLoading(true);setPage(page-1);}}>Anterior</button><button type="button" className="subtle-button" disabled={busy||loading||page>=result.total_pages} onClick={()=>{setLoading(true);setPage(page+1);}}>Siguiente</button></div></nav>
    </section>
  </>;
}
