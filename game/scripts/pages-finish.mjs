// Vite writes the Pages entry to dist-pages/pages/index.html because its input
// lives in pages/. GitHub Pages needs it at dist-pages/index.html.
import { renameSync, rmSync } from "node:fs";
import { resolve } from "node:path";

const out = resolve(import.meta.dirname, "..", "dist-pages");
renameSync(resolve(out, "pages", "index.html"), resolve(out, "index.html"));
rmSync(resolve(out, "pages"), { recursive: true });
