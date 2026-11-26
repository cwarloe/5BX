# Prone back-extension: photographic master-v2 regression (2026-11-25)

**Status: REVIEW — four-phase still card and deterministic six-second loop. User signoff still pending.**

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

## Subsequent Flow motion tests and results (2026-11-25)

**The two raw AI-generated motion attempts were not acceptable; the edited loop is a strong REVIEW candidate.**

| ID | Input anchor | Sampled result | Status |
| --- | --- | --- | --- |
| [12](https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/edit/325cabc8-cd49-4847-a5d2-3187c5c66bf4) | Flow-native REST single still derived from blue-shirt knee-push-up video | At ~2.03s chest rises correctly. At ~3.13s feet lift but BOTH knees flex ~90°, so shoes approach buttocks; returns REST at ~5.04s. | **REJECT:** knee curl, not straight-leg hip extension |
| [13](https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/edit/eb3f4cd4-a420-4b74-b351-438aa24ac470) | New corrected PEAK single still; torso and legs modestly raised with visibly straight knees | ~0–3.0s lowering from peak to REST keeps long legs; at ~5.05 and 5.19s the return lift again bends knees conspicuously. | **PARTIAL:** good first-half descent, bad generated ascent |
| [14](https://drive.google.com/file/d/1aLi_1ByXmYxxjp8DNROAHyRa1HylKprf/view) | First 3.0s of 13, with those exact frames reversed to create second half | Six-second PEAK→REST→PEAK loop, reviewed via 12-frame 4×3 contact sheet; knees appear straight, feet move from hips, pelvis remains grounded, same boy and background. | **REVIEW:** good mechanics after deterministic edit, full-speed owner approval pending |

**Core lesson:** Repeating strong no-bend prose may not dislodge the video model's prior for a prone knee curl. The correction required (a) obtaining a correct **PEAK still** with strict straight knees and (b) borrowing only the valid downward movement from the partial video, playing it backward for a safe upward movement. This avoids inventing a new knee-flexing ascent. Treat the result as an **edited video**, not a fresh coherent AI six-second motion render. Check transitions for perceptible time reversal at normal playback speed.

**Deterministic remix command (720p H.264, 24 fps source):**

```bash
ffmpeg -i source.mp4 -filter_complex '[0:v]trim=start=0:duration=3.0,setpts=PTS-STARTPTS,split=2[down][r];[r]reverse,setpts=PTS-STARTPTS[up];[down][up]concat=n=2:v=1:a=0[v]' -map '[v]' -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart output.mp4
```

Flow video exports are now accessible via the observed download path and can be uploaded directly to the [mobile Drive gallery](https://drive.google.com/drive/folders/1W9dWViCZENv2UvoZ_k0EME8h9xRUWNKY); see the [playbook](PHOTO_VIDEO_PILOT_PLAYBOOK.md). Keep prior rejected assets with exact reasons; do not silently delete evidence or call Video 14 approved without Charles's decision.
