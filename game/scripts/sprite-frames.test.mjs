// Every frame the game declares in FRAME_COUNTS must exist as public/sprites/<action>/<n>.png,
// or the browser requests a missing image mid-workout (toe-multi once declared 6 frames with only 4 drawn).
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = readFileSync(join(root, "src/lib/levels.ts"), "utf8");
const table = src.match(/export const FRAME_COUNTS[^{]*\{([\s\S]*?)\n\};/);

test("FRAME_COUNTS table is found", () => assert.ok(table, "FRAME_COUNTS not found in src/lib/levels.ts"));

const counts = [...(table?.[1] ?? "").matchAll(/^\s*"?([a-z0-9-]+)"?\s*:\s*(\d+)\s*,/gm)].map(([, action, n]) => [action, Number(n)]);

test("every declared sprite frame exists", () => {
  assert.ok(counts.length > 5, `parsed only ${counts.length} actions`);
  const missing = [];
  for (const [action, n] of counts) {
    for (let i = 0; i < n; i++) {
      const f = join(root, "public/sprites", action, `${i}.png`);
      if (!existsSync(f)) missing.push(`${action}/${i}.png`);
    }
  }
  assert.deepEqual(missing, [], `declared but not drawn: ${missing.join(", ")}`);
});
