/**
 * Fail-closed build gate for video files while the photographic registry is empty.
 *
 * No photographic clip has an authenticated owner approval. This gate therefore
 * allows NO new public video. The sole exception is a byte-pinned historical
 * animation reference already shipped at the site root (not player footage).
 *
 * The exception is code-owned, never supplied by CLI or environment. A future
 * owner-approved photographic media delivery must replace this deny-by-default
 * policy with authenticated exact-version and served-byte verification.
 *
 * Example from repo root after `npm run pages`:
 *   node game/scripts/assert-approved-media.mjs \
 *     --app-root game/public --app-root game/dist-pages --site-source .
 * Example before Pages artifact upload:
 *   node game/scripts/assert-approved-media.mjs --site-root _site
 */

import { execFile } from "node:child_process";
import { constants } from "node:fs";
import { lstat, open, opendir } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const VIDEO_EXTENSIONS = new Set([
  ".mp4", ".m4v", ".mov", ".webm", ".ogv", ".avi", ".mkv",
  ".mpg", ".mpeg", ".3gp", ".3g2", ".m3u8", ".mpd", ".m4s",
  ".flv", ".wmv", ".vob", ".mts", ".m2ts",
]);
const SKIP_FROM_PAGES_SOURCE = new Set([
  ".git", ".github", "_site", "node_modules", "game", "specs",
]);
const HISTORICAL_SITE_EXCEPTION = Object.freeze({
  "video/design/explorations/animation-abc-test.mp4":
    "36234e23fcbb5f9aa63b59bf8ed6b922c6bc0e246305941302015cad75374dbe",
});

export class PublicMediaGateError extends Error {}

function hold(reason, locationIndex) {
  // Never print a path/filename: private asset IDs might appear in either.
  return { reason, locationIndex };
}

function looksLikeVideo(bytes, filename) {
  const ext = path.extname(filename).toLowerCase();
  if (VIDEO_EXTENSIONS.has(ext)) return true;
  if (bytes.length >= 12 && bytes.subarray(4, 8).toString("ascii") === "ftyp") {
    // AVIF/HEIF still images are also ISO base-media containers; keep images.
    const brand = bytes.subarray(8, 12).toString("ascii");
    if (/^(?:avif|mif1|heic|heix|hevc|heim|heis)$/.test(brand)) return false;
    return true;
  }
  if (bytes.length >= 4 && bytes.subarray(0, 4).equals(Buffer.from([0x1a, 0x45, 0xdf, 0xa3]))) return true;
  if (bytes.length >= 12 && bytes.subarray(0, 4).toString("ascii") === "RIFF" &&
      bytes.subarray(8, 12).toString("ascii") === "AVI ") return true;
  return false;
}

async function inspectFile(file, filename, relativeName, locationIndex, mode, exceptions) {
  const handle = await open(file, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    const prefix = Buffer.alloc(64);
    const { bytesRead } = await handle.read(prefix, 0, prefix.length, 0);
    if (!looksLikeVideo(prefix.subarray(0, bytesRead), filename)) return [];
    if (mode === "site" && Object.hasOwn(exceptions, relativeName)) {
      const hash = createHash("sha256");
      const buffer = Buffer.alloc(1 << 16);
      for (let position = 0;;) {
        const { bytesRead: count } = await handle.read(buffer, 0, buffer.length, position);
        if (!count) break;
        hash.update(buffer.subarray(0, count));
        position += count;
      }
      if (hash.digest("hex") === exceptions[relativeName]) return [];
      return [hold("HISTORICAL_REFERENCE_BYTES_CHANGED", locationIndex)];
    }
    return [hold("UNAPPROVED_VIDEO_MEDIA", locationIndex)];
  } finally {
    await handle.close();
  }
}

async function scanDirectory(root, mode, exceptions, locationIndex) {
  const findings = [];
  const visit = async (directory) => {
    const dir = await opendir(directory);
    const entries = [];
    for await (const entry of dir) entries.push(entry.name);
    entries.sort();
    for (const name of entries) {
      const absolute = path.join(directory, name);
      const st = await lstat(absolute);
      if (st.isSymbolicLink()) {
        findings.push(hold("PUBLIC_SYMLINK_UNINSPECTABLE", locationIndex));
      } else if (st.isDirectory()) {
        await visit(absolute);
      } else if (st.isFile()) {
        const relativeName = path.relative(root, absolute).split(path.sep).join("/");
        findings.push(...await inspectFile(absolute, name, relativeName, locationIndex, mode, exceptions));
      } else {
        findings.push(hold("PUBLIC_ENTRY_UNINSPECTABLE", locationIndex));
      }
    }
  };
  const st = await lstat(root);
  if (st.isSymbolicLink() || !st.isDirectory()) throw new PublicMediaGateError("public scan root must be a real directory");
  await visit(root);
  return findings;
}

async function scanTrackedSiteSource(root, exceptions, locationIndex) {
  const { stdout: gitRoot } = await execFileAsync("git", ["rev-parse", "--show-toplevel"], { cwd: root });
  if (path.resolve(gitRoot.trim()) !== root) throw new PublicMediaGateError("site source is not repository root");
  const { stdout } = await execFileAsync("git", ["ls-files", "--cached", "-z", "--full-name"], { cwd: root, maxBuffer: 16 << 20 });
  const findings = [];
  for (const relativeName of stdout.split("\0").filter(Boolean).sort()) {
    if (SKIP_FROM_PAGES_SOURCE.has(relativeName.split("/")[0])) continue;
    const absolute = path.join(root, relativeName);
    const st = await lstat(absolute);
    if (st.isSymbolicLink()) {
      findings.push(hold("TRACKED_SITE_SYMLINK_UNINSPECTABLE", locationIndex));
    } else if (st.isFile()) {
      findings.push(...await inspectFile(absolute, path.basename(absolute), relativeName, locationIndex, "site", exceptions));
    } else {
      findings.push(hold("TRACKED_SITE_ENTRY_UNINSPECTABLE", locationIndex));
    }
  }
  return findings;
}

/** Purely technical evidence gate. PASS is never photographic owner approval. */
export async function inspectPublicMedia({ appRoots = [], siteRoots = [], siteSources = [], exceptions = HISTORICAL_SITE_EXCEPTION } = {}) {
  if (![appRoots, siteRoots, siteSources].every(Array.isArray) ||
      appRoots.length + siteRoots.length + siteSources.length === 0) {
    throw new PublicMediaGateError("at least one public output or site source root is required");
  }
  const findings = [];
  let locationIndex = 0;
  for (const rawRoot of appRoots) {
    findings.push(...await scanDirectory(path.resolve(rawRoot), "app", exceptions, ++locationIndex));
  }
  for (const rawRoot of siteRoots) {
    findings.push(...await scanDirectory(path.resolve(rawRoot), "site", exceptions, ++locationIndex));
  }
  for (const rawRoot of siteSources) {
    findings.push(...await scanTrackedSiteSource(path.resolve(rawRoot), exceptions, ++locationIndex));
  }
  return findings;
}

export async function main(argv = process.argv.slice(2)) {
  const config = { appRoots: [], siteRoots: [], siteSources: [] };
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i];
    const value = argv[i + 1];
    const field = { "--app-root": "appRoots", "--site-root": "siteRoots", "--site-source": "siteSources" }[key];
    if (!field || !value || value.startsWith("--")) {
      console.error("HOLD media gate: expected one or more --app-root, --site-root or --site-source paths");
      return 2;
    }
    config[field].push(value);
  }
  try {
    const findings = await inspectPublicMedia(config);
    if (findings.length) {
      findings.forEach(({ reason, locationIndex }) => {
        console.error(`HOLD public media: scan root #${locationIndex}, ${reason} (path redacted)`);
      });
      return 1;
    }
    console.log("PASS public video-media admission boundary (not owner approval)");
    return 0;
  } catch (error) {
    console.error(`HOLD public media: cannot verify scan inputs (${error instanceof PublicMediaGateError ? error.message : "I/O or Git failure"})`);
    return 2;
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = await main();
}
