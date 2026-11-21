# AI-Generated Exercise Video (5BX Workout Mixer): Lessons Learned

**Date:** November 19, 2026
**Project:** A full 5BX workout video starring a cartoon "sprite boy"
**Repos involved:** `cwarloe/5BX` (data and the original `video/chart.py` pipeline), `cwarloe/video-game-5bx` and `cwarloe/5bx-video-game` (two Grok Build exports of the same idea; the second is a later iteration)

**Short version:** Image-to-video clips look great and get the form wrong. One generated *strip per exercise*, checked against the booklet and assembled by a data-driven script, gets the form right and keeps the character identical. Total image spend for the working set was about 56,000 ElevenLabs credits (about $10).

---

## Character spec (locked by Charles, 2026-11-19)

Keep the clothing from the original Grok sprites: cyan-blue sleeveless tank, red shorts, white ankle socks, **blue sneakers with white soles and laces**. **No green shoes.** Green shoes only ever appeared in the Grok image-to-video clips (back extension, run, cadet-run) as part of the character drift. Spiky black hair, warm tan skin. Measured on the six chosen strips: 0 green pixels on the figure.

Put the shoe colour in every prompt in words ("blue sneakers"), because the model will not keep it on its own across separate generations.

---

## Design principle (Charles, 2026-11-19): build as if it will change, because it will

Everything gets updated in one to four ways, so each kind of change has to be small, quick and cheap. What that meant in practice:

- **One home per kind of change.** Look and wording in `theme.json`, the character in `character.json`, exercises and charts in `strips.json`. Nothing about the plan is typed into the code; the data file is a parameter.
- **Layers kept apart.** Backdrop, the cut-out boy and the on-screen text are separate, so changing one never touches the others.
- **Free fixes before paid ones.** Colours are a hue shift on the transparent cut-out (no credits). Only a wrong pose or a new exercise costs credits, about $1.33 per strip.
- **Cache by what a result depends on** (strip file, theme, code). Measured: an unchanged rebuild 3 s, one cached exercise under a second, a two-exercise recolour about 27 s, against 5:37 for the whole video.
- **Keep the prompts.** The pose list that made each strip is in the repo, so any strip can be regenerated the same way.
- **A smoke test that takes 15 seconds**, so a change can prove it broke nothing.

The kit lives in `cwarloe/knowledge-harvest` at `playbooks/exercise-sprite-video/`.

---

## Layers and in-painting (2026-11-19)

- **Save layers as files, not as workspace state.** Baked sprites (one transparent file per pose, plus anchors), seven backdrop layer files, props and a layer-pack export with a `scene.json` manifest. The kit then rebuilds from files, and another tool can recombine them.
- **The edit tool is a usable in-painting tool.** "Change X, preserve Y" re-renders the strip. On two real weak spots, the untouched figures kept 96-99% of their shape, and it cost about 433 credits a take (about a quarter of a fresh generation). It is not a mask brush: the output size changed (1376x768 to 1280x720) and some takes lost the darker far-side shading. Say what to keep, and check.
- **An edit cannot add a difference that the camera angle hides.** Scissor stance A and B still look alike in profile. That needs a front view, not an edit.
- **Some exercises need another camera.** Astride and jack jumps and chart 3's toe touch cannot be read from the side.
- **Count what is really new before estimating.** By name, starting position and movement, six charts need 32 distinct strips (not 36), and 26 are left. Compare on what changes the picture; comparing the notes made everything look new.

## Camera angle (2026-11-19)

- **The author prefers a slight turn toward the camera** (about 30 to 45 degrees off a pure side view), not a 90 degree profile. Grok Imagine drew the first toe-touch figure that way unprompted and it was liked. New strips ask for it; chart 1 stays in strict side view.
- **It also helps legibility:** near and far limbs are easier to tell apart than in pure profile.
- **Keep one angle inside a strip.** Grok drew pose 1 turned toward the camera and poses 2 to 5 in profile. The crossfade then shows a ghost of the turn. Ask for "the SAME camera angle in every pose".
- **Some exercises still need a true front view** (astride jumps), because the legs and arms move sideways.
- **Tools differ in how many figures they return.** Asked for 4, Grok Imagine returned 5 (an extra bounce pose). Measure the figures before deciding how to use them: here pose 4 was the real press, pose 3 a near-duplicate that works as the rebound.

## Keep and grade every take (2026-11-20)

- **Index the takes you reject as well as the ones you use.** The wired strips were saved, but the alternates lived only in a scratch folder and in the chat. A rejected take with a note ("knees straight in the squat") saves generating it again.
- **Measure what can be counted, grade what cannot.** Figures found, fringe, stray green are automatic. Form, legibility, one camera angle and the same boy are judgment. Record who judged; a model's reading is not an exercise expert's.
- **Weigh form first.** A good-looking strip with the wrong movement is worse than a plain one with the right movement.
- The library is `library/` in the kit (`kit/library.py`).

## What we started with

| Source | What it produced | Verdict |
|---|---|---|
| 5BX `video/chart.py` | A 700 s chart-1 video from flat 4-ink pose strips, every number read from `data/5bx-charts.json` | Right method, flat art |
| Grok Build: 6 image-to-video clips (944×944, 6 s) | Smooth, detailed cartoon boy | Best look, wrong form, character drifts |
| Grok Build: 96×96 pixel sprites, 4 frames each | Cute, cheap | Same form errors, a few outfit changes between sets |

Form problems in the Grok output, compared with the exercise text in `data/5bx-charts.json` (transcribed from the booklet):

- **Partial sit-up:** knees bent, hands behind head, sitting fully upright. The booklet says legs straight, arms at sides, sit up only far enough to see your heels.
- **Knee push-up:** read as a toe push-up. The booklet keeps the knees on the floor.
- **Exercise 3:** drew a back extension. Chart 1 is the alternate leg raise (palms under thighs, one straight leg up at a time).
- **Toe touch:** no backward bend in the frames checked.
- **Stationary run:** a full running stride. The booklet lifts the feet about 4 inches.
- **Character drift between clips:** shoes blue in some clips and green in others, hair and background changing from clip to clip.

---

## What worked

1. **One image per exercise, all poses in a single strip.** Generated pose by pose, the character drifts. Generated as a strip, he stays one boy. Already recorded in 5BX `video/design/NOTES.md`; this run confirmed it again.
2. **Write the pose list from the booklet's own words**, not from "do a push-up". The `start`, `movement` and `notes` fields in the data file became the prompt. Pose counts came from the shipped 5BX sheets (3 poses each, 4 for the run).
3. **One camera angle per exercise, strict side view.** The original booklet changes angle mid-movement, which no tweening can fix.
4. **Shade the far-side arm and leg darker.** In profile the near and far legs look identical. A darker far side is the standard cel-animation fix and the model follows it.
5. **Pin the first good strip as the character reference** for the rest. All six exercises came back as the same boy.
6. **Ask for 4 variations and pick.** Picking is where form gets fixed. For the sit-up, take 1 bent the knees; take 4 was right. Look at every strip against the booklet text before it goes anywhere near video.
7. **Flat magenta background and a soft hue key.** Key on "how much more magenta than green is this pixel", with a ramp and a despill. See "Keying" below.
8. **Reuse the data-driven assembler.** Timing, reps, steps and jump windows all come from the JSON, so the video cannot disagree with the plan.
9. **Anchor each exercise so the figure doesn't slide.** Feet for the sit-up, planted foot for the leg raise, hands for the push-up, head for the run and the jumps. Scale once per exercise so the widest and tallest poses both fit.
10. **A backdrop drawn in code.** Identical across exercises, costs nothing, cannot drift.
11. **Stills before the full render, and temp file plus full-decode check before it counts.** Both come from the Knowledge Harvest video playbook and both paid off again.

## What did not work

1. **Image-to-video for the whole workout.** Drift, wrong form, and no way to correct a single pose. Great for a hero shot, wrong tool for instruction.
2. **A reference image leaks its pose.** Using the push-up strip as the reference for the leg raise returned push-up arms and a bent, kicking leg in all four takes. Fix that worked: use a neutral (standing) reference, say "use it only for appearance, ignore its poses", and spell out the geometry ("arms straight back, palms under the thighs, knee locked straight").
3. **"No ground shadow" was ignored** in all 28 generations that carried it. Do not fight it; key it out.
4. **The background is not exactly #FF00FF.** Measured (255, 59, 253) in the middle fading to (246, 84, 238) at the corners. An exact-color key leaves it behind.
5. **Near leg did all the work in the run.** The first run strips lifted the near leg in both lift poses. It needed "the two lifts must use DIFFERENT legs", with the far leg named and shaded.
6. **Splitting poses on empty columns.** Neighbouring poses overlap in x (one pose's head tip sits over the next pose's shoe). Split by connected shape instead.
7. **A translucent dark banner behind the title** turned the white clouds muddy gray. Outlined text on the sky is enough.
8. **A 3-second hold, then a hard cut,** reads as a slideshow at the booklet's real pace. A short eased crossfade (0.3 s at most) fixed it.
9. **Polling many sessions at once.** The status tool echoes every prompt back, and 20 sessions returned about 80,000 characters. Poll one session, or send the output to a file and read it with jq or Python.
10. **No way to upload a local file** to ElevenLabs from the cloud sandbox. Workarounds: describe the character in text for the first strip, then pin that generation as the reference. A public GitHub raw URL also works with `creative_attach_reference_file`.

## Still unresolved (not fixed, just known)

- **Scissor jumps, stance A against stance B,** look almost the same in profile. Only the shading differs. Same weak spot as the 5BX README lists.
- **The run lifts more than 4 inches.** The model will not draw a small lift reliably. The stride reads as a gentle jog, not a march.
- **I checked every strip against the booklet text as transcribed in `data/5bx-charts.json`, not against the scanned booklet.** Exercise form is the one place being wrong can hurt someone. A person who knows the exercises should look at all six before this is published.
- **Run cadence.** 5BX's `chart.py` plays one four-pose run cycle over four counted steps. The booklet counts a step each time the left foot touches down, which is once per cycle, so the new build plays one cycle per step. I think the new build is right, but that is my reading. Check it.
- **No voiceover, and the break cards have no character.** Both are easy next steps.

---

## Keying (the part that is easy to get wrong)

```python
excess = min(R, B) - G                           # about 190 on the background, about 0 on skin, red, blue, white, black
alpha  = clip((95 - excess) / (95 - 28), 0, 1)   # soft ramp, no erosion needed
R, B  -= max(excess, 0)                          # despill the rim
```

- The purple ground shadow keys out with the background, because its excess is also high.
- Red shorts and blue shoes are safe, because `min(R, B)` is low for both.
- On a green test card there was no pink fringe.

## Prompt skeleton that worked

```
Using the attached reference image ONLY for the character's appearance and art style
(...character details...). IGNORE the poses in the reference image completely.

Create a NEW wide 16:9 pose sheet of that same boy doing <EXERCISE>, shown <N> times
left to right in strict side view, same scale, same invisible floor line, wide gaps.

THE <N> POSES (official exercise, follow exactly):
1. <start position, from the booklet>
2. <middle>
3. <end>   (say what must NOT happen: knees bent, hips piked, hands behind head)

Draw the arm and leg on the far side of the body in a noticeably darker shade.

BACKGROUND: perfectly flat solid magenta (#FF00FF), nothing else. No ground shadow,
no floor line, no scenery, no text.
```

Model: `gemini-3-pro-image`, 16:9, 1K (1376×768), 4 variations. Cost: 1,218 credits per image with no reference, 1,827 with one.

## Spend

| Step | Images | Credits |
|---|---|---|
| Push-up pilot (no reference) | 4 | 4,872 |
| Five other exercises (with reference) | 20 | 36,540 |
| Leg raise retry | 4 | 7,308 |
| Run retry | 4 | 7,308 |
| **Total** | **32** | **56,028 (about $10)** |

## Checklist for the next exercise video

- [ ] Pose list written from the source text, with "must not" lines for the common errors
- [ ] One strip per exercise, one camera angle, far side darker
- [ ] First strip generated with no reference; later strips pin it, with "ignore the poses"
- [ ] 4 variations each; pick against the source text, not against taste
- [ ] Key on magenta excess, check on a green test card
- [ ] Split by connected shape; anchor per exercise; scale once
- [ ] Contact sheet of every composed pose before the full render
- [ ] Render to a temp file, full-decode check, then move into place
- [ ] A person who knows the exercises reviews the final video
