# Design notes — how the workout video got its look

Everything in this folder is a design that was made and then *not* used, plus the
one that was. It is kept so the next person (or the next me) does not re-run the
same experiments. The look that shipped is `revisions/dark-coloured-kit-a-CHOSEN.jpg`,
and the production pose sheets that came out of it are in `../sheets/`.

The brief: an avatar-animated 5BX workout video, in the spirit of the
"Scientific 7-Minute Workout" video — a looping figure demonstrating the movement
while a timer and rep count run — but not a copy of it. That reference video uses
soft illustrated figures against a park backdrop with trees.

---

## 1. Can we animate the booklet's own figures?  → partly

`explorations/animation-abc-test.mp4` — three ways of animating the 1961 booklet's
scanned line figures, side by side, same 15 seconds.

| | technique | verdict |
|---|---|---|
| **A** | hard cut between booklet poses | Honest but strobe-like. The figure teleports. |
| **B** | `minterpolate` motion-interpolated tween | **Rejected.** The in-betweener has no idea it is looking at a body. Limbs smear into double exposures and the figure grows ghost arms. Unusable, and no parameter fixes it. |
| **C** | timed holds on each pose, cut on a deliberate cadence, over a drawn backdrop | **Kept as the method.** Reads as a demonstration rather than a glitch. |

C is still the animation method in `chart.py` today. What the test also exposed is
the reason the booklet art could not be the final art:

> **The booklet changes camera angle mid-movement.** Exercise 1 starts front-on and
> the fold is drawn from the side. No in-betweening can rotate a camera. Any
> technique that works on those scans inherits that cut.

That is the whole argument for drawing our own poses: one consistent camera per
exercise, which the booklet never had.

## 2. Does a generated figure hold up at all?  → yes, if all poses come from one image

`explorations/flat-cream-a|b.jpg` — cream ground, full multi-pose strip, coloured kit,
hair, a bit of illustration.
`explorations/silhouette-a|b.jpg` — the opposite extreme: white silhouettes on black,
no interior detail at all.

Both proved the thing that mattered: **generate every pose of a movement in a single
image**, as one strip. Generated per-pose, the character drifts — different build,
different hair, different shorts — and the cycle flickers. Generated as one strip, the
model keeps one character across the row. That constraint has governed every sheet since
and is why `../sheets/` holds one file per exercise, not one file per pose.

The silhouettes also showed the floor: with no interior detail the body is legible but
the *movement* is not — you cannot see which way the torso is facing.

## 3. Three aesthetic directions

Asked for three ideas that might beat the reference video's look rather than copy it.

### `directions/1-rcaf-screenprint.jpg`
1961 recruiting-poster screen print. Cream stock, halftone grain, navy figure, RCAF
roundel behind. Period-correct and genuinely the best-looking image of the three.
**Rejected as the main look:** the figure and the roundel are the same tonal family, so
the body dissolves into the logo. Over 11 minutes of video, the one thing that must stay
readable is the body.

### `directions/2-dark-app-native.jpg`
Black ground, single orange horizon line, white figure. No texture, no scenery.
**Selected direction.** It matches the app's own dark UI, it survives being watched on a
phone at arm's length, and it is cheap to render consistently.
**Note taken:** *"white by itself, there's no differentiation in the body"* — a solid
white figure has no shirt, no shorts, no waist.

### `directions/3-blueprint.jpg`
Technical drawing: navy grid, white contour line-work, motion arcs, callout annotations,
corner registration marks.
**Rejected.** The style's appeal is its annotations, and annotations are exactly what a
generator will get wrong — an arc pointing the wrong way or a mislabelled joint is worse
than no diagram, and it would need hand-checking on all 36 chart/level combinations.

## 4. Revisions — fixing both notes

Two problems to solve: body differentiation (direction 2) and figure/logo contrast
(direction 1). Four attempts:

- **`revisions/dark-lines-only.jpg`** — differentiate with contour lines only: a thin
  line for the shirt hem, another for the waistband, no fill. **Rejected:** at phone size
  a 2px line on white disappears, and the pipeline's palette snap (below) would eat it.
- **`revisions/dark-coloured-kit-a-CHOSEN.jpg`** and **`-b`** — grey tank, orange shorts,
  white skin, black ground, orange ground line. Solves the differentiation note with
  *areas* rather than lines, so it survives both downscaling and palette snapping. **a**
  shipped; **b** is the same idea with a heavier glow under the figure, dropped because the
  glow is a gradient and the pipeline's 4-ink palette cannot keep gradients.
- **`revisions/rcaf-knockout-a|b.jpg`** — the screen-print direction with a cream knockout
  around the figure, so the body sits clearly in front of the roundel instead of inside it.
  This *did* fix the contrast note.

On the knockouts:

> *"The period image that has the roundel is really cool … I think I would like it in the
> top right or something and it might be a nice starting image, maybe even something for
> the thumbnail, but in practice, probably not the best."*

So the RCAF screen print is parked as a **title card / thumbnail** candidate, not the
body of the video. It is kept here for that.

**Final choice:** black background, single orange ground line, white skin, grey tank,
orange shorts — chosen because it differentiates the body, fits the brand colours already
in the app, and is simple enough to reproduce identically across every exercise.

## 5. Production alternates

`../sheets/` holds the six sheets in use. Two exercises got a second take that was not
used:

- **`alternates/ex1-toe-touching-alt.png`** — correct and on-model, but shallower through
  the movement: the fold is tucked rather than reaching (silhouette 228px wide against the
  chosen sheet's 365px) and the final extension opens less. The figure is the only
  instruction the viewer gets, so the version with more range won.
- **`alternates/ex4-knee-push-up-alt.png`** — the bottom of the rep never reaches the
  floor. Bottom-to-top travel is 1.75× in the alternate against 2.08× in the chosen sheet,
  which on a loop reads as a half push-up.

### Why the sheets are 4-ink flats on magenta

The pipeline chroma-keys the magenta, erodes 1px, despills, then snaps what is left to an
explicit four-colour palette. That last step is why nothing in the shipped style may use a
gradient, a soft shadow, texture or an airbrushed edge: automatic quantisation *fails* on
this art, because the background dominates by area and all the palette slots come back as
shades of magenta. Snapping to a fixed palette is the only thing that works, and a fixed
palette means flat areas. Several of the rejected designs above are rejected for exactly
this reason, not for taste.

See `../README.md` for the pipeline itself.
