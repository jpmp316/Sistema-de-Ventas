import { expect, test, vi } from "vitest";
import { apiRequest } from "../api";
import { api, json } from "./helpers";

test("errores 422 conservan el estado HTTP y muestran las validaciones", async () => {
  api(() =>
    json(
      { detail: [{ msg: "Precio inválido" }, { msg: "Stock inválido" }] },
      422,
    ),
  );
  await expect(apiRequest("/products/")).rejects.toMatchObject({
    status: 422,
    message: "Precio inválido Stock inválido",
  });
});
test("204 se interpreta como operación exitosa sin cuerpo", async () => {
  api(() => json(null, 204));
  await expect(
    apiRequest("/auth/logout", { method: "POST" }),
  ).resolves.toBeNull();
});
test("un error sin JSON utiliza el estado HTTP como mensaje", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response("upstream down", { status: 503 })),
  );
  await expect(apiRequest("/products/")).rejects.toMatchObject({ status: 503 });
});
