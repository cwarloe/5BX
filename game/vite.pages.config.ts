import { resolve } from "node:path";
import { defineConfig } from "vite";
import viteReact from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { grokPwaPlugin } from "./scripts/grok-pwa-plugin.mjs";

/**
 * Static build for GitHub Pages: https://cwarloe.github.io/5BX/game/
 * Keeps grokPwaPlugin(): game/AGENTS.md requires the branding injector, and a static
 * deployment has no server middleware, so its transformIndexHtml hook is what puts the
 * Created with Grok pill's script into the built page.
 */
export default defineConfig({
  base: "/5BX/game/",
  plugins: [tailwindcss(), viteReact(), grokPwaPlugin()],
  resolve: {
    alias: { "@": resolve(import.meta.dirname, "src") },
  },
  publicDir: resolve(import.meta.dirname, "public"),
  build: {
    outDir: resolve(import.meta.dirname, "dist-pages"),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(import.meta.dirname, "pages/index.html"),
    },
  },
});
