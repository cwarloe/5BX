export type Unit = "REPS" | "STEPS";

export type Action =
  | "idle"
  | "toe"
  | "situp"
  | "back"
  | "pushup"
  | "run"
  | "scissor"
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
  "D-": { id: "D-", label: "Chart 1: D-", exercises: chart([2, 3, 4, 2, 100]) },
  D: { id: "D", label: "Chart 1: D", exercises: chart([3, 4, 5, 3, 145]) },
  "D+": { id: "D+", label: "Chart 1: D+", exercises: chart([4, 5, 6, 3, 175]) },
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

export const FRAME_COUNTS: Record<Action, number> = {
  idle: 4,
  toe: 4,
  situp: 4,
  back: 4,
  pushup: 4,
  run: 4,
  scissor: 4,
  crash: 1,
};

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
