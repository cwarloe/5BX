# 5BX Chart 1 knee UP — One targeted V2 identity correction, high-resolution edit

Date: 2026-11-26 UTC
Status: **REVIEW / PROVISIONAL IMPROVEMENT**. No second correction attempt authorized or performed. No Flow/GitHub/Drive write. Original full-res source preserved separately.

## Files and provenance

- EDIT TARGET: `C1_E4_UP_FULLRES_16x9_PHOTO_REVIEW.png`, newly synthesized 1672×941 single photograph (not 2×2 crop).
- Identity authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`; standing and portrait appearances ONLY, not pose.
- OUTPUT: `C1_E4_UP_FULLRES_V2_IDENTITY_CORRECTED_REVIEW.png`, still 1672×941, SHA256 `4cd53cb10eb7037fdbebf17dbde741fd5af49dc587d48d7a69601df3eb9b7a45`, 2.49 MB PNG.
- Tools: built-in imagegen image edit, exactly one pass; no local pixel retouch. `QA_FULLRES_BEFORE_AFTER.jpg` is comparison only.

## Exact executed edit prompt

```text
Use case: identity-preserve.
Asset: HIGH-FIDELITY IDENTITY CORRECTION to an already generated 16:9 SINGLE-FRAME 35mm photographic Chart 1 kneeling push-up UP image. Edit the first attached photograph as the TARGET. The second attached 2×2 master V2 sheet is the ONLY identity authority. This is a strictly LOCAL identity correction—not an exercise regeneration, camera recomposition, age redesign, new portrait or new contact sheet.

Change ONLY these tightly related aspects to match the master V2 boy:
(1) HAIR: reduce the currently excessive wavy/fluffy hair volume on top by ~10–15%, preserve the same naturally slightly messy short medium-dark brown hair, modest hair at sides, approximate hairline of master V2. No close skin fade, no quiff, no perfectly styled curls.
(2) FACE IDENTITY: match V2's approved normal 13–14-year-old Caucasian middle-school face, moderately youthful eyes, brow, nose, ear SIZE and shape, jaw/cheek proportions. The first image looks slightly older and more sharply sculpted in profile; soften that subtle excess only, with NO babyish round cheeks, exaggerated button nose, narrowed chin, or changes in bone lengths. Face still right-facing side profile and looking straight ahead.
(3) SKIN and MUSCLE SHADING: return fair untanned natural skin tone matching V2, lightly soften shadow/highlight separation at deltoids/biceps/triceps so his NORMAL EARLY-TEEN arms look gently undeveloped without changing arm circumference, elbow/wrist/shoulder size, chest or waist. Maintain ordinary healthy, neither skinny nor heavy proportions. No visible facial, armpit, leg or chest hair.

LOCK ALL OTHER PIXELS/FEATURES AS MUCH AS IMAGE EDITING ALLOWS. Absolutely preserve the original target's full-resolution photorealistic 16:9 single-frame composition at 1672x941-like resolution; static eye-level 90° right-facing side camera; exact shoulder-hip-knee straight geometry, palms and both kneecaps firmly planted, folded shins and both raised shoes; limb lengths, stature, waist, natural thigh/seat, head location, hand locations, shoes and wristband; exactly the SAME medium-blue athletic tank with the SAME wrinkles and stitching and SAME charcoal-gray shorts, socks, gray/yellow shoes; red track lines, blade-level grass, tree-lined background, daylight, horizon, all ground-contact shadows, 6–8% margins, entire full-body in frame; genuine 35mm documentary photographic texture.

Preserve, or improve without altering geometry, the fine individual hair strands, skin pores, blue jersey weave, shorts seams, shoe laces/sole details, track granules and tree foliage. Do NOT blur, posterize, cartoonize, beautify, soften or downsample the whole image to remove visible muscle. Retain all existing native photographic fidelity. No new muscles, no changing the boy's overall size, no extra people/limbs, no added text, no split panels, no artificial skin smoothing. A single original photographic frame, not a new multi-panel contact sheet.
```

## Strict before/after QA

| Check | Original full-resolution | V2-corrected full-resolution | Judgment |
| --- | --- | --- | --- |
| Hair | Fuller/wavier and raised on top | Moderate height reduction, darker natural messy hair, some side hair retained | **IMPROVED** toward approved V2 |
| Face age/nose/jaw | Slightly older/sharper profile | Softer youthful early-teen contours; nose/ears reasonably similar to V2; not babyish | **IMPROVED provisionally**, exact identity still human-review |
| Skin | Warmer/tanned cast | More fair untanned complexion closer to V2 | **IMPROVED** |
| Upper arms | Visible sculpted deltoid/triceps contours | Less pronounced separation, no major change in arm width | **IMPROVED** |
| Outfit | Medium-blue tank, charcoal shorts, gray/yellow shoes and wristband | Same general colors, garment wrinkles, shoes and wristband | **PASS** |
| Exercise mechanics | Both knees/palms planted; folded shoes lifted; shoulder/hip/knee aligned | Same geometry and near/far side arrangement with no obvious broken joint | **PASS provisional** |
| Framing | 1672×941, 16:9-like, fixed 90° right-facing, full body | Exactly 1672×941, similar subject scale and static full-body camera | **PASS** |
| Photographic detail | Fine hair strands, shirt weave/creases, shoe laces and track grit | Fine fabric/track/shoe/hair textures visibly retained; some minor natural background texture re-synthesis | **NO MATERIAL DETAIL LOSS VISUALLY** |
| Pixel invariance | Original generated pixels | Different RGB pixels beyond requested identity edits (the background was partially resynthesized despite explicit lock) | **CAVEAT**: semantic consistency, not strict pixel-perfect edit |
| Temporal quality | Not tested | Not tested | **PENDING** |

## Recommendation

Accept the corrected photo as a **better V2-aligned high-resolution VIDEO START CANDIDATE**, not as a production-approved image. It keeps native ~1.57 MP texture and correct kneeling geometry, reduces the most prominent identity drift, and retains the static camera.

However, the edit does regenerate the whole photo to some extent (trees/grass texture differ), so it is not a deterministic identity layer swap. This one pass validates an *appearance-corrective* hypothesis but does not prove identity pixels can remain fixed through a video cycle.

**Stop condition met:** one targeted identity-correction iteration completed, visually evaluated, no further retries. Use corrected source for any *isolated* Flow experiment only after coordinator confirms desired chart-level character continuity. Original remains preserved for comparison.

