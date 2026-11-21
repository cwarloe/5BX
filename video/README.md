# Chart videos

Builds a complete 5BX workout video from a handful of still poses. Every timing,
target and label comes from `../data/5bx-charts.json` — the same file the app
runs on — so a video and the app can never disagree about the plan.

## Building

```bash
pip install pillow numpy          # plus ffmpeg on PATH
python3 video/chart.py landscape "A+" chart1.mp4
python3 video/chart.py portrait  "A+" chart1-vertical.mp4
```

Chart 1, level A+ comes out at **700.1s** — 660s of exercise (the plan's
2/1/1/1/6 allotments) plus four 10s breaks. Change the level argument and the
rep counts, cadence and countdowns all follow.

Pass a different sheet directory and work directory as the 4th and 5th
arguments to build another chart.

## How it works

1. **Chroma-key** each sheet in `sheets/`. The figures are drawn on flat
   magenta; the key is "red and blue both high, green low".
2. **Despill and erode.** The anti-aliased rim is a magenta/figure blend that
   reads as a pink halo on a dark backdrop. One pixel of erosion, then a despill
   that only fires where red *and* blue exceed green — so magenta dies and the
   orange shorts (blue well below green) are untouched.
3. **Split** into poses on the empty gutters, all aligned to one floor line.
4. **Composite** onto a backdrop drawn in code, not generated. Generated
   backdrops drift on every run; a drawn one is identical across all 30
   exercises and costs nothing. The current one is on its way out - see
   **The backdrop is being retired** below.
5. **Loop** each pose cycle at the exercise's real cadence, overlay the title,
   countdown and progress bar, and concatenate with break cards.

One scale is used for every pose in a sheet, so the figure does not resize
mid-rep: on a toe touch the *widest* pose is the fold and the *tallest* is the
stand, and they are not the same pose. How that one scale is chosen is below,
under **Scale and staging** - fitting it to the frame is the obvious answer and
the wrong one.

Each pose is also available on its own, cut out on transparency and numbered in
movement order, under `poses/`. Those are generated from the sheets by
`extract_poses.py`; see `poses/README.md`.

## Exercise 5

Not a flat six-minute loop. The run is split into blocks of `jumpEvery` steps
with a jump window after each, exactly as the booklet describes, and the pacing
is derived rather than guessed:

```
400 steps, 5 jump sets x 12s = 60s of jumps
360s - 60s = 300s of running -> 80 steps/min
```

Each block carries a time offset so the countdown runs continuously *through*
the jump windows instead of restarting.

## The sheets

Six pose sheets, one per movement, generated from the booklet's own wording —
its start position, its movement description, its pose count. The booklet stays
the reference; generation only renders those poses more completely. Two things
it buys over the scanned figures:

- **One camera angle per movement.** The booklet switches from front view to
  side view mid-toe-touch, which no amount of in-betweening can smooth over.
- **Legible limbs.** The scanned knee push-up "down" pose is a flat blob where
  the arm merges into the torso.

They are snapped to four flat inks (magenta, white, grey, orange). That is not
only for file size — 5.2MB to 34KB — it also removes the generator's noise from
the chroma edge. Keep that if you regenerate: median-cut quantisation will
instead spend its whole palette on the background, which covers the most area,
and crush the figure's colours entirely.

**Check any new sheet against the booklet before shipping it.** A model can
produce plausible-but-wrong form, and exercise form is the one place in this
project where being wrong can hurt someone.

## Scale and staging

Each pose sheet is generated on its own, so the figures arrive at unrelated
sizes and nothing in the art says how big the person is. The scale therefore
has to be decided here, and the obvious way is wrong.

**Do not fit the figure to the box.** A standing figure is tall and narrow, a
prone one is long and flat, so box-fitting pins each to a different edge: the
standing figure is limited by the box height and the prone figure by its width.
On chart 1 that made the same man 660px tall standing and 1250px long lying
down - he almost doubled in size every time he got on the floor.

Scale is set instead by **how long the body is**: the longest extent of the
figure in any pose of the sheet, which is standing height for an upright
movement and body length for a floor one. That one number goes to `F['body']`,
so the person stays the same person throughout.

> **Superseded (2026-11-21):** Charles approved the opposite: one camera, no
> zoom, lying figures scaled up to 1.537548 x the standing scale, calibrated on
> head landmarks rather than the bounding box, head never cropped. The spec is
> `sprites/config/theme.json` (`stage`). The text below describes the old rule.

`DEPTH` then stages the exercises front to back on purpose. Floor work sits at
`.88`, slightly further from camera than standing work at `1.0`. That is partly
taste and partly honesty: a kneeling push-up really is shorter than a man is
tall, so holding floor work at full body length would oversize it.

A pose can never leave the box - the box fit still applies as a ceiling, it is
just no longer what chooses the scale.

## Pose sheets are per chart

`SHEETS` is keyed by chart id, because the exercises change between charts:
chart 1's knee push-up is a chin-forehead push-up by chart 3 and a chest-slap
push-up by chart 6. A chart with no sheets raises rather than borrowing another
chart's figures, which would demonstrate the wrong movement.

Only chart 1 is drawn. `chart.py ... --chart 4` fails with a message saying so.

`CYCLE_KIND` says how a movement loops, and the pose order is derived from
however many poses the sheet actually holds - sheets are not required to have
three. The kinds are `pingpong` (there and back), `centre` (pose 1 is the
neutral the body returns through) and `loop` (a continuous gait that wraps).

## The backdrop is being retired

**Decision, 2026-11-21: stop using the current drawn backdrop.**

`backdrop()` draws a navy vertical gradient, a receding perspective grid and an
orange glow pooling at the ground line. That is a 2D video-game look, and it
only works if everything in front of it commits to the same look. The figures
no longer do - the art moved to flat screen-print shapes on near-black, and the
grid now fights them instead of supporting them.

Nothing replaces it yet. The figures already carry their own ground reference
through the orange horizon line, so the cheapest honest replacement is a flat
dark field and that line, with the grid and glow dropped.

One caveat on this note: the backdrop was described as "the mountain
background" when the decision was made, and there is nothing by that name
anywhere in this repository - no mountain asset, no mountain code path. The
decision is recorded here against the gradient-and-grid backdrop in
`backdrop()`, which is the only drawn backdrop the pipeline has. If a different
image was meant, this note is filed in the wrong place.

## Known weak spots

- **Alternate leg raise** — in strict side profile, "near leg" and "far leg"
  look nearly identical, so the alternation is subtle.
- **Scissor jumps** — the mid-air pose does not read as clearly airborne.
- No voiceover yet. `Voice.say()` in the app is the equivalent seam.

## Why it looks the way it does

`design/NOTES.md` records the aesthetic directions that were tried and dropped
on the way here, with the images themselves in `design/`. Read it before
changing the style — several of the obvious-looking alternatives are already
ruled out, some of them by the pipeline rather than by taste.
