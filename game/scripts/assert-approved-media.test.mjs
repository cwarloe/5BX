import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtemp, mkdir, writeFile, symlink, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, test } from "node:test";

import { inspectPublicMedia, PublicMediaGateError } from "./assert-approved-media.mjs";

const script = fileURLToPath(new URL("./assert-approved-media.mjs", import.meta.url));
const allocated = [];
const fakeMp4 = Buffer.concat([Buffer.alloc(4), Buffer.from("ftypisom0000", "ascii")]);
const fakeWebm = Buffer.from([0x1a, 0x45, 0xdf, 0xa3, 0x00]);

async function fixture() {
  const root = await mkdtemp(path.join(os.tmpdir(), "5bx-public-media-synthetic-"));
  allocated.push(root);
  return root;
}

afterEach(async () => {
  for (const item of allocated.splice(0)) await rm(item, { recursive: true, force: true });
});

test("empty public app tree and ordinary photo/still images pass", async () => {
  const root = await fixture();
  await mkdir(path.join(root, "sprites"));
  await writeFile(path.join(root, "sprites", "frame.png"), Buffer.from([0x89, 0x50, 0x4e, 0x47]));
  const avif = Buffer.concat([Buffer.alloc(4), Buffer.from("ftypavif", "ascii")]);
  await writeFile(path.join(root, "still.avif"), avif);
  assert.deepEqual(await inspectPublicMedia({ appRoots: [root] }), []);
});

test("known and disguised synthetic videos fail the empty approved-media registry", async () => {
  const root = await fixture();
  await writeFile(path.join(root, "unapproved.mp4"), fakeMp4);
  await writeFile(path.join(root, "renamed.jpg"), fakeWebm);
  const result = await inspectPublicMedia({ appRoots: [root] });
  assert.equal(result.length, 2);
  assert.ok(result.every((item) => item.reason === "UNAPPROVED_VIDEO_MEDIA"));
  assert.ok(result.every((item) => !Object.hasOwn(item, "path")));
});

test("extensionless and harmless-looking filenames cannot conceal common video signatures", async () => {
  const root = await fixture();
  const fakeAvi = Buffer.concat([Buffer.from("RIFF0000AVI ", "ascii"), Buffer.alloc(4)]);
  await writeFile(path.join(root, "opaque-iso"), fakeMp4);
  await writeFile(path.join(root, "opaque-webm"), fakeWebm);
  await writeFile(path.join(root, "opaque-avi"), fakeAvi);
  const result = await inspectPublicMedia({ appRoots: [root] });
  assert.equal(result.length, 3);
  assert.ok(result.every((item) => item.reason === "UNAPPROVED_VIDEO_MEDIA"));
});

test("historical site reference is allowed only for its exact pinned path and bytes", async () => {
  const root = await fixture();
  const relative = "video/design/explorations/animation-abc-test.mp4";
  const file = path.join(root, relative);
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, fakeMp4);
  const digest = createHash("sha256").update(fakeMp4).digest("hex");
  const exceptions = { [relative]: digest };
  assert.deepEqual(await inspectPublicMedia({ siteRoots: [root], exceptions }), []);
  assert.equal((await inspectPublicMedia({ appRoots: [root], exceptions }))[0].reason,
    "UNAPPROVED_VIDEO_MEDIA", "historical site exception cannot admit app footage");
  await writeFile(file, Buffer.concat([fakeMp4, Buffer.from("modified")]));
  assert.equal((await inspectPublicMedia({ siteRoots: [root], exceptions }))[0].reason,
    "HISTORICAL_REFERENCE_BYTES_CHANGED");
});

test("an unrelated public video is rejected even with historical exception present", async () => {
  const root = await fixture();
  const historical = path.join(root, "video/design/explorations/animation-abc-test.mp4");
  await mkdir(path.dirname(historical), { recursive: true });
  await writeFile(historical, fakeMp4);
  await writeFile(path.join(root, "video", "new-photo-preview.m4v"), fakeMp4);
  const exceptions = {
    "video/design/explorations/animation-abc-test.mp4": createHash("sha256").update(fakeMp4).digest("hex"),
  };
  const result = await inspectPublicMedia({ siteRoots: [root], exceptions });
  assert.equal(result.length, 1);
  assert.equal(result[0].reason, "UNAPPROVED_VIDEO_MEDIA");
});

test("symlinked video and directories are rejected without following a private target", async () => {
  const root = await fixture();
  const target = path.join(await fixture(), "private-target.mp4");
  await writeFile(target, fakeMp4);
  await symlink(target, path.join(root, "video.mp4"));
  assert.equal((await inspectPublicMedia({ appRoots: [root] }))[0].reason,
    "PUBLIC_SYMLINK_UNINSPECTABLE");
  const other = await fixture();
  await symlink(path.dirname(target), path.join(other, "public-subdirectory"), "dir");
  assert.equal((await inspectPublicMedia({ siteRoots: [other] }))[0].reason,
    "PUBLIC_SYMLINK_UNINSPECTABLE");
});

test("missing, non-directory and empty sets of scan roots fail closed", async () => {
  const root = await fixture();
  await assert.rejects(inspectPublicMedia(), PublicMediaGateError);
  await assert.rejects(inspectPublicMedia({ appRoots: [path.join(root, "missing")] }));
  const file = path.join(root, "not-dir");
  await writeFile(file, "file");
  await assert.rejects(inspectPublicMedia({ appRoots: [file] }), PublicMediaGateError);
});

test("tracked Pages source allows only an exact synthetic historical reference", async () => {
  const root = await fixture();
  execFileSync("git", ["init", "-q"], { cwd: root });
  const relative = "video/design/explorations/animation-abc-test.mp4";
  const file = path.join(root, relative);
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, fakeMp4);
  await mkdir(path.join(root, "game/public"), { recursive: true });
  await writeFile(path.join(root, "game/public", "not-copied.mp4"), fakeMp4);
  execFileSync("git", ["add", "--", relative, "game/public/not-copied.mp4"], { cwd: root });
  const exceptions = { [relative]: createHash("sha256").update(fakeMp4).digest("hex") };
  assert.deepEqual(await inspectPublicMedia({ siteSources: [root], exceptions }), []);
  await writeFile(path.join(root, "new-direct.mp4"), fakeMp4);
  execFileSync("git", ["add", "--", "new-direct.mp4"], { cwd: root });
  assert.equal((await inspectPublicMedia({ siteSources: [root], exceptions }))[0].reason,
    "UNAPPROVED_VIDEO_MEDIA");
});

test("CLI HOLD omits the sensitive filename from reports", async () => {
  const root = await fixture();
  const sensitiveName = "private-opaque-video-identifier.mp4";
  await writeFile(path.join(root, sensitiveName), fakeMp4);
  const run = spawnSync(process.execPath, [script, "--app-root", root], { encoding: "utf8" });
  assert.equal(run.status, 1);
  assert.match(run.stderr, /HOLD public media/);
  assert.ok(!run.stderr.includes(sensitiveName));
});

test("CLI reports missing roots without printing path contents", async () => {
  const root = await fixture();
  const run = spawnSync(process.execPath, [script, "--site-root", path.join(root, "secret-directory")],
    { encoding: "utf8" });
  assert.equal(run.status, 2);
  assert.ok(!run.stderr.includes("secret-directory"));
});
