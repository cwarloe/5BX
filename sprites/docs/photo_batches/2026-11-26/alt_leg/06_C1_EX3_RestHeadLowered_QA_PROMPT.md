# Chart1 EX3 — lower rest head/chest, preserve active alternation

2026-11-26. Single instructed localized imagegen edit, then stop. Source: `05_C1_EX3_AlternateLegRaise_CleanNoBands_CANDIDATE.png` as EDIT TARGET, approved v2 master as second identity authority. Tool: OpenAI built-in imagegen. Output `06_C1_EX3_AlternateLegRaise_RestHeadLowered_CANDIDATE.png`, 1774×887. Assistant-only QA; no human approval or video.

## Independent QA

- **Rest-pose head/chest: PASS.** TOP-LEFT and BOTTOM-LEFT now show head/face close to track with neck/shoulders noticeably lower, physically plausible prone rest, both legs and shoes grounded, arms directed back with palm beneath thigh. No neck contortion and body proportions remain plausible. This fixes the major known rest defect from 04/05.
- **ACTIVE poses: CONDITIONAL PASS.** TOP-RIGHT and BOTTOM-RIGHT still display individual straight-knee single-leg lifts from hip at modest height; one leg remains grounded; near/far shoe silhouettes, hips and active head/chest positions look substantially unchanged. Relative shoe foreground/depth ordering matches clean 05 and marker 04 under visual inspection. **But** without colored bands the exact physical alternating hip ownership is difficult to prove from these nearly side-on photos in isolation.
- **Pixel preservation caveat:** The edit model visually recreated some non-target photo details. A right-half-of-card pixel comparison against prior clean 05 yields FFmpeg SSIM about **0.939**, not 1.000, so do not claim literal unchanged pixels. By contrast left (intended altered) half SSIM ~0.838. This supports that major change was concentrated in left rest tiles, but there were still smaller incidental changes in active tiles.
- **Identity/outfit: CANDIDATE.** Same apparent early teen, dark moderately messy hair, non-muscular normal body, blue tank, charcoal shorts, uniform charcoal socks, gray/yellow sneakers, black wristband; consistent track/treeline and static camera. Minor re-synthesis of face/light likely; compare to v2 before production.
- **Anatomy/count: PASS as visible.** No duplicated legs/arms, no knee bending, no floating pelvis, no foot retraction in active tiles.
- **Verdict: STRONG CONDITIONAL PHOTO CANDIDATE; not final-approved because physical alternating leg ownership is still inferred from marker ancestor and model re-synthesis rather than independently verified after edit, and no video motion has been tested.** If choosing one for Flow later, start from a clean 06 rest frame but test alternation carefully; do not accept repeated same-leg lift.

## Lesson

Fixing rest head/chest AFTER getting the opposite-leg geometry preserved most active positions visually; SSIM comparison still shows nonzero unintended changes, so 'do not touch active panels' wording is a quality target, not deterministic mask. Preserve archived color-marker 04 as physical leg-ownership ground truth and compare to all subsequent clean candidates.

## Verbatim image edit prompt

```text
Use case: identity-preserve.
This is a ONE-DEFECT LOCAL EDIT to an existing four-panel 2×2 high-resolution 35mm documentary photo contact card (Input image 1) of 5BX Chart 1 alternating single leg raise. Input image 2 is only the boy's approved v2 photographic identity reference. Do NOT generate a new card or redesign the boy. Retain four equally sized panels, exact static camera, tracks, grass, trees, face, normal soft 13–14-year-old physique, blue tank, loose charcoal shorts, dark charcoal socks, gray/yellow sneakers, black wristband, shoes and identity exactly as already pictured.

CHANGE ONLY THE TWO REST PANELS ON THE LEFT: TOP LEFT and BOTTOM LEFT. In both left tiles the boy is lying fully prone, face-down on red track, arms back along his sides with BOTH PALMS tucked beneath upper thighs. His TWO COMPLETE LEGS and both shoes remain straight and fully GROUNDED exactly where they currently rest; both hips/belly remain grounded. His HEAD and upper CHEST should now lower gently to a believable relaxed rest: torso and shoulders close to the track, face turning a few degrees to the side for breathing so his near cheek and chin hover perhaps 1–2 cm above the running surface, not his chest lifted as if actively exercising. Do not push up with hands or bend elbows; no exaggerated neck contortion. Keep his same youthful face and hair, but drop the neck/upper back angle naturally, not stretch or flatten head. Both left panels should match each other in this realistic lowered resting posture. No other movement in left panels.

DO NOT TOUCH THE TWO ACTIVE PANELS ON THE RIGHT, TOP RIGHT and BOTTOM RIGHT. They are the approved-for-diagnostic opposite leg ownership geometry and MUST stay physically the same: TOP RIGHT raises only the camera-near foreground straight leg from hip while camera-far background leg stays grounded; BOTTOM RIGHT raises only the camera-far background straight leg while camera-near foreground leg stays grounded. Preserve both active panels' head/chest lift, foot positions, two distinct shoes, physical knee-to-hip leg attachments, opposite-leg ownership, exact occlusion layering, face, lighting, posture, perspective, and entire pixel composition. Do not accidentally copy the same raised shoe into both right panels. Treat these panels as IMMUTABLE PHOTOGRAPHIC MATERIAL, not a source for regeneration.

The only intended change is lowering head and upper chest in the TWO REST TILES. Keep no orange or teal bands, uniform dark socks and the same outfit across the card. No other person, colors, lenses, zooms, borders, text, labels, props, new muscles, extra limbs, bent knees, shoe slides, or pose reversal. Photorealistic documentary quality, natural believable proportions and ordinary middle-school flexibility.
```
