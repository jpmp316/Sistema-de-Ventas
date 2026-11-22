import { render, screen, waitFor } from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import { expect, test } from "vitest";

import App from "../App";

import { api, json, renderAuthenticated } from "./helpers";

test("credenciales inválidas muestran el mensaje de FastAPI y permiten reintentar", async () => {
  const requests = api(() => json({ detail: "Credenciales inválidas" }, 401));

  const user = userEvent.setup();

  render(<App />);

  await user.type(screen.getByLabelText("Usuario"), "ana");

  await user.type(
    screen.getByLabelText("Contraseña", { exact: true }),
    "incorrecta",
  );

  await user.click(screen.getByRole("button", { name: "Entrar a mi espacio" }));

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Credenciales inválidas",
  );

  expect(
    screen.getByRole("button", { name: "Entrar a mi espacio" }),
  ).toBeEnabled();

  expect(requests[0].body).toEqual({ username: "ana", password: "incorrecta" });
});

test.each([
  ["admin", "Resumen general"],
  ["vendedor", "Ventas"],
])(
  "el rol %s determina la pantalla inicial después del login",
  async (role, heading) => {
    api((r) =>
      r.url.pathname === "/auth/login"
        ? json({ access_token: "jwt-prueba", username: "ana", role })
        : undefined,
    );

    const user = userEvent.setup();

    render(<App />);

    await user.type(screen.getByLabelText("Usuario"), "ana");

    await user.type(
      screen.getByLabelText("Contraseña", { exact: true }),
      "Password123!",
    );

    await user.click(
      screen.getByRole("button", { name: "Entrar a mi espacio" }),
    );

    expect(
      await screen.findByRole("heading", { name: heading, level: 1 }),
    ).toBeVisible();

    expect(JSON.parse(sessionStorage.getItem("nexo_session")).role).toBe(role);
  },
);

test("vendedor recupera sesión y solo encuentra sus opciones de navegación", async () => {
  api();

  const { user } = renderAuthenticated(<App />, "vendedor");

  const nav = screen.getByRole("navigation", { name: "Navegación principal" });

  expect(nav).toHaveTextContent("Ventas");

  expect(nav).not.toHaveTextContent("Productos");

  expect(nav).not.toHaveTextContent("Usuarios");

  await user.click(
    screen.getByRole("button", { name: "Mi contraseña", exact: true }),
  );

  expect(screen.getByRole("heading", { name: "Mi contraseña" })).toBeVisible();
});

test("logout limpia la sesión incluso si se pierde la conexión", async () => {
  const requests = api((r) => {
    if (r.url.pathname === "/auth/logout") throw new TypeError("offline");
  });

  const { user } = renderAuthenticated(<App />);

  await user.click(
    screen.getByRole("button", { name: /admin.*Administrador/ }),
  );

  await user.click(screen.getByRole("button", { name: "Cerrar sesión" }));

  expect(
    await screen.findByRole("heading", { name: "Inicia sesión" }),
  ).toBeVisible();

  await waitFor(() =>
    expect(sessionStorage.getItem("nexo_session")).toBeNull(),
  );

  expect(
    requests
      .find((r) => r.url.pathname === "/auth/logout")
      .headers.get("Authorization"),
  ).toBe("Bearer test-token");
});

test("una sesión malformada permite volver al login", () => {
  api();

  sessionStorage.setItem("nexo_session", "{broken");

  render(<App />);

  expect(screen.getByRole("heading", { name: "Inicia sesión" })).toBeVisible();
});
