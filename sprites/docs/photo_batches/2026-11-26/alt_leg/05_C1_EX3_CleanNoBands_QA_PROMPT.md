# Chart 1 EX3 — remove orange/teal leg-tracking bands

Date 2026-11-26. One targeted edit, then stop. Input1 EDIT TARGET: `04_C1_EX3_AlternatingLegRaise_OrangeTealDiagnostic.png`; Input2 SUBJECT AUTHORITY: approved v2 four-view master. Output: `05_C1_EX3_AlternateLegRaise_CleanNoBands_CANDIDATE.png`, 1774×887.

## Independent strict QA

- **Color-band removal: PASS.** All bright orange/teal ankle bands are removed in all four tiles, replaced by continuous dark-charcoal socks. Shoe geometry, yellow accents and clothing palette substantially retained.
- **Action poses: CONDITIONAL PASS.** Top-right leg lift, bottom-right opposite intended leg lift, and two prone resting phases appear to have retained the same thigh/calf/shoe overlap and spatial positions as the color-tagged diagnostic; no evident knee bend, pelvic lift, or extra limb. However after color markers vanish, which exact anatomical leg is raised remains difficult to confirm from the almost side-on view alone.
- **Non-surgical regeneration caveat:** Despite 'change only bands' instruction, the image tool reconstructed pixels across the card, not a literal tiny pixel-only fill; one-image structural similarity measurement of marked source vs unmarked output (FFmpeg SSIM) was approximately **0.876**. SSIM includes expected band color changes and minor photo shading differences; it doesn't alone prove anatomical morphing. Visually the leg pose/hip attachment remains similar, but exact pixel-identical geometry cannot be guaranteed.
- **Identity/camera/scene: CANDIDATE.** Same normal fair 13–14-year-old look, hair shape, outfit, black wristband, track/grass/treeline, camera framing across four tiles. Minor generative facial/lighting details may have shifted; compare against approved master before production.
- **Rest-phase known limitation remains:** Head and upper chest are still lifted in the two rest tiles. User/owner must decide if this is acceptable historical form; do not falsely present as fully prone relaxation.
- **Verdict: CONDITIONAL CLEAN CANDIDATE for further visual form review.** Do not call production-approved. The marker diagnostic is the stronger proof of opposite leg identity; this clean card is plausibly position-preserving but ambiguous in isolation. No Flow video generated.

## Lessons

Temporary visual markers enabled the successful alternating-leg tracking test, but removing them through generative edit is not equivalent to deterministic pixel masking. To reduce drift, keep the marker original as geometry truth, compare near/far hip-to-shoe contours after each edit, and use a strict static angle with more obvious two-shoe separation in a later phase. The clean image looks strong enough to test as a still candidate, but form acceptance remains separate.

## Exact submitted edit prompt

```text
Use case: identity-preserve.
Precise photo edit, ONE VARIABLE ONLY: REMOVE THE TWO TEMPORARY COLORED ANKLE MARKER BANDS FROM EACH OF FOUR PANELS, restore the original uniform dark charcoal athletic socks underneath. Input image 1 is the exact existing four-panel orange/teal diagnostic test card to EDIT; input image 2 is the approved four-view original boy reference solely for the exact matching plain charcoal sock/gray-and-yellow shoe appearance and unchanged subject identity. Do not generate new exercise poses, a new boy, a new grid or a new camera.

Edit all four panels of input image 1 non-destructively:
- Wherever an ORANGE band encircles the CAMERA-NEAR foreground ankle, erase only that orange fabric, replacing those pixels with seamless continuous dark charcoal sock fabric consistent with the sock immediately adjacent.
- Wherever a TEAL band encircles the CAMERA-FAR background ankle, erase only the teal colored fabric, replacing those pixels with the same continuous dark charcoal athletic sock texture.
- Restore both socks in ALL tiles to identical unmarked CHARCOAL athletic socks, as in input image 2. Preserve original gray running shoes with restrained yellow accents, shoelaces, soles, shape and exact positions.
- Absolutely retain original pose and *physical anatomical leg identity* despite removing the color cues: TOP-RIGHT action panel stays EXACTLY the same physical CAMERA-NEAR FOREGROUND leg lifted at the hip with a straight knee, background/far leg grounded. BOTTOM-RIGHT action panel stays EXACTLY the OPPOSITE physical CAMERA-FAR BACKGROUND leg lifted at the hip with a straight knee, foreground/near leg grounded. TOP-LEFT and BOTTOM-LEFT both legs are grounded. Raised shoe heights and both shoes' horizontal/vertical positions stay pixel-identical to input image 1. Do not swap legs, mirror, change occlusion, recolor the shoes, bend knees or move any joint.
- Leave EVERYTHING OUTSIDE those colored ankle-band rings untouched, including the current resting head and slightly elevated chest exactly as photographed, hip/abdomen support, both palms under thighs, face, age, hair, skin, arms, waist, shorts, sky-blue tank, wristband, track stripes, grass, trees, daylight, vignette, crop, 2x2 gutters, camera angle and full 35mm photographic detail.

This is a small LOCAL COLOR RESTORATION, NOT an instruction to redraw the person or change motion. Exactly two legs, exactly two unmarked charcoal socks in each panel. No added text/labels, no orange or teal color anywhere on the figure.
```
