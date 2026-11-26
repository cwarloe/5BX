import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  APPROVED_PHOTO_REGISTRY,
  approvedMediaPath,
  matchesReviewedDuration,
  photoMayAutoPlay,
  photoRegistryKey,
  photoWorkSlot,
  resolvePhotoClip,
  tilesSlot,
  type ApprovedPhotoClip,
  type ApprovedPhotoRegistry,
  type PhotoPlaybackSlot,
} from "./photo-video.ts";

const scissor = photoWorkSlot("scissor", 1, 4, 40, 360)!;
const run = photoWorkSlot("run", 1, 4, 0, 360)!;
const sha = "a".repeat(64);
const clip: ApprovedPhotoClip = {
  chart: 1, exercise: 5, action: "scissor", exerciseId: "chart1-scissor-jump",
  revision: "synthetic-unreleased-test", sha256: sha, url: approvedMediaPath(sha),
  mediaType: "video/mp4", codec: "h264", durationSeconds: 5,
  frameCount: 120, fps: 24,
};

function registry(item: ApprovedPhotoClip, key = scissor.registryKey): ApprovedPhotoRegistry {
  return { schemaVersion: 1, clips: { [key]: item } };
}

describe("photographic video admission remains fail-closed", () => {
  it("ships absolutely no approved media and never treats a diagnostic as release-ready", () => {
    assert.deepEqual(APPROVED_PHOTO_REGISTRY, { schemaVersion: 1, clips: {} });
    assert.deepEqual(resolvePhotoClip(APPROVED_PHOTO_REGISTRY, scissor), { status: "missing" });
  });

  it("separates exercise-5 running from its scissor-jump segments", () => {
    assert.notEqual(scissor.registryKey, run.registryKey);
    assert.equal(scissor.registryKey, "c1-e5-scissor");
    assert.equal(run.registryKey, "c1-e5-run");
    assert.equal(resolvePhotoClip(registry(clip), run).status, "missing");
    assert.equal(resolvePhotoClip(registry({ ...clip, action: "run" }), scissor).status, "invalid");
    const wrongExercise = { ...clip, exerciseId: "chart1-toe-touch" };
    assert.equal(resolvePhotoClip(registry(wrongExercise), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry({ ...clip, chart: 2 }), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry({ ...clip, exercise: 4 }), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry(clip, "c2-e5-scissor"), scissor).status, "missing");
  });

  it("requires exact same-origin content-addressed path and digest", () => {
    assert.equal(resolvePhotoClip(registry(clip), scissor).status, "ready");
    const invalid = [
      "https://attacker.example/approved-photo/" + sha + ".mp4",
      "https://cwarloe.github.io/5BX/game/approved-photo/" + sha + ".mp4",
      "//attacker.example/" + sha + ".mp4",
      "/../../private/" + sha + ".mp4",
      "/5BX/game/approved-photo/../" + sha + ".mp4",
      "/5BX/game/approved-photo/%2e%2e/" + sha + ".mp4",
      "/5BX/game/approved-photo/%2f" + sha + ".mp4",
      "/5BX/game/approved-photo/%5c" + sha + ".mp4",
      approvedMediaPath(sha) + "?token=anything",
      approvedMediaPath(sha) + "#fragment",
      approvedMediaPath(sha).replace(sha, "b".repeat(64)),
      "/approved-photo/" + sha + ".mp4",
    ];
    for (const url of invalid) {
      assert.equal(resolvePhotoClip(registry({ ...clip, url }), scissor).status, "invalid", url);
    }
    assert.equal(resolvePhotoClip(registry({ ...clip, sha256: sha.toUpperCase() }), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry({ ...clip, mediaType: "video/webm" as "video/mp4" }), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry({ ...clip, codec: "vp9" as "h264" }), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry({ ...clip, revision: "synthetic " }), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry({ ...clip, revision: 42 as unknown as string }), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(null as unknown as ApprovedPhotoRegistry, scissor).status, "invalid");
    assert.equal(resolvePhotoClip({ schemaVersion: 1, clips: [] } as unknown as ApprovedPhotoRegistry, scissor).status, "invalid");
    assert.equal(resolvePhotoClip({ schemaVersion: 1, clips: { [scissor.registryKey]: null } } as unknown as ApprovedPhotoRegistry, scissor).status, "invalid");
    const rootSiteClip = { ...clip, url: approvedMediaPath(sha, "/") };
    assert.equal(resolvePhotoClip(registry(rootSiteClip), scissor, "/").status, "ready");
    assert.equal(resolvePhotoClip(registry(rootSiteClip), scissor).status, "invalid");
    assert.equal(resolvePhotoClip(registry(clip), scissor, "/arbitrary/").status, "invalid");
  });

  it("cannot be tricked by a forged slot or unsupported chart", () => {
    assert.equal(photoWorkSlot("scissor", 2, 4, 40, 360), null);
    assert.equal(photoWorkSlot("toe-multi", 1, 0, 10, 120), null);
    assert.equal(photoWorkSlot("scissor", 1, 4, 39, 360), null);
    assert.equal(photoWorkSlot("run", 1, 4, 40, 360), null);
    assert.equal(photoWorkSlot("situp", 1, 0, 0, 120), null);
    assert.equal(photoWorkSlot("toe", 1, 0, 120, 120), null);
    assert.equal(resolvePhotoClip(registry(clip), { ...scissor, chart: 2 } as unknown as PhotoPlaybackSlot).status, "invalid");
    assert.equal(resolvePhotoClip(registry(clip), { ...scissor, registryKey: "c1-e1-toe" }).status, "invalid");
    assert.equal(resolvePhotoClip(registry({ ...clip, frameCount: 144, durationSeconds: 6 }),
      { ...scissor, slotSeconds: 6 }).status, "invalid");
    assert.equal(resolvePhotoClip(registry(clip), { ...scissor, elapsedSeconds: 500 }).status, "invalid");
    assert.equal(photoWorkSlot("scissor", 1, 4, 40, 5), null);
    assert.equal(photoRegistryKey(1, 5, "scissor"), "c1-e5-scissor");
  });

  it("enforces complete loop tiles, not a plausible but truncated clip", () => {
    assert.equal(tilesSlot(5, 5), true);
    assert.equal(tilesSlot(4, 40), true);
    for (const durationSeconds of [4.95, 5.0005, 5.01, 5.05, 6, 0, -1, Number.NaN]) {
      assert.equal(tilesSlot(durationSeconds, 5), false, String(durationSeconds));
      assert.equal(resolvePhotoClip(registry({ ...clip, durationSeconds }), scissor).status,
        Number.isFinite(durationSeconds) ? "duration-mismatch" : "invalid", String(durationSeconds));
    }
    assert.equal(tilesSlot(6, 40), false);
    assert.equal(resolvePhotoClip(registry({ ...clip, frameCount: 121 }), scissor).status, "duration-mismatch");
    assert.equal(resolvePhotoClip(registry({ ...clip, fps: 23.9 }), scissor).status, "duration-mismatch");
  });

  it("checks decoded/media metadata before a hypothetical frame may be shown", () => {
    assert.equal(matchesReviewedDuration(5, clip, 5), true);
    for (const actual of [4.95, 5.0005, 5.01, 5.05, 6, Number.NaN]) {
      assert.equal(matchesReviewedDuration(actual, clip, 5), false, String(actual));
    }
  });

  it("uses exact simulation boundaries and distinct running/jump cycles", () => {
    const beforeJump = photoWorkSlot("run", 1, 4, 39.999, 360)!;
    const jump = photoWorkSlot("scissor", 1, 4, 40, 360)!;
    const endJump = photoWorkSlot("scissor", 1, 4, 44.9, 360)!;
    const nextJog = photoWorkSlot("run", 1, 4, 45, 360)!;
    assert.equal(beforeJump.slotSeconds, 40);
    assert.equal(jump.slotSeconds, 5);
    assert.equal(jump.elapsedSeconds, 0);
    assert.ok(endJump.elapsedSeconds < 5);
    assert.equal(nextJog.elapsedSeconds, 0);
    assert.notEqual(run.segmentKey, jump.segmentKey);
    assert.notEqual(jump.segmentKey, nextJog.segmentKey);
    assert.equal(nextJog.segmentKey, "c1-e5-1-jog");
    const toe = photoWorkSlot("toe", 1, 0, 43, 120)!;
    assert.equal(toe.slotSeconds, 120);
    assert.equal(toe.elapsedSeconds, 43);
    assert.equal(toe.registryKey, "c1-e1-toe");
  });

  it("does not override reduced-motion preference or simulation pause", () => {
    assert.equal(photoMayAutoPlay(true, true, false), false);
    assert.equal(photoMayAutoPlay(true, true, true), true);
    assert.equal(photoMayAutoPlay(true, false, false), true);
    assert.equal(photoMayAutoPlay(false, false, true), false);
    assert.equal(photoMayAutoPlay(false, true, true), false);
  });
});
