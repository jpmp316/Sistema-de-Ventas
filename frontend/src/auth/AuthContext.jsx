import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { apiRequest, logoutUser } from "../api";

const AuthContext = createContext(null);

function readSession() {
  try { return JSON.parse(sessionStorage.getItem("nexo_session")) ?? null; }
  catch { return null; }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(readSession);

  const login = useCallback(async (username, password) => {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username, password }),
    });
    const next = { token: data.access_token, username: data.username, role: data.role };
    sessionStorage.setItem("nexo_session", JSON.stringify(next));
    sessionStorage.setItem("nexo_access_token", next.token);
    setSession(next);
    return next;
  }, []);

  const logout = useCallback(async (tokenToRevoke = session?.token) => {
    try {
      if (tokenToRevoke) await logoutUser(tokenToRevoke);
    } catch {
      // El cierre local debe completarse aunque la API no esté disponible.
    } finally {
      sessionStorage.removeItem("nexo_session");
      sessionStorage.removeItem("nexo_access_token");
      setSession(null);
    }
  }, [session?.token]);

  const value = useMemo(() => ({ session, token: session?.token ?? null, login, logout }), [session, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return context;
}
