# Test 23 — Chart 2 Exercise 2 full sit-up, exact imagegen prompt

**Date:** 2026-11-26 (UTC). **One built-in imagegen call**, no retries. The entire block below was submitted as one prompt.

**Reference inputs, in order:**

1. `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` — PRIMARY appearance/identity authority.
2. `artifacts/parallel_batch_20261126/partial_situp/01_CANDIDATE__Chart1_PartialSitup_FourPhase_35mm.png` — SECONDARY setting and supine start arrangement, not maximum sit-up height.

**Output:** `23_C2_EX2_FullSitup_FourPhase_35mm_CANDIDATE.png` (1199×1312).

## Exact submitted prompt

```text
Use case: photorealistic-natural.
Asset: TEST 23, a single four-panel photographic motion-reference contact sheet for authentic RCAF 5BX Chart 2 Exercise 2, the FULL SIT-UP (distinct from Chart 1's partial sit-up).

References: Image 1 is the PRIMARY authority for ONE identical 13–14-year-old middle-school boy's identity and appearance, facial shape, dark somewhat messy modest-volume hair, fair untanned Caucasian skin, soft normal undeveloped arms/shoulders and legs, sky-blue sleeveless athletic top, charcoal-gray shorts, dark-gray socks, gray trainers with restrained yellow accents, black band on one wrist. Image 2 is SECONDARY for the same red running track/green field/trees daylight environment and for a relaxed supine starting arrangement ONLY; its small torso curls are NOT the desired maximum for Chart 2. Never make a different or older athlete.

Generate ONE clean 2×2 GRID of four separately photographed key frames, equal framing and camera, thin white gutters, no captions and no text. At every frame use the SAME boy, exact same clothes/shoes/face/hair, same static tripod and environmental geometry, eye-level slightly elevated side-oblique camera approximately 20–30° from perfect profile so BOTH legs can be recognized. Entire body, hands, heels and both shoes visible in every frame, with generous margins. Natural 35mm film-inspired color photograph, fine real-world texture, soft natural daylight, accurate anatomy, normal human flexibility.

Authentic motion: lying on his BACK on the track, heels six inches apart, knees mostly straight and softly natural, ankles relaxed, arms resting alongside his hips/thighs. ONE COMPLETE controlled FULL SIT-UP. The boy's heels and full soles NEVER lift from the track. He does not grasp his legs or push on the ground with his hands.

A (upper-left) START: flat supine, head/shoulders/back resting on track, legs extended forward, both heels touching the track, arms beside body.
B (upper-right) RISING MIDPOINT: head and shoulders and upper torso rising about 40–50° from track in a smooth natural curl, pelvis remains grounded, both legs remain out straight with feet/heels touching SAME track positions, hands beside outer thighs.
C (lower-left) HISTORICAL FULL UPRIGHT POSITION: seated on his seat/pelvis, spine and torso raised to near-vertical 85–90° relative to track (NOT a mere 25° abdominal crunch), both straight legs extended in front and heels completely grounded, arms relaxed beside body, normal soft waist and no visible abdominal muscles.
D (lower-right) CONTROLLED RETURN: torso lowering to about 35–45° above the track, shoulders off track, lower back approaching floor; feet remain planted, hands alongside thighs, same physical leg order and outfit.

Physical rules: a sit-up rotates the torso around the anchored pelvis; NEVER move or levitate the legs or feet as the torso comes up. Legs remain lying on track, both knees/ankles attached normally and consistently. Keep the same face size and body segment lengths across four panels; a normally proportioned 13–14-year-old, unmuscular limbs and chest, smooth face/limbs, no facial/underarm hair. No V-shaped cut waist, abs, muscular arms, or mature adult head; no child-like elementary student. His expression calm neutral focused. No extra hands/feet, no bent knees tucked up, no ballerina pointed toes, no gym mats, no props, no changing camera, no motion blur or duplicates.
```

**Tool settings:** built-in `image_gen.imagegen`, two `referenced_image_paths`, `transparent_background:false`. No labels composited afterwards; copy only to project-bound artifact folder.
