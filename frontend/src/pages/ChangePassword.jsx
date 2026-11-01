import { useState } from "react";
import { changePassword } from "../api";
import { useAuth } from "../auth/AuthContext";
import { isSecurePassword, PASSWORD_HELP } from "../passwordPolicy";

export default function ChangePassword() {
  const { token } = useAuth();
  const [form, setForm] = useState({ current: "", next: "", confirmation: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  function update(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
    setError(""); setMessage("");
  }
  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    setError(""); setMessage("");
    if (!isSecurePassword(form.next)) { setError(PASSWORD_HELP); return; }
    if (form.next !== form.confirmation) { setError("La confirmación no coincide con la nueva contraseña."); return; }
    if (form.current === form.next) { setError("La nueva contraseña debe ser diferente a la actual."); return; }
    setBusy(true);
    try {
      await changePassword(token, form.current, form.next);
      setForm({ current: "", next: "", confirmation: "" });
      setMessage("Contraseña actualizada. Usa la nueva contraseña en tu próximo inicio de sesión.");
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <>
    <section className="page-heading"><div><p className="eyebrow">MI CUENTA</p><h1>Mi contraseña</h1><p className="page-subtitle">Actualiza la contraseña de tu cuenta.</p></div></section>
    <form className="panel new-product-form" onSubmit={submit}>
      <div className="new-product-fields">
        <label className="new-product-field"><span>Contraseña actual</span><input name="current" type="password" autoComplete="current-password" required maxLength={1024} disabled={busy} value={form.current} onChange={update}/></label>
        <label className="new-product-field"><span>Nueva contraseña</span><input name="next" type="password" autoComplete="new-password" required minLength={8} maxLength={128} aria-describedby="password-help" disabled={busy} value={form.next} onChange={update}/><small id="password-help">{PASSWORD_HELP}</small></label>
        <label className="new-product-field"><span>Confirmar nueva contraseña</span><input name="confirmation" type="password" autoComplete="new-password" required minLength={8} maxLength={128} disabled={busy} value={form.confirmation} onChange={update}/></label>
      </div>
      {error && <p className="new-product-error" role="alert">{error}</p>}
      {message && <p role="status">{message}</p>}
      <div className="new-product-form-actions"><button type="submit" className="primary-button" disabled={busy}>{busy ? "Guardando…" : "Actualizar contraseña"}</button></div>
    </form>
  </>;
}
