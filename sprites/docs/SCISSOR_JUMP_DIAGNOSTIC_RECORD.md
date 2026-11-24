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

## Additional five-pose reference-image experiment (2026-11-24)

**Input:** user-provided illustrated runner (`13627.png`) in a side-facing right stride. Distinctive reference geometry: the **trailing leg extends toward image-left but belongs to the foreground/near side of the body**. Charles explicitly requested this person's face/build/art style, cyan-blue tank, red shorts, blue sneakers, and a four/five-pose scissor-jump card. This is a new **candidate avatar reference**, not an approved replacement for the canonical Sprite Boy.

**Attempt 1:** Generated five figures on flat magenta, arranged as three above and two below, with pose instructions: original trailing-near-leg stance, airborne exchange, opposite lead stance, return exchange, original stance. **Visual success:** the reference face/style, cyan top/red shorts/blue shoes, full bodies, and near-side trailing-leg depiction were broadly consistent. **Movement failure:** the top-right supposed opposite stance retained essentially the same rightward lead-leg silhouette/near-far overlap as the first; a leg-identity switch was not demonstrated. No approved cycle.

**Attempt 2 (targeted edit):** Reused the generated five-pose card and original image, asking to change the middle poses only: the *same physical foreground leg* must lead in pose 3, with shorts/thigh overlap reversed, and poses 2/4 must show distinct airborne exchanges. **Result:** lifted-knee geometry changed but the sequence still looks like multiple variants of the same leading/trailing stride; the physical near leg was not demonstrably tracked through a real exchange. **Rejected for instructional use.** This does not establish a DWPose failure because no pose estimator or skeleton data was involved.

**Countermeasure / next test:** Do not spend repeated prompt edits on the five-pose composite. First create and review **two individually valid inverse keyframes** with an explicit stable anatomical marker or source-grounded hip/knee/ankle track. Confirm which thigh emerges in front of which shorts hem in each inverse stance. Only then request the two transition poses and assemble a five-frame card, retaining the same locked identity/style. Review gait mechanics against the 5BX booklet and film; these images are motion-structure experiments, not form-approved 5BX exercise art.

## Gentle 5BX warm-up scissor-jump card test (2026-11-24)

**Request:** Charles liked the new illustrated runner identity but asked to replace exaggerated running strides with a **subtle, warm-up-style 5BX scissor jump**. Canonical Chart 1 exercise 5 data specifies one leg and the opposite arm forward, the other pair back, jumping to exchange positions before landing, with arms around shoulder height. This is distinct from the earlier running/sprinting pose reference.

**First five-pose card:** Preserved curly-haired boy, cyan tank/red shorts/blue shoes and fixed magenta background; shortened front/back steps, mostly upright torso and very small airborne transitions. **Worked:** the new scale and low lift looked closer to a gentle warm-up than a sprint. **Unresolved:** the supposed opposite landing still looked very similar to the initial leg configuration; arm identity was not tracked.

**Targeted wristband test:** The original reference has a single black wristband. On the follow-up edit, instructing the wristband to follow the *same physical arm* moved it to the rearward arm in pose 3 while it stayed on the forward arm in poses 1/5. **Worked:** this clear asymmetry improved visual arm-continuity evidence. **Still unresolved:** legs remain insufficiently distinct to certify a genuine anatomical left/right exchange. A wristband validates only its arm, not both legs. This remains a visually promising **unapproved form candidate**, not a release asset.

**Lesson:** Begin from the intended motion amplitude and the booklet's arm/leg opposition; do not let a running reference silently turn a scissor jump into exaggerated stride/knee drive. Use persistent asymmetric markers on source anatomy to test identity, but require a separate leg marker/pose trace before claiming the legs exchange correctly. A five-frame attractive card is not a form-validated scissor cycle.

## Accepted running depth exemplar and generalization (2026-11-24)

Charles explicitly confirmed that the latest **four-pose running reference** correctly shows the **foreground/camera-near leg trailing toward screen-left** while the far leg leads toward screen-right. This corrects the recurrent visual mistake of letting the *screen-right leading leg* own the foreground overlap. [Preserved illustrated reference (Drive ID 1lSzvp-SjsNDOClhmQquGk7tqUAmb1HAh)](https://drive.google.com/file/d/1lSzvp-SjsNDOClhmQquGk7tqUAmb1HAh/view).

**Positive control:** near trailing thigh visibly overlaps the far leading thigh at the hip/shorts junction in a right-facing running silhouette; the shoes remain attached to plausible legs. **Limit:** Charles's approval covers this running **depth depiction only**. No tracked physical left/right leg IDs, exercise-correct scissor-jump exchange, transitions, or release-quality animation were demonstrated or approved. It is a different curly-haired candidate actor, not a new canonical Sprite Boy.

**Reusable fix:** use the [conditional foreground-trailing-leg prompt and QA reference](FOREGROUND_TRAILING_LEG_RULE.md) whenever the verified source pose has a camera-near trailing leg. Reverse the screen directions for a left-facing shot, preserve near-over-far occlusion, and *do not* automatically apply the rule to poses where the camera-near leg leads. Make near/far hip overlap an independent visual acceptance gate before attempting inverse stances, transitions, or loops. This supersedes any earlier implicit assumption that the screen-right-leading leg should be foreground in all frames.

## Independent inverse-endpoint prompt experiment (2026-11-24)

**User direction:** Work exclusively on the two difficult opposing scissor-jump landing positions; the easy intermediate poses can be generated later. Make multiple modest-stride alternatives rather than exaggerated ballet/sprint movements. Preserve the curly-haired candidate runner, cyan tank, red shorts, blue shoes and magenta background. The [conditional hip-depth rule](FOREGROUND_TRAILING_LEG_RULE.md) is the reference.

**Experiment A, six near-leading variations:** [Drive candidate sheet](https://drive.google.com/file/d/1kHIR9Lg5R2MCPpcFmj96fHW-zn9W5_Aw/view). Generated independently with camera-near/foreground thigh **leading screen-right** and far thigh trailing screen-left, explicitly requiring the leading near thigh to overlap at the shorts/crotch. Six low-amplitude stance variants were produced with consistent visual character. **Preliminary visual observation:** several have plausible forward-thigh overlap; **not** source-verified or human approved, and do not establish persistent physical leg identity.

**Experiment B, three A/B pairs in one sheet:** [Drive failed comparison](https://drive.google.com/file/d/1tRxbi4nNx94FmKJnIUpmPP8kG_owggQW/view). Requested left-column near-trailing and right-column near-leading positions at matched stride amplitudes, with shorts-overlap reversal and a physical wristband on one arm. **Observed failure:** adjacent columns are nearly duplicated in hip/shorts occlusion and arm/wristband position. Text specifying an inverse role was insufficient to cause an anatomical swap in a mixed-state contact sheet. **Do not use this card as an accepted A/B cycle.**

**Experiment C, six near-trailing variations:** [Drive candidate sheet](https://drive.google.com/file/d/10-yl-i3xjLPJulv7tImmCAW4QP_-DJJ3/view). Generated independently from the **approved four-pose running depth exemplar** with near/foreground leg trailing screen-left and thigh crossing in front of far leading leg, but with more modest 5BX-like splits. Six alternatives returned; several appear plausibly distinct at shorts/hip crossing. **Not** human form approved or paired to A by physical leg ID.

**Lesson:** The model can produce *candidate* near-leading and near-trailing silhouettes when each contact sheet is constrained to only one depth assignment. Asking for both opposing states **within the same sheet** continued to collapse them into the same topology. For the next step, have Charles choose one valid A and one valid B *from the two independent sheets*, manually verify both occlusions and 5BX amplitude, then test a **separate** paired composition or identity-tracked transition. Preserve the failed composite as a regression case. No motion video, pose-tracking evidence, canonical Sprite Boy substitution, generator code or production art changed. None of these new sheets has a recorded human exercise-form verdict yet.

## Charles's review of the third six-pose sheet and prompt generalization (2026-11-24)

Charles said the **third attempt** finally got it right: [six independent near-trailing variants](https://drive.google.com/file/d/10-yl-i3xjLPJulv7tImmCAW4QP_-DJJ3/view) show the foreground/camera-near thigh trailing in image direction while overlapping in front of the camera-far leading thigh at the hip. **This is an explicit user acceptance of the near-trailing depth depiction.** Do not extend it into unrecorded approval of a matched near-leading pair, physical leg identity through a swap, the specific 5BX exercise form, or a loop. The prior mixed A/B sheet remains a confirmed failed comparison.

The [complete six-chart applicability audit](FOREGROUND_TRAILING_EXERCISE_AUDIT.md) identifies two high-priority opposing-foot movements (Chart 1 scissor jumps and Chart 4 semi-squat jumps) and two reusable **conditional** stationary-running prompt recipes. `sprites/prompts/strips.json` now explicitly requests near-trailing hip occlusion in the affected poses and avoids turning low stationary runs into long forward strides. The [research index](research/README.md) also links the additional identified Repo Scout reports and historical failure brief. Those reports describe research possibilities, not tools already tested or deployed.
