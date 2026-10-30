const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");

export async function apiRequest(path, { token, ...options } = {}) {
  if (!API_BASE_URL) {
    throw new Error("Configura VITE_API_BASE_URL en el archivo .env del frontend.");
  }

  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error("No se pudo conectar con la API. Revisa la URL y que FastAPI esté activo.");
  }

  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(" ")
      : detail || `La API respondió con el estado ${response.status}.`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return data;
}

const jsonBody = (data) => JSON.stringify(data);

export const getProducts = (token) => apiRequest("/products/", { token });
export const getCategories = (token) => apiRequest("/categories/", { token });
export const createProduct = (token, product) => apiRequest("/products/", { method: "POST", token, body: jsonBody(product) });
export const updateProduct = (token, productId, changes) => apiRequest(`/products/${productId}`, { method: "PUT", token, body: jsonBody(changes) });
export const setProductActive = (token, productId, isActive) => updateProduct(token, productId, { is_active: isActive });
export const createCategory = (token, name) => apiRequest("/categories/", { method: "POST", token, body: jsonBody({ name }) });
