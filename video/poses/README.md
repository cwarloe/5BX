# Pose library

Every pose of every movement as a standalone transparent PNG, numbered in the
order the movement is performed.

```
chart1/
  ex1-toe-touching/      1.png 2.png 3.png
  ex2-partial-sit-up/    1.png 2.png 3.png
  ex3-alternate-leg-raise/ 1.png 2.png 3.png
  ex4-knee-push-up/      1.png 2.png 3.png
  ex5-stationary-run/    1.png 2.png 3.png 4.png
  ex5-scissor-jumps/     1.png 2.png 3.png
chart1.json              what each folder is, and the loop order
```

`1` is the start of the movement and the numbers run through it in order. A
movement has as many poses as it needs — the run is drawn in four, the rest in
three — so read the count from `chart1.json` rather than assuming.

Regenerate with `python3 ../extract_poses.py --chart 1`. These are derived
files: the sheets in `../sheets/` are the source of truth.

## What you can rely on

- **Nothing but figure and transparency.** No key colour survives anywhere in
  any file, verified at every alpha level, so they drop onto any background.
- **Three flat inks only** — `#FFFFFF` skin, `#969696` tank, `#F57D0F` shorts.
  Every fully opaque pixel is exactly one of those, with no blends or noise.
- **Registered within a movement.** Every pose of one movement is on an
  identical canvas, standing on a shared floor line and centred. Stack them,
  flip through them or assemble them into a loop with no further alignment.
- **Anti-aliased edges**, so they hold up when scaled above native size.

## What to watch for

- **They are drawn for dark backgrounds.** The skin is pure white, so the
  figure all but vanishes on a light one. That is the art's intent, not a fault
  in the extraction.
- **Canvas size differs between movements**, because a man lying down needs a
  different frame from a man standing up. Registration is guaranteed *within* a
  movement, not across movements. Relative sizing between exercises is the
  video pipeline's job — see `DEPTH` and the scale notes in `../README.md`.
- **Native resolution is whatever the sheet gave.** The sheets are 1280x720, so
  a single pose is a few hundred pixels. That is enough for a 1080p render; it
  is not enough for print or a large upscale. Those need the sheets regenerated
  at a larger size, not these files resampled.

## Loop order

`chart1.json` gives each movement a `loop`: the pose order that reads as one
repetition. It is not simply 1..N — a toe touch returns through the standing
pose between the fold and the back bend, so its loop is `1 2 1 3`.
