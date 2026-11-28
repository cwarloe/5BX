# gravity_check: TEST ONLY

> **Experimental. Not part of the production pipeline.** Nothing in `tools/video_finish`, `video/` or
> the app calls this. It exists to test one idea: can we measure how floaty an AI-generated jump is,
> and retime it to Earth gravity? Charles decides later whether it becomes a pipeline step.

## The idea

AI video generators don't simulate gravity. A body in the air is a projectile, so its height
follows `y = y0 + v0·t − ½·g·t²`, and the time in the air depends only on how high it rises:

```
airtime  T = 2·√(2h / 9.81)
frames   n = T × fps
```

| Rise | Airtime | Frames at 24 fps |
|---|---|---|
| 5 cm | 0.20 s | ~5 |
| 8 cm (3 in) | 0.26 s | ~6 |
| 10 cm (4 in) | 0.29 s | ~7 |
| 15 cm | 0.35 s | ~8 |
| 20 cm | 0.40 s | ~10 |

Playing footage `s` times faster multiplies every acceleration by `s²`, so the speed-up that puts a
flight back on Earth gravity is `s = √(9.81 / g_apparent)`.

`gravity_retime.py`:
1. Cuts the person out (rembg u2net) and tracks the pelvis (dark shorts, a stand-in for the centre
   of mass) and the lowest foot.
2. Finds each flight, meaning both feet clearly above the ground line.
3. Fits a parabola to the pelvis to get the apparent gravity, using pixels-per-metre from the
   person's pixel height and `--height-m`.
4. Speeds up only the airborne frames by each jump's own `s`, eased over 2 frames at takeoff and
   landing. Ground contact stays at normal speed.
5. Blends the compressed source frames into motion blur (`--no-blur` picks one frame instead).
6. Measures its own output again and writes `<out>.gravity.json`.

```bash
pip install rembg numpy pillow      # plus ffmpeg on PATH
python3 tools/gravity_check/gravity_retime.py clip.mp4 --height-m 1.55 --out clip_retimed.mp4
python3 -m unittest discover -s tools/gravity_check/tests
```

## First test (2026-11-28): LEGACY outdoor-track clip

- **Clip:** `generated_video_19.mp4`, uploaded by Charles. 752x416, 24 fps, 16 s. Mark on the
  **legacy outdoor running track**, doing big split-leg scissor leaps.
- **This is test material only.** The outdoor-track assets are retired for production
  (`AGENTS.md`), so neither the clip nor its outputs are committed or approved for any workout video.
- Result: `sample_result_legacy_track_test.json`.

| | As generated | Retimed |
|---|---|---|
| Pelvis rise per jump | 7–23 cm | same (unchanged) |
| Time in the air per jump | 1.0–1.4 s (24–33 frames) | 0.29–0.42 s (7–10 frames) |
| Apparent gravity (median) | **0.94 m/s²** (about a tenth of Earth; less than the Moon's 1.6) | **8.2 m/s²** measured, and every airtime matches `2·√(2h/g)` within one frame |
| Speed-up per jump | — | 2.1x–4.2x (median 3.2x) |
| Length | 16.0 s | 8.5 s |

**What it shows:** the timing fix works, and the retimed clip looks quicker and a little jerky. That
is the point. These leaps hang in the air three times longer than any person could, and once the
timing is real, it's obvious no middle-school boy could do them. The split-leg flight with the pelvis
barely rising is itself impossible. Retiming fixes timing, not poses.

The re-measured gravity reads a little under 9.81 because fitting a parabola to 7–10 blurred frames
is noisy. The airtime-versus-rise check is the stronger test.

## Known limits
- The scale assumes a level side view with the person at one distance. A height error of x% shifts
  `g` by x% and the speed-up by about x/2 %.
- The pelvis is only a proxy for the centre of mass, so large leg swings make the fit approximate
  (r² is reported per flight).
- The shorts detector expects the dark charcoal shorts. Other wardrobes need a different tracker.
- Motion blur from blending shows some ghosting on fast limbs.

## If this graduates (needs Charles's OK)
- Run it as a check inside `tools/video_finish` for any clip with a hop: report airtime and
  apparent g, and flag clips whose flights are more than about 1.5x too long.
- Put the target into prompts instead, e.g. "each hop about 3 in, about 0.25 s in the air,
  quick return to the floor" (6–7 airborne frames at 24 fps), so less correction is needed.
