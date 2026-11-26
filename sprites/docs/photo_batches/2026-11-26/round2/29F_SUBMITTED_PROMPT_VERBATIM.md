# Test 29F — verbatim submitted built-in imagegen request

Model: built-in `image_gen.imagegen` (one call, 2026-11-26 UTC), transparent_background: false. No CLI fallback. Local image references passed, in exactly this order:

1. `/workspace/scratch/29470ce0e8a3/artifacts/parallel_batch_20261126/chart3_ex4/29E_C3_ChinForehead_FourPhase_Headroom_CANDIDATE.png` — edit target
2. `/workspace/scratch/29470ce0e8a3/artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` — identity
3. `/workspace/scratch/29470ce0e8a3/artifacts/parallel_tests/v_pushup_realistic/02_almost_there.png` — natural elbow geometry
4. `/workspace/scratch/29470ce0e8a3/artifacts/restore_build_20261125/build_source/docs/reference/rcaf-1959-stills/ex4-c3-forehead-08m32s0.png` — original adult movement only

## Exact submitted prompt

```text
Use case: identity-preserve.
Asset type: four-panel 35mm photographic 5BX Chart 3 chin-to-forehead push-up prototype card; one controlled anatomy correction.
Input roles:
Image 1 EDIT TARGET: existing 2×2 four-phase card (A high plank, B chin-in-front of palms, C lower-left forehead-behind-hands pike, D high plank). Preserve full card with only C altered.
Image 2 IMMUTABLE APPEARANCE AUTHORITY: approved four-view soft natural fair-skinned 13–14-year-old middle-school boy, restrained messy dark hair, same face, blue tank, charcoal shorts, dark socks, gray-yellow shoes, wristband.
Image 3 NATURAL ELBOW GEOMETRY ONLY: prior less-extreme pike pose with ordinary elbow line, not an identity reference.
Image 4 ORIGINAL RCAF MOVEMENT ONLY: adult 1959 high V and stationary supports, not hypermobile child joint authority.
PRIMARY CHANGE ONLY IN LOWER-LEFT C: repair odd cocked/double-jointed-looking elbows. Keep hips raised in believable inverted V, natural near-straight knees, shoes supporting toes. Two distinct shoulder→upper-arm→single elbow→forearm→palm chains; ordinary symmetrical elbow hinge bending plane, no backward elbow, dislocated shoulder, elbow wrapping around head, extra wrist, forearm rubber bending or crossing upper arms. Palms flat, wrists aligned under forearms, shoulders structurally plausible. Head/forehead may stop 8–15cm (3–6 inches) ABOVE track; DO NOT FORCE forehead-to-floor or head-on-hands contact. Forehead still screen-right/behind the planted palms in pike. Natural comfortable load-bearing mechanics for average middle schooler supersede literal contact.
Preserve A/B/D nearly unchanged, including B chin front of hand line; preserve hip/limb lengths, muscle softness, same youth identity and camera, track/grass/trees, 2×2 gutters, footwear, colors, all background and image margins. No adult muscles or raised V waist, no stretched arms, no extra or missing limbs, no text. Natural 35mm candid photographic realism and static side-view camera. Explicitly prioritize believable elbow anatomy over depth.
```
