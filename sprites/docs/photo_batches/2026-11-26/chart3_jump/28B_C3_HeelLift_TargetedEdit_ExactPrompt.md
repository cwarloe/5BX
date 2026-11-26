# Test 28B — fix visible heel raise at upright phase C

Single targeted built-in imagegen edit. V1 failed the original 5BX Chart 3 finish condition: upright phase C had flat-looking shoes instead of clearly lifted heels. Full prompt supplied verbatim:

```text
Use case: precise-object-edit
Asset type: targeted 5BX Chart 3 half-knee-bend four-panel photo contact sheet correction
Input image 1: EDIT TARGET, exact four-panel photographic exercise card showing the same middle-school boy, track, outfit and camera in all tiles. Input image 2: identity authority only, approved four-view boy photographic reference.
Primary request: Change ONLY the LOWER-LEFT / BOTTOM-LEFT panel's TWO ATHLETIC SHOES, ANKLES and VERY LOW CALVES so the boy is correctly performing the TOP of the 1959 RCAF 5BX half-knee-bend motion: he is fully upright, knees straight, weight balanced naturally on the balls and forefeet of BOTH shoes, with BOTH HEELS lifted a subtle but UNMISTAKABLE 2–4 centimeters off the red track. The rounded toe/ball section of EACH shoe remains touching the red track, bearing weight, while the rear heel rubber is visibly above ground with an actual small shadow/air gap. Sneakers flex naturally at the metatarsal region without long pointed ballet toes. The person's head, upright torso, hands fixed on hips, shorts, hair, nose, ears, feet-Together spacing, expression, background trees/grass/red track, sunlight and camera stay exactly the same.
All other panels A TOP LEFT, B TOP RIGHT, D BOTTOM RIGHT must remain unchanged: A/D modest bent knee about 110 degrees interior knee angle with flat heels and hands hips; B transitioning upward with heels starting to lift. Do NOT change overall 2x2 layout, frame crop, age/face/skin tone, clothing colors, shoe identity, eye direction or number of limbs. NO extra toes/shoes/legs. Do NOT make him jump in the air; toes of both shoes MUST stay in contact and only the heels rise. Do not make his knees bend in bottom-left C. No text/captions/logo/watermark. Correct exercise mechanics, not a new pose family.
```

Image references in order: `28_C3_HalfKneeBends_V1_HEEL_NOT_RAISED_REJECT.png` edit target; `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` approved identity only. Review heel-ground contact and side-camera leg mechanics after generation; do not claim success automatically.
