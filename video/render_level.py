#!/usr/bin/env python3
"""Render one 5BX level as a follow-along video from data, not from typed numbers.

    python3 video/render_level.py --chart 1 --level D- --out out/c1_D-.mp4
    python3 video/render_level.py --chart 1 --all --out-dir out/           # all 12 levels
    python3 video/render_level.py --chart 1 --level A+ --plan-only         # print the timeline

Inputs:
- data/5bx-charts.json: seconds per exercise, reps and steps per level, the jump rule
  and the app's pacing defaults. Nothing numeric is typed in this script.
- video/level_clips.json: which looping studio MP4 (from tools/video_finish) plays each
  exercise, and how many counted reps one loop shows.
- video/level_cards.json: card and overlay wording (draft; the long-term home is the
  exercise contract, see specs/production-framework).

Output: the MP4 plus <name>.build.json (input hashes, code revision, the timeline,
warnings, output hash). A render is a REVIEW candidate. Charles approves final videos.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from level_plan import ClipInfo, Segment, load_data, plan_level, total_seconds  # noqa: E402

W, H, FPS = 1280, 720, 24
OLIVE = (52, 69, 44)
ORANGE = (200, 97, 42)
CREAM = (247, 240, 226)
INK = (35, 45, 30)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_fonts: dict = {}


def font(size: int, bold: bool = True):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_B if bold else FONT_R, size)
    return _fonts[k]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- clips ----------

def clip_info(name: str, spec: dict) -> ClipInfo:
    """cycle_frames = frames in the file / loop repeats reported by video_finish."""
    report = json.loads((ROOT / spec["report"]).read_text())
    m = re.search(r"x(\d+)", report["loop"])
    repeats = int(m.group(1)) if m else 1
    n = int(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
         "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(ROOT / spec["file"])]).strip())
    return ClipInfo(name, n // repeats, float(spec["reps_per_loop"]))


class Clip:
    def __init__(self, path: Path, cycle: int):
        raw = subprocess.check_output(
            ["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", str(cycle),
             "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        self.frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
        self.n = len(self.frames)

    def at(self, pos: float) -> np.ndarray:
        return self.frames[int(pos) % self.n]


# ---------- overlays ----------

def text_w(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def overlay(title: str, tip: str, remaining: int | None, total: float, counter: str,
            banner: str, footer: str) -> tuple[np.ndarray, np.ndarray]:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # title panel, top left
    tw = max(text_w(d, title, font(40)), text_w(d, tip, font(19))) + 48
    d.rounded_rectangle((24, 22, 24 + tw, 128), 14, fill=OLIVE + (232,))
    d.rectangle((24, 120, 24 + tw, 128), fill=ORANGE + (255,))
    d.text((46, 32), title, font=font(40), fill=CREAM)
    d.text((48, 84), tip, font=font(19), fill=(246, 214, 178))
    # countdown ring, top right
    if remaining is not None:
        cx, cy, r = 1188, 84, 58
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=OLIVE + (235,))
        d.arc((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), 0, 360, fill=(110, 122, 98, 255), width=9)
        frac = max(0.0, min(1.0, remaining / total)) if total else 0
        if frac > 0:
            d.arc((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), -90, -90 + 360 * frac,
                  fill=ORANGE + (255,), width=9)
        s = f"{remaining // 60}:{remaining % 60:02}"
        f = font(32)
        b = d.textbbox((0, 0), s, font=f)
        d.text((cx - (b[2] - b[0]) / 2, cy - (b[3] - b[1]) / 2 - b[1]), s, font=f, fill=CREAM)
    # counter pill, bottom left
    counter_right = 0
    if counter:
        f = font(38)
        cw = text_w(d, counter, f) + 48
        d.rounded_rectangle((24, H - 104, 24 + cw, H - 34), 16, fill=CREAM + (240,), outline=ORANGE + (255,), width=4)
        d.text((48, H - 96), counter, font=f, fill=INK)
        counter_right = 24 + cw
    # alert banner, centre
    if banner:
        f = font(34)
        bw = text_w(d, banner, f) + 60
        x0 = W - 24 - bw   # bottom right, clear of the standing figure's head
        y0 = H - 104 if x0 > counter_right + 16 else H - 184   # step up a row if it would touch the counter
        d.rounded_rectangle((x0, y0, x0 + bw, y0 + 70), 16, fill=ORANGE + (240,))
        d.text((x0 + 30, y0 + 10), banner, font=f, fill=CREAM)
    d.text((W - 24 - text_w(d, footer, font(13, False)), H - 26), footer, font=font(13, False), fill=(90, 90, 80, 200))
    a = np.asarray(img)
    ys, xs = np.nonzero(a[..., 3])
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    # Keep only the overlay's bounding box, premultiplied, so the cache stays small.
    crop = a[y0:y1, x0:x1].astype(np.float32)
    alpha = crop[..., 3:] / 255.0
    return (y0, y1, x0, x1), (crop[..., :3] * alpha).astype(np.float32), (1.0 - alpha).astype(np.float32)


def card_frame(bg: np.ndarray | None, kicker: str, title: str, lines: list[str], countdown: int | None) -> np.ndarray:
    if bg is not None:
        base = Image.fromarray(bg).filter(ImageFilter.GaussianBlur(2))
        base = Image.blend(base, Image.new("RGB", (W, H), CREAM), 0.35)
    else:
        base = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(base, "RGBA")
    d.rounded_rectangle((40, 40, 760, 680), 22, fill=CREAM + (238,))
    d.rectangle((40, 40, 760, 58), fill=OLIVE)
    d.rectangle((40, 58, 760, 64), fill=ORANGE)
    d.text((76, 96), kicker, font=font(22), fill=ORANGE)
    f = font(54 if len(title) < 16 else 44)
    d.text((72, 140), title, font=f, fill=OLIVE)
    y = 240
    for ln in lines:
        d.text((76, y), ln, font=font(26, ln.startswith("•") is False), fill=INK)
        y += 46
    if countdown is not None:
        d.text((76, 600), f"STARTS IN {countdown}", font=font(30), fill=ORANGE)
    return np.asarray(base)


# ---------- render ----------

def git_rev() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def render(chart: int, level: str, out: Path, pacing: str, max_speed: float, plan_only: bool) -> dict:
    data = load_data()
    clips_cfg = json.loads((HERE / "level_clips.json").read_text())
    cards = json.loads((HERE / "level_cards.json").read_text())
    order = clips_cfg["order"]
    infos = {k: clip_info(k, clips_cfg["clips"][k]) for k in set(order)}
    segs = plan_level(data, chart, level, infos, order, pacing=pacing, max_speed=max_speed)
    warnings = [n for s in segs for n in s.notes]
    lv = data["charts"][chart - 1]["levels"][level]
    record = {
        "chart": chart, "level": level, "pacing": pacing, "max_speed": max_speed,
        "seconds": round(total_seconds(segs), 2),
        "targets": {"reps": lv["reps"], "steps": lv["steps"]},
        "inputs": {"data/5bx-charts.json": sha256(ROOT / "data/5bx-charts.json"),
                   **{clips_cfg["clips"][k]["file"]: sha256(ROOT / clips_cfg["clips"][k]["file"]) for k in infos},
                   "video/level_cards.json": sha256(HERE / "level_cards.json")},
        "code_revision": git_rev(),
        "clips": {k: {"cycle_frames": v.cycle_frames, "reps_per_loop": v.reps_per_loop,
                      "seconds_per_rep": round(v.rep_seconds, 3)} for k, v in infos.items()},
        "timeline": [{"kind": s.kind, "exercise": s.exercise, "seconds": round(s.seconds, 2),
                      "clip": s.clip, "speed": round(s.speed, 3), "count": f"{s.count_from}->{s.count_from + s.reps}/{s.count_total}"}
                     for s in segs],
        "warnings": warnings,
        "status": "REVIEW render, not approved",
    }
    if plan_only:
        return record

    footer = f"5BX CHART {chart}  ·  LEVEL {level}  ·  REVIEW RENDER"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                           "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    loaded: dict[str, Clip] = {}

    def get(name: str) -> Clip:
        if name not in loaded:
            for k in [k for k in loaded if k not in (order[4], order[5])]:
                del loaded[k]
            loaded[name] = Clip(ROOT / clips_cfg["clips"][name]["file"], infos[name].cycle_frames)
        return loaded[name]

    cache: dict = {}
    heads: dict[str, float] = {}   # playhead per clip, in source frames
    ex_names = {i + 1: cards["exercises"][str(i + 1)] for i in range(5)}
    jump_card = cards["exercises"]["5b"]
    frame_no = 0
    upcoming = [s for s in segs]

    for si, s in enumerate(segs):
        nframes = max(1, round(s.seconds * FPS))
        if s.kind == "card":
            if s.exercise == 0:
                kicker, title, lines = cards["opening"]["kicker"].format(chart=chart, level=level), cards["opening"]["title"], [
                    l.format(**{"r1": lv["reps"][0], "r2": lv["reps"][1], "r3": lv["reps"][2], "r4": lv["reps"][3], "steps": lv["steps"]})
                    for l in cards["opening"]["lines"]]
                bg = None
            elif s.exercise == 6:
                kicker, title, lines, bg = cards["closing"]["kicker"].format(chart=chart, level=level), cards["closing"]["title"], cards["closing"]["lines"], None
            else:
                e = ex_names[s.exercise]
                secs = data["timing"]["secondsPerExercise"][s.exercise - 1]
                target = (f"{lv['reps'][s.exercise - 1]} {e['unit']} in {secs // 60}:{secs % 60:02}" if s.exercise < 5
                          else f"{lv['steps']} steps in {secs // 60}:00  ·  {jump_card['title'].lower()} every 75")
                kicker = f"EXERCISE {s.exercise}  ·  LEVEL {level}"
                title, lines = e["title"], [target] + ["• " + c for c in e["cues"]]
                bg = get(s.clip).at(0)
            for i in range(nframes):
                left = math.ceil((nframes - i) / FPS)
                cd = left if (s.exercise not in (0, 6) and left <= 5) else None
                key = ("card", si, cd)
                if key not in cache:
                    cache[key] = card_frame(bg, kicker, title, lines, cd)
                ff.stdin.write(cache[key].tobytes())
            frame_no += nframes
            continue

        clip = get(s.clip)
        info = infos[s.clip]
        head = heads.get(s.clip, 0.0)
        e = jump_card if s.clip == order[5] else ex_names[s.exercise]
        per = (s.seconds / s.reps) if s.reps else None
        nxt = segs[si + 1] if si + 1 < len(segs) else None
        for i in range(nframes):
            t = i / FPS
            if s.kind in ("reps", "run", "jumps"):
                pos = head + i * s.speed
            elif s.kind == "done" and s.exercise == 5:
                pos = head + i       # steps done: keep jogging gently at natural speed
            else:
                pos = head          # hold / done: freeze on the pose where the last rep ended
            frame = clip.at(pos)
            done_count = s.count_from + (min(s.reps, int(t / per + 1e-6)) if per else 0)
            if s.kind in ("reps",):
                done_count = s.count_from + min(s.reps, int((t + 1e-6) / per))
            counter = f"{s.label} {done_count} / {s.count_total}"
            banner = ""
            if s.kind == "hold":
                if s.exercise == 5:
                    banner = "SET DONE · BACK TO RUNNING"
                else:
                    banner = "REST · NEXT REP COMING" if s.count_from < s.count_total else "SET DONE · REST"
            if s.kind == "done":
                banner = cards["done_banner_run"] if s.exercise == 5 else cards["done_banner"]
            if nxt is not None and nxt.kind == "jumps" and s.kind == "run" and s.seconds - t <= 3:
                banner = f"{jump_card['title']} IN {math.ceil(s.seconds - t)}"
            if s.kind == "jumps" and s.seconds - t <= 2 and not (nxt and nxt.kind == "hold"):
                banner = "BACK TO RUNNING"
            remaining = max(0, math.ceil(s.timer_start - t - 1e-6))
            key = (e["title"], e["tip"], remaining, s.timer_total, counter, banner)
            if key not in cache:
                if len(cache) > 12:   # overlays change about once a second; keep memory flat
                    for k in [k for k in cache if k[0] != "card"][:6]:
                        del cache[k]
                cache[key] = overlay(e["title"], e["tip"], remaining, s.timer_total, counter, banner, footer)
            (y0, y1, x0, x1), pre, inv = cache[key]
            out_f = frame.copy()
            region = out_f[y0:y1, x0:x1].astype(np.float32)
            out_f[y0:y1, x0:x1] = (region * inv + pre).astype(np.uint8)
            ff.stdin.write(out_f.tobytes())
        if s.kind in ("reps", "run", "jumps"):
            heads[s.clip] = head + nframes * s.speed
        frame_no += nframes

    ff.stdin.close()
    ff.wait()
    record["output"] = {"file": str(out), "sha256": sha256(out), "frames": frame_no}
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chart", type=int, default=1)
    ap.add_argument("--level")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--pacing", choices=["spread", "front"], default="spread")
    ap.add_argument("--max-speed", type=float, default=1.6)
    ap.add_argument("--plan-only", action="store_true")
    a = ap.parse_args()
    data = load_data()
    levels = data["levelOrder"] if a.all else [a.level]
    for lv in levels:
        out = Path(a.out) if (a.out and not a.all) else Path(a.out_dir) / f"5bx_c{a.chart}_{lv}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        rec = render(a.chart, lv, out, a.pacing, a.max_speed, a.plan_only)
        if a.plan_only:
            print(json.dumps(rec, indent=1))
        else:
            out.with_suffix(".build.json").write_text(json.dumps(rec, indent=1))
            print(f"{out}  {rec['seconds']}s  warnings: {len(rec['warnings'])}")
            for w in rec["warnings"]:
                print("  !", w)


if __name__ == "__main__":
    main()
