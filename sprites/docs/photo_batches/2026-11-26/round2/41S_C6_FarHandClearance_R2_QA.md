# Chart 6 Ex4 test 41S — far-palm airborne clearance in launch frame

Date: 2026-11-26 UTC. Image-only QA; original 5BX requires both palms to leave support momentarily and make two distinct chest taps, then return planted. **No motion/video or human approval claimed.**

## Source / submitted edit

- Appearance authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`.
- Edit target (retained): `artifacts/parallel_batch_20261126/chart6_ex4/41_C6_EX4_ChestSlapPushup_FourPhase_35mm_REFINED_R1.png`.
- New one-call `image_gen` output: `artifacts/next_batch_20261126/41S_C6_FarHandClearance_R2_CANDIDATE.png` (1536 × 1024 PNG).
- Exact submitted text: `41S_C6_FarHandClearance_R2_ExactPrompt.md`.

## Before / after panel inspection

| Phase | Source 41R | Revised 41S | QA |
| --- | --- | --- | --- |
| A (top-left) | Two palms planted near shoulders; toe support, torso low | Same essential pose, both ground contacts, face, shoe angle and youth build retained | **PASS invariants** |
| B (top-right) | Foreground near hand clearly off track, but far/background fingertips appear at or barely above track surface | **Visible red-track clearance under both hands**, far/back hand lifted modestly with natural elbow/wrist chain, near hand also remains airborne; torso not elevated again | **TARGETED IMPROVEMENT / CONDITIONAL PASS** |
| C (bottom-left) | Two distinct hands contact separate parts of shirt/chest | Same separate chest-tap posture, hands not clasped together, no extra limb or obvious contact reversal | **PASS invariants** |
| D (bottom-right) | Extended two-arm plank with palms and toes planted | Same pose with both palms on track and body aligned; no shoulder-width or foot shift obvious | **PASS invariants** |

Frame B zoom checked at 2×: the far hand is now visibly above the boundary between green field and red track; image has a thin natural air gap beneath its fingertips. This is *visual* clearance, not a calibrated measurement of centimeters in depth. No additional hand, wrist, foot, or limbs seen. The subject still looks a bit too muscular in upper arms/shoulders compared to the v2 neutral master, **but that drift was present in 41R already**; this edit neither measurably corrects nor obviously worsens it. Preserve torso and hand motion first; do a separate appearance-only correction later if needed.

## Regeneration / pixel-change caution

The image editor was generative, not a guaranteed mask edit. Full-panel normalized RMSE against 41R:

| Panel | RMSE |
| --- | ---: |
| A | 0.0192581 |
| B (target) | 0.0310885 |
| C | 0.0212235 |
| D | 0.0222529 |

Target B changed more than the three supposed invariant panels. About 2% normalized RMSE even outside target shows incidental pixel resynthesis of hair/track/fabric/background. Therefore preserve both R1 and 41S, compare visually and in actual video before promotion; do not claim identity/camera lock is pixel exact.

## Verdict / next gate

**41S = preferred conditional still diagnostic for dual hand release**, improving the ambiguous far hand without altering the historical exercise endpoint. Not yet proof of an achievable, coherent child's ballistic chest-slap push-up. A short one-start-frame video must be checked for (1) both hands departing support simultaneously, (2) the brief momentary two-palm chest contact, (3) immediate two-palm landing without a held body hover, (4) persistent same boy/wardrobe and no camera jitter, and (5) no invented arm or reverse phase interpolation. Human form review remains a separate gate.
