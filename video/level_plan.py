"""Timeline planning for a per-level 5BX workout video. Pure functions, no media.

Everything numeric comes from data/5bx-charts.json: the per-exercise seconds, the
level's reps and steps, the jump rule (every N steps, M jumps, window seconds) and
the app's pacing defaults (cadence floor/ceiling, transition seconds). The
exercise-5 plan uses the same rules as app.js (Metro.plan), so the video and the
app agree on how many jump sets there are and how fast to step.

A "clip" here is a looping studio MP4 from tools/video_finish, described by its
frames per loop (cycle_frames) and how many counted reps one loop shows
(reps_per_loop). The planner never slows a clip down (slow motion looks wrong);
when the level needs fewer reps than fit, it either spaces them with a held start
pose between reps ("spread") or does them first and then holds ("front").
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "5bx-charts.json"


def load_data(path: Path = DATA) -> dict:
    return json.loads(path.read_text())


@dataclass
class Segment:
    """One stretch of the timeline. kind: card | reps | hold | run | jumps | done."""
    kind: str
    exercise: int | None
    seconds: float
    clip: str | None = None
    speed: float = 1.0
    reps: int = 0            # counted reps (or steps / jumps) performed in this segment
    count_from: int = 0      # counter value at the segment start
    count_total: int = 0     # the number the counter counts toward
    label: str = ""          # what the counter counts: REPS, STEPS, JUMPS
    timer_start: float = 0.0 # exercise countdown remaining at segment start (s)
    timer_total: float = 0.0 # exercise allotted time (s)
    notes: list[str] = field(default_factory=list)


@dataclass
class ClipInfo:
    name: str
    cycle_frames: int
    reps_per_loop: float
    fps: int = 24

    @property
    def rep_seconds(self) -> float:
        return self.cycle_frames / self.fps / self.reps_per_loop


def ex5_plan(data: dict, chart: int, level: str) -> dict:
    """Same rules as app.js Metro.plan."""
    c = data["charts"][chart - 1]
    ex5 = c["exercises"][4]
    target = c["levels"][level]["steps"]
    every = ex5.get("jumpEvery", 75)
    window = ex5.get("jumpWindowSeconds", 12)
    sets = max(0, math.ceil(target / every) - 1)
    allot = data["timing"]["secondsPerExercise"][4]
    step_seconds = max(30, allot - sets * window)
    needed = target / step_seconds * 60
    d = data["appDefaults"]
    cadence = min(d["cadenceCeiling"], max(d["cadenceFloor"], needed))
    return dict(target=target, every=every, count=ex5.get("jumpCount", 10), window=window,
                sets=sets, cadence=cadence, needed=needed, allot=allot)


def plan_reps(ex: int, n: int, allot: float, clip: ClipInfo, pacing: str,
              max_speed: float) -> list[Segment]:
    """Exercises 1-4: n counted reps inside allot seconds."""
    natural = n * clip.rep_seconds
    segs: list[Segment] = []
    notes: list[str] = []
    if natural <= allot:
        speed = 1.0
    else:
        speed = natural / allot
        if speed > max_speed:
            notes.append(f"clip needs {speed:.2f}x to fit {n} reps in {allot:.0f}s "
                         f"(limit {max_speed}x): source clip is too slow for this level")
    rep_s = clip.rep_seconds / speed
    work = n * rep_s
    spare = max(0.0, allot - work)
    t = allot
    if pacing == "spread" and n > 0 and spare > 0:
        gap = spare / n           # hold after each rep, so the set ends with a hold
        for i in range(n):
            segs.append(Segment("reps", ex, rep_s, clip.name, speed, 1, i, n, "REPS", t, allot))
            t -= rep_s
            segs.append(Segment("hold", ex, gap, clip.name, speed, 0, i + 1, n, "REPS", t, allot))
            t -= gap
    else:
        segs.append(Segment("reps", ex, work, clip.name, speed, n, 0, n, "REPS", t, allot))
        t -= work
        if spare > 0:
            segs.append(Segment("done", ex, spare, clip.name, speed, 0, n, n, "REPS", t, allot))
    if segs:
        segs[0].notes += notes
    return segs


def plan_ex5(p: dict, run: ClipInfo, jump: ClipInfo, max_speed: float) -> list[Segment]:
    """Exercise 5: run blocks of `every` steps, a jump set after each full block
    except the one that finishes the target, then a 'done' hold if time remains."""
    natural_cadence = 60.0 / run.rep_seconds          # counted steps per minute
    speed = p["cadence"] / natural_cadence
    notes = []
    if speed > max_speed:
        notes.append(f"run clip needs {speed:.2f}x to reach {p['cadence']:.0f} steps/min "
                     f"(natural {natural_cadence:.0f}): re-render the run at a quicker natural pace")
    step_s = 60.0 / p["cadence"]
    # Jumps play at natural speed or faster (never slow motion); any time left in the
    # jump window becomes a short hold before running resumes.
    jump_speed = max(1.0, (p["count"] * jump.rep_seconds) / p["window"])
    jump_s = p["count"] * jump.rep_seconds / jump_speed
    segs: list[Segment] = []
    t = p["allot"]
    done = 0
    for s in range(p["sets"] + 1):
        block = min(p["every"], p["target"] - done)
        secs = block * step_s
        segs.append(Segment("run", 5, secs, run.name, speed, block, done, p["target"], "STEPS", t, p["allot"]))
        t -= secs
        done += block
        if s < p["sets"]:
            segs.append(Segment("jumps", 5, jump_s, jump.name, jump_speed, p["count"], 0,
                                p["count"], "SCISSOR JUMPS", t, p["allot"]))
            t -= jump_s
            if p["window"] - jump_s > 0.05:
                segs.append(Segment("hold", 5, p["window"] - jump_s, jump.name, jump_speed, 0,
                                    p["count"], p["count"], "SCISSOR JUMPS", t, p["allot"]))
                t -= p["window"] - jump_s
    if t > 0.05:
        segs.append(Segment("done", 5, t, run.name, speed, 0, p["target"], p["target"], "STEPS", t, p["allot"]))
    elif t < -0.05:
        notes.append(f"exercise 5 runs {-t:.1f}s over its {p['allot']}s (cadence ceiling reached)")
    segs[0].notes += notes
    return segs


def plan_level(data: dict, chart: int, level: str, clips: dict[str, ClipInfo],
               order: list[str], pacing: str = "spread", max_speed: float = 1.6,
               card_seconds: float | None = None, open_seconds: float = 5,
               close_seconds: float = 5) -> list[Segment]:
    """Whole workout. `order` names the clip for exercises 1-4 then run, jump."""
    c = data["charts"][chart - 1]
    reps = c["levels"][level]["reps"]
    allots = data["timing"]["secondsPerExercise"]
    card = data["appDefaults"]["transitionSeconds"] if card_seconds is None else card_seconds
    segs = [Segment("card", 0, open_seconds)]
    for i in range(4):
        segs.append(Segment("card", i + 1, card, order[i]))
        segs += plan_reps(i + 1, reps[i], allots[i], clips[order[i]], pacing, max_speed)
    segs.append(Segment("card", 5, card, order[4]))
    segs += plan_ex5(ex5_plan(data, chart, level), clips[order[4]], clips[order[5]], max_speed)
    segs.append(Segment("card", 6, close_seconds))
    return segs


def total_seconds(segs: list[Segment]) -> float:
    return sum(s.seconds for s in segs)
