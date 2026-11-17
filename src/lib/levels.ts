export type Unit = "REPS" | "STEPS";

export type Action =
  | "idle"
  | "toe"
  | "toe-multi"     // Charts 3+: multi-point + trunk circle
  | "situp"
  | "back"
  | "pushup"
  | "pushup-c3"     // Chart 3: three discrete positions
  | "run"           // All charts: feet ~4 inches off floor
  | "scissor"       // Chart 1 jump
  | "astride"       // Chart 2 jump
  | "halfknee"      // Chart 3: half knee bends (feet stay on floor)
  | "crash";

export type Exercise = {
  name: string;
  seconds: number;
  goal: number;
  unit: Unit;
  action: Exclude<Action, "idle" | "scissor" | "crash">;
  note?: string;
};

export type LevelId = "D-" | "D" | "D+";

export type Level = {
  id: LevelId;
  label: string;
  chart: number;          // 1–6; controls run height and jump style
  exercises: Exercise[];
};

const RUN_NOTE = "10 SCISSOR JUMPS EVERY 75 STEPS";

function chart(goals: [number, number, number, number, number]): Exercise[] {
  return [
    { name: "TOE TOUCHES", seconds: 120, goal: goals[0], unit: "REPS", action: "toe" },
    { name: "SIT-UPS", seconds: 60, goal: goals[1], unit: "REPS", action: "situp" },
    { name: "BACK EXTENSIONS", seconds: 60, goal: goals[2], unit: "REPS", action: "back" },
    { name: "KNEE PUSH-UPS", seconds: 60, goal: goals[3], unit: "REPS", action: "pushup" },
    {
      name: "STATIONARY RUN",
      seconds: 360,
      goal: goals[4],
      unit: "STEPS",
      action: "run",
      note: RUN_NOTE,
    },
  ];
}

export const LEVELS: Record<LevelId, Level> = {
  "D-": { id: "D-", label: "Chart 1: D-", chart: 1, exercises: chart([2, 3, 4, 2, 100]) },
  D: { id: "D", label: "Chart 1: D", chart: 1, exercises: chart([3, 4, 5, 3, 145]) },
  "D+": { id: "D+", label: "Chart 1: D+", chart: 1, exercises: chart([4, 5, 6, 3, 175]) },
};

export const LEVEL_ORDER: LevelId[] = ["D-", "D", "D+"];

export function isLevelId(value: string): value is LevelId {
  return value === "D-" || value === "D" || value === "D+";
}

export const INTRO_SECONDS = 5;
export const OUTRO_SECONDS = 10;
export const RUN_INDEX = 4;
export const JOG_SECONDS = 40;
export const SCISSOR_SECONDS = 5;
export const RUN_CYCLE = JOG_SECONDS + SCISSOR_SECONDS;

export const RUN_BANNERS = [
  { at: 60, text: "5 MINUTES LEFT" },
  { at: 120, text: "4 MINUTES LEFT" },
  { at: 180, text: "3 MINUTES LEFT" },
  { at: 240, text: "2 MINUTES LEFT" },
  { at: 300, text: "1 MINUTE LEFT" },
] as const;

/**
 * HARD RULE: Frame counts are NOT fixed at 4.
 * Each action uses exactly the number of frames that match the actual
 * beats described in the 5BX chart text and the original RCAF figures.
 * Do not pad, truncate, or force any exercise to 4 frames.
 * Chart 1 examples:
 *   toe: 4 (arms up, floor, stretch up, backbend)
 *   situp: 2 (lying, partial see-heels)
 *   back: 3 (lying, right leg, left leg)
 *   pushup: 2 (chest down, arms straight knees down)
 *   scissor: 2 (start stance, reverse in air)
 */
export const FRAME_COUNTS: Record<Action, number> = {
  idle: 4,
  toe: 4,           // Chart 1: arms up, floor, stretch up, backbend
  "toe-multi": 6,   // Chart 3+: arms up, outside L, between, press, outside R, backbend
  situp: 2,         // Chart 1: lying, partial (see heels)
  back: 3,          // Chart 1: lying, right leg, left leg
  pushup: 2,        // Chart 1: chest down, arms straight (knees down)
  "pushup-c3": 3,   // chin front, downward-dog/pike, arms straight
  run: 4,
  scissor: 2,       // start stance, reverse in air
  astride: 4,
  halfknee: 3,      // upright, ~110° bend, upright on toes
  crash: 1,
};

/** All charts use the same low-foot run (~4 inches). */
export function runActionForChart(_chart: number): "run" {
  return "run";
}

/** Returns the correct toe-touch action. */
export function toeActionForChart(chart: number): "toe" | "toe-multi" {
  return chart >= 3 ? "toe-multi" : "toe";
}

/** Returns the correct push-up action. */
export function pushupActionForChart(chart: number): "pushup" | "pushup-c3" {
  return chart === 3 ? "pushup-c3" : "pushup";
}

/** Returns the correct every-75-steps action for the chart. */
export function jumpActionForChart(chart: number): Action {
  if (chart === 1) return "scissor";
  if (chart === 2) return "astride";
  if (chart === 3) return "halfknee";
  // Charts 4–6 jumps not yet sprite-ready; fall back
  return "scissor";
}

export function spriteSrc(action: Action, frame: number): string {
  return `/sprites/${action}/${frame}.png`;
}

export function formatRemain(seconds: number): string {
  const s = Math.max(0, Math.ceil(seconds - 1e-6));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, "0")}`;
}

export function formatClock(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds + 1e-6));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${pad(h)}:${pad(m)}:${pad(r)}`;
}

export function exerciseCue(exercise: Exercise): string {
  const unit = exercise.unit === "STEPS" ? "steps" : "reps";
  return `${exercise.name.toLowerCase()}. ${exercise.goal} ${unit}.`;
}
