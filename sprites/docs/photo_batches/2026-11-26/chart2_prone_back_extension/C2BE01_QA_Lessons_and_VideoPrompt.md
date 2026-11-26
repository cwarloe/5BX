# C2-BE-01 — Chart 2 prone back-extension, four-phase photographic pilot

Status: **CONDITIONAL STILL / NOT VIDEO-APPROVED** (no user final visual or video validation).

## Direct review links

- [Complete 2×2 photo card](https://drive.google.com/file/d/17ar4EuRfdFoKt0gDliqojccwGdMW9ec5/view)
- [1959 RCAF original pose vs our peak](https://drive.google.com/file/d/1IJFOcLlcPb1GSNWqNpIp25C-y0yzpx2A/view)
- [Single peak frame, mechanically upscaled for optional one-image Flow seed](https://drive.google.com/file/d/14LeZyp-JHndAps6C753gBNxbI4aRtYJc/view)

## The pose test

The 1959 RCAF photograph and three prior 35mm-style stills supplied the physical movement: **face-down (prone)**, hands kept alongside thighs, simultaneous modest chest lift and straight legs raised **upward from the hip sockets**, abdomen/hip front remaining supported. Our recent 34K high-knee boy card supplied current character wardrobe/identity.

- **A:** start, prone, straight legs near track, head modestly raised.
- **B:** partial ascent, straight legs begin lifting off track; no hands planted like a push-up.
- **C:** moderate attainable peak, feet well above track; knees stay near-straight, forefoot and pelvis point anatomically correctly; no supine flip.
- **D:** controlled partial descent, feet still slightly above track.

This safely relaxes the huge foot height in the adult 1959 demonstration rather than demanding 99th-percentile lumbar/hip extension from a normal middle-schooler.

## Manual skeptical QA

- **PASS as exploratory still:** all four positions are clearly belly/front-down; single continuous head/torso/hips/thigh/knee/shin/shoe chain; feet lift upward, not translate backward on the track; torso arch is moderate; no reversed feet, detached shoes, duplicated hands, or hyperextended elbows spotted.
- **PASS as exploratory photographic identity:** fixed woodland/track composition, bright blue tank, charcoal shorts, gray socks/sneakers with yellow accents; one dark near-wrist band, no major face/hair transformation between four panels.
- **WATCH:** near shoulder and triceps may still look somewhat more athletic than soft undeveloped 13–14-year-old target. The peak height and exact mechanics need user exercise-form judgment before instructional use.
- **No video claim:** this is a still-card candidate only. For actual video, seed from a **single** source frame. Multiframe images can cause reversal/teleportation and scale drift.

## Optical continuity measurement

The automated 2×2 continuity screen found **blue tank median RGB maximum per-channel range just 4/255 (PASS)** and **track boundary spread 1px (PASS)** using the corrected margin-column track-edge estimator. The original generic majority-red scan had incorrectly reported 32px REVIEW (A=386, B=354, C=355, D=363) because the boy's prone torso obscures a long horizontal stretch of the track. This caught and resolved a *measurement artifact*, not an image defect. The script still cannot certify joint positions, identity, or exercise safety.

## Single-frame 6-second Flow/Grok test prompt (not submitted)

> Animate this **one image** of the same boy lying face-down in a safe back extension. Fixed side-view camera and unchanging track/forest. In 6 seconds, he slowly lowers chest and both straight legs almost to the track, then lifts them together gently back to the reference raised position. His pelvis/front hips remain in contact with track throughout; knees remain nearly straight, feet move up and down around the hip joints and never scoot horizontally. Both arms remain relaxed at his sides, hands next to shorts. He stays the exact same early-teen boy with same blue shirt, charcoal shorts, gray shoes and proportions. One human body, two natural arms, two legs, no camera movement, no cuts, no reversed frames, no shape morphing, no floating entire body, no extreme arch, no hyperextension. Return to the original peak pose at end for seamless loop. Natural sports-film footage.

## Original reference paths

1. Current identity: `artifacts/next_batch_20261126/round8_high_far_elbow/34K_HigherFarElbow_Review.png`
2. 1959 exercise: `artifacts/overnight_tests/references/rcaf_back_extension_1959.png`
3. Previous start: `artifacts/overnight_tests/back_extension_01_start.png`
4. Previous mid: `artifacts/overnight_tests/back_extension_02_halfway.png`
5. Previous peak: `artifacts/overnight_tests/back_extension_03_peak.png`

## Reproduction

Input refs above in order; apply the **verbatim prompt** in `C2BE01_ExactSubmittedPrompt.md` using the built-in image generator. The result may not reproduce pixel-for-pixel, so retain the full card and the exact seed/prompt record. No external video was rendered.

