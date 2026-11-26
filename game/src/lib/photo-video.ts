import {
  JOG_SECONDS,
  LEVELS,
  RUN_CYCLE,
  RUN_INDEX,
  SCISSOR_SECONDS,
  type Action,
} from "./levels.ts";

/** A trusted build may eventually emit this shape after independent owner review. */
export type PhotoAction = "toe" | "situp" | "back" | "pushup" | "run" | "scissor";

export type ApprovedPhotoClip = Readonly<{
  chart: number;
  exercise: number;
  action: PhotoAction;
  exerciseId: string;
  revision: string;
  url: string;
  sha256: string;
  mediaType: "video/mp4";
  codec: "h264";
  durationSeconds: number;
  frameCount: number;
  fps: number;
}>;

export type ApprovedPhotoRegistry = Readonly<{
  schemaVersion: 1;
  clips: Readonly<Record<string, ApprovedPhotoClip>>;
}>;

/** No diagnostic or speculative video may enter either build by default. */
export const APPROVED_PHOTO_REGISTRY: ApprovedPhotoRegistry = Object.freeze({
  schemaVersion: 1,
  clips: Object.freeze({}),
});

/** Current publishing target, not permission for arbitrary CDN URLs. */
const APPROVED_BUILD_BASES = new Set(["/", "/5BX/game/"]);
export const DEFAULT_APPROVED_BUILD_BASE = "/5BX/game/";

const SHA256_HEX = /^[0-9a-f]{64}$/;
const DURATION_ROUNDING_SECONDS = 0.001;

const EXERCISE_IDENTITY: Readonly<Record<PhotoAction, Readonly<{
  chart: 1;
  exercise: number;
  exerciseId: string;
}>>> = Object.freeze({
  toe: { chart: 1, exercise: 1, exerciseId: "chart1-toe-touch" },
  situp: { chart: 1, exercise: 2, exerciseId: "chart1-partial-situp" },
  back: { chart: 1, exercise: 3, exerciseId: "chart1-alternate-leg-raise" },
  pushup: { chart: 1, exercise: 4, exerciseId: "chart1-kneeling-pushup" },
  run: { chart: 1, exercise: 5, exerciseId: "chart1-stationary-low-run" },
  scissor: { chart: 1, exercise: 5, exerciseId: "chart1-scissor-jump" },
});

export type PhotoPlaybackSlot = Readonly<{
  chart: 1;
  exercise: number;
  action: PhotoAction;
  registryKey: string;
  segmentKey: string;
  elapsedSeconds: number;
  slotSeconds: number;
}>;

export type PhotoClipResolution =
  | { status: "ready"; clip: ApprovedPhotoClip }
  | { status: "missing" | "invalid" | "duration-mismatch" };

/** Distinct exercise-5 running and scissor slots never overwrite one another. */
export function photoRegistryKey(chart: number, exercise: number, action: PhotoAction): string {
  return `c${chart}-e${exercise}-${action}`;
}

/** No partial clips, time stretching, or missing loop tails. */
export function tilesSlot(clipSeconds: number, slotSeconds: number): boolean {
  if (!Number.isFinite(clipSeconds) || !Number.isFinite(slotSeconds)) return false;
  if (clipSeconds <= 0 || slotSeconds <= 0 || clipSeconds > slotSeconds) return false;
  const repeats = Math.round(slotSeconds / clipSeconds);
  return repeats >= 1 && Math.abs(repeats * clipSeconds - slotSeconds) <= DURATION_ROUNDING_SECONDS;
}

/**
 * Browser metadata is checked *before display or playback*. Exact decoded
 * frames and served-byte identity are independent trusted build gates.
 */
export function matchesReviewedDuration(
  observedSeconds: number,
  clip: ApprovedPhotoClip,
  slotSeconds: number,
): boolean {
  if (!Number.isFinite(observedSeconds) || observedSeconds <= 0 || observedSeconds > slotSeconds) return false;
  if (!Number.isInteger(clip.frameCount) || clip.frameCount <= 0 || !Number.isFinite(clip.fps) || clip.fps <= 0) return false;
  const decodedSeconds = clip.frameCount / clip.fps;
  return (
    Math.abs(observedSeconds - clip.durationSeconds) <= DURATION_ROUNDING_SECONDS &&
    Math.abs(observedSeconds - decodedSeconds) <= DURATION_ROUNDING_SECONDS &&
    tilesSlot(observedSeconds, slotSeconds)
  );
}

export function photoMayAutoPlay(
  workoutRunning: boolean,
  prefersReducedMotion: boolean,
  explicitMotionOptIn: boolean,
): boolean {
  return workoutRunning && (!prefersReducedMotion || explicitMotionOptIn);
}

/** Canonical, same-origin, content-addressed path only. */
export function approvedMediaPath(sha256: string, buildBase = DEFAULT_APPROVED_BUILD_BASE): string {
  if (!APPROVED_BUILD_BASES.has(buildBase)) return "";
  return `${buildBase}approved-photo/${sha256}.mp4`;
}

function isPhotoAction(action: Action): action is PhotoAction {
  return Object.hasOwn(EXERCISE_IDENTITY, action);
}

/**
 * Reject wrong chart/exercise, action collisions, untrusted URLs/hashes, and
 * invalid native timing. Browser parsing does NOT authenticate an owner.
 */
export function resolvePhotoClip(
  registry: ApprovedPhotoRegistry,
  slot: PhotoPlaybackSlot,
  buildBase = DEFAULT_APPROVED_BUILD_BASE,
): PhotoClipResolution {
  if (!registry || typeof registry !== "object" || registry.schemaVersion !== 1 ||
      !registry.clips || typeof registry.clips !== "object" || Array.isArray(registry.clips) ||
      !APPROVED_BUILD_BASES.has(buildBase) || !slot || typeof slot !== "object") {
    return { status: "invalid" };
  }
  const expected = EXERCISE_IDENTITY[slot.action];
  const canonicalSlotSeconds = slot.action === "run" ? JOG_SECONDS :
    slot.action === "scissor" ? SCISSOR_SECONDS :
      LEVELS["D-"].exercises[slot.exercise - 1]?.seconds;
  if (!expected || expected.chart !== slot.chart || expected.exercise !== slot.exercise ||
      photoRegistryKey(slot.chart, slot.exercise, slot.action) !== slot.registryKey ||
      slot.slotSeconds !== canonicalSlotSeconds || !Number.isFinite(slot.elapsedSeconds) ||
      slot.elapsedSeconds < 0 || slot.elapsedSeconds >= slot.slotSeconds) {
    return { status: "invalid" };
  }
  if (!Object.hasOwn(registry.clips, slot.registryKey)) return { status: "missing" };
  const clip = registry.clips[slot.registryKey];
  if (!clip || typeof clip !== "object" || Array.isArray(clip)) return { status: "invalid" };
  if (
    clip.chart !== expected.chart || clip.exercise !== expected.exercise ||
    clip.action !== slot.action || clip.exerciseId !== expected.exerciseId ||
    typeof clip.revision !== "string" || !clip.revision || clip.revision.trim() !== clip.revision ||
    clip.mediaType !== "video/mp4" || clip.codec !== "h264" ||
    typeof clip.sha256 !== "string" || !SHA256_HEX.test(clip.sha256) ||
    typeof clip.url !== "string" || clip.url !== approvedMediaPath(clip.sha256, buildBase) ||
    !Number.isFinite(clip.durationSeconds) || !Number.isFinite(clip.fps) ||
    !Number.isInteger(clip.frameCount) || clip.frameCount <= 0 || clip.fps <= 0
  ) {
    return { status: "invalid" };
  }
  if (!tilesSlot(clip.durationSeconds, slot.slotSeconds) ||
      !matchesReviewedDuration(clip.frameCount / clip.fps, clip, slot.slotSeconds)) {
    return { status: "duration-mismatch" };
  }
  return { status: "ready", clip };
}

/**
 * Source-of-truth interval lengths live in levels.ts. A mismatched action
 * or unsupported chart never becomes a playable photographic slot.
 */
export function photoWorkSlot(
  action: Action,
  chart: number,
  exerciseIndex: number,
  phaseElapsed: number,
  exerciseSeconds: number,
): PhotoPlaybackSlot | null {
  if (chart !== 1 || !Number.isInteger(exerciseIndex) || exerciseIndex < 0 || exerciseIndex > RUN_INDEX ||
      !Number.isFinite(phaseElapsed) || phaseElapsed < 0 || !Number.isFinite(exerciseSeconds) ||
      exerciseSeconds <= 0 || phaseElapsed >= exerciseSeconds) return null;
  const exercise = exerciseIndex + 1;
  if (exerciseSeconds !== LEVELS["D-"].exercises[exerciseIndex]?.seconds) return null;
  if (exerciseIndex === RUN_INDEX) {
    const cycle = Math.floor(phaseElapsed / RUN_CYCLE);
    const inCycle = phaseElapsed - cycle * RUN_CYCLE;
    const jump = inCycle >= JOG_SECONDS;
    const expectedAction = jump ? "scissor" : "run";
    if (action !== expectedAction) return null;
    return {
      chart: 1, exercise, action: expectedAction,
      registryKey: photoRegistryKey(1, exercise, expectedAction),
      segmentKey: `c1-e5-${cycle}-${jump ? "jump" : "jog"}`,
      elapsedSeconds: jump ? inCycle - JOG_SECONDS : inCycle,
      slotSeconds: jump ? SCISSOR_SECONDS : JOG_SECONDS,
    };
  }
  if (!isPhotoAction(action)) return null;
  const expected = EXERCISE_IDENTITY[action];
  if (expected.exercise !== exercise) return null;
  return {
    chart: 1, exercise, action,
    registryKey: photoRegistryKey(1, exercise, action),
    segmentKey: `c1-e${exercise}`,
    elapsedSeconds: phaseElapsed,
    slotSeconds: exerciseSeconds,
  };
}
