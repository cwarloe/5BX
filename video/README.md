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
   exercises and costs nothing.
5. **Loop** each pose cycle at the exercise's real cadence, overlay the title,
   countdown and progress bar, and concatenate with break cards.

One scale is used for every pose in a sheet, and it must satisfy both width and
height: on a toe touch the *widest* pose is the fold and the *tallest* is the
stand, and they are not the same pose. Scaling on width alone pushes the
standing figure off the top of the frame.

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

## Known weak spots

- **Alternate leg raise** — in strict side profile, "near leg" and "far leg"
  look nearly identical, so the alternation is subtle.
- **Scissor jumps** — the mid-air pose does not read as clearly airborne.
- No voiceover yet. `Voice.say()` in the app is the equivalent seam.
