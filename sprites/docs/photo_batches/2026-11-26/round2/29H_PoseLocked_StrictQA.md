# 29H — strict pose-preserving edit QA

**Disposition: PASS for spatial pose retention; CONDITIONAL / HOLD for approved-boy identity and production use.** This is markedly better at preserving the original natural arm/elbow contour than the 29G free generation. It is **not** a demonstration that the model can animate a safe, deeper forehead-to-floor push-up.

## Inputs and outputs

- True target: `artifacts/parallel_tests/v_pushup_realistic/02_almost_there.png`, unchanged original.
- Appearance reference only: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`.
- Exact submitted prompt: `29H_PoseLocked_ExactSubmittedPrompt.md`.
- Single attempted result: `29H_PoseLocked_Photographic_CANDIDATE.png`.
- Quick two-column comparator: `29H_OriginalVsPoseLocked_MobileCompare.jpg`.
- No external publication or next-stage four-card expansion.

## Direct visual A/B review

| Check | Observation | Disposition |
|---|---|---|
| Shoulder/elbow/wrist contours | Near arm maintains the original gently flexed shoulder→elbow→wrist line. Far arm is parallel/partly behind near arm but appears separately planted and no added elbow flexion or backwards hinge is seen. | **Pose retention pass, far-depth ambiguity** |
| Palms, wrists, shoes | Both palms, both wristbands and shoe contacts occupy practically the same visible positions. Heels, forefeet, and ground alignment are not visibly displaced. | **Pass visually** |
| Forehead spacing | Downward-facing head stays just above track, behind hands toward the feet. No forced contact, and neck/shoulder contour unchanged. | **Pass; near-touch approximation** |
| Torso/hips/legs | Pike apex, torso lean, long diagonal legs and knee extension are almost unchanged. No stretched limb or age-height gain. | **Pass** |
| Camera and background | Original track lanes, grass/tree layout, static camera and field of view remain aligned to the eye. | **Pass** |
| Approved v2 facial identity | Head is down and partly occluded by arms/hair; crucial face/eye/nose/ear detail cannot be matched convincingly to the identity sheet. | **Unverifiable; hold** |
| Hair & musculature | Hair still reads textured/curly and somewhat full; shoulder/deltoid contour still athletic rather than clearly soft/undeveloped. Any improvements are subtle, not a reliable v2-lock transformation. | **Partial miss; hold** |
| Motion | One still, no proof of elbow trajectory under repeated flexion; deep stage is deliberately not attempted. | **Not evaluated** |

## Interpretation

The *edit-as-target* phrasing worked for preserving the precise safe-ish original-pose geometry. It mostly retained the original person and simply refined details rather than performing a clear identity replacement. That is an acceptable **geometry baseline**, but not a final child-identity frame. Both ends of the exercise pose and elbow axis should be rechecked in motion; we should not infer joint safety across future animation from this still.

**Next cautious step, if authorized:** retain 29H/02 as the pose anchor and make a small localized face/hair/shoulder appearance edit without changing a single contact point or elbow line. But pose and identity compete: avoid escalating pose instructions to a deeper touch merely to appear closer to 1959 film. If a deeper render demands atypical elbows, reject it.
