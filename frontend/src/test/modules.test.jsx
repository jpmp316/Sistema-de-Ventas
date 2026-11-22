import { screen, within, waitFor } from "@testing-library/react";

import { expect, test } from "vitest";

import Sales from "../pages/Sales";

import Users from "../pages/Users";

import Inventory from "../pages/Inventory";

import Dashboard from "../pages/Dashboard";

import Statistics from "../pages/Statistics";

import ChangePassword from "../pages/ChangePassword";

import {
  api,
  json,
  product,
  paginate,
  report,
  renderAuthenticated,
} from "./helpers";

test("carrito cambia cantidades, elimina artículos y bloquea stock insuficiente", async () => {
  api();

  const { user } = renderAuthenticated(<Sales />);

  await user.click(
    await screen.findByRole("button", { name: "Agregar", exact: true }),
  );

  const quantity = screen.getByRole("spinbutton", {
    name: "Cantidad de Cuaderno",
  });

  await user.clear(quantity);

  await user.type(quantity, "4");

  expect(
    screen.getByRole("button", { name: "Confirmar venta" }),
  ).toBeDisabled();

  await user.clear(quantity);

  await user.type(quantity, "2");

  expect(screen.getByText("$30.000")).toBeVisible();

  await user.click(screen.getByRole("button", { name: "Quitar" }));

  expect(
    screen.getByRole("button", { name: "Confirmar venta" }),
  ).toBeDisabled();
});

test("confirma una venta, bloquea doble envío y vacía el carrito", async () => {
  let finish;

  const requests = api((r) => {
    if (r.method === "POST")
      return new Promise((resolve) => {
        finish = () => resolve(json({ id: 7 }, 201));
      });
  });

  const { user } = renderAuthenticated(<Sales />);

  await user.click(
    await screen.findByRole("button", { name: "Agregar", exact: true }),
  );

  await user.click(screen.getByRole("button", { name: "Confirmar venta" }));

  expect(screen.getByRole("button", { name: "Procesando…" })).toBeDisabled();

  expect(requests.filter((r) => r.method === "POST")).toHaveLength(1);

  expect(requests.find((r) => r.method === "POST").body).toEqual({
    items: [{ product_id: 1, quantity: 1 }],
  });

  finish();

  expect(await screen.findByRole("status")).toHaveTextContent(
    "Venta #7 registrada.",
  );

  expect(
    await screen.findByRole("button", { name: "Confirmar venta" }),
  ).toBeDisabled();
});

test("venta rechazada mantiene el carrito para corregir la operación", async () => {
  api((r) =>
    r.method === "POST"
      ? json({ detail: "Stock insuficiente" }, 409)
      : undefined,
  );

  const { user } = renderAuthenticated(<Sales />);

  await user.click(
    await screen.findByRole("button", { name: "Agregar", exact: true }),
  );

  await user.click(screen.getByRole("button", { name: "Confirmar venta" }));

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Stock insuficiente",
  );

  expect(
    screen.getByRole("spinbutton", { name: "Cantidad de Cuaderno" }),
  ).toHaveValue(1);
});

test("catálogo pagina ocho productos y reinicia al buscar", async () => {
  api((r) =>
    r.url.pathname === "/products/"
      ? json(
          paginate(
            Array.from({ length: 9 }, (_, i) => ({
              ...product,
              id: i + 1,
              name: "Artículo " + (i + 1),
            })),
          ),
        )
      : undefined,
  );

  const { user } = renderAuthenticated(<Sales />);

  await screen.findByText("Artículo 1");

  const nav = screen.getByRole("navigation", {
    name: "Paginación del catálogo de venta",
  });

  await user.click(within(nav).getByRole("button", { name: "Siguiente" }));

  expect(screen.getByText("Artículo 9")).toBeVisible();

  expect(screen.queryByText("Artículo 1")).not.toBeInTheDocument();

  await user.type(screen.getByRole("searchbox"), "Artículo 1");

  expect(screen.getByText("Artículo 1")).toBeVisible();
});

test("usuarios muestra roles y crea vendedores desde el formulario", async () => {
  const requests = api((r) =>
    r.method === "POST"
      ? json({ id: 3, ...r.body, role: "vendedor" }, 201)
      : undefined,
  );

  const { user } = renderAuthenticated(<Users />);

  expect(await screen.findByText("Tu cuenta")).toBeVisible();

  expect(screen.getByText("Administrador")).toBeVisible();

  expect(screen.getByText("Vendedor")).toBeVisible();

  await user.type(screen.getByLabelText("Usuario", { exact: true }), "luis");

  await user.type(screen.getByLabelText(/^Contraseña inicial/), "Segura123!");

  await user.click(screen.getByRole("button", { name: "Crear vendedor" }));

  expect(await screen.findByRole("status")).toHaveTextContent(
    "Cuenta de vendedor creada.",
  );

  expect(requests.find((r) => r.method === "POST").body).toEqual({
    username: "luis",
    password: "Segura123!",
  });
});

test("cancelar eliminación no envía DELETE y el conflicto del servidor se explica", async () => {
  const requests = api((r) =>
    r.method === "DELETE"
      ? json({ detail: "El usuario tiene ventas" }, 409)
      : undefined,
  );

  const { user } = renderAuthenticated(<Users />);

  await user.click(
    await screen.findByRole("button", { name: "Eliminar", exact: true }),
  );

  await user.click(
    screen.getByRole("button", { name: "Cancelar", exact: true }),
  );

  expect(requests.some((r) => r.method === "DELETE")).toBe(false);

  await user.click(
    screen.getByRole("button", { name: "Eliminar", exact: true }),
  );

  await user.click(
    screen.getByRole("button", { name: "Confirmar eliminación", exact: true }),
  );

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "El usuario tiene ventas",
  );
});

test("inventario filtra por tipo y fechas", async () => {
  const requests = api();

  const { user } = renderAuthenticated(<Inventory />);

  await screen.findByText("No hay movimientos con esos filtros.");

  await user.selectOptions(screen.getByRole("combobox"), "adjustment");

  await user.type(screen.getByLabelText("Desde"), "2026-01-01");

  await waitFor(() =>
    expect(requests.at(-1).url.searchParams.get("date_from")).toBe(
      "2026-01-01",
    ),
  );

  expect(requests.at(-1).url.searchParams.get("type")).toBe("adjustment");
});

test.each([
  [Dashboard, "1", "Hoy"],
  [Statistics, "90", "90 días"],
])("el periodo cambia los indicadores de %s", async (Component, period) => {
  api((r) =>
    r.url.pathname === "/reports/summary"
      ? json({
          ...report,
          revenue: r.url.searchParams.get("days") === period ? 99000 : 30000,
        })
      : undefined,
  );

  const { user } = renderAuthenticated(<Component />);

  await screen.findAllByText("$30.000");

  await user.selectOptions(
    screen.getByRole("combobox", { name: "Periodo del informe" }),
    period,
  );

  expect((await screen.findAllByText("$99.000")).length).toBeGreaterThan(0);
});

test("contraseñas distintas muestran error sin enviar la petición", async () => {
  const requests = api();

  const { user } = renderAuthenticated(<ChangePassword />, "vendedor");

  await user.type(screen.getByLabelText("Contraseña actual"), "Actual123!");

  await user.type(screen.getByLabelText(/^Nueva contraseña/), "Nueva123!");

  await user.type(
    screen.getByLabelText("Confirmar nueva contraseña"),
    "Otra123!",
  );

  await user.click(
    screen.getByRole("button", { name: "Actualizar contraseña" }),
  );

  expect(screen.getByRole("alert")).toHaveTextContent(
    "La confirmación no coincide",
  );

  expect(requests).toHaveLength(0);
});

test("cambio de contraseña exitoso limpia los campos", async () => {
  api(() => json(null, 204));

  const { user } = renderAuthenticated(<ChangePassword />, "vendedor");

  await user.type(screen.getByLabelText("Contraseña actual"), "Actual123!");

  await user.type(screen.getByLabelText(/^Nueva contraseña/), "Nueva123!");

  await user.type(
    screen.getByLabelText("Confirmar nueva contraseña"),
    "Nueva123!",
  );

  await user.click(
    screen.getByRole("button", { name: "Actualizar contraseña" }),
  );

  expect(await screen.findByRole("status")).toHaveTextContent(
    "Contraseña actualizada.",
  );

  expect(screen.getByLabelText("Contraseña actual")).toHaveValue("");
});

test("el detalle de venta muestra los artículos y permite cerrarlo", async () => {
  const sale = {
    id: 7,
    date: "2026-01-01T12:00:00Z",
    status: "completed",
    total: 30000,
  };
  api((r) => {
    if (r.url.pathname === "/sales/") return json(paginate([sale]));
    if (r.url.pathname === "/sales/7")
      return json({
        ...sale,
        username: "ana",
        details: [
          {
            id: 1,
            product_name: "Cuaderno vendido",
            product_code: "CUA-001",
            quantity: 2,
            unit_price: 15000,
            subtotal: 30000,
          },
        ],
      });
  });
  const { user } = renderAuthenticated(<Sales />);
  await user.click(await screen.findByRole("button", { name: "Ver detalle" }));
  expect(
    await screen.findByRole("heading", { name: "Venta #7" }),
  ).toHaveFocus();
  expect(screen.getByText("Cuaderno vendido")).toBeVisible();
  await user.click(screen.getByRole("button", { name: "Cerrar detalle" }));
  expect(
    screen.queryByRole("heading", { name: "Venta #7" }),
  ).not.toBeInTheDocument();
});
test("una contraseña débil muestra las reglas sin enviar cambios", async () => {
  const requests = api();
  const { user } = renderAuthenticated(<ChangePassword />, "vendedor");
  await user.type(screen.getByLabelText("Contraseña actual"), "Actual123!");
  await user.type(screen.getByLabelText(/^Nueva contraseña/), "abcdefgh");
  await user.type(
    screen.getByLabelText("Confirmar nueva contraseña"),
    "abcdefgh",
  );
  await user.click(
    screen.getByRole("button", { name: "Actualizar contraseña" }),
  );
  expect(screen.getByRole("alert")).toHaveTextContent("mayúscula");
  expect(requests).toHaveLength(0);
});

test("edita un vendedor conservando la contraseña cuando el campo queda vacío", async () => {
  const requests = api((r) =>
    r.method === "PUT"
      ? json({
          id: 2,
          username: r.body.username,
          role: "vendedor",
          created_at: "2026-01-01",
        })
      : undefined,
  );
  const { user } = renderAuthenticated(<Users />);
  await user.click(
    await screen.findByRole("button", { name: "Editar", exact: true }),
  );
  await user.clear(screen.getByLabelText("Usuario", { exact: true }));
  await user.type(
    screen.getByLabelText("Usuario", { exact: true }),
    "ana_nueva",
  );
  await user.click(screen.getByRole("button", { name: "Guardar cambios" }));
  expect(await screen.findByText("ana_nueva")).toBeVisible();
  expect(requests.find((r) => r.method === "PUT").body).toEqual({
    username: "ana_nueva",
  });
});
test("inventario identifica ajustes de entrada y salida con su responsable", async () => {
  api((r) =>
    r.url.pathname === "/inventory/movements"
      ? json(
          paginate([
            {
              id: 1,
              product_name: "Agenda",
              type: "adjustment",
              quantity: 3,
              previous_stock: 1,
              resulting_stock: 4,
              date: "2026-01-01",
              username: "ana",
            },
            {
              id: 2,
              product_name: "Cuaderno",
              type: "adjustment",
              quantity: 2,
              previous_stock: 4,
              resulting_stock: 2,
              date: "2026-01-01",
              username: "ana",
            },
          ]),
        )
      : undefined,
  );
  renderAuthenticated(<Inventory />);
  expect(await screen.findByText("Ajuste de entrada")).toBeVisible();
  expect(screen.getByText("Ajuste de salida")).toBeVisible();
  expect(screen.getByText("+3")).toBeVisible();
  expect(screen.getByText("−2")).toBeVisible();
});
