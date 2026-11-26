# Chart 1 Knee Push-up UP — Native high-resolution single-photo experiment

Date: 2026-11-26 UTC
Status: **REVIEW / HIGH-FIDELITY CANDIDATE ONLY.** No Flow run, no human exercise-form approval, and no GitHub/Drive publication.

## Files and provenance

- Image: `C1_E4_UP_FULLRES_16x9_PHOTO_REVIEW.png`, true generated single-image frame 1672×941 (~16:9), 2.6 MB PNG, SHA256 `dd4d6b2dacda46403992447293d62e8a70726b57a9937cbbeb1df2567d837444`.
- Tool: built-in imagegen, `photorealistic-natural`, one generation with two reference images; **not a resize or crop** of earlier 883×438 photo.
- Reference 1 (identity/outfit): `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`.
- Reference 2 (kneeling up pose geometry only): `artifacts/parallel_batch_20261126/knee_pushup/C1_E4_KNEELING_4PHASE_V2_REVIEW.png`.

## Exact submitted prompt

```text
Use case: photorealistic-natural.
Asset: One genuinely new, full-resolution, SINGLE-FRAME 16:9 wide 35mm documentary photograph that will be a clean Chart 1 5BX kneeling push-up UP start anchor for image-to-video. Do NOT upscale, collage, crop or recycle a panel of either reference. Synthesize all original realistic fine detail at native full-frame quality.

REFERENCE IMAGE 1: the four-view character master V2 is the ONLY authoritative source for the actual boy's identity, facial geometry and apparent 13–14-year-old age, moderately messy close-to-head medium-dark brown hair, fair untanned Caucasian skin, gently soft and naturally undeveloped non-athletic arm/shoulder/chest/waist/thigh development, body stature, medium sky-blue tank, loose charcoal-gray shorts, dark ankle socks, gray/yellow-accent sneakers and simple black wristband. Reproduce that exact recognizable individual in a single photographic moment, not a generic younger elementary child or older high-school athlete. Keep modest believable nose and same small/medium ears and jawline, no round baby face or sculpted adult muscles.

REFERENCE IMAGE 2: four-phase knee push-up sheet. Its TOP-LEFT UP pose is the binding POSE AUTHORITY only. Match the physically possible kneeling push-up mechanics but do NOT copy the card layout, low-resolution pixels, face or identity from this source. Do not use its bottom/other poses in the output.

ONE photograph of ONE person in ONE location, no panel dividers, no text, no extra figures. He is in the STRAIGHT-ARM KNEELING PUSH-UP UP START: true 90° clean RIGHT-SIDE PROFILE, face toward IMAGE RIGHT, knees and elevated folded shins/shoes extending toward IMAGE LEFT. BOTH kneecaps firmly on the red running-track surface, BOTH hands planted shoulder-width flat on the track just below his shoulders; two naturally straight attached arms, elbows extended, far arm behind near arm and plausible. His shoulders, hips and kneecaps form one gently inclined almost straight line without rounded spine or butt in air; hips naturally proportional, knees bent backwards at ~90° so shoes rise behind but do NOT support body weight. Face neutral and open-eyed, slight breathing realism. One clear continuous body, no fused shoes or extra arms/hands.

PHOTOGRAPHIC DETAIL IS THE VARIABLE UNDER TEST. Crisp 35mm film documentary realism: true individual flyaway hair strands, fine skin texture but NO facial/body/armpit hair, soft realistic pores with no artificial beauty retouch, naturally wrinkled blue jersey fabric with subtle weave, garment stitching and realistically loose charcoal shorts; sharp lifelike gray/yellow shoe materials, laces, tread and sock knit; physically coherent track grain and shadows. Natural daylight with careful focus on face, arms and outfit and mildly softer tree-line background, no excessive bokeh, color grading or smoothing. His blue shirt and charcoal shorts must match exactly the V2 reference shade, not brighter/paler/cyan, no olive green. No anatomical exaggeration or adult musculature.

Composition: EXACT 16:9 LANDSCAPE and genuinely high native resolution, full-bleed photograph. Fixed tripod at track height, no pan/tilt/zoom effect; the COMPLETE boy including head, fingers, kneecaps and shoes is present with a comfortable 6–8% safety margin at the left edge and above hair and below grounded hands/knees. The boy fills roughly 75–82% of image width so his face and fabric receive abundant actual pixels but all joints remain visible, and space remains to lower his chest in later video. Grounded horizontal track lines, green grass and leafy trees behind. The single photo must be ready to serve directly as the ONE start image for a 6-second exercise video.

Absolute avoid: four-panel card, split-screen, storyboard, duplicated/ghosted person, extra limb, toe-supported push-up, a gymnast's shoulders, muscular defined teen body, narrowed waist, changed face/hair, richer tans, blue-gray faded shorts, any identity/outfit drift, text, watermark, cartoon or illustration.
```

## Visual QA and comparison

| Gate | Result |
| --- | --- |
| Genuine higher resolution | **PASS:** output 1672×941 = ~1.57 megapixels, compared to 883×438 = ~0.39 MP from a 2×2 crop. Approximately **4.1× the actual pixel count**. |
| Fine photographic detail | **PASS:** noticeably more face/skin texture, hair strands, blue knit weave/creases, track surface grit, shoe seams and laces. This is a real newly synthesized photograph, not upscaling. |
| Single frame / fixed camera | **PASS:** one shot only, near-exact 16:9 landscape, right-facing true side profile, full body and feet visible with decent safety margins. No labels/ghosts. |
| 5BX kneeling UP geometry | **PASS provisionally:** hands and knees grounded, raised folded shoes, normal hip–shoulder–knee line; no toe push-up. Two hands and two shoes appear plausible, but far elbow remains naturally occluded in a true side view. |
| Outfit continuity | **PASS provisionally:** medium sky-blue tank, dark charcoal shorts, dark socks, gray-yellow shoes, wristband match V2 broad palette. Shirt richer/darker blue than earlier 09 crop; not pale blue drift. |
| Exact V2 identity | **REVIEW / potential drift:** photo boy has slightly fuller/wavier top hair than V2 master (approved preference was less volume), marginally more defined nose/jaw and upper arms, and warmer skin tone. These differences may make him read a little older/more athletic. A fidelity win should NOT automatically replace the chart master identity. |
| Age/body/skin | **REVIEW:** still plausibly ~13–14, normal youth build, no obviously exaggerated musculature, but arm contour is more pronounced than ideal. Smooth face/armpit visible, no notable hair artifacts. |
| Video suitability | **CANDIDATE:** good full body, static setting and native >720p dimensions. Motion/contacts and face persistence not tested; only a single starting photograph. |

## Conclusion

**High-resolution method succeeded technically:** one newly synthesized single full-frame photograph provides materially better native texture fidelity than the 2×2 crop. Unlike the old 883×438 up-frame, this source can feed a 1280×720 video without relying on enlarging a sub-720p card tile.

**Identity caution:** More realism also caused a small return of fluffy hair, a slightly more mature profile/upper-arm definition and warmer complexion versus approved V2. Do not silently promote this image as the new canonical character. Options for coordinator: (1) user review as test, (2) one targeted hair/upper-arm softening edit at full-resolution with explicit no-loss-of-detail rule, or (3) retain source for motion QA but compare resulting video identity to the V2 chart master. Because edits can lower fidelity/introduce drift, do not pursue repeated corrective attempts without an explicit focused hypothesis.

This resolves the earlier panel-crop limitation and creates a true full-resolution Flow start-frame candidate, but **exercise form and identity remain independent QA gates**.

