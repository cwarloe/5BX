# Chart 2 ID24 → 24R — standard push-up shoulder-softness trial

**2026-11-26 · Built-in imagegen edit (one attempt only).** No human form approval, no video claim, no outside upload. Baseline identity: approved v2 four-view soft, fair-skinned 13–14-year-old boy. Original mechanics authority: the original ID24 four-phase toe-supported push-up card. This revision addresses **only an overly hard deltoid/triceps contour**, not the body shape, strength, or exercise form.

## Assets

- **Original untouched:** `artifacts/parallel_batch_20261126/chart2_ex4/24_C2_EX4_StandardPushup_FourPhase_35mm_CANDIDATE.png`
- **Identity authority:** `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`
- **Revised candidate:** `artifacts/next_batch_20261126/24R_C2_StandardPushup_ShoulderSoftness_CANDIDATE.png`
- **Exact submitted prompt:** `artifacts/next_batch_20261126/24R_C2_StandardPushup_IdentitySoftness_ExactEditPrompt.md`

## Skeptical panel-by-panel review

| Panel | Original → refined comparison | Movement/identity status |
|---|---|---|
| A upper left (low) | Near shoulder/upper-arm surface appears slightly less sharply modeled but silhouette and natural elbow bend preserved. Profile, messy hair, wristband and ground-contact hands remain visually in place. | **Conditional PASS**, not a measured physique transformation. |
| B upper right (high) | Elbows still extend, hips/knees/ankles remain aligned from shoulders to planted toes; near and far palms stay grounded. Shoulder cap still visible due to load/perspective, not obviously bulkier than before. | **PASS of visible static mechanics**. |
| C lower left (deep low) | Foreground elbow remains bent, both hands near same track contact positions, chest close to ground, legs straight. Deltoid still carries plausible load tension; no extra hand or arm seen. | **Conditional PASS**, camera profile still obscures far elbow detail. |
| D lower right (high) | Returned upper support is recognizable with two arms, two legs, planted shoe toes, same outfit and hair. No new posing, face or scale change evident. | **PASS of visible static mechanics**. |

The global ImageMagick normalized mean absolute pixel difference was approximately **0.0186 (1.86%)** at identical **1536×1024** output dimensions. That number only describes average pixel difference, including background resynthesis; it is **not** proof that bone/limb geometry or identity is pixel-locked. A magnified A-panel side-by-side visual crop supported small smoothing of shoulder/upper-arm shading without obvious circumference change. Minor texture changes extend beyond the targeted skin, as expected from a generative edit.

## Verdict and lessons

**24R = MODEST CONDITIONAL KEEP**, alongside untouched original 24 as reliable fallback. The appearance improvement is small, not a newly approved youth identity. The important success is that the requested softening did **not visibly sacrifice** low/high toe-supported push-up mechanics or cause body-size, hair, outfit, hand/foot placement, or background drift in static panels. Future video can still introduce arm-ownership or contact errors.

**Process lesson:** On moderate muscle-drift cases, a minimal shading-only identity edit with the approved multi-view boy as separate *appearance* reference is safer than prompting the character to be “smaller,” “skinny,” or to shrink thighs/arms. Keep anatomy and natural loaded-muscle tension; soften the hard division lines only. Never replace a mechanics-proven card without verifying every phase anew.
