# Test 31 — Chart 4 Ex3 arms-sideways back extension: exact QA

**Status: STRONG CONDITIONAL PHOTOGRAPHIC STILL.** One imagegen built-in generation (no retry), 2026-11-26 UTC. Not a human-approved 5BX exercise or a verified animation.

**Output:** `31_C4_EX3_BackExtension_ArmsSideways_FourPhase_35mm_CANDIDATE.png`, **1672 × 941**, SHA-256 `85353b6e763e7ce743f7dacaf538ec9bb9a4de0859b0cf2aae796ec84df17cb3`.

**Exactly submitted prompt:** `31_C4_EX3_ExactPrompt.md`, text from `Use case:` to final Avoid sentence, excluding Markdown fences.

**Reference roles:** (1) owner-approved `identity_sheet_v2_hair_arm_refinement.png` is immutable age, face, wardrobe, hair/skin/body-softness authority. (2) `chart2_ex3/21_C2_EX3_BackExtension_FourPhase_35mm_CANDIDATE.png` is baseline prone extension body motion only. Chart 4 changes the arm configuration to straight lateral shoulder-height extension; Chart 2's hands-under-thighs must not be copied. The actual Chart 4 movement comes from `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`: "Front lying, hands and arms stretched sideways"; "Lift head, shoulders, arms, chest and both legs as high as possible."

## Four-panel mechanical review

| Panel | Arms and head/chest | Both legs/pelvis/feet | Verdict |
| --- | --- | --- | --- |
| A top-left start | Two clear straight arms out to sides in a low T; near arm projects diagonally toward camera, far arm away from viewer, palms near track. Forehead/chin close to track. | Belly/hips on track, legs straight, shoes complete and down. | **PASS start**; head not perfectly flat, a minor variation. |
| B top-right rise | Head and shoulders modestly rise; both arms stay visibly straight and laterally extended, palms lifted off ground. Far arm emerges behind head but recognizable, not tucked under thigh. | Both straight shins/shoes appear upward relative to track, hips still contacting track; foot overlap makes exact far-leg height hard to prove independently. | **PASS / conditional far leg**. |
| C bottom-left peak | Chest rises a little more; near and far straight arms remain transverse to torso in horizontal T and raised, no bent elbows/arm doubling. Chin neutral, no extreme neck arch. | Pelvis/abdomen grounded, paired straight legs lift from hips with natural unpointed sneakers; no knee curl or gymnast hyperextension. Far shoe partly overlaps near shoe. | **STRONG PASS visual**, far-leg trace limited by occlusion. |
| D bottom-right return | Arms remain out to sides, one nearer and one farther, both lower; head returns close to track. | Straight legs and full shoes settle toward track, same pelvis position. | **PASS return**. |

## Identity, framing, and source fidelity

- **AGE / BODY: PASS provisional.** Fair-skinned normal 13–14yo boy; proportional waist/chest/thighs, no adult muscle bulk, six-pack, or added limb length. Slight shoulder muscle contour and curlier/frizzier hair than master; monitor before chart-level lock.
- **OUTFIT: PASS.** Consistent royal-blue loose tank, charcoal-gray athletic shorts, dark crew socks, gray/yellow real running shoes, a small black wristband; no hair/body color shift across the four panel card.
- **PERSPECTIVE: BETTER than earlier Chart2 prone profile.** Camera appears slightly elevated and oblique (rather than exact 90° side), making both arms legible. Do not over-assert exact 25–30° measurement from one generated image.
- **REGISTRATION: CONDITIONAL.** Similar pose scale/background and lane lines among panels, but generative photos shift head, shoe, arm and tree texture by several pixels. No frame-to-frame motion or exact contact continuity is established.
- **NO extras:** two anatomical arms/hands and legs/shoes, no doubled shoulders, no spider arm, no balletic pointed toes. All silhouettes complete, with ample edge margin; figure relatively low in panel but visible.
- **REALISTIC RANGE:** The back lift is modest enough for an ordinary middle-schooler, accepting slight head/chest rise; avoid demanding an adult's maximum back arch or 99th percentile flexibility.

## Lesson and next gate

The explicit **T-arm identity against a raised slightly oblique camera** seems to have solved the common side-profile arm-occlusion problem in this one card. Reusing the prior Chart 2 prone card for modest torso/paired-leg geometry while **prohibiting its hands-under-thighs detail** helped isolate the new Chart 4 requirement. This is an inference from one generation, not controlled evidence that the camera or prompt clause caused the success.

For animation use one high-quality separately generated start frame or accepted tile only after checking same-boy identity and complete near/far arms. Review actual motion for both arms remaining lateral and rising with head/chest, both legs lifting together, pelvis staying planted, and a loop without register drift. **No video generated; no human form approval; no Drive/GitHub publication from this agent.**
