import {
  INTRO_SECONDS,
  OUTRO_SECONDS,
  RUN_BANNERS,
  RUN_INDEX,
  type Exercise,
  type Level,
  type LevelId,
} from "@/lib/levels";

export type Phase = "idle" | "intro" | "work" | "outro" | "done";

export type Banner = { text: string; until: number };

export type Sim = {
  phase: Phase;
  levelId: LevelId;
  index: number;
  phaseElapsed: number;
  workoutBase: number;
  running: boolean;
  banner: Banner | null;
  firedMarks: number;
  lastPop: number;
  wall: number;
};

export type Hooks = {
  onCountdown: (n: number, speakIt: boolean) => void;
  onIntervalStart: (exercise: Exercise) => void;
  onMinute: () => void;
  onComplete: () => void;
  onOutroDone: () => void;
};

export function createSim(): Sim {
  return {
    phase: "idle",
    levelId: "D-",
    index: 0,
    phaseElapsed: 0,
    workoutBase: 0,
    running: false,
    banner: null,
    firedMarks: 0,
    lastPop: 0,
    wall: 0,
  };
}

export function snapshot(sim: Sim): Sim {
  return {
    ...sim,
    banner: sim.banner ? { ...sim.banner } : null,
  };
}

function resetFields(sim: Sim) {
  sim.phase = "idle";
  sim.index = 0;
  sim.phaseElapsed = 0;
  sim.workoutBase = 0;
  sim.running = false;
  sim.banner = null;
  sim.firedMarks = 0;
  sim.lastPop = 0;
}

export function resetSim(sim: Sim) {
  const levelId = sim.levelId;
  resetFields(sim);
  sim.levelId = levelId;
}

function popFor(remain: number): number {
  if (remain <= 0 || remain > 5) return 0;
  return Math.ceil(remain - 1e-9);
}

function syncPop(sim: Sim, duration: number, speakIt: boolean, hooks: Hooks) {
  const pop = popFor(duration - sim.phaseElapsed);
  if (pop === sim.lastPop) return;
  if (pop > 0) hooks.onCountdown(pop, speakIt);
  sim.lastPop = pop;
}

function enterWork(sim: Sim, level: Level, index: number, hooks: Hooks) {
  sim.phase = "work";
  sim.index = index;
  sim.phaseElapsed = 0;
  sim.banner = null;
  sim.firedMarks = 0;
  sim.lastPop = 0;
  sim.running = true;
  hooks.onIntervalStart(level.exercises[index]!);
}

function enterOutro(sim: Sim, hooks: Hooks) {
  sim.phase = "outro";
  sim.phaseElapsed = 0;
  sim.banner = null;
  sim.lastPop = 0;
  sim.running = true;
  hooks.onComplete();
}

function completeInterval(sim: Sim, level: Level, hooks: Hooks) {
  const exercise = level.exercises[sim.index]!;
  sim.workoutBase += exercise.seconds;
  if (sim.index < level.exercises.length - 1) enterWork(sim, level, sim.index + 1, hooks);
  else enterOutro(sim, hooks);
}

export function beginIntro(sim: Sim, hooks: Hooks) {
  if (sim.phase === "done") resetFields(sim);
  sim.phase = "intro";
  sim.index = 0;
  sim.phaseElapsed = 0;
  sim.workoutBase = 0;
  sim.banner = null;
  sim.firedMarks = 0;
  sim.running = true;
  sim.lastPop = 5;
  hooks.onCountdown(5, false);
}

export function pauseSim(sim: Sim) {
  sim.running = false;
}

export function resumeSim(sim: Sim) {
  if (sim.phase === "idle" || sim.phase === "done") return;
  sim.running = true;
}

export function skipSim(sim: Sim, level: Level, hooks: Hooks) {
  if (sim.phase === "done") resetFields(sim);
  if (sim.phase === "idle" || sim.phase === "intro") {
    sim.workoutBase = 0;
    enterWork(sim, level, 0, hooks);
    return;
  }
  if (sim.phase === "work") {
    completeInterval(sim, level, hooks);
    return;
  }
  if (sim.phase === "outro") {
    sim.phase = "done";
    sim.running = false;
    sim.phaseElapsed = OUTRO_SECONDS;
    hooks.onOutroDone();
  }
}

export function advance(sim: Sim, dt: number, level: Level, hooks: Hooks) {
  sim.wall += dt;
  if (!sim.running) return;

  if (sim.phase === "intro") {
    sim.phaseElapsed += dt;
    if (sim.phaseElapsed >= INTRO_SECONDS) {
      enterWork(sim, level, 0, hooks);
      return;
    }
    syncPop(sim, INTRO_SECONDS, false, hooks);
    return;
  }

  if (sim.phase === "work") {
    const prev = sim.phaseElapsed;
    sim.phaseElapsed += dt;
    const exercise = level.exercises[sim.index]!;
    if (sim.index === RUN_INDEX) {
      RUN_BANNERS.forEach((mark, bit) => {
        const flag = 1 << bit;
        if (prev < mark.at && sim.phaseElapsed >= mark.at && (sim.firedMarks & flag) === 0) {
          sim.firedMarks |= flag;
          sim.banner = { text: mark.text, until: sim.phaseElapsed + 2.6 };
          hooks.onMinute();
        }
      });
    }
    if (sim.banner && sim.phaseElapsed >= sim.banner.until) sim.banner = null;
    if (sim.phaseElapsed >= exercise.seconds) {
      completeInterval(sim, level, hooks);
      return;
    }
    syncPop(sim, exercise.seconds, true, hooks);
    return;
  }

  if (sim.phase === "outro") {
    sim.phaseElapsed += dt;
    if (sim.phaseElapsed >= OUTRO_SECONDS) {
      sim.phaseElapsed = OUTRO_SECONDS;
      sim.phase = "done";
      sim.running = false;
      hooks.onOutroDone();
    }
  }
}
