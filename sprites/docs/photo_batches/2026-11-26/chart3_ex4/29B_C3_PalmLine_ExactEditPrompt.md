# Test 29B — precise palm-line relation diagnostic, verbatim image edit prompt

Date: 2026-11-26 UTC. ONE targeted built-in image_gen edit. Input images in order: (1) `29_C3_EX4_ChinForehead_FourPhase_35mm_DIAGNOSTIC.png` **EDIT TARGET**: preserve its same 2×2 photographic layout, boy, track, plank phases; (2) `identity_sheet_v2_hair_arm_refinement.png` identity/age/outfit authority only. The 1959 film still is NOT submitted for this edit because its forehead/hand screen relation was ambiguous.

Submitted prompt verbatim:

```text
Use case: identity-preserve / precise-object-edit
Asset type: one revised, four-panel 35mm photographic 5BX Chart 3 chin–forehead push-up diagnostic contact sheet, exact same 2×2 composition and character.

IMAGE 1 IS THE EDIT TARGET. Retain the original four photographic panels A/B/C/D, same fair-skinned normal 13–14-year-old boy, same recognizable face and modest messy brown hair, soft undeveloped shoulders/arms/body, same blue sleeveless athletic tank, charcoal shorts, dark socks, gray/yellow running shoes, black near wristband, red track/grass/trees, fixed almost 90-degree side-on tripod with boy facing SCREEN RIGHT. IMAGE 2 is appearance authority, not a new pose. Keep same height, chest and waist size, arm length, elbow anatomy, thighs, shoe size and age. No muscles, extra limbs or adult gymnast flexibility.

TARGETED CHANGE: Make the CHIN versus FOREHEAD target clearly distinguishable by a physically FIXED palm-line coordinate on the track. Across ALL FOUR tiles add ONE very thin, high-contrast short YELLOW-VERTICAL floor-tape guideline on the red running track running from just beneath his BOTH flat planted palms toward the tile's bottom edge, exactly at the same screen-X coordinate as the planted hand/wrist base. It is painted on the GROUND, not a wristband, rope, overlay caption or attached object. Keep his hands/palms and toes at their original track contact points in every panel. No lettering or arrows.

In this near-perfect SIDE VIEW, the boy faces SCREEN RIGHT. The feet and rear body are SCREEN LEFT. The hands are fixed at coordinate X = PALM_LINE. The strict original 5BX movements require TWO OPPOSITE SIDES:
- A TOP LEFT: same normal HIGH PLANK, face SCREEN RIGHT of PALM_LINE, both hands planted, toes remain support.
- B TOP RIGHT: lower in straight body; CHIN NEAR TRACK on the SCREEN-RIGHT / FRONT side of PALM_LINE, visibly beyond his hands toward the boy's face direction, both elbows naturally bent. The guideline remains at the palms, left of the chin contact. Do not move the hands forward to meet chin.
- C BOTTOM LEFT: lift the hips into a moderate child-friendly inverted-V pike, keep BOTH toes and BOTH palms at their ORIGINAL contact points, gently lower and CURL THE HEAD BACK TOWARD THE FEET so FOREHEAD is NEAR TRACK on the SCREEN-LEFT / REAR side of PALM_LINE, clearly left of the palms by a visible fraction of a head width. The yellow guideline now lies visibly TO THE RIGHT of the forehead contact, while still exactly under the palms. Do NOT leave the forehead screen-right of the hands, and do NOT just paint a line to the right of a stationary head. This is the ONE geometry correction to make: head position relative to mechanically fixed hands. Preserve normal anatomical shoulders/elbows, do not hyperextend, do not grow taller/longer, allow forehead to hover slightly above track if a full touch is anatomically awkward. Both arms intact and knees nearly straight; retain his realistic ordinary adolescent size.
- D BOTTOM RIGHT: back to EXACT high plank A, with the painted guideline still under the same planted palms.

Every panel must show exactly two attached arms/hands, two attached legs/shoes, no spider-elbow or stretched forearms. One track guideline at the same hand coordinate per tile, all hands/feet complete and in frame, no moving horizon/camera or changing clothing colors. NO TEXT labels. A physically honest near-contact behind the hands is preferable to a perfect forehead touch gained by impossible shoulder extension. Keep the other THREE panels as unchanged as possible; only C head/neck/upper-torso articulation and the diagnostic track stripes should change.
```

Do not assume success. QA in `29B_C3_PalmLine_QA.md` tests head vs physically stationary palm X rather than whether a pike merely looks plausible.
