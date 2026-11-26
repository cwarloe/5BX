# Charts 4–6 photo identity drift audit — tests 30–41

**Visual-only cross-chart QA, 2026-11-26.** Reference authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` (approved v2 four-view boy). This audit is **only about character identity and wardrobe**, not endorsement of exercise mechanics or video quality. I visually inspected all twelve preferred photographic cards, plus the original 35 card and updated 35R cleaned card. No images were regenerated.

## Executive finding

The 13–14-year-old identity is generally recognizable throughout: fair Caucasian skin, short dark-brown messy hair, natural smooth face, realistic slightly soft undeveloped build, blue sleeveless top, charcoal shorts, dark socks and gray shoes with yellow accents. **I do not see a severe elementary-school age regression in tests 30–41.** The stronger recurring drift is *upward* toward a fitter/older teen: shoulders, upper arms, chest and more angular profile get too developed on dynamic push-up poses. Low side-profile prone images limit confidence about face and exact age, so do not interpret a good body pose as pixel-level facial identity lock.

### Preferred-card ranking, closest to v2 → most correction-needed

The ordering is approximate, not a metric; camera angle and limb loading affect how mature the body looks. Within a tier, small differences are subjective.

| Rank | Test / preferred image | Identity judgment and specific drift |
| --- | --- | --- |
| **1** | **33** Chart 4 semi-squat jump | **High fidelity.** Good natural early-teen face/waist/thighs, proportional chest, brown messy hair, no pronounced body sculpting. Very minor panel-to-panel face and hair shift. |
| **2** | **38** Chart 5 semi-spread-eagle jump | **High.** Similar to #33 and master; natural legs, face and outfit. Jump apex looks a touch longer/older and hair a little tidier, likely perspective/pose. |
| **3** | **30** Chart 4 toe-touch sit-up | **High.** Most convincingly soft trunk/arms and fair skin; modestly fuller crown and slightly rounder face from some angles. No clear age regression. |
| **4** | **39** Chart 6 pike sit-up | **High.** Fair skin, ordinary torso, slim-normal waist and normal proportions. A little extra shoulder contour in peak and slightly curlier hair. |
| **5** | **35R CLEAN** Chart 5 twisting sit-up | **Good.** Better pose-tracking successor to #35. Face and age plausible; slight extra crown volume, blue tank brighter/saturated, upper chest/arm definition in B/C. |
| **6** | **31** Chart 4 T-arm back extension | **Good / face-limited.** Soft legs, shorts/shoes and fair complexion stable. Hair curlier/full, shoulders subtly outlined; head turned down/up limits facial certainty. |
| **7** | **36** Chart 5 overhead back extension | **Good / face-limited.** Same youth broadly, but a touch more curly hair and raised-arm muscle contour. Profile expression appears slightly sharper at peak. |
| **8** | **40** Chart 6 overhead back extension + press | **Good / face-limited.** Consistent outfit and age; same family as 36, some facial angle change and upper-arm definition when lifted. |
| **9** | **34 V3 CLEAN** Chart 4 stationary high knees | **Moderate.** Facial profile/jaw and nose appear a little more angular/prominent, hair more carefully sculpted, torso/arms a little more athletic than master. Still plausible 13–14, no severe change. |
| **10** | **37** Chart 5 clap push-up | **Moderate.** Stronger deltoid and upper-arm sculpting, longer/angular profile and slightly warmer skin; suggests an athletic older teen more than canonical soft youth. |
| **11** | **41** Chart 6 chest-slap push-up | **Moderate / correction priority.** Same near-match family as 37, but push-off and chest-slap panels accentuate upper arms, shoulder caps and mature profile. Fairness/clothes remain approximately right. |
| **12** | **32** Chart 4 wide-hand push-up | **Lowest relative fidelity, still recognizable.** Most noticeable broad/defined shoulders and thick upper-arm/triceps appearance, face a little angular and hair full. Do not confuse exercise loading with genuine age change; but this needs the strongest softness correction before any final identity lock. |

**Notes on version selection:** #34 V1 is explicitly a pose reject; #34 V2 has temporary ORANGE/TEAL identity bands; use **#34 V3 CLEAN** for public identity comparison while retaining V2 for leg provenance. #35 initial card had unresolved near/far leg twist and is superseded for preferred review by **35R CLEAN**; keep the color-tracked 35R diagnostic alongside its clean output. Do not collapse these records into an unqualified #34 or #35 claim.

## Drift by attribute

- **Apparent age:** Most look 13–14. Main risk is *older/more athletic* in 32, 37 and 41, and a more angular profile in 34; no major recurring childlike regression in this set. Camera angle and facial tension can cause false age cues, so this is visual judgment only.
- **Hair:** Canonical medium-dark messy, gently wavy/curling short hair is preserved. 31, 35R, 36, 39, 40 have a bit too much curly crown volume; 37 and 41 show a slightly styled/upward coiffure, 34 an intentionally groomed/swept top. Don't buzz the sides or give an extreme fade. 33/38 are close.
- **Skin and face:** Fair/untanned smooth skin generally remains. Some warm/tanned cast and sharply lit arms in 32/37/41; slight cheek/jaw/nose angularity particularly 34/37/41. Ear size and general facial structure remain broadly plausible; no visible facial, leg or armpit hair.
- **Musculature:** 30/33/38/39 closest to normal softer undeveloped limbs; 31/35R/36/40 light workload contour; **32/37/41 stronger shoulder/upper-arm definition**. Soften surface relief rather than reducing body width, waist, bone lengths or movement posture. No conspicuous washboard abs or unnatural V-line in the reviewed cards.
- **Waist/shorts:** Most have the approved natural waist and loose charcoal short silhouette. 37/41 have a somewhat narrow, stretched athletic silhouette from the plank and 32 a broader shoulder-to-waist taper; don't shrink or fatten torso to repair this, preserve the master’s ordinary waist/chest.
- **Palette:** Tank remains recognizable mid-bright blue throughout; 35R and some sit-ups a bit brighter, 32/37/41 slightly stronger saturation or contrast. Shorts remain charcoal/gray, though lighting occasionally pushes them blue-gray or darker. Gray sneakers with subtle yellow details and charcoal socks remain consistent. None of these is a wardrobe identity breaker. Black wristband mostly stable where visible.
- **Continuity:** Every 2×2 card is locally coherent, but camera scale, shadows and head orientation vary. This review **does not** prove stable facial identity across independently generated moving frames or a full video.

## Copy-ready correction prompts — one variable at a time, no regeneration in this audit

### Baseline identity lock (append to future pose prompts)

> **Identity priority:** Copy the approved v2 four-view reference as the immutable identity of one ordinary 13–14-year-old American middle-school boy. Keep the exact gentle cheek fullness, small natural nose, ear size, fair untanned skin, short dark-brown slightly messy naturally waved hair with moderate—not fluffy—crown volume, smooth skin without facial/armpit/leg hair, softly undeveloped arms/chest/legs, and normal neither-thin-nor-heavy waist. Bright medium-blue tank, loose charcoal athletic shorts, dark charcoal socks, worn gray running shoes with muted yellow detailing. His face, height, chest/waist proportions and limb lengths must not change with the exercise. Preserve the approved pose, both limb paths, fixed track camera and background. **Do not** make him a little child, a mature older teen, a muscular athlete, or a different person.

### Targeted identity-only edits by issue

1. **32 / 37 / 41 — shoulder/arm overdefinition:** “Retain exact body and arm placement, shoulder width and limb length. Gently soften highlights/shadows over deltoids, triceps, biceps and chest so arms resemble the ordinary undeveloped v2 boy; no defined muscular separation. Do not make arms stick-thin, thicken waist or alter hands, pose, shoes, track or camera.” Use #32 as first priority.
2. **34 V3 / 37 / 41 — older angular profile:** “Preserve current head orientation and facial expression but match approved v2 cheek fullness, softer youthful jaw, understated button-like nose and unchanged ears. Reduce the hard sculpted face/nose shadow, keeping him visibly 13–14, without artificially baby-rounding the cheeks.”
3. **31 / 35R / 36 / 39 / 40 — hair volume:** “Keep the same dark short lightly messy hair with natural small curls, but reduce bulky fluffy top mass subtly and avoid perfectly styled curls. Retain moderate hair on the sides; no buzz cut, high skin fade or exaggerated crest. Do not change face/age.”
4. **35R / some sit-ups — blue saturation:** “Match the exact approved medium blue of the v2 tank and charcoal gray shorts in neutral daylight. Preserve fabric fold and shading; recolor only, no skin or pose edits.” Avoid fixing legitimate lighting as if it were wardrobe.
5. **33 / 38 / 30 / 39 — already faithful:** “Use v2 as identity authority and freeze face, hair volume, skin softness and torso proportions; change only the new exercise pose.” No aesthetic overcorrection warranted.

**Process recommendation:** For any future single-frame crop or animation, compare a clean neutral-profile crop against master **before** running motion, then inspect earliest and latest frames for age and shoulder definition. Do not use 32/37/41 as new identity anchors merely because their push-up mechanics are good; derive from v2. Keep the four-phase card method to reduce drift, and preserve marker diagnostics in separate files when physical limb ownership is important.

## Scope and confidence

All findings are manual visual judgments at original-card and comparison-montage scale; not biometric verification, colorimetry, or a safety assessment of actual adolescent exercise. Prone and partially obscured faces receive lower identity confidence. No images edited, no rerenders, videos, Drive or GitHub changes in this QA pass.

