# Pose fixes and loops: lessons learned (Chart 1, November 2026)

**Dates:** 2026-11-21 to 2026-11-24
**Scope:** Chart 1 scissor jumps (four tries) and the Chart 1 knee push-up loop, plus the stage and process
decisions made along the way.
**Goal of this file:** a reproducible handbook, so that the next avatar needs only new pose sprites and none of
the trial and error below.

This file adds to the earlier lessons rather than repeating them. Read these too:

- `sprites/docs/AI_SPRITE_VIDEO_LESSONS.md` for the strip-per-exercise method, the magenta keyer and the prompt skeleton.
- `sprites/qc-line/LESSONS.md` sections 10 to 12 for the knee push-up render pilot and the stage, overlay and prompt decisions of 2026-11-21.
- `video/design/NOTES.md` for the design reasoning. This PR does not edit it.
- `docs/reference/rcaf-1959-film.md` for the 1959 RCAF film, which is the movement reference.
- `data/5bx-charts.json` for every exercise description. Never quote the booklet from memory.

The working files named below (`scissor-fix-v2/`, `scissor-v3/`, `scissor-v4/`, `kneepushup-v1/`,
`layout-mockups/v3/`) are in the animator bot's work folder `/workspace/5bx-anim/`. They are not in Git, in line
with `ART.md`. Helpers worth keeping are in `sprites/kit/posefix.py`.

---

## 1. Locked stage and pipeline decisions

These were decided by Charles on 2026-11-21 and 2026-11-22. They hold for every exercise and every avatar.

| Decision | Value | Why |
|---|---|---|
| Camera | One fixed camera. No zoom and no camera move between exercises | A zoom reads as the boy changing size |
| Frame | 1280x720 for layout work. Render default 1080p at 30 fps; 720p at 24 fps is allowed if it is smoother | Repo default stays 1080p30 |
| Floor line | `floor_y = 650`, `foot_x = 640` on 1280x720 | Same floor in every clip |
| Standing scale | 0.9366 (from `layout-mockups/v3/stage.json`) | Matches the approved v2 row 1 |
| Lying scale | 1.440, which is about 1.54 times standing | A lying figure at the standing scale looked tiny |
| Loops | One seamless 6 to 10 second loop per exercise, repeated to fill the exercise time | No rework per session length |
| Crossfade | Not used | A crossfade between two full drawings shows two bodies at once (D-14) |
| Generated motion | GenerateVideo with the start image as both the first and the last frame, and the end pose as a middle keyframe if needed. Use a start and end pair for transitions between exercises. Short prompts work best | Pinning the first and last frame makes the loop close |
| Bake first | Composite the sprite onto the background at the locked scale **before** any image or video generation | If the model gets a loose sprite it changes his size |
| Overlay | Name card top left, ring timer top right. Every background is subtly darker behind the top corners | The white timer needs a little contrast |

---

## 2. Sprite rules that held up

- **Background.** Ask for flat magenta, about RGB 240,10,240. Image sheets usually come back close to that and the
  kit keyer (`sprites/kit/keyer.py`) handles them.
- **Generated video is different.** The knee push-up source video came back on a textured pink-magenta, measured
  at RGB 221,5,196 from the frame corners. Key it by measuring that colour and unmixing the edge pixels
  (`posefix.key_unmix`), otherwise a pink fringe stays on the outline.
- **Far limbs only slightly darker.** About 18 percent darker (multiply by 0.82), same hue. Never brown or black,
  and never darken a near limb. Chart 3 takes came back 25 to 46 percent darker with a brown shift and had to be
  recoloured (`/workspace/5bx-anim/c3-pushup/out/REPORT.md`). Fix those once with a colour-class recolour saved as a
  new sprite version beside the original, and ask for "only slightly darker" in the prompt.
- **The image model drifts toward lying on his back or sitting.** For the Chart 2 back extension, wording it as
  "yoga locust pose (Salabhasana)" got a prone lift where plain exercise wording did not.
- **When the model will not draw a pose, composite it.** Cut, rotate, mirror and recolour existing drawn parts
  with PIL and numpy. Do not swap in a different movement that the model finds easier. A wrong movement is worse
  than a slightly stiff right one.

---

## 3. Case study: Chart 1 scissor jumps

### What the booklet says

From `data/5bx-charts.json`, Chart 1 exercise 5:

> Scissor jumps - Stand with right leg and left arm extended forward, and left leg and right arm extended backward.
> Jump up - change position of arms and legs before landing. Repeat (arms shoulder high).

The four keyframes are stance A, air A to B, stance B and air B to A. The view is a slight three-quarter, facing
image-right, with his right side nearest the camera.

| Keyframe | Legs | Arms |
|---|---|---|
| Stance A | Right (near) leg forward, left (far) leg back | Left (far) arm forward, right (near) arm back |
| Air A to B | Already in B, feet off the floor | Already in B |
| Stance B | Left (far) leg forward, right (near) leg back | Right (near) arm forward, left (far) arm back |
| Air B to A | Already in A, feet off the floor | Already in A |

The far limbs are drawn about 18 percent darker in every frame, so which leg is forward reads at a glance.

### What we tried and why each one failed

| Try | Approach | Result | Why it failed |
|---|---|---|---|
| v2 (`scissor-fix-v2/`) | Rigged one generated drawing into four poses at about 30 to 35 degrees off side view, far limbs times 0.88 | Rejected | Charles said the angle was too slight. The arms came out as a T or crossed over the chest, and the legs passed close together in the air, so the split did not read |
| v3 (`scissor-v3/`) | Keyed three ChatGPT drawings (stance A, stance B, airborne), built B by swapping parts, scale 0.555, far limbs times 0.82 | Rejected | In stance A and air B to A the near arm was "cocked all the way around his body", across the chest. Charles called it very unnatural |
| ChatGPT sheets (`scissor-v4/src/sheet1.png` to `sheet3.png`) | Asked ChatGPT for all four poses on one sheet | Partly useful | The arms looked natural, but every pose on a sheet had the same arm arrangement, and no pose was clearly airborne |
| v4 (`scissor-v4/`, `work/build4.py`) | Kept the natural ChatGPT arms and swapped them between stances by reusing the drawn arm shapes | Best so far, not approved | See below |

### What v4 does

- The drawn forward arm is cut off, darkened, and placed **behind** the torso as the far forward arm.
- The drawn back arm is moved to the near shoulder, over the body, so the near arm **hangs down and back behind the
  hip** along his side. It never crosses the chest.
- A dark arc is redrawn on the shoulder cap where the old arm was removed.
- Air frames lift the lowest foot 65 px. All four frames share one head from one sheet, so the hair does not change.
- Scale 0.897, floor 650, torso centred at x 640. The numbers are in `scissor-v4/layout.json`.

### What is still wrong with v4

- **Stance B and air A to B reuse the stance A legs with the shading swapped.** The shorts still drape as if his
  right leg were forward, so the hips contradict the shading. Charles caught the same thing earlier.
- **The near arm in A looks pasted on up close.** It starts a little in front of the shoulder, and the redrawn
  shoulder outline is heavier than the original lines.
- **He barely leaves the floor.** The feet rise 65 px, but the split legs are drawn shorter, so the head rises only
  about 4 px.
- **Open form question.** The booklet says "arms shoulder high". v4 keeps the forward arm at shoulder height but
  lets the back arm hang behind the hip, because that is what looked natural. The 5BX Form Adversary should rule on
  this before it is called done.

### The lesson

**Which leg is forward is read from the hips and the drape of the shorts, not from shading.** Darkening the far leg
cannot turn a right-leg-forward drawing into a left-leg-forward one. Each stance needs its own source drawing with
the correct leg forward and the shorts drawn that way. Arms can be fixed by compositing afterward; legs and hips
mostly cannot.

The next step for scissor jumps is one generated drawing of a lunge with his **left (far)** leg clearly forward and
the shorts drawn to match, then the v4 arm method on top.

---

## 4. Case study: Chart 1 knee push-up loop (`kneepushup-v1/`)

### The starting point

Charles supplied a 944x944, 24 fps, 145-frame generated video (`src/kneepushup-source.mp4`) and a standing reference.
The push-up motion was close, but his knees floated above the floor, so it looked like push-ups in the air.
`work/measure.py` found the lowest skin pixel of the legs 40 to 107 px above the floor line (y 653) across the
clip, with the hands planted at about x 650, y 653.

### What worked

1. **Measure landmarks per frame** (`work/measure.py`): background colour from the corners (221,5,196), hand
   position (lowest figure pixel on the right) and knee position (lowest skin pixel on the left), saved to
   `work/landmarks.json`.
2. **Smooth the knee track** with a 7-frame moving average that wraps around the loop, so the correction does not
   jitter.
3. **Rotate each frame about the planted hands** so the knee lands on the floor line. The hands do not move, which
   matches the exercise. A small horizontal correction keeps the knee on the same pixel in every frame
   (`work/fix.py`, now `posefix.rotate_about` with `sx`).
4. **Use one fixed shin and foot**, cut from the first frame and rotated about the knee (14 degrees, the default in `fix.py`) so it lies along
   the floor, then composite the moving body over it with a cut line through the knee.
5. **Loop at frames 1 to 144.** Frame 145 nearly repeats frame 1, so it is dropped. The seam check gave a
   last-to-first difference of 1.18 against a normal frame step of 1.07, so there is no visible jump
   (`posefix.loop_seam`).
6. **Review sheets with words on every tile** (`work/sheets.py`): "frame 17: bottom, chest low", "BEFORE
   (original), top, frame 1", and so on.

Delivered: `01-kneepushup-loop.mp4` (6 s, four push-ups), `02-kneepushup-loop-60s.mp4`, `03-contact-sheet.png`,
`04-before-after.png`.

### What is still wrong

- **The knee join shows.** The seam between the fixed shin and the moving thigh is visible, and there is a pinkish
  patch at the knee at the bottom of the push-up.
- **The feet are frozen.** That is correct for the exercise but looks a little pasted on next to the moving body.
- **The bottom is shallow.** His chest stays about a fist above the floor. That comes from the source video.
- **It is fast.** About 1.5 seconds per push-up. It can be slowed in the render.

### The lesson

A generated motion that is nearly right is worth fixing geometrically before regenerating. Pin whatever touches
the floor (hands, knees) by rotating about it, measure the error per frame, and fix it with one smooth transform.
Regenerating the video would have risked new errors elsewhere.

---

## 5. Process lessons

- **Name every image with a numbered filename and refer to it by that name.** The scissor poses look alike, and
  "that image", "the third one" or "stance C" left Charles unable to tell which picture was meant. Use names such
  as `1-stance-A.png`, `2-air-A-to-B.png`, `3-stance-B.png`, `4-air-B-to-A.png`, and put the label on the tile.
- **Ask ChatGPT for all the poses on one sheet.** One sheet keeps the character, hair, palette and scale
  consistent. Separate requests drift.
- **Check that a chat attachment is really on disk before you start.** Some attachments can be viewed but are not
  on disk, so a copy fails. Verify with `ls` or `cp`; asking for the file again fixed it every time.
- **Describe poses by body side and camera side together:** "right (near) leg forward", not "front leg".
- **Give an honest list of what is still wrong with every delivery,** and get a 5BX Form Adversary biomechanics
  review before anything is called done.

---

## 6. Checklist for the next avatar or exercise

- [ ] Read the exercise text from `data/5bx-charts.json` and the matching moment in the 1959 RCAF film.
- [ ] Write the keyframe table first: each keyframe's legs and arms, by body side and camera side.
- [ ] Generate every keyframe on **one** sheet on flat magenta, far limbs only slightly darker.
- [ ] Make sure each stance has its own drawing with the correct leg forward (hips and shorts, not shading).
- [ ] Key (kit `keyer.key` for sheets, `posefix.key_unmix` for video frames) and check on a white or green card.
- [ ] Composite onto the background at the locked scale and floor line before any generation.
- [ ] Fix small pose errors by compositing or by rotating about the planted joint. Do not change the movement.
- [ ] Build one 6 to 10 second loop, pin the first and last frames, and run `posefix.loop_seam`.
- [ ] Deliver with numbered filenames, a labelled contact sheet and an honest list of what is left.
- [ ] Form Adversary review, then Charles's OK.

---

## 7. What this file could not verify

- The locust wording, the lying-on-back bias and the v2 "angle too slight" verdict are recorded from the working
  conversation. The prompt text that produced the successful back extension is not copied here.
- The scissor v4 frames and the knee push-up loop have not had a Form Adversary review or Charles's final approval.
- The work folders are on the bot's workstation only. If they matter long term, they should be uploaded to the
  Drive folder *Sprite Art 5BX Workout* and listed in `ART.md`.
