# Chart 1 — Exercise 4: Kneeling push-up, photorealistic V2 test

Date: 2026-11-26 UTC
Status: **REVIEW / CANDIDATE ONLY**. Assistant visual QA, not Charles' exercise-form approval. No video generation or production Mixer changes.

## Inputs and provenance

- Image 1 — **PRIMARY immutable identity/outfit authority:** `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`
- Image 2 — **POSE GEOMETRY authority only:** `artifacts/photo_pilot_kneeling_20261125/09_CARD__CurrentIdentity_KneePushup_FourPhase__2026-11-25.png`
- Built-in image generation tool (photorealistic-natural), one jointly generated 2×2 card, no transparency, no image-edit chain from other exercise video.
- Output: `C1_E4_KNEELING_4PHASE_V2_REVIEW.png`, 1774×887, SHA256 `ea48c9c006f325690f46dae9d04fb9f21afe275b538037b1510b5976f24efb53`.

## Exact submitted prompt

```text
Use case: photorealistic-natural.
Asset: Chart 1 5BX Exercise 4 — ONE HIGH-RES 2×2 photographic four-phase kneeling push-up contact card, suitable for selecting an image-to-video start frame.

INPUT 1 (PRIMARY, BINDING): the approved four-view blue-tank/charcoal-shorts middle-school boy identity sheet. Reproduce this same recognizable normal American 13–14-year-old boy, its precise medium-dark naturally messy modest hair, realistic non-babyish face, nose/ears/brow/jaw, fair untanned skin, proportionate soft undeveloped arms/shoulders/waist/hips, all clothing/shoes and wristband. Do not copy his STANDING poses; identity/outfit only. No sculpted deltoids or biceps, six-pack, sharply narrow waist, facial, chest or armpit hair.
INPUT 2 (POSE AUTHORITY ONLY): successful 4-frame side-on kneeling push-up reference. Match its orientation and exercise phases, but replace with exact boy from INPUT 1 and slightly improve elbow synchronization. Do not derive identity from INPUT 2 if any detail conflicts with INPUT 1.

Produce one UNLABELED precisely aligned 2×2 grid with narrow clean white dividers. Four adjacent true 35mm candid photographs of EXACTLY THE SAME BOY wearing a light medium-blue sleeveless athletic tank, loose charcoal mid-thigh shorts, dark ankle socks, gray sneakers with subtle yellow details and a dark wristband, on the same outdoor reddish rubber school running track, grassy field, soft trees, realistic daylight. Real fabric wrinkles, pores, natural hair strands, subtle 35mm film grain, crisp figure texture. Four equal full-body right-facing 90-DEGREE SIDE PROFILES, knees and shoes to IMAGE LEFT, face and hands to IMAGE RIGHT. Camera at track level, rigid tripod, unchanged scale, exposure, background, horizontal track lines and boy identity across tiles. Entire head, both hands, both kneecaps and both shoes visible in every tile with clear edge margins.

KNEELING PUSH-UP body geometry in every tile: BOTH palms root to the exact same physical marks on the rubber track, elbow joints belong to the same anatomically attached TWO arms, BOTH knees rooted to one track line with natural hip-to-knee segment, BOTH lower legs fold up backward with shoes floating behind, never toes planted. Keep a plausible straight shoulder–hip–knee trunk line; pelvis should travel down as the chest lowers, not poke upward; no bowed/humped back, no butt sticking up. Natural range for a healthy ordinary middle-schooler.

TOP LEFT panel: correct UP start, elbows fully straight, head aligned with trunk, hands under shoulder axis, knees planted.
TOP RIGHT: QUARTER TO HALF DOWN, BOTH elbows visibly bend together (including far-side elbow), shoulders chest pelvis lower together, same two hands rooted.
BOTTOM LEFT: LOW, BOTH elbows bent at roughly 90°, shoulders/chest near track but not touching, hips still on straight shoulder–hip–knee line, knees unmoved, two elbows and two hands only, naturally supported.
BOTTOM RIGHT: completely RETURNED TO UP, same form and exact planted hand/knee positions and physical body lengths as panel 1.

NO extra limb, spider-like third arm, fused hands, hidden far elbow magically straight, shifted shoe, toe push-up, elongating bones, floating knee, camera move, younger child, different adult, out of focus boy, changing outfit color, black hair quiff, overdeveloped muscles, text or watermark. The scientific priority is correct, believable body mechanics and consistent individual boy throughout all four positions.
```

## Visual QA

| Gate | Finding |
| --- | --- |
| Identity | **PASS provisionally**: young teen face/hair and outfit close to V2; all four panels same boy; no exaggerated baby face. |
| Camera and orientation | **PASS**: fixed side right-facing view, similar scale, consistent red track/horizon/background, all limbs fit. |
| Knee supports | **PASS**: knees fixed on track, shins folded upward with shoes off track, no toe push-up. |
| Near arm | **PASS**: near elbow straight / half-flex / near-90° low / straight cycle. |
| Far arm | **REVIEW**: far forearm/hand appears partly visible in some panels but the far elbow is mostly occluded by near arm and torso; cannot independently verify synchrony at low position. No obvious spider-style third arm. |
| Hip–shoulder line | **PASS provisionally**: hips lower with chest, no extreme raised rear or broken back; natural child movement range. |
| Garment color / skin | **PASS provisionally**: consistent blue tank, charcoal loose shorts, dark socks, gray-yellow shoes, fair skin. |
| Body proportions | **REVIEW**: reasonably soft, though shoulders and biceps still slightly more defined than the preferred average undeveloped middle-school boy; do not over-correct width/waist. |
| Temporal feasibility | **NOT TESTED**: static sheet only; registration, far elbow dynamics and return loop require future video. |

## Compared to original 09

- The new card is a faithful reproduction of 09's already promising anatomical scheme, NOT a major pose breakthrough.
- The principal improvement is the explicit rebase to the approved V2 identity source rather than the previous 08 video pose-edit chain; facial/wardrobe details remain coherent within the card.
- It still has a 90° far-elbow visibility tradeoff inherent to actual side photography; prompting extra arm visibility may produce a spider limb or artificially splayed posture. We intentionally do not force that.
- Camera is full-body and steady; larger face detail could be improved later with higher-quality individual start-frame export while retaining suitable full-body movement margins.
- We chose **not** to spend another generation on a tiny elbow-visibility imperfection, because major form and identity gates passed provisionally.

## Next independent test

Use **only the top-left up frame** as the image-to-video start in Flow, with explicit both-palms/both-knees planted and shoulders+hips moving as one line. Preserve complete 2×2 card as geometry reference, but do not pass all four phases to the video tool simultaneously. Compare resulting blue/charcoal costume and face to V2 master before promoting. Owner form judgment still required before production.

## Native start-frame extraction and prior-09 comparison (follow-up)

- Saved deterministic **top-left native crop**: `C1_E4_UP_NATIVE_CROP_883x438.png` (ImageMagick crop x=0, y=0, 883×438; no resizing, retouching, or re-generation). SHA256: `68eb00eaa5762163369156ed98cd5bba4c80636f94ebe07393d6baf0bd657304`.
- **Full figure present:** shoes, knees, both arms, hands and hair remain fully in frame. Approximate margins: left ~75 px, top ~24 px, bottom ~35 px, right ~280 px; plausible space to lower/shift head in a Flow sequence.
- **Important limitation:** this crop is only **883×438**, NOT native 720p. The source contact card is 1774×887 but contains four panels, so its individual frame can never be a genuine 1280×720 photograph by cropping alone. We intentionally did **not** upscale or pad it and did not claim a lossless 720p start frame. A separate full-resolution single-frame image generation (or export of a genuinely high-res original) would be required for 720p+ source fidelity.
- Created internal before/after card `QA_09_VS_V2_UP.png` using native top-left crops from original 09 and this test; it is a comparison artifact, not a Flow start frame.
- **Identity/fidelity:** The new V2 boy is recognizably the same approximate age with the same shoe, tank, shorts and wristband, and the camera/framing is essentially unchanged. Hair appears **slightly lower/less fluffed** and new face slightly softer/rounder; the tank is marginally darker/richer blue. The boy remains crisp, while the new tree/field background is slightly more defocused/softer. These are small color/identity variations, not an objectively superior high-res render. If chart-wide master fidelity is paramount, preserve the exact preferred single up photo across exercises rather than swapping these two near-identical generated variants.
- This exercise is a **still candidate**; do not automatically launch video if the 883×438 panel source resolution is unsuitable. For a fair Flow quality test, generate or acquire a true full-resolution single-pose current-boy source and pin it at chart-level.

