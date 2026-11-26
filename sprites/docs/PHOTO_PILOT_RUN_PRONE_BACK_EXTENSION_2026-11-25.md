# Prone back-extension: photographic master-v2 regression (2026-11-25)

**Status: REVIEW — four-phase still card only; no animation rendered or user signoff.**

- [Open the phone-friendly four-position card](https://drive.google.com/file/d/1oGTAZeOCDSb5QY7iujNaAH2k91dlU5U3/view)
- [Exact original generation prompt and QA](https://drive.google.com/file/d/1mzgHAcWjC17_M1IseJewe53CP3HqZuG-/view)
- [Mobile video/photo review index](https://drive.google.com/file/d/1cgY4-fVmfIlNHC_GtxZRA-IGlDSjiuVZ/view)

This curates an **existing** four-panel master-v2 identity regression result, not a new generation. All four positions were generated together to constrain age and anatomy drift.

## Objective and observed results

Prior prone back-extension generations often moved the boy's sneakers **horizontally backward** rather than **up off the track**. This card explicitly grounds the pelvis/abdomen and separately shows REST, mild CHEST lift, mild STRAIGHT-LEG upward lift (approximately 8–12 cm), then combined modest peak. Head points image right, feet left, fixed 20–30-degree side-oblique viewpoint.

**Assistant provisional passes:** same fair-skinned, normal-proportioned, blue-tank/charcoal-shorts middle-school boy across panels; two distinct legs and shoes; soles hover up in the later phases; no visible extra arms, reversed motion or implausible extreme flexibility.

**Issues to watch:** upper arms remain slightly too defined for the reference age, and track stripes/horizon drift a little across the 2×2 grid. Stills alone cannot verify actual motion coherence. Final user approval is pending.

## Reproduction constraints

- Reference identity is the 13–14-year-old photorealistic master-v2, **not the legacy cartoon sprite** or adult 1959 film actor. Historical film only constrains body geometry.
- Soft undeveloped upper arms/shoulders, unmuscular natural torso, unchanged waist/thigh proportions; fairly pale skin; moderately messy dark hair without extreme volume.
- Maintain face, shoes, track, focal length, age and size across all phases. Generate the entire exercise together.
- At rest, belly, thighs and shoes on track; when lifting legs, keep pelvis down and move both straight legs **vertically upward**, not laterally or toward the buttocks.
- No gymnast's large arch, dislocated shoulder, floating pelvis, hands pressing torso upward, or artificially elongated spine/limbs.

## Next motion test (not run yet)

Use a single Flow-native still of that same boy prone in REST. Ask for six seconds with stationary 35-mm side view: 0s REST → by 2s small chest/head lift → by 3s gentle combined chest and straight-leg lift, pelvis down → by 6s full REST. Shoes remain separate and both move UP off track. Keep arms along his sides, no camera travel and no outfit/identity change. Compare a sampled 0/2/3/5-second sequence to the four-pose card. Reject if the feet translate backward, hips hover, arms become muscular, or age changes.

See [photographic pilot playbook](PHOTO_VIDEO_PILOT_PLAYBOOK.md) for single-frame Flow methodology and review statuses.