import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";

beforeEach(() => {
  sessionStorage.clear();
  // Every test must explicitly provide a fake HTTP boundary.
  vi.stubGlobal(
    "fetch",
    vi.fn(() => {
      throw new Error("Unexpected fetch: configure the test API first");
    }),
  );
});
afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
Object.defineProperty(Element.prototype, "scrollIntoView", {
  configurable: true,
  value() {},
});
// jsdom has no layout engine. Give real Recharts components a stable viewport.
globalThis.ResizeObserver = class {
  observe(element) {
    this.callback?.([
      { target: element, contentRect: { width: 800, height: 300 } },
    ]);
  }
  constructor(callback) {
    this.callback = callback;
  }
  unobserve() {}
  disconnect() {}
};
