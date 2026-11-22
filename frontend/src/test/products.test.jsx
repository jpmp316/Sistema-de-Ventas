import { screen } from "@testing-library/react";

import { expect, test } from "vitest";

import Products from "../pages/Products";

import { api, json, paginate, product, renderAuthenticated } from "./helpers";

test("consulta, busca por código y muestra un resultado vacío", async () => {
  api();

  const { user } = renderAuthenticated(<Products />);

  expect(await screen.findByText("Cuaderno")).toBeVisible();

  await user.type(screen.getByRole("searchbox"), "CUA-001");

  expect(screen.getByText("Cuaderno")).toBeVisible();

  await user.clear(screen.getByRole("searchbox"));

  await user.type(screen.getByRole("searchbox"), "inexistente");

  expect(screen.getByText(/No hay productos que coincidan/)).toBeVisible();
});

test("edita el nombre conservando el código visible y fuera de la petición", async () => {
  const requests = api((r) =>
    r.method === "PUT" ? json({ ...product, ...r.body }) : undefined,
  );

  const { user } = renderAuthenticated(<Products />);

  await user.click(
    await screen.findByRole("button", { name: "Editar Cuaderno" }),
  );

  const code = screen.getByLabelText(/^Código/);

  expect(code).toHaveAttribute("readonly");

  expect(code).toHaveValue("CUA-001");

  await user.clear(screen.getByLabelText("Nombre", { exact: true }));

  await user.type(
    screen.getByLabelText("Nombre", { exact: true }),
    "Cuaderno grande",
  );

  await user.click(screen.getByRole("button", { name: "Guardar cambios" }));

  expect(await screen.findByRole("status")).toHaveTextContent(
    "Producto actualizado.",
  );

  expect(screen.getByText("Cuaderno grande")).toBeVisible();

  expect(requests.find((r) => r.method === "PUT").body).not.toHaveProperty(
    "code",
  );
});

async function fillProduct(user) {
  await user.click(screen.getByRole("button", { name: "Nuevo producto" }));

  await user.type(screen.getByLabelText("Nombre", { exact: true }), "Agenda");

  await user.type(screen.getByLabelText(/^Código/), "AGE-001");

  await user.selectOptions(screen.getByLabelText(/^Categoría/), "1");

  await user.type(screen.getByLabelText("Precio"), "12000");

  await user.type(screen.getByLabelText(/^Existencias/), "4");

  await user.type(screen.getByLabelText("Stock mínimo"), "1");
}

test("crea un producto y muestra la respuesta real del servidor", async () => {
  const requests = api((r) =>
    r.method === "POST"
      ? json({ ...product, ...r.body, id: 2 }, 201)
      : undefined,
  );

  const { user } = renderAuthenticated(<Products />);

  await screen.findByText("Cuaderno");

  await fillProduct(user);

  await user.click(screen.getByRole("button", { name: "Crear producto" }));

  expect(await screen.findByText("Agenda")).toBeVisible();

  expect(requests.find((r) => r.method === "POST").body).toMatchObject({
    code: "AGE-001",
    price_cents: 1200000,
  });
});

test("un código duplicado devuelve un error y conserva el formulario", async () => {
  api((r) =>
    r.method === "POST"
      ? json({ detail: "El código del producto ya existe" }, 409)
      : undefined,
  );

  const { user } = renderAuthenticated(<Products />);

  await screen.findByText("Cuaderno");

  await fillProduct(user);

  await user.click(screen.getByRole("button", { name: "Crear producto" }));

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "El código del producto ya existe",
  );

  expect(screen.getByLabelText("Nombre", { exact: true })).toHaveValue(
    "Agenda",
  );
});

test("desactiva y reactiva sin alterar las existencias", async () => {
  api((r) =>
    r.method === "PUT" ? json({ ...product, ...r.body }) : undefined,
  );

  const { user } = renderAuthenticated(<Products />);

  await user.click(
    await screen.findByRole("button", { name: "Desactivar Cuaderno" }),
  );

  expect(await screen.findByText("Inactivo")).toBeVisible();

  expect(screen.getByText("3 unidades")).toBeVisible();

  await user.click(screen.getByRole("button", { name: "Reactivar Cuaderno" }));

  expect(await screen.findByText("Activo")).toBeVisible();
});

test("paginación consulta la siguiente página", async () => {
  api((r) =>
    r.url.pathname === "/products/"
      ? json(
          paginate(
            [
              {
                ...product,
                name:
                  r.url.searchParams.get("page") === "2"
                    ? "Agenda"
                    : "Cuaderno",
              },
            ],
            Number(r.url.searchParams.get("page")),
            2,
          ),
        )
      : undefined,
  );

  const { user } = renderAuthenticated(<Products />);

  await screen.findByText("Cuaderno");

  await user.click(screen.getByRole("button", { name: "Siguiente" }));

  expect(await screen.findByText("Agenda")).toBeVisible();
});

test("fallo de conexión permite reintentar la carga", async () => {
  let offline = true;

  api((r) => {
    if (r.url.pathname === "/products/" && offline)
      throw new TypeError("offline");
  });

  const { user } = renderAuthenticated(<Products />);

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "No se pudo conectar",
  );

  offline = false;

  await user.click(screen.getByRole("button", { name: "Reintentar" }));

  expect(await screen.findByText("Cuaderno")).toBeVisible();
});

test.each([
  ["Precio", "0"],
  ["Precio", "-1"],
  ["Precio", "1.234"],
  ["Existencias", "-1"],
  ["Existencias", "1.5"],
  ["Stock mínimo", "-1"],
])("el navegador impide guardar %s con valor %s", async (label, value) => {
  const requests = api();
  const { user } = renderAuthenticated(<Products />);
  await screen.findByText("Cuaderno");
  await fillProduct(user);
  const field = screen.getByLabelText(new RegExp("^" + label));
  await user.clear(field);
  await user.type(field, value);
  await user.click(screen.getByRole("button", { name: "Crear producto" }));
  expect(field).toBeInvalid();
  expect(requests.some((r) => r.method === "POST")).toBe(false);
});
test("un formulario vacío señala los campos requeridos", async () => {
  const requests = api();
  const { user } = renderAuthenticated(<Products />);
  await screen.findByText("Cuaderno");
  await user.click(screen.getByRole("button", { name: "Nuevo producto" }));
  await user.click(screen.getByRole("button", { name: "Crear producto" }));
  expect(screen.getByLabelText("Nombre", { exact: true })).toBeInvalid();
  expect(requests.some((r) => r.method === "POST")).toBe(false);
});
test("cancelar el formulario no crea un producto", async () => {
  const requests = api();
  const { user } = renderAuthenticated(<Products />);
  await screen.findByText("Cuaderno");
  await user.click(screen.getByRole("button", { name: "Nuevo producto" }));
  await user.click(
    screen.getByRole("button", { name: "Cancelar", exact: true }),
  );
  expect(
    screen.queryByLabelText("Nombre", { exact: true }),
  ).not.toBeInTheDocument();
  expect(requests.some((r) => r.method === "POST")).toBe(false);
});
