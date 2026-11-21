# Chart 1 sprite form review — commit bb6e03a

**Status:** review plus one proposed option. Not a mandate. Charles has asked for alternatives to be brainstormed; the plan below is one candidate.

**Canonical source:** [cwarloe/5BX](https://github.com/cwarloe/5BX) `data/5bx-charts.json` (transcribed from the scanned 1965 RCAF booklet) and `figures/c1e1.png` to `figures/c6e5.png`. Where a web transcription disagrees with that file, the file wins (for example, the Chart 4–6 run height).

Judged by eye at `bb6e03a`. The sprites carry no pose data, so nothing here is machine-checked.

## Review

`FRAME_COUNTS` matches the Chart 1 files: toe 4, situp 2, back 3, pushup 2, scissor 2, run 4. `back/3.png` is a stray file.

### toe (Exercise 1 — "Feet astride, arms upward. Forward bend to floor touching then stretch upward and backward bend.")
- Poses 0–3 follow the wording in sequence.
- Frame 1 is drawn larger than the others; frame 3 faces the opposite way.
- Frame 0 has the elbows bent and the hands clasped above the head. The text says "arms upward", which means straight arms.
- Frame 0's stance is much wider than frame 2's, so the stance changes during the set.

### situp (Exercise 2 — "Back lying, feet 6" apart, arms at sides. Sit up just far enough to see your heels. Keep legs straight.")
- `situp/0` hasn't changed: hands behind the head and knees bent about 90°. The text says arms at the sides and legs straight.
- `situp/1` is the right pose, but it's drawn larger, the shirt is a different colour, and its floor line is about a quarter of the frame higher.

### back (Exercise 3 — "Front lying, palms placed under the thighs. Raise head and one leg, repeat using legs alternately. Keep leg straight at the knee.")
- `back/1`: the raised leg bends sharply at the knee (the text says to keep it straight), and the body is propped up on the hands instead of having the palms under the thighs.
- `back/2`: both feet are off the floor, one high and one at about hip height. That's the Chart 2 both-legs raise. Chart 1 lifts one leg and keeps the other on the floor. The body also floats above the floor line.
- `back/1` and `back/2` sit above `back/0`'s floor line and face the other way.

### pushup (Exercise 4 — knee push-up: "Straighten arms lifting upper body, keeping the knees on the floor… chest must touch floor.")
- `pushup/0`: the knees are down, but the chest doesn't touch the floor.
- `pushup/1`: a full push-up on the toes with the knees off the floor. That's wrong for a knee push-up.
- `pushup/1`: the hands are ahead of the shoulders. The text says hands under the shoulders.
- `pushup/1` is drawn larger with a lower floor line, and `pushup/0` has grey trousers instead of red shorts.

### run (Exercise 5 — "Lift feet approximately 4 inches off floor", Charts 1–3)
- `run/2` hasn't changed: the thigh comes up to about horizontal, which is roughly a foot of lift instead of about 4 inches.
- `run/0` looks like a different character: larger, with different shorts and hair, and a blue shirt instead of cyan.

### scissor ("Stand with right leg and left arm extended forward, and left leg and right arm extended backward. Jump up, change position before landing. Arms shoulder high.")
- Arms at shoulder height is fixed now.
- `scissor/0` has the arms straight out to the sides like a T, so it reads as an astride jump rather than one arm forward and one back.
- `scissor/1` is the reverse-in-the-air frame, but it touches the floor, while `scissor/0` is the one that's airborne.
- Both frames switch to dark trousers (and `scissor/1` to white shoes).
- The side view can't show which leg pairs with which arm, or that the legs switch, so neither can be checked.

### Outside Chart 1 (same problem, other sets)
- `toe-multi` is set to 6 frames but has 4 files; `pushup-c3` is set to 3 but has 4; `halfknee` is set to 3 but has 4, so the heels-raised frame the text requires never plays; `c4-toe` is missing `4.png`.
- `toeActionForChart` sends Charts 3+ to the side-view `toe-multi`, which can't show the outside-left, between and outside-right touches. The front-view `c3-toe` and `c4-toe` sets aren't used anywhere.
- `runActionForChart` uses the low run for every chart. The booklet says "Lift knees waist high" on Charts 4–6.

## Root cause

Every frame is drawn separately, so the scale, floor line, outfit, facing direction and pose wander from frame to frame, and nothing checks frames against the chart text.

## One option: a single rig with poses stored as data

This is one candidate. **Switching from the current generated pixel art to a code-drawn jointed rig would visibly change the art style. Charles decides that before anyone builds it.**

1. **One rig.** A single 2D figure built from jointed parts, with one outfit (red shorts, one shirt colour), one scale, one floor line and one facing direction. The PNG frames are rendered by code at build time.
2. **Poses as data.** Each frame stores joint angles plus which body parts touch the floor, with one pose for each distinct position the chart text describes. Chart 1:
   - toe: arms straight up; floor touch with the knees slightly bent; stretch up; backward bend.
   - situp: lying flat with the arms at the sides; then a small lift with the legs straight and the head and shoulders off the floor.
   - back: lying face down with the palms under the thighs; right leg raised straight; left leg raised straight; the head up and the other leg on the floor.
   - pushup: knees and chest on the floor with the hands under the shoulders; then arms straight with the knees down and the body straight from the knees.
   - run: low foot, no more than about 4 inches (Charts 1–3).
   - scissor: right leg and left arm forward with the arms at shoulder height; then in the air with the limbs switched.
3. **Rules as tests that fail the build:**
   - size, scale or floor line differs within a set;
   - outfit or facing changes partway through a set;
   - knees off the floor in a knee push-up;
   - chest not on the floor in the push-up down position;
   - hands not under the shoulders in a push-up (except Chart 4, where the booklet puts them about 1 foot from the ears);
   - a leg the text says to keep straight bends more than about 10°;
   - a body part that should be on the floor is floating;
   - the run height doesn't follow the booklet for that chart: foot no higher than about 4 inches on Charts 1–3, knees at waist height on Charts 4–6 (`data/5bx-charts.json`);
   - scissor arms not near shoulder height;
   - the scissor in-the-air frame touches the floor.
4. **Telling left from right.** Draw the scissor jump at three-quarter view, or give the left and right limbs different colours, so a test can check the arm-and-leg pairing.
5. **A contact sheet for each exercise on every build,** with the frames side by side next to the matching RCAF figure.
6. **`FRAME_COUNTS` built from the pose files** for every sprite set, not just Chart 1, and stray files deleted.

**Done when** the Chart 1 tests pass, the contact sheets match the chart text, and a fresh form review comes back clean. Deliver it as a PR; nothing gets pushed to main without Charles's OK.

---
Review by Chief of Staff with additions from 5BX Form Adversary.
