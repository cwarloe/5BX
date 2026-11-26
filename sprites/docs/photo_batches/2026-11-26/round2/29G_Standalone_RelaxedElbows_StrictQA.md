# 29G — standalone relaxed-elbow pike, strict QA

**Disposition: CONDITIONAL / IDENTITY HOLD.** The arm mechanics look substantially more anatomically credible than the 29E/29F deep-head-contact attempts. **Do not classify as an approved instructional exercise, animate it, or expand it into a card yet**: photographic identity and some body proportions drift from approved v2, and this is only one generated still rather than a motion-validated sequence.

## Provenance

- New output: `29G_Standalone_RelaxedElbows_CONDITIONAL.png`.
- Exact submitted prompt and ordered input references: `29G_Standalone_RelaxedElbows_ExactSubmittedPrompt.md`.
- Image 1 pose geometry authority: `../../parallel_tests/v_pushup_realistic/02_almost_there.png` (relative context: project `artifacts/parallel_tests/v_pushup_realistic/02_almost_there.png`).
- Image 2 approved boy identity authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`.
- Generator: built-in image generation; **one attempt**; no image post-processing edits or external publication.

## Skeptical anatomy assessment

| Check | Finding | QA status |
|---|---|---|
| Near arm chain | One shoulder, one visible hinge elbow, continuous forearm and planted open hand. No backwards hinge or extra arm seen. Near elbow is *more strongly bent* than the requested gentle 130–155° included angle, but the bend appears within normal anatomical range. | **Plausible; prompt-angle miss** |
| Far arm chain | Separate hand planted in the background; forearm appears nearly straight / mildly flexed, with part of hinge region foreshortened against torso. No visible elbow reversal. Exact load path is less independently verifiable than near arm. | **Plausible, partially occluded** |
| Head and cervical spine | Forehead stays off the track and behind the near-hand line; no forced forehead-to-hands contact. Neck appears continuous. Pixel geometry cannot validate the exact requested 10–20 cm clearance. | **Improvement; estimated spacing only** |
| Pike shape and feet | Hips elevated, shoes supported on forefoot, ordinary-looking knees and ankles; no ballet point, foot growth, or obvious reversed joint. | **Pass, still visual-only** |
| Motion validity | One generated frame does not prove the same elbows remain coherent through up/down transitions. | **Not tested** |

## Identity / rendering regression

- **Hair:** Bigger and more tightly curled/fluffy than approved v2's low-volume, messy crop. This is an identity miss.
- **Arms/shoulders:** Visible anterior deltoid and upper-arm thickness/tension read somewhat too mature and muscular compared with approved ordinary middle-school boy. Unlike earlier renders, the near shoulder is very prominent.
- **Legs:** Thigh/calf definition and overall leg thickness are more pronounced than ideal, though body proportions are not catastrophically distorted.
- **Face/age:** Generally adolescent and pale, but head angle and curled hair impair exact comparison; face may be softer/rounder than v2. Do not certify a facial match from an oblique downturned view.
- **Colors/setting:** Blue tank, charcoal shorts, muted red track, grass/trees, gray/yellow shoes, black band remain approximately within target palette.

## Comparison and lesson

`02_almost_there` was preferable as a geometry seed to the close-head-contact 29E because it offered a relaxed, feasible shoulder/arm configuration. 29G confirms a useful **prompt direction**: explicitly *allow incomplete forehead depth*, make two normal arm chains visually traceable and reject forced contortion. The price here was drift in the identity master and deeper-than-requested near-elbow bend. Next candidate should retain this safer space around head while **reasserting the v2 boy's hair silhouette, less-developed shoulders and slimmer natural leg musculature** and possibly use the 29G photograph only for elbow geometry—not as identity. Avoid describing an exact angle as verified from the projection.

**Guardrail going forward:** A nominally 5BX-accurate deep forehead touch must be rejected as an instructional reference if it only works through anatomically implausible elbow hinges, shoulder distortion, added limbs, or change in the boy's size. An achievable shallow pike is acceptable, explicitly labeled as such.
