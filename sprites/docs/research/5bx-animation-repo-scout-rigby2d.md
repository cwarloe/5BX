# 5BX animation Repo Scout: Rigby2D and alternative workflows

**Source:** [For Grok Build — Repo Scout findings for 5BX (Rigby2D pilot)](https://docs.google.com/document/d/1WwEc2idsoYsw9EHDjJenNv1EtIkfe9mNxOJcYe2fVdc/edit), a user-owned Drive document preserved in GitHub on 2026-11-24. The original combines **two read-only research reports**: internal cwarloe repository search and external tools/papers search. Below is a faithful text transfer with headings/lists reconstructed from Docs structure. Repo Scout did **not run** the tools. Treat star counts, dates, prices, licenses, and all linked claims as historical and **unverified for current production**. No solution is approved merely by inclusion.

# For Grok Build — Repo Scout findings for 5BX (Rigby2D pilot)

This note is for Grok Build. It is a faithful write-up of two read-only Repo Scout reports: a search of Charles's own repos, and a later search of other people's public GitHub repos, the web, and AI animation options. Repo Scout changed nothing and did not touch video/design/NOTES.md. It checked code, docs, and papers, but ran none of the outside tools, so none of these is proven on a real 5BX figure. Dates in the outside search are Pacific Time (PT). Times in the internal search are Mountain Time (MT). Links below were verified by Repo Scout. The last sentence of each original report was cut off in the message that reached Chief of Staff. Those unfinished words are omitted here rather than completed.

## Recommendation

Pilot Rigby2D first, on one hard move such as the knee push-up. Judge the result on a contact sheet viewed by a person.

Try PixelLab second, on the same move, and judge it the same way. PixelLab is a paid hosted service. It needs Charles's OK before any spend.

None of these tools has been tested on the 5BX figure yet.

## Cause 1. Animate the existing figure

The need is a way to drive the kept figure from pose data without redrawing or replacing it. The kept figure is the booklet figure, or the grey-tank, orange-shorts sprite on the 4-ink sheets.

- Rigby2D. MIT or Apache-2.0, 295 stars, last commit 2026-11-18. It is a Spine-style editor with weighted meshes, IK and keyframes, plus a CLI and an MCP server. Repo Scout found real mesh code in src/core/meshgeom.js (triangulateMesh and weightsAt). The CLI docs show rigby export --format spritesheet, and Nearest texture sampling keeps edges crisp. PWA fit is very good. It runs as a build step and outputs plain PNGs. The four inks would still need to be snapped afterwards. Risks: it is one person's new public beta. The figure must be cut into parts with hidden areas filled in, and the booklet's camera switch likely needs a separate rig per view.
- Meta Animated Drawings. MIT for code and weights, 12.8k stars, archived, last commit 2025-09-03. This is the proven but archived alternative. Evidence: a real ARAP mesh warp of a raster character (animated_drawings/model/arap.py). A character is a texture, a mask, and a hand-editable joint list. Motion comes from BVH files, and an example jumping-jacks config exists. Limits: it works best for planar limb motion. Output is GIF or MP4 (Repo Scout did not verify a PNG-frame mode). It needs Python and OpenGL, and RCAF motions would have to be authored in BVH. Both this and Rigby2D need the figure cut into parts or given hand-placed joints.
- godot-pixel-cutout-rig. MIT, 3 stars, last commit 2026-06. It is a rigid-parts cutout rig with no mesh, which suits a flat 4-colour look, but it needs Godot and is experimental.
- DragonBonesJS. MIT, 863 stars, last commit 2025-05. It is a runtime only and needs a separate editor. It is useful only for live in-browser playback rather than baked PNGs.
- Skeletal-Animator. MIT, 1 star. A Windows exe with bones and IK that exports PNG plus JSON sheets. It is one person's early project.
Poor fit: First Order Motion and Thin-Plate-Spline. Both are MIT, but they are driven by video rather than pose numbers, are trained on faces and dance, and only ship 256px checkpoints. No tool exists for a palette snap after warping, but 5BX's pipeline already does it.

## Cause 2. A check that looks at the pixels, not the pose numbers

The need is a test that fails on the rendered contact sheet of the kept character (off the canvas, through the floor, a limb detached), backed by a person looking at it. No ready-made test fails a bad rendered character. Pose estimators are known to be weak on drawings.

- agent-sprite-forge sprite QC. MIT, 5.8k stars, last commit 2026-11-12. This is the closest real code. Its generate2dsprite.py has connected_components() with a touches_edge field, bbox_touches_edge(), and a --reject-edge-touch flag. The off-canvas check is built and enforced. Connected components exist, but no rule fails on a detached limb. Floor contact is not covered. It is already vendored in 5bx-video-game under .grok/skills/generate2dsprite.
- pixelmatch (ISC, 7k stars), Playwright toHaveScreenshot (Apache-2.0), and jest-image-snapshot (Apache-2.0). These are visual-regression tools. A person approves the contact sheet once and later changes fail the build. They catch changes, not wrong poses. All three run in Node CI.
- OpenCV or scipy connected components. These are standard building blocks for the detached-limb rule. Nothing packaged exists.
- Pose estimators run on rendered frames: MediaPipe and tfjs pose-detection, both Apache-2.0. tfjs runs in a browser. Meta's paper (arXiv 2303.12741) says photo-trained models "do not perform well upon images of drawn human figures". A drawing-tuned fine-tune exists, animated_drawings_yolov8 (MIT, ONNX, 0 stars). Repo Scout found no evidence for flat 4-ink figures or for lying poses.
Nothing exists for hands-through-floor or shoulders-off-torso checks. Those would have to be custom rules.

## Cause 3. Booklet moves shown on the right body for the right chart

Nothing good exists outside Charles's repos. Existing 5BX and XBX apps show static booklet images, and no repo has pose data tied to the RCAF charts.

The existing 5BX and XBX apps declare no licence and contain no animation or pose data. They are rcaf-daily (an offline PWA with static pamphlet PNGs), ya-5bx-app, louisabraham/5BX, and layolayo/5bx.

free-exercise-db (Unlicense, 2.1k stars) has start and end photos plus text, and includes a sit-up, a scissors jump, and standing toe touches. It has no keypoints and is not RCAF form.

Penn Action has per-frame 13-joint keypoints for jumping jacks, push-ups, and sit-ups. It has no licence and shows real sport rather than RCAF form, so it is timing reference only.

Kabi mascot (CC-BY-4.0) is a rigged Rive bull with 29 workout poses stored as angles, the same approach already rejected.

## Part 4. AI animation alternatives

Anything that redraws per frame breaks the no-new-drawing rule. The only AI option that takes per-frame pose data plus one reference is PixelLab (hosted, paid), and it still redraws.

- Rigby2D or Animated Drawings, from Cause 1. They are the only options that keep the existing pixels. AI is optional: Animated Drawings auto-rigs, and Rigby2D has an MCP server whose level of automation Repo Scout did not check.
- PixelLab, hosted. Cost: "Animate with skeleton v3" (beta) is $0.0436 for 3 frames and $0.0622 for 15. A Tier 1 subscription is required. It takes one skeleton per frame drawn from one reference image, at up to 256x256, and returns PNGs, so it works offline as a build step. It still redraws, so identity is not guaranteed. Its own docs say skeleton estimates "might require touch ups". Pilot it before trusting it. It needs Charles's OK before any spend.
- ControlNet plus IP-Adapter, run locally. The code is Apache-2.0 and ComfyUI is GPL-3.0. It needs a GPU. This is the same approach that already produced a different person every frame. Guides report that OpenPose "does not preserve identity" and that lying or upside-down poses are often missed. Fallback only.
- Sprite diffusion research (arXiv 2412.03685) adapted Animate Anyone to sprites. It reports weaker fine details, and its baselines produced "only stylistically similar outputs". Repo Scout found no released sprite code.
- Hosted image-edit models such as Gemini image. They take no pose-data input and Google itself lists consistency as still being refined. They are weak for booklet accuracy.
In-betweeners are a poor fit. ToonCrafter (Apache-2.0, 6k stars) outputs 512x320 at 16 frames and needs 16 GB or more of GPU memory. The original sentence continued past that point and was cut off, so nothing further is recorded here.

## Internal search of Charles's repos

This section is the earlier Repo Scout search of cwarloe/lessons-learned, cwarloe/5BX, cwarloe/5bx-video-game, and any other relevant cwarloe repo. Every link returned HTTP 200, and blob links are pinned to commit SHAs.

### Short answer

Cause 1: The repos explain why the booklet art was dropped and why drawing each pose separately drifts. Nothing describes driving the existing figure from pose data, whether by cutting it into parts, rigging it, or deforming it.

Cause 2: There is a proposal for rule tests and a contact sheet on every build. No pixel check exists in any repo.

Cause 3: There is one sprite-by-sprite review that says what is wrong with each of the six moves. Nothing says how any move should be drawn correctly. Nothing at all covers the Chart 4-6 jumps.

Issues: cwarloe/5BX, cwarloe/5bx-video-game, and cwarloe/lessons-learned have no issues, open or closed. cwarloe/lessons-learned has nothing relevant to any cause.

### Cause 1 in the repos: moving the kept figure without redrawing it

- 5BX video/design/NOTES.md L15-34 (2026-11-13, merged in PR #6). It tested hard cuts, minterpolate, and timed holds on the booklet figures. Minterpolate was rejected because the in-betweener "has no idea it is looking at a body." Timed holds won. It also says: "The booklet changes camera angle mid-movement... No in-betweening can rotate a camera."
- Same file, L36-50. When each pose is generated separately, "the character drifts: different build, different hair, different shorts." The fix was one strip per movement, which is why video/sheets has one file per exercise.
- Same file, L77-105 and L120-128, plus video/README.md L56-76. These document why the grey-tank, orange-shorts kit was chosen and the 4-ink pipeline: magenta key, then 1px erode, then despill, then snap to four colours. This is a partial match. It is a constraint that any warp or rig of this art has to survive, not a way to move the figure.
- 5bx-video-game docs/sprite-form-review-bb6e03a.md L50-81 (2026-11-17, only on the open PR #1 branch). It proposes "One rig" with "poses as data," meaning joint angles plus which parts touch the floor. It warns this "would visibly change the art style. Charles decides." This looks like where the rejected stick figure came from.
- The template skill .grok/skills/game-character-consistency is generic Grok Build guidance, not Charles's writing. It says to edit from one base image.
### Cause 2 in the repos: a check that looks at pixels

- Same PR #1 doc, L7 and L66-78. Line 7 says "Judged by eye... nothing here is machine-checked." Option 3 proposes build-failing rules on pose data: scale or floor line drift, floating contact parts, a straight leg bending more than about 10 degrees, and a scissor in-air frame touching the floor. Option 5 proposes a contact sheet per exercise on every build, next to the matching RCAF figure. Option 4 suggests a three-quarter view or different limb colours so arm-leg pairing can be tested. This is partial: pose data, not pixels.
- 5BX video/README.md L37-40 and chart.py L81-82 (from PR #5) say "Scaling on width alone pushes the standing figure off the top of the frame." Someone found it by eye and it was never turned into a test.
- 5BX video/README.md L74-83 gives a human-look rule: "Check any new sheet against the booklet before shipping." It lists known weak spots: near and far leg look alike in side view, and the scissor does not read as airborne.
- 5BX tests/01-core.js only checks that the figure images load (naturalWidth > 0).
- Same habit in other products: knowledge-harvest playbook L54-58 says to render a contact sheet before the full render, which "caught 3 layout bugs." mr-life-manager video/PRODUCTION.md L58 shows contact frames were inspected for clipping. Neither is about a character.
### Cause 3 in the repos: booklet moves on the right body for the right chart

- 5BX data/5bx-charts.json has the booklet text, for example L113 "Lift feet approximately 4 inches" and L225 for the outside-left, between, and outside-right toe touch.
- PR #1 sprite review L9-48 is a partial match for all six moves. It says what is wrong and fixes nothing.
- Run: run/2 lifts about a foot, not 4 inches. runActionForChart uses the low run for every chart, but Charts 4-6 say knees waist high (levels.ts L108-111). Commit 307b52e removed run-high, which conflicts with the booklet. 5BX README L73 flagged the same mismatch in August.
- Toe touch: Charts 3 and up go to the side-view toe-multi. The front-view c3-toe and c4-toe sets are unused, and c4-toe is missing 4.png (levels.ts L113-116). Commit 20d0374 lists the six c3-toe beats.
- Knee push-up: the chest is not down, pushup/1 is a full push-up on the toes, and the hands are ahead of the shoulders.
- Sit-up: situp/0 has hands behind the head and knees bent. situp/1 has the right pose but a different size and shirt.
- Back raise: back/1 bends the raised knee. back/2 lifts both legs, which is the Chart 2 move.
- Scissor: scissor/0 has T-arms like an astride jump. The in-air frame touches the floor. The side view cannot show arm-leg pairing.
- levels.ts confirms the context that 5bx-video-game only has Chart 1 levels, and Charts 4-6 jumps fall back to the scissor. L26 shows Chart 1 levels only. L124-130 has "Charts 4-6 jumps not yet sprite-ready; fall back" and returns scissor. The booklet's Chart 4-6 jumps are semi-squat, semi-spread eagle, and jack jumps.
- Camera change in the booklet's own toe touch: NOTES.md L29-34 and video/README.md L63-66. The README also says the scanned knee push-up "down" pose is a flat blob.
