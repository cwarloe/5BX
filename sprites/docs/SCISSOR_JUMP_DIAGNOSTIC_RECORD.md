# Chart 1 exercise 5: scissor-jump diagnostic record and lessons

**Date:** 2026-11-24  
**Status:** Diagnostic findings and proposed tests; **not exercise-form approval**.  
**Scope:** Existing source footage, AI pose/sprite attempts, white-shoe test, flipbook, and knee-push-up motion comparison. No art, pipeline, app, workout data, or released video was changed by this record.

## Why this record exists

We spent repeated attempts trying to make a visually consistent scissor jump. A recurring failure was that the two legs appeared to switch identities, failed to alternate, or were drawn on the wrong side. Prompt revisions and shoe recoloring did not establish anatomical correctness. **The process did not carry a stable, source-grounded left/right leg identity from recording through sprite generation and animation.** This is a confirmed *workflow gap*, not proof that any particular pose estimator is faulty: no pose estimator was run in the prior six-pose experiment.

Do not generate further scissor-jump candidates solely to solve this defect by rewording a prompt. Isolate the stage that is wrong, test it, and preserve an accepted baseline before paying for another take.

## Sources and preservation

- Authoritative exercise description and timing: original 5BX booklet, its illustrated poses, the RCAF reference film/stills under [`docs/reference/`](../../docs/reference/), and [`data/5bx-charts.json`](../../data/5bx-charts.json). The data file remains the program's timing/count source of truth. Human review resolves form ambiguity; neither an LLM nor the user's test demonstration automatically constitutes approval.
- Original human reference: `VID_20261123_213002.mp4`, Google Drive file ID `1z9mmCui_0FQKlDPOL_6FI_Drij-fPCr8`, approximately 90.13 seconds, 1920 x 1080 at 120 fps. **Keep this original unchanged.** See [`ART.md`](../../ART.md) for external-art indexing. Raw/rejected/reference media belong in Drive, not Git.
- Four working extracts, each approximately 8.5 seconds and normalized to 1280 x 720 at 60 fps: `angle_1_left_profile.mp4` (source 12.0-20.5 s), `angle_2_right_threequarter.mp4` (32.0-40.5 s), `angle_3_left_threequarter.mp4` (47.5-56.0 s), `angle_4_right_profile.mp4` (70.0-78.5 s). Angle labels are *approximate*; check the actual image before prescribing an angle.
- Experimental local outputs: `six_pose_source_sheet.png`, `cartoon_six_pose_sheet.png`, `sprite_pose_01.png` through `_06.png`, `shoe_tracking_v2_sheet.png`, `shoe_tracking_v2_pose_01.png` through `_06.png`, `shoe_tracking_v2_flipbook.mp4`, `angle_4_posterized_motion.mp4`, and knee-push-up loop/interpolation tests. These were scratch/Drive experiments, **not** shipped assets; availability outside the originating session needs verification before a clean-checkout recovery claim.
- Supplied research guide: [`research/limb-swap-depth-fix-guide.md`](research/limb-swap-depth-fix-guide.md). Its third-party assertions, example parameters, and sample code are exploratory, not a verified or implemented 5BX control.
- Existing lessons and requirements: [`AI_SPRITE_VIDEO_LESSONS.md`](AI_SPRITE_VIDEO_LESSONS.md), [`PRODUCTION_CONTROL_PLAN.md`](PRODUCTION_CONTROL_PLAN.md), [`sprites/qc-line/LESSONS.md`](../qc-line/LESSONS.md), and [`specs/sprite-production-line/requirements.md`](../../specs/sprite-production-line/requirements.md).

## What is confirmed, and what is not

| Layer | Evidence observed | Finding / confidence | Next diagnostic |
|---|---|---|---|
| Source capture | Sampled frames from the profile and three-quarter recordings show feet at or outside the lower edge, overlapping lower legs, and motion blur. Both original shoes are unmarked. | **Confirmed limitation:** anatomical foot identity cannot be validated reliably from every sample; no assertion that the human performed the exercise incorrectly. | Reframe with both shoes visible and one *physical* shoe/sock/ankle marker; compare current three-quarter clip first. |
| Pose detection | No DWPose/OpenPose JSON or temporal skeleton trace was produced for the earlier six-pose experiment. | **Not tested.** A pose-label swap is a plausible general defect, not a measured cause here. | Extract and overlay hip/knee/ankle/heel/toe keypoints, keep confidence values, inspect crossing frames. |
| Source-to-sprite generation | Six separate cartoon poses generally retained the cyan-shirt/red-shorts character, but occluded anatomy was inferred; leg identity was not specified as persistent data. | **Confirmed workflow gap:** individual attractive poses do not prove a correct alternating cycle. | Compare source frame, labeled skeleton, and generated pose side by side. |
| White/blue shoe test | The **screen-left/rear** shoe was recolored white in the already-generated poses, while screen-right/front stayed blue. | **Confirmed failed measurement design:** screen position and near/far depth are not an anatomical left/right ID. A different physical foot can inherit white across poses. Color contrast improved readability but not identity proof. | Apply marker to the actual source foot *before* any generative transform; carry that ID through every frame. |
| Depth / occlusion | Side views cause near/far legs to overlap. Some cartoon drawings put outlines or colors over the wrong limb. | **Visually ambiguous; causal depth-control failure not tested.** Near/far is camera-relative and may change during scissor movement. | Check depth/occlusion separately from left/right labels; consider a 3D or part-ID control only if needed. |
| Sprite sequence | Earlier eight-to-twelve-pose attempts kept the same leg forward and included wrong pose order (a tucked/descent frame before an extension). | **Confirmed by review:** the sequence did not demonstrate alternating right-forward -> left-forward -> right-forward landings. | Review an *ordered contact sheet* against a labeled reference cycle before making video. |
| Looping video | `shoe_tracking_v2_flipbook.mp4` is nine seconds at **4 fps**, repeating six drawings; it is not continuous motion capture or video-to-video stylization. | **Confirmed limitation:** repeating stills cannot prove an accurate intermediate foot path. | Inspect one true repetition with preserved identity and no ghosting before testing loop seam. |
| Posterization | `angle_4_posterized_motion.mp4` retained continuous movement from the real recording. | **Worked for motion retention**, but it did not replace the actor with Sprite Boy. | Use as a non-generative baseline in controlled comparisons. |
| Interpolation / crossfade | Earlier generated frame blends produced doubled limbs, face/arm ghosts, or translucent duplicate bodies. The no-fade knee-push-up preview showed a single crisp figure. | **Confirmed:** no-fade removed blending artifacts in that pilot; abruptness remains a different defect. Charles chose **no fade** on 2026-11-21. | Test any interpolator independently on approved source poses and reject double bodies even when FPS is high. |
| Exercise-form approval | Existing candidate strips were artistically chosen but do not have a final named human form approval for this movement. | **Hold release.** Mechanical QC, image similarity, and successful MP4 decoding are not form validation. | Compare every pose/cycle with source booklet/film and record the reviewer and disposition. |

## Lessons to keep (these worked)

1. **Record a real demonstrator for difficult movement.** The original 120-fps take exposes real transition order and improves posed references compared with pure text generation; keep the best camera views and raw footage unchanged.
2. **One appearance reference plus a stable prompt is useful.** Neutral standing character references reproduced the look well in repeated static tests. The cyan tank, red shorts, tan skin, spiky dark hair, white socks, and **blue sneakers** remain the approved Sprite Boy appearance; a visually similar re-generation is not a pixel-identical or anatomically validated sprite.
3. **Keep the motion and appearance as separate variables.** The original 5BX illustration/film is form authority; the cartoon sprite is the appearance authority. Never transfer an erroneous pose simply because the image looks attractive.
4. **Make multiple poses in a shared sheet when practical.** This improved within-sheet consistency over generating individual unrelated character images; however, it **does not** guarantee correct anatomical identity or order.
5. **Moderate three-quarter views make near/far legs more legible** than strict profile for scissor jumps. This updates the earlier Chart 1 strict-side convention *for this exercise only*; do not change an exercise's view without checking the form reference.
6. **Visual markers and asymmetric clothing aid QA** if attached to a particular physical leg at capture. The white-shoe recolor trial demonstrated contrast usefulness, but it was *not* such a physical marker.
7. **Far-side shading can clarify depth**, at the same hue and about 10% darker as recorded in the earlier D-15 decision; excessive darkening reads as a dirty shadow. Shading never substitutes for anatomical ID.
8. **Single-body no-fade previews avoid crossfade ghosts** and are cheap to re-render. Pin first/last frames and inspect the loop; do not confuse a clean cut with smooth motion.
9. **Non-generative posterization preserves source timing** and offers a low-cost comparison, even if it is not the target finished cartoon.
10. **Use repeatable, inexpensive diagnostics first:** source frame contact sheets, per-frame annotations, one-cycle previews, exact camera and pose count checks, same-input comparisons, and original clip retention. The existing kit can render subsets and cache unchanged assets.
11. **Keep negative examples.** The failed ballet-like/slender-legged outputs, repeated same-lead-leg sheets, red/magenta fringe, unwanted green shoes, blurred/cut-off feet, mismatched frontal face, and ghosted loops are all valuable defect signatures. Record their prompt/model/source and archive location when available instead of silently regenerating.

## Lessons that cost time (do not repeat)

| Failure mode | Why changing the prompt alone could not establish success | Prevention |
|---|---|---|
| Asking models to invent unfamiliar scissor motion | No grounded leg-identity or temporal movement control; the model can substitute running or ballet-like movement. | Provide actual movement/video or controlled skeleton; check athletic proportions and actual exercise mechanics. |
| Treating a leading or screen-left shoe as the left foot | The anatomical left foot can appear anywhere in the image, and a near limb can move behind another. | Track the physical left/right joint identity across time. |
| Recoloring shoes after independently generating frames | It tests color placement, not whether the same real foot survived the generation. | Physically mark the source; inspect color continuity in the *generated* result. |
| Treating an attractive pose sheet as a valid cycle | Incorrect order, same-leg repetition, missing exchange, or fake airborne phase can remain hidden. | Review a fixed right-forward -> exchange -> left-forward -> exchange -> right-forward sequence against booklet/film. |
| Raising FPS by simple optical flow | Doubled arms/face and morphing can appear between correctly drawn endpoints. | Reject on frame-by-frame anatomical QA; no fade is safer until a controlled in-between method passes. |
| Reusing a dynamic pose as an identity reference | Model may leak that pose into the next exercise. | Neutral standing appearance image; movement from a separate reference. |
| Excessive camera/profile changes within one strip | Turning, scale and pose become ambiguous and can ghost during transitions. | One prescribed view per shot; multi-view tests use the *same* motion track. |
| Exact magenta/color assumptions | Generated backgrounds and edges are not exact RGB keys, causing halos. | Soft measured chroma key and alpha/edge inspection; no generator-drawn shadow. |
| Ignoring source feet at frame edge | Hidden toe/heel positions must be invented by a tracker or image generator. | Full-body capture, margin around both feet, floor visible, locked camera, good shutter/lighting. |
| Confusing a 4-fps flipbook with motion-transfer video | No continuous motion was generated or verified. | Label experiment type, real FPS, source frames, and interpolation method. |

## Failure-location diagnostic (use before choosing a tool)

1. **Source video:** Is every relevant limb and both feet visible during the critical crossing? Is one physical shoe/ankle uniquely marked? If not, tag the missing evidence; do not invent confidence.
2. **Pose trace:** Run a pose estimator with heel/toe points. Overlay its **anatomical** right/left colors on every frame. If labels jump while real continuity is clear, repair the *pose trace* (temporal continuity/Viterbi); log which frames were relabeled. Confirm the JSON index convention (COCO-18 vs BODY_25).
3. **Depth/occlusion trace:** If the labels are correct but near/far order is wrong, add depth, a semantic part map, or a 3D rig. Do not “repair” the correct anatomical IDs merely to force an image-left/front convention.
4. **Generated keyframes:** If source and controls are correct but rendered shoes/limbs flip, the generator is the failing component. Reject or use more direct stylization/part-based control. Check its actual final pixels, not only its inputs.
5. **Animation:** If isolated frames are correct but intermediate frames fail, the temporal animator/interpolator is at fault. No-fade source-frame playback is the diagnostic control.
6. **Loop and exercise form:** Only after steps 1–5, review the complete return-to-start sequence at intended cadence against the 5BX form reference. Form approval remains a human decision.

**Important:** A clean pose trace does not guarantee a faithful video generator. A script that swaps 2D labels does not solve depth by itself. A left/right marker in the *generated* output is insufficient unless its assignment was established on the actual source subject.

## Next proposed test (not yet performed)

1. Pick one complete repetition from an existing three-quarter angle, retaining original-frame timestamps and a 2–3-frame margin on either side. Score feet visibility and blur first. If unusable, record a short locked-camera 30–45-degree take with both feet in frame, good separation, and a conspicuous marker on the **same physical left or right shoe/ankle** for all repetitions. Record a short neutral front view to establish identity, then the movement view without changing the marker.
2. Extract keypoints with a suitable pose estimator, **including toe/heel points**. Save per-frame JSON/confidence, raw overlay video, and a crossing/contact-frame contact sheet. Do not run the guide's sample script on an MP4: it expects one-person COCO-18 JSON frames and assumes an initially correct label anchor.
3. Audit an entire right-forward -> left-forward -> right-forward cycle manually. Record any lost joints, label changes, wrong side occlusions, and timing. A tracker pass is a *measurement*, not proof of 5BX form.
4. If tracking is accurate, use the same recorded motion to compare (A) non-generative posterization/stylization, (B) prompt-based image-to-video using the pinned character, and (C) a pose/depth-conditioned video pipeline if available. Avoid changing camera, timing, and character simultaneously.
5. Only if the controlled candidate passes the human gate, render a no-fade short loop and test a **separate** smoother method. Keep all original files and versions.

### Proposed acceptance evidence (requires Charles's approval before it becomes a release gate)

- Stable anatomical left/right identity at **every observable frame**, with all ambiguous/occluded frames explicitly identified, and no white-marker foot migration.
- Clearly different opposite lead-leg landings and an actual return to the initial stance; no fused or additional legs, ballet-like body shrink, implausible joints, or missing feet.
- Same Sprite Boy identity, clothing and camera framing across poses; consistent height, limb proportions, ground contact, and suitable scale.
- Correct exercise mechanics and cadence per booklet/film/data, as judged by a **named human form reviewer**; model/skeleton QC is not a substitute.
- Clean loop seam with no duplicate body or fading/ghosting. Smoothness and any interpolation acceptance target remain separately undecided.
- Provenance record: source offset/frame range, pose estimator/version, mapping convention, motion-control representation, avatar image, prompt/model/settings, frame order, human review verdict, cost/time when known, and archive location.

## Research-guide caveats

The attached guide is a useful **research inventory** (pose-label repair, near/far occlusion, depth, 3D semantic maps, ComfyUI conditioning, QA), not a validated 5BX recipe. Its example Python repair code reads per-frame `pose_keypoints_2d` JSON; it does not extract keypoints from video, know the physically marked foot, detect multi-person errors, solve depth, or correct a generator's already-rendered limb. Its suggested ControlNet weights are heuristics for compatible tools, **not** Grok Imagine controls. More sophisticated methods add latency and model/GPU cost; try them only after a smaller test identifies the broken layer. Verify links, licenses, package versions, and performance before production use.

## Decisions still open

This record **does not approve** the proposed quality thresholds, name a final human form reviewer, select/approve a second avatar, establish the source-art restore path, or choose a smooth-tween target. Those decisions remain open in [`specs/sprite-production-line/requirements.md`](../../specs/sprite-production-line/requirements.md) and PR #16's history. Do not silently change production art, chart data, `--no-fade` preference, or release criteria on the basis of a diagnosis.
