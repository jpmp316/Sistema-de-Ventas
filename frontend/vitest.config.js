import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config.js";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      setupFiles: ["./src/test/setup.js"],
      include: ["src/**/*.test.{js,jsx}"],
      env: { VITE_API_BASE_URL: "https://api.nexo.test" },
      coverage: {
        provider: "v8",
        reporter: ["text", "html", "json-summary"],
        include: ["src/**/*.{js,jsx}"],
        exclude: ["src/test/**", "src/main.jsx"],
        thresholds: { lines: 75, statements: 75, branches: 70, functions: 70 },
      },
    },
  }),
);
