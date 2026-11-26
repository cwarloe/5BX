import { useCallback, useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import {
  advance,
  beginIntro,
  createSim,
  pauseSim,
  resetSim,
  resumeSim,
  skipSim,
  snapshot,
  type Hooks,
  type Phase,
  type Sim,
} from "@/lib/engine";
import {
  FRAME_COUNTS,
  INTRO_SECONDS,
  JOG_SECONDS,
  LEVELS,
  isLevelId,
  LEVEL_ORDER,
  OUTRO_SECONDS,
  RUN_CYCLE,
  RUN_INDEX,
  exerciseCue,
  formatClock,
  formatRemain,
  runActionForChart,
  toeActionForChart,
  pushupActionForChart,
  jumpActionForChart,
  spriteSrc,
  type Action,
  type Exercise,
  type Level,
  type LevelId,
} from "@/lib/levels";
import {
  beepCountdown,
  chimeMinute,
  chimeStart,
  fanfare,
  resumeAudio,
  setSfxEnabled,
  unlockAudio,
} from "@/lib/sfx";
import { resumeSpeech, setVoiceEnabled, speak, speakCount, stopSpeech } from "@/lib/voice";
import { PhotographicExerciseVideo } from "@/components/photographic-exercise-video";
import { APPROVED_PHOTO_REGISTRY, photoWorkSlot } from "@/lib/photo-video";

const VICTORY_LINES = [
  { at: 0.4, text: "CHART 1 COMPLETE!" },
  { at: 2.15, text: "YOU WIN!" },
  { at: 4.05, text: "PERFECT!" },
] as const;

const TREE_SLOTS = ["tree-a", "tree-b", "tree-c", "tree-d", "tree-e", "tree-f"];

function frameOf(sim: Sim): "teal" | "gold" | "red" {
  const level = LEVELS[sim.levelId];
  if (sim.phase === "outro" || sim.phase === "done") return "red";
  if (sim.phase === "work" && sim.index === RUN_INDEX) {
    const remain = level.exercises[RUN_INDEX]!.seconds - sim.phaseElapsed;
    return remain <= 10 ? "red" : "gold";
  }
  return "teal";
}

function actionOf(sim: Sim, level: Level): Action {
  if (sim.phase === "idle" || sim.phase === "intro") return "idle";
  const t = sim.phase === "done" ? OUTRO_SECONDS : sim.phaseElapsed;
  if (sim.phase === "outro" || sim.phase === "done") return t >= 2.62 ? "crash" : runActionForChart(level.chart);
  if (sim.index === RUN_INDEX && sim.phaseElapsed % RUN_CYCLE >= JOG_SECONDS) {
    return jumpActionForChart(level.chart);
  }
  if (sim.index === RUN_INDEX) return runActionForChart(level.chart);
  const base = level.exercises[sim.index]!.action;
  if (base === "toe") return toeActionForChart(level.chart);
  if (base === "pushup") return pushupActionForChart(level.chart);
  return base;
}

function popOf(sim: Sim, level: Level): number | null {
  const duration =
    sim.phase === "intro"
      ? INTRO_SECONDS
      : sim.phase === "work"
        ? level.exercises[sim.index]!.seconds
        : 0;
  if (!duration) return null;
  const remain = duration - sim.phaseElapsed;
  if (remain <= 0 || remain > 5) return null;
  return Math.ceil(remain - 1e-9);
}

function remainOf(sim: Sim, level: Level): number {
  if (sim.phase === "idle") return INTRO_SECONDS;
  if (sim.phase === "intro") return Math.max(0, INTRO_SECONDS - sim.phaseElapsed);
  if (sim.phase === "work") {
    return Math.max(0, level.exercises[sim.index]!.seconds - sim.phaseElapsed);
  }
  if (sim.phase === "outro") return Math.max(0, OUTRO_SECONDS - sim.phaseElapsed);
  return 0;
}

function clockOf(sim: Sim): number {
  if (sim.phase === "work") return sim.workoutBase + sim.phaseElapsed;
  if (sim.phase === "outro" || sim.phase === "done") return sim.workoutBase;
  return 0;
}

function nextOf(sim: Sim, level: Level): Exercise | null {
  if (sim.phase === "idle" || sim.phase === "intro") return level.exercises[0]!;
  if (sim.phase === "work" && sim.index < level.exercises.length - 1) {
    return level.exercises[sim.index + 1]!;
  }
  return null;
}

function athleteMotion(phase: Phase, elapsed: number): string {
  if (phase !== "outro" && phase !== "done") return "none";
  const t = phase === "done" ? OUTRO_SECONDS : elapsed;
  if (t < 1.15) {
    const eased = (t / 1.15) ** 2;
    return `translateY(${(-eased * 155).toFixed(1)}%) rotate(${(-eased * 18).toFixed(1)}deg)`;
  }
  if (t < 2.15) return "translateY(-160%) rotate(-18deg)";
  if (t < 2.7) {
    const p = (t - 2.15) / 0.55;
    return `translateY(${(-160 * (1 - p)).toFixed(1)}%) rotate(${(-18 * (1 - p)).toFixed(1)}deg)`;
  }
  if (t < 3.15) {
    const squash = Math.sin(Math.min(1, (t - 2.7) / 0.45) * Math.PI);
    return `translateY(${(squash * 6).toFixed(1)}%) scale(${(1 + squash * 0.42).toFixed(3)}, ${(1 - squash * 0.5).toFixed(3)})`;
  }
  return "none";
}

function shadowAmount(phase: Phase, elapsed: number): number {
  if (phase !== "outro" && phase !== "done") return 1;
  const t = phase === "done" ? OUTRO_SECONDS : elapsed;
  if (t < 1.15) return 1 - (t / 1.15) * 0.82;
  if (t < 2.15) return 0.16;
  if (t < 2.7) return 0.16 + ((t - 2.15) / 0.55) * 0.9;
  return 1;
}

function frameIndex(action: Action, sim: Sim): number {
  const count = FRAME_COUNTS[action];
  if (count <= 1) return 0;
  const time = sim.phase === "idle" ? sim.wall : sim.phaseElapsed;
  const fps = action === "idle" ? 4 : 8;
  return Math.floor(time * fps) % count;
}

function Pines() {
  return (
    <>
      {TREE_SLOTS.map((slot) => (
        <div className={`tree ${slot}`} key={slot} aria-hidden>
          <svg viewBox="0 0 40 70">
            <polygon points="20,2 37,30 31,30 39,50 1,50 9,30 3,30" fill="var(--color-pine)" />
            <polygon points="20,16 31,36 9,36" fill="var(--color-pine-dark)" />
            <rect x="16" y="50" width="8" height="16" fill="var(--color-trunk)" />
          </svg>
        </div>
      ))}
    </>
  );
}

export function WorkoutApp() {
  // The existing published sprite experience stays unchanged. Photographic
  // development preview can be enabled only in a development build, and still
  // admits no footage until an owner-approved registry is generated.
  const photoPreview =
    import.meta.env.DEV && import.meta.env.VITE_PHOTO_PLAYER_PREVIEW === "1";
  const sim = useRef<Sim>(createSim());
  const [view, setView] = useState<Sim>(() => snapshot(sim.current));
  const [sfxOn, setSfxOn] = useState(true);
  const [voiceOn, setVoiceOn] = useState(true);
  const wakeRef = useRef<WakeLockSentinel | null>(null);
  const hooksRef = useRef<Hooks | null>(null);

  // Phones can drop or delay the click after a tap; act on pointer-up and
  // ignore the click that follows it, so each tap runs exactly once.
  const pressStamp = useRef(0);
  const press = (run: () => void) => ({
    onPointerUp: (event: ReactPointerEvent<HTMLButtonElement>) => {
      if (event.button !== 0) return;
      pressStamp.current = performance.now();
      run();
    },
    onClick: () => {
      if (performance.now() - pressStamp.current < 700) return;
      run();
    },
  });
  const apiRef = useRef({ start: () => {}, skip: () => {}, reset: () => {} });

  const acquireWake = useCallback(async () => {
    try {
      if (!("wakeLock" in navigator)) return;
      wakeRef.current = await navigator.wakeLock.request("screen");
    } catch {
      /* unsupported or denied */
    }
  }, []);

  const releaseWake = useCallback(() => {
    const lock = wakeRef.current;
    wakeRef.current = null;
    void lock?.release().catch(() => {});
  }, []);

  hooksRef.current = {
    onCountdown(n, speakIt) {
      beepCountdown(n);
      if (speakIt) speakCount(n);
    },
    onIntervalStart(exercise) {
      chimeStart();
      speak(exerciseCue(exercise));
    },
    onMinute() {
      chimeMinute();
    },
    onComplete() {
      stopSpeech();
      fanfare();
    },
    onOutroDone() {
      releaseWake();
    },
  };

  const publish = useCallback(() => {
    setView(snapshot(sim.current));
  }, []);

  const onStart = useCallback(() => {
    unlockAudio();
    const current = sim.current;
    const hooks = hooksRef.current!;
    if (current.phase === "idle" || current.phase === "done") {
      beginIntro(current, hooks);
      void acquireWake();
      speak("Ready, go!");
      publish();
      return;
    }
    if (current.running) {
      pauseSim(current);
      releaseWake();
      stopSpeech();
      publish();
      return;
    }
    resumeSim(current);
    void acquireWake();
    publish();
  }, [acquireWake, publish, releaseWake]);

  const onSkip = useCallback(() => {
    unlockAudio();
    const current = sim.current;
    skipSim(current, LEVELS[current.levelId], hooksRef.current!);
    if (current.running) void acquireWake();
    else releaseWake();
    publish();
  }, [acquireWake, publish, releaseWake]);

  const onReset = useCallback(() => {
    resetSim(sim.current);
    releaseWake();
    stopSpeech();
    publish();
  }, [publish, releaseWake]);

  apiRef.current.start = onStart;
  apiRef.current.skip = onSkip;
  apiRef.current.reset = onReset;

  useEffect(() => {
    const storedLevel = localStorage.getItem("5bx-level");
    if (storedLevel && isLevelId(storedLevel)) sim.current.levelId = storedLevel;
    if (localStorage.getItem("5bx-sfx") === "0") {
      setSfxEnabled(false);
      setSfxOn(false);
    }
    if (localStorage.getItem("5bx-voice") === "0") {
      setVoiceEnabled(false);
      setVoiceOn(false);
    }
    publish();
  }, [publish]);

  useEffect(() => {
    let raf = 0;
    let last = performance.now();
    let published = 0;
    let dead = false;
    const loop = (now: number) => {
      if (dead) return;
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      const current = sim.current;
      const mark = `${current.phase}|${current.index}|${current.running}|${current.banner?.text ?? ""}`;
      advance(current, dt, LEVELS[current.levelId], hooksRef.current!);
      const next = `${current.phase}|${current.index}|${current.running}|${current.banner?.text ?? ""}`;
      if (next !== mark || now - published > 50) {
        published = now;
        setView(snapshot(current));
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => {
      dead = true;
      cancelAnimationFrame(raf);
    };
  }, []);

  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState !== "visible") return;
      resumeAudio();
      resumeSpeech();
      const current = sim.current;
      if (current.running && current.phase !== "idle" && current.phase !== "done") {
        void acquireWake();
      }
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [acquireWake]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const tag = (event.target as HTMLElement | null)?.tagName;
      if (tag === "SELECT" || tag === "INPUT" || tag === "TEXTAREA") return;
      if (event.code === "Space") {
        event.preventDefault();
        apiRef.current.start();
      } else if (event.key === "s" || event.key === "S") {
        apiRef.current.skip();
      } else if (event.key === "r" || event.key === "R") {
        apiRef.current.reset();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!photoPreview) {
      const actions = Object.keys(FRAME_COUNTS) as Action[];
      for (const action of actions) {
        for (let frame = 0; frame < FRAME_COUNTS[action]; frame += 1) {
          const img = new Image();
          img.src = spriteSrc(action, frame);
        }
      }
    }
    return () => {
      releaseWake();
    };
  }, [photoPreview, releaseWake]);

  const level = LEVELS[view.levelId];
  const action = actionOf(view, level);
  const pop = popOf(view, level);
  const exercise = view.phase === "work" ? level.exercises[view.index]! : null;
  const scissoring = action === "scissor";
  const outroTime = view.phase === "done" ? OUTRO_SECONDS : view.phaseElapsed;
  const showVictory = view.phase === "outro" || view.phase === "done";
  const impact = view.phase === "outro" && view.phaseElapsed >= 2.62 && view.phaseElapsed < 2.95;
  const shaking = view.phase === "outro" && view.phaseElapsed >= 2.62 && view.phaseElapsed < 3.15;
  const shadow = shadowAmount(view.phase, view.phaseElapsed);
  const upcoming = nextOf(view, level);
  const photoSlot =
    view.phase === "work" && exercise
      ? photoWorkSlot(
          action,
          level.chart,
          view.index,
          view.phaseElapsed,
          exercise.seconds,
        )
      : null;
  const paused =
    !view.running && (view.phase === "intro" || view.phase === "work" || view.phase === "outro");
  const status =
    view.phase === "work" && exercise
      ? `${exercise.name}. Goal ${exercise.goal} ${exercise.unit}.`
      : view.phase === "intro" || view.phase === "idle"
        ? `5BX workout, ${level.label}. Get ready.`
        : "Chart 1 complete.";

  const onLevel = (id: LevelId) => {
    if (id === sim.current.levelId && sim.current.phase === "idle") {
      return;
    }
    sim.current.levelId = id;
    resetSim(sim.current);
    localStorage.setItem("5bx-level", id);
    releaseWake();
    stopSpeech();
    publish();
  };

  return (
    <main className="shell" data-frame={frameOf(view)} data-phase={view.phase} data-interval={view.index + 1}>
      <p className="sr-only" aria-live="polite">
        {status}
      </p>
      <section className={photoPreview ? "stage photographic-stage" : shaking ? "stage shake" : "stage"} aria-label="Workout stage">
        {photoPreview ? (
          <div className="photographic-player-stage">
            <PhotographicExerciseVideo
              registry={APPROVED_PHOTO_REGISTRY}
              slot={photoSlot}
              playing={view.running}
              label={exercise?.name ?? "5BX workout"}
              buildBase={import.meta.env.BASE_URL || "/"}
            />
          </div>
        ) : (
          <>
            <div className="sky" />
            <div className="sun" aria-hidden />
            <div className="ground" />
            <Pines />
            <div
              className="contact-shadow"
              style={{ transform: `translateX(-50%) scaleX(${shadow.toFixed(3)})`, opacity: Math.max(0.12, shadow) }}
              aria-hidden
            />
            <div className={action === "crash" ? "athlete splat" : "athlete"}>
              <div className="athlete-motion" style={{ transform: athleteMotion(view.phase, view.phaseElapsed) }}>
                <img
                  src={spriteSrc(action, frameIndex(action, view))}
                  alt=""
                  className={view.phase === "idle" || view.phase === "intro" ? "ghost" : undefined}
                  draggable={false}
                />
              </div>
            </div>
          </>
        )}

        <header className="hud-top">
          {photoPreview ? <p className="photo-preview-label">PHOTOGRAPHIC PREVIEW — UNRELEASED</p> : null}
          {view.phase === "idle" || view.phase === "intro" ? (
            <>
              <p className="kicker">— CHART 1 —</p>
              <h1 className="title">5BX WORKOUT — {level.id}</h1>
              <p className="ready-line">GET READY</p>
              {view.phase === "idle" ? <p className="press-start">PRESS START</p> : null}
            </>
          ) : showVictory ? (
            <>
              <p className="kicker">— FINISH —</p>
              <h1 className="title">CHART 1</h1>
              <p className="goal">COMPLETE</p>
            </>
          ) : (
            <>
              <p className="kicker">— No. {view.index + 1}/5 —</p>
              <h1 className="title">{exercise?.name}</h1>
              <p className="goal">
                GOAL: {exercise?.goal} {exercise?.unit}
              </p>
              {exercise?.note ? <p className="note">{exercise.note}</p> : null}
            </>
          )}
        </header>

        {paused ? <p className="paused-flag">PAUSED</p> : null}
        {pop ? (
          <div className="countdown">
            <span className="countdown-num">{pop}</span>
          </div>
        ) : null}
        {view.banner && view.phase === "work" ? <div className="milestone">{view.banner.text}</div> : null}
        {scissoring && !pop ? <div className="alert-badge">10 SCISSOR JUMPS!</div> : null}
        {impact ? <div className="impact-flash" /> : null}

        {showVictory ? (
          <div className="victory">
            {VICTORY_LINES.filter((line) => outroTime >= line.at).map((line) => (
              <p className="victory-line slam" key={line.text}>
                {line.text}
              </p>
            ))}
          </div>
        ) : null}

        <footer className="ground-hud">
          <div className="hud-cell">
            <span className="hud-label">TIME REMAINING</span>
            <span className="hud-time">{formatRemain(remainOf(view, level))}</span>
          </div>
          <div className="hud-cell">
            <span className="clock">{formatClock(clockOf(view))}</span>
          </div>
          <div className="hud-cell hud-next">
            <span className="hud-label">NEXT</span>
            {upcoming ? (
              <div className="mini">
                {!photoPreview ? <img src={spriteSrc(upcoming.action, 0)} alt="" /> : null}
                <span>{upcoming.name}</span>
              </div>
            ) : (
              <span className="mini-finish">FINISH</span>
            )}
          </div>
        </footer>
      </section>

      <nav className="controls" aria-label="Workout controls">
        <select
          aria-label="Level"
          value={view.levelId}
          onChange={(event) => {
            const id = event.target.value;
            if (isLevelId(id)) onLevel(id);
          }}
        >
          {LEVEL_ORDER.map((id) => (
            <option key={id} value={id}>
              {LEVELS[id].label}
            </option>
          ))}
        </select>
        <button type="button" className={view.running ? undefined : "primary"} {...press(onStart)}>
          {view.running ? "Pause" : "Start"}
        </button>
        <button type="button" {...press(onReset)}>
          Reset
        </button>
        <button type="button" aria-label="Skip interval" {...press(onSkip)}>
          Skip
        </button>
        <button
          type="button"
          aria-pressed={sfxOn}
          aria-label={sfxOn ? "Sound effects on" : "Sound effects off"}
          {...press(() => {
            const next = !sfxOn;
            setSfxOn(next);
            setSfxEnabled(next);
            localStorage.setItem("5bx-sfx", next ? "1" : "0");
            if (next) unlockAudio();
          })}
        >
          SFX {sfxOn ? "ON" : "OFF"}
        </button>
        <button
          type="button"
          aria-pressed={voiceOn}
          aria-label={voiceOn ? "Voice on" : "Voice off"}
          {...press(() => {
            const next = !voiceOn;
            setVoiceOn(next);
            setVoiceEnabled(next);
            localStorage.setItem("5bx-voice", next ? "1" : "0");
          })}
        >
          Voice {voiceOn ? "ON" : "OFF"}
        </button>
      </nav>
    </main>
  );
}
