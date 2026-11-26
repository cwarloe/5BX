# 5BX high-knees — round 6: far-left-arm geometry and handedness

All variants are experimental photographs, not human-approved video reference frames.

> **Superseded by next human review / round 7:** The user explicitly selected **34H** (image hash verified) and found the far upper arm still too exposed and unnatural for a background limb. The new approach is to occlude the far forearm and hand entirely behind the torso, leaving only a small rear elbow. See `../round7_occluded_far_arm/ROUND7_OCCLUDED_FAR_ARM_FINDING.md` and 34J. **34I was a parallel alternative, not the user-selected source**, and remains an unapproved diagnostic.

## Controlling human finding

The user re-examined the explicit **34G selected source** and found that the lower-left high-knee pose still has an apparently duplicated **right/foreground arm** at the rear. Merely opening the curled fingers did not solve the true anatomy. The far-side arm appears **too long, with an upper arm that extends too far down the torso**; because the far shoulder is shifted in depth, visible far upper-arm length should be foreshortened. The rear elbow and hand should be higher and closer to the body. This issue affects the entire shoulder → elbow → wrist chain, not only fist orientation.

## Tests (both directly edited the user's exact selected file)

| ID | Intent | Visual QA | Gate |
| --- | --- | --- | --- |
| **34H** | Shorten visible far upper arm, place elbow higher and rear hand by waistband; insist on actual left-arm attachment while preserving 2x2 leg and near-arm exchange. | Far-side elbow and fist are now much closer to the torso/waist. However, the hand closed again and looks right-fisted in silhouette. | **Diagnostic only / REJECT for current motion**. |
| **34I** | Alternative edit from same selected base: similar far-upper-arm foreshortening plus a visible, slightly OPEN, anatomically left hand. | Assistant saw improved finger visibility, but the user selected 34H instead; 34I has not received separate human form approval. | **HOLD / diagnostic, not source for 34J**. |

## Reusable manufacturing lesson

- A wrong-handed arm can mimic a length problem. **Inspect shoulder depth → upper-arm apparent length → elbow height/angle → forearm → actual handedness** as a *single anatomical chain*. Do not repeatedly edit the fist in isolation when the far shoulder is placed as though it belongs to the foreground side.
- With a 3/4 camera, far limbs are partly occluded and can be *visually foreshortened* without literally giving a child different bone lengths. Upper arm should be less exposed; rear hand can sit near the rear waistband during running arm swing.
- Pose and limb-identity QA is cross-frame: panel A foreground right arm back; panel C foreground right arm forward. Any edit that freezes it fails even when single frames look polished.
- This experiment is superseded by the **34J occlusion** attempt, using 34H as its exact selected source. Retain 34I as a parallel diagnostic; no image here is approved for animation.

## Versioned files

- `34G_UserSelected_ExactEditBase.png` — exact user-selected source for both edits
- `34H_FarLeftArm_Foreshortening_Review.png` — rejected fist morphology
- `34I_FarLeftArm_RelaxedHand_Review.png` — review candidate
- `34G_34H_34I_FarArm_Comparison.jpg` — close comparison
- `34H_ExactSubmittedPrompt.md` and `34I_ExactSubmittedPrompt.md`

No animation was generated. No existing production video input was overwritten.
