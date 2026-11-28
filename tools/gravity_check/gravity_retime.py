#!/usr/bin/env python3
# TEST ONLY: experimental. Not part of the production pipeline and not wired into
# tools/video_finish. See README.md in this folder.
"""gravity_retime.py: measure how "floaty" an AI-generated jump is, and retime it to real gravity.

    python3 gravity_retime.py input.mp4 --height-m 1.55 --out corrected.mp4

How it works
------------
1. Cut the person out of every frame (rembg u2net) and track two things:
   - the pelvis (centroid of the dark shorts inside the cut-out), a stand-in for the
     centre of mass;
   - the lowest foot (bottom of the cut-out).
2. A "flight" is a run of frames where the lowest foot is clearly above the ground line.
3. In flight a body is a projectile, so its height follows y(t) = y0 + v0 t - 1/2 g t^2.
   Fit a parabola to the pelvis over each flight. The t^2 term gives the apparent
   gravity in pixels/s^2. Divide by pixels-per-metre (person's pixel height / real
   height) to get m/s^2.
4. Playing footage s times faster multiplies every acceleration by s^2, so the speed-up
   that makes the flight obey Earth gravity is
        s = sqrt(9.81 / g_apparent)
   Equivalently, real airtime for a rise h is T = 2 * sqrt(2h / g), i.e. T * fps frames.
5. Build a time map. Ground frames keep their speed; each flight is played s times
   faster, with a short ease in and out so takeoff and landing don't jerk. Output frames
   are made by averaging the source frames each output frame covers. That gives natural
   motion blur (like a camera shutter) instead of skipped frames.
6. Re-measure the output the same way and report the new apparent g, as a check.

Limits
------
- The pixel scale assumes the camera is level and the person stays at one distance
  (side view). A wrong height guess scales g by the same ratio; the speed-up changes
  by its square root, e.g. 10% height error = 5% speed error.
- The pelvis is only a proxy for the centre of mass. Big leg swings move the true centre
  of mass a little, so fits are approximate (r^2 is reported per flight).
- This fixes timing only. If the AI drew an impossible pose, retiming can't fix that.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

G = 9.81


def read_frames(path: Path):
    w, h = map(int, subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(path)], text=True).strip().split(","))
    fps_s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=r_frame_rate", "-of", "csv=p=0", str(path)], text=True).strip()
    num, den = map(int, fps_s.split("/"))
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3), num / den


def masks(frames: np.ndarray, cache: Path | None):
    if cache and cache.exists():
        return np.unpackbits(np.load(cache))[: frames[..., 0].size].reshape(frames.shape[:3]).astype(bool)
    from rembg import new_session, remove
    s = new_session("u2net")
    m = np.stack([np.asarray(remove(Image.fromarray(f), session=s, only_mask=True)) > 128 for f in frames])
    if cache:
        np.save(cache, np.packbits(m))
    return m


def track(frames: np.ndarray, m: np.ndarray):
    """Per frame: pelvis y (shorts centroid), lowest foot y, person pixel height."""
    hip, bot, hgt = [], [], []
    for f, mk in zip(frames, m):
        ys, xs = np.nonzero(mk)
        t, b = ys.min(), ys.max()
        a = f.astype(int)
        mx, mn = a.max(2), a.min(2)
        dark = mk & (mx < 120) & (mx > 35) & ((mx - mn) < 28)      # charcoal shorts
        dy, _ = np.nonzero(dark)
        sel = (dy > t + 0.3 * (b - t)) & (dy < t + 0.75 * (b - t))
        hip.append(dy[sel].mean() if sel.sum() > 30 else np.nan)
        bot.append(b)
        hgt.append(b - t)
    hip = np.array(hip, float)
    nan = np.isnan(hip)
    if nan.any():
        hip[nan] = np.interp(np.nonzero(nan)[0], np.nonzero(~nan)[0], hip[~nan])
    return hip, np.array(bot, float), np.array(hgt, float)


def flights(bot: np.ndarray, clearance_px: float, min_frames: int):
    ground = np.percentile(bot, 90)
    air = bot < ground - clearance_px
    out, i = [], 0
    while i < len(air):
        if air[i]:
            j = i
            while j + 1 < len(air) and air[j + 1]:
                j += 1
            if j - i + 1 >= min_frames:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out, ground


def fit(hip, segs, fps, px_per_m):
    res = []
    for i, j in segs:
        t = np.arange(i, j + 1) / fps
        y = hip[i:j + 1]
        a, b, c = np.polyfit(t, y, 2)
        f = np.polyval([a, b, c], t)
        r2 = 1 - ((y - f) ** 2).sum() / max(1e-9, ((y - y.mean()) ** 2).sum())
        g_app = 2 * a / px_per_m              # image y grows downward, so falling = +a
        res.append(dict(start_frame=i, end_frame=j, frames=j - i + 1, airtime_s=round((j - i + 1) / fps, 3),
                        pelvis_rise_m=round(float((y[0] - y.min()) / px_per_m), 3),
                        g_apparent=round(float(g_app), 2), fit_r2=round(float(r2), 3),
                        speedup=round(float(np.sqrt(G / g_app)) if g_app > 0 else float("nan"), 2)))
    return res


def time_map(n, fps, flight_res, ease_frames=2, max_speed=6.0):
    """Source-frame speed per source frame: 1 on the ground, s in flight, eased at edges."""
    speed = np.ones(n)
    for r in flight_res:
        s = min(max_speed, max(1.0, r["speedup"]))
        i, j = r["start_frame"], r["end_frame"]
        speed[i:j + 1] = s
        for k in range(1, ease_frames + 1):           # ease in and out
            w = k / (ease_frames + 1)
            if i - k >= 0:
                speed[i - k] = max(speed[i - k], 1 + (s - 1) * (1 - w))
            if j + k < n:
                speed[j + k] = max(speed[j + k], 1 + (s - 1) * (1 - w))
    # output time at which each source frame is shown
    t_out = np.concatenate([[0], np.cumsum(1.0 / (speed[:-1] * fps))])
    return speed, t_out


def render(frames, fps, t_out, out: Path, blur: bool = True):
    """Each output frame averages every source frame whose display time falls inside it (motion blur)."""
    n_out = int(np.floor(t_out[-1] * fps)) + 1
    h, w = frames.shape[1:3]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    src_idx = np.arange(len(frames))
    for k in range(n_out):
        lo, hi = k / fps, (k + 1) / fps
        sel = src_idx[(t_out >= lo) & (t_out < hi)]
        if len(sel) == 0:                              # slower than source: hold nearest
            sel = [int(np.argmin(np.abs(t_out - lo)))]
        if blur and len(sel) > 1:
            img = frames[sel].astype(np.float32).mean(0)
        else:
            img = frames[sel[len(sel) // 2]]           # crisp: middle source frame only
        ff.stdin.write(np.asarray(img, np.uint8).tobytes())
    ff.stdin.close()
    ff.wait()
    return n_out


def analyse(path: Path, height_m: float, cache: Path | None, clearance_px: float, min_frames: int):
    frames, fps = read_frames(path)
    m = masks(frames, cache)
    hip, bot, hgt = track(frames, m)
    px_per_m = np.percentile(hgt, 95) / height_m
    segs, ground = flights(bot, clearance_px, min_frames)
    return frames, fps, hip, bot, px_per_m, fit(hip, segs, fps, px_per_m)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--height-m", type=float, default=1.55, help="real standing height of the person (m)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--clearance-px", type=float, default=14, help="how far above ground both feet must be to count as airborne")
    ap.add_argument("--min-frames", type=int, default=6)
    ap.add_argument("--max-speed", type=float, default=6.0)
    ap.add_argument("--no-blur", action="store_true", help="pick one source frame per output frame instead of averaging (crisper, slightly steppier)")
    a = ap.parse_args()

    frames, fps, hip, bot, ppm, res = analyse(a.video, a.height_m, a.video.with_suffix(".masks.npy"), a.clearance_px, a.min_frames)
    speed, t_out = time_map(len(frames), fps, res, max_speed=a.max_speed)
    n_out = render(frames, fps, t_out, a.out, blur=not a.no_blur)

    # check: measure the corrected video the same way
    _, _, _, _, _, res2 = analyse(a.out, a.height_m, a.out.with_suffix(".masks.npy"), a.clearance_px, max(3, a.min_frames // 3))
    g_before = float(np.median([r["g_apparent"] for r in res])) if res else None
    g_after = float(np.median([r["g_apparent"] for r in res2])) if res2 else None
    report = dict(input=str(a.video), fps=fps, height_m=a.height_m, px_per_m=round(float(ppm), 1),
                  seconds_in=round(len(frames) / fps, 2), seconds_out=round(n_out / fps, 2),
                  median_g_before=g_before, median_g_after=g_after, flights_before=res, flights_after=res2)
    a.out.with_suffix(".gravity.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: v for k, v in report.items() if not k.startswith("flights")}, indent=1))


if __name__ == "__main__":
    main()
