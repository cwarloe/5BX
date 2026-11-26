# Test 26B — knee-flexion correction QA

**Date:** 2026-11-26 UTC. **Status: PARTIAL IMPROVEMENT / CONDITIONAL DIAGNOSTIC; not a video anchor yet.** One targeted built-in imagegen edit of Test 26, no retry. Exact submitted prompt: `26B_SlightKneeBend_ExactEditPrompt.md`.

**Image:** `26B_C3_EX2_SlightKneeBend_35mm_CANDIDATE.png`, 1199×1312 PNG; SHA-256 `07f9bebdbb367112cb7d44006a8d47e1126d294bf613f91eddb713117c8a51f0`. Global normalized MAE versus Test26 ~= **3.55%** (the edit also repaints incidental background/face/cloth pixels; NOT pixel-perfect pose preservation).

## Compared to Test 26 original

- **Knees:** All four phases changed from near 90° bend to substantially shallower angles. Visual knee geometry is still approximately 40–50° bent (far from the requested gentle 15–25°), but the silhouette is more consistent with the original 'allow knees to bend slightly' than the first right-angle bent-knee render. **PARTIAL PASS**, not exact.
- **Feet/grounding:** Both shoes appear to rest on the red track with heels down throughout, and the same dark sock / gray-yellow trainer set persists. However the feet are pushed almost to the **right image edge** in every tile; top-left shoe has only about 1–2% side clearance. A future animation could clip toes as feet shift. **BORDERLINE framing.**
- **Hands/head:** Both elbows remain clearly bent outward with hands at/back of skull in A/B/C/D; no floor-propping. Fingers/clasp contact itself is partly hidden by hair/ear and perspective. **Apparent continuity PASS; interlocked-finger detail unverified.**
- **Torso:** A lying, B rising ~45°, C almost vertical upright, D lowering ~35° retained. Pelvis stays on track and no waist/chest growth or absurd abdominal musculature observed. **PASS.**
- **Character:** Fair-skinned 13–14yo, short natural dark slightly messy hair, soft arms/chest/legs, blue tank, charcoal shorts, dark socks and ordinary running shoes. Minor image-generator redrawing of face/scene but no obvious change to age or body category. **PASS CANDIDATE, not pixel identity.**
- **Viewpoint:** It is again effectively strict 90° profile, hiding far heel/hand and making precise feet-apart distance hard to verify. **Unresolved.**

**Overall:** Test26B looks *better than Test26 in knee posture*, while preserving the key behind-head sit-up and full-upright mechanics. It **does not fully meet the requested mild 15–25° knee flexion**, and right-edge shoe margin is insufficient for a robust video start. Retain both 26 and 26B as conditional diagnostic variants. A next targeted test should widen all four panels uniformly and flatten knees slightly further *without* leg length growth; if doing so forces body/face drift or unplants heels, prefer honest modest bend and document the deviation rather than demanding impossible flexibility. No 5BX approval and no video generated.
