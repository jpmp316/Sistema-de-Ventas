import { StrictMode } from "react";

import { render } from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import { vi } from "vitest";

import { AuthProvider } from "../auth/AuthContext";

export const category = { id: 1, name: "Papelería", is_active: true };

export const product = {
  id: 1,
  name: "Cuaderno",
  code: "CUA-001",
  category_id: 1,

  category,
  price_cents: 1500000,
  stock: 3,
  min_stock: 1,
  is_active: true,
};

export const report = {
  revenue: 30000,
  operations: 2,
  average_ticket: 15000,

  low_stock_products: 1,
  inventory_movements: 2,

  sales_by_day: [],
  top_products: [],
  inventory_by_day: [],
  stock_by_category: [],
};

export const paginate = (items, page = 1, totalPages = 1) => ({
  items,
  page,
  total: items.length,
  total_pages: totalPages,
  page_size: 10,
});

export const json = (data, status = 200) =>
  new Response(status === 204 ? null : JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });

export function api(handler = () => undefined) {
  const requests = [];

  vi.stubGlobal(
    "fetch",
    vi.fn(async (url, options = {}) => {
      const request = {
        url: new URL(url),
        method: options.method ?? "GET",

        body:
          options.body instanceof URLSearchParams
            ? Object.fromEntries(options.body)
            : options.body
              ? JSON.parse(options.body)
              : null,

        headers: options.headers,
      };

      requests.push(request);

      const response = await handler(request);

      if (response !== undefined) return response;

      switch (request.url.pathname) {
        case "/products/":
          return json(paginate([product]));

        case "/categories/":
          return json([category]);

        case "/sales/":
          return json(paginate([]));

        case "/users/paginated":
          return json(
            paginate([
              {
                id: 1,
                username: "admin",
                role: "admin",
                created_at: "2026-01-01",
              },

              {
                id: 2,
                username: "ana",
                role: "vendedor",
                created_at: "2026-01-01",
              },
            ]),
          );

        case "/inventory/movements":
          return json(paginate([]));

        case "/reports/summary":
          return json(report);

        default:
          throw new Error("Unhandled test request " + request.url);
      }
    }),
  );

  return requests;
}

export function renderAuthenticated(component, role = "admin") {
  sessionStorage.setItem(
    "nexo_session",
    JSON.stringify({
      username: role === "admin" ? "admin" : "ana",
      role,
      token: "test-token",
    }),
  );

  return {
    user: userEvent.setup(),
    ...render(
      <StrictMode>
        <AuthProvider>{component}</AuthProvider>
      </StrictMode>,
    ),
  };
}
