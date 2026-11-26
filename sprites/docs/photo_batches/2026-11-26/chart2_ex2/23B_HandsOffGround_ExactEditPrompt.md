# Test 23B — full sit-up apex hands off ground, exact edit prompt

**2026-11-26 UTC. One targeted built-in imagegen EDIT, one candidate, no retry.**

**Inputs:** (1) EDIT TARGET `chart2_ex2/23_C2_EX2_FullSitup_FourPhase_35mm_CANDIDATE.png`; (2) PRIMARY IDENTITY ONLY `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`.

**Output:** `chart2_ex2/23B_C2_EX2_FullSitup_HandsOffGround_35mm_CANDIDATE.png`.

## Exact verbatim submitted text

```text
Use case: precise-object-edit; exact motion-reference repair.
Image 1 is the EDIT TARGET, a 2x2 contact sheet of a photographic 13–14-year-old boy doing a full sit-up; Image 2 is the PRIMARY identity reference only for the existing face, clothes and normal soft build.

Make ONE tiny localized biomechanical correction in the LOWER-LEFT PANEL C ONLY. That is the frame where he sits with his torso almost vertical and legs straight forward. His two hands are currently flat on the red running-track ground just alongside his hips; this can look as though he pushes himself into the sit-up. Lift BOTH existing hands and all fingers only about 3–5 centimeters above the track, hovering naturally beside the outside of his hips/upper thighs without touching the track. Relax the fingers slightly curved as real hands; retain exactly five fingers where anatomically visible and keep each physical hand attached to its original forearm/elbow/shoulder. It is okay if the lower-left elbows relax by a few degrees to achieve a plausible natural resting hand-height. Preserve the black wristband on the same near wrist.

ALL ELSE MUST BE PIXEL-REGISTRATION CONSISTENT with Image 1: do not change upper-left panel A, upper-right panel B, or lower-right panel D whatsoever; do not change the lower-left boy's face/age/hair, blue shirt/charcoal shorts, soft unmuscular body shape, nearly vertical torso angle, pelvis touching the track, extended straight legs, ankles, grounded heels, full running shoes, camera, backgrounds, trees, track lines, lighting, panel sizes, white dividers, or photograph's detail. He must still look like a normal unmuscular middle-schooler and the same specific person. Do not shift hips, legs, shoes or head even slightly. Only repair lower-left hands' ground contact to hovering relaxed hands. No captions, labels, object additions, duplicate hands or anatomy artifacts. This is a local retouch, not a re-imagining of the 4 poses.
```

**Tool settings:** built-in `image_gen.imagegen`, 2 `referenced_image_paths`, `transparent_background:false`.
