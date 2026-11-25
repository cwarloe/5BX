# 5BX film-to-sprite pose transfer: experiment and lessons

**Date:** November 24, 2026 (Boise)  
**Status:** Reference experiment and production guidance; **no exercise-form or animation release approval**.  
**Character:** Established Sprite Boy, cyan sleeveless tank, loose red shorts, white socks, blue running shoes, short dark hair, magenta background. The separately tested olive-shirt/gray-shorts runner is not a change to this canonical profile.

## Sources already in the repository

The 1959 Royal Canadian Air Force 5BX film and extracted stills are already cataloged in [the film index](https://github.com/cwarloe/5BX/blob/main/docs/reference/rcaf-1959-film.md) and [`docs/reference/rcaf-1959-stills/`](https://github.com/cwarloe/5BX/tree/main/docs/reference/rcaf-1959-stills). Key stills for the current test:

- `ex4-c3-chin-08m30s6.png`: Chart 3 chin-contact push-up.
- `ex4-c3-forehead-08m32s0.png`: Chart 3 **forehead-contact pike**.
- `ex4-c1-up-08m09s0.png`: Chart 1 knee-supported push-up.
- `ex5-c2-midair-07m26s4.png`: Chart 2 astride jump.
- `ex5-c4-squat-bottom-09m49s0.png`: Chart 4 semi-squat bottom.
- `ex1-c2-bottom-05m45s0.png`: Chart 2 toe touch.

Relevant existing records: [`AI_SPRITE_VIDEO_LESSONS.md`](https://github.com/cwarloe/5BX/blob/main/sprites/docs/AI_SPRITE_VIDEO_LESSONS.md), [`SCISSOR_JUMP_DIAGNOSTIC_RECORD.md`](https://github.com/cwarloe/5BX/blob/main/sprites/docs/SCISSOR_JUMP_DIAGNOSTIC_RECORD.md), [`FOREGROUND_TRAILING_EXERCISE_AUDIT.md`](https://github.com/cwarloe/5BX/blob/main/sprites/docs/FOREGROUND_TRAILING_EXERCISE_AUDIT.md), and [`AUDIT-01-09.md`](https://github.com/cwarloe/5BX/blob/main/sprites/qc-line/audits/AUDIT-01-09.md).

User-provided comparison evidence also included an existing cyan/red three-pose push-up row, the 1959 chin/forehead comparison, a posterized pike example with approximately 10% darker far-side shading, a 1959 film contact card, and two test-transition MP4s. This record does not assert that the MP4 motion was evaluated; only their supplied presence and basic metadata were observed.

## Corrected interpretation: forehead phase is a pike

**Previous prompt error:** The earlier nine-pose diagnostic prompt required the forehead-contact push-up to retain a straight horizontal body. That is inconsistent with the supplied 1959 film still.

**Correct source-based geometry:** The Chart 3 forehead phase raises the hips into a pronounced inverted V, with nearly straight supporting legs, palms grounded, toes/forefeet grounded, and head lowered so the forehead reaches the floor **behind the hands**. The chin phase is a separate low, approximately horizontal plank, with the chin contacting the floor **in front of the hands**. Do not treat these as two head positions on an otherwise identical horizontal push-up.

**Quality gates:** Confirm hip height, feet/hand support, knees off floor, which part of the face touches, and placement of head relative to palms against the film. Facial/hairline overlap can make exact contact ambiguous in cartoon drawings; a visually close result must not be called approved contact.

## Photo-to-sprite test (2026-11-24)

**Input roles:** (1) 1959 original film frame determines motion/form/joint placement; (2) prior sprite drawings determine character appearance, clothing, and line style. Do not let the appearance reference's pose override the film frame.

**Single-pose result:** Two successive generations reproduced the high-hip inverted-V posture, straight supporting legs, loose shorts, and established character better than the prior text-only straight-body attempts. The targeted second edit lowered the face but did not prove exact forehead-to-floor contact. **Candidate, not accepted form.**

**Nine-pose contact-sheet test:** One generation using the film montage as pose authority showed distinct interpretations of (1) toe touch, (2) backward lean, (3) back-extension peak, (4) astride jump, (5) knee push-up, (6) chin-contact push-up, (7) forehead pike, (8) semi-squat bottom, and (9) floor sweep. Character appearance stayed generally consistent. This is promising evidence that source-grounded pose transfer helps with pose diversity; it is **not** per-pose QC approval, temporal identity validation, or video validation.

**Source-art policy:** Keep original film and user-provided reference drawings unchanged. Put candidate/reference media in the project art archive, not the shipped sprite library, until reviewed. Initial archive upload was paused pending authorization; after the user explicitly authorized it, nine reference/candidate media files were archived and verified on November 24 (Boise time). No originals were overwritten or deleted.

**Verified project archive:** [2026-11-24 1959 RCAF film-to-sprite pose test](https://drive.google.com/drive/folders/1_xuq2ZA8rGe1d750EDxP8pcPPg8ejgJO), a subfolder of the existing `Sprite Art 5BX Workout` Drive folder. It contains five reference images (existing push-up/pike sprite row, 1959 chin/forehead comparison, far-side recolor, and two slightly different 1959 film montage frames); two generated candidates (single forehead pike v2 and nine-pose film-to-sprite card); two provided motion-test videos (`test-transition-stitch.mp4` and `test-transition-closeup-v2.mp4`); and this lessons record as Markdown. All ten were confirmed by Drive folder readback. The videos are archived as *supplied examples*, not independently certified animation quality.

### Evidence and dispositions: what worked, what did not

| Attempt or observation | Result and evidence | Status / prevention |
|---|---|---|
| Text-only nine-pose forehead instruction requiring straight horizontal body | Repeated a conventional low push-up despite the historical forehead phase being a pike | **Failed specification**: do not impose straight-plank geometry on the forehead phase |
| Film-still as geometry reference, Sprite Boy reference for appearance | Recovered a clearly raised-hip pike, nearly straight legs, correct loose shorts and character palette | **Promising candidate**: [forehead-pike v2](https://drive.google.com/file/d/1-DpynvTovobEC2AMwO-Fhrp4nNAO-P6M/view); forehead contact still not established |
| Nine individually named 1959 film positions in a single source-guided sheet | Produced diverse toe, bend, extension, jump, knee-push-up, chin, pike, squat and sweep shapes without nine copies of one pose | **Promising candidate**: [nine-pose card](https://drive.google.com/file/d/18V_VlUk-iu7tYh6tSFKcj5zVZUdcwtWa/view); no per-pose sign-off or video validation |
| Repeated near/far scissor requests inside nine-figure cartoon sheet | Generated near-identical forward/rear shorts topology despite explicit inverse language | **Failed composition/depth control**: individually validate near/far endpoints and track physical leg IDs, not silhouette or shoe hue alone |
| Single near-trailing scissor reference with explicit shorts occlusion | Visually showed trailing foreground thigh overlapping leading background thigh at waist/shorts seam | **Useful anatomy reference**, not a complete alternating jump cycle; see scissor diagnostic and trailing-leg rule |
| User's prior high-detail → posterized → cartoon workflow | User reports stronger anatomy preservation from staged outputs | **Experience to test**, not measured in the current run; generate and compare separate intermediate files before making a production rule |
| Jump sprite foot articulation | Some generated jumps have dancer-like pointed toes rather than the original sneaker orientation | **Defect to prevent**: reference-neutral foot/ankle geometry, no exaggerated pointe, but allow natural filmed takeoff extension |
| Camera angle | Slight oblique views make hips/overlap easier to read; exact profile can hide crossing; outside-foot toe touches are clearer from near-front | **Conditional design choice**; validate each view against visible form, do not force one angle across all exercises |

### Archived media index (reference only)

| File | Role |
|---|---|
| [`reference-existing-sprite-pushup-and-pike-row.webp`](https://drive.google.com/file/d/1qxOM1cRtwtNhM4OMG7s-ltyC5omrxmWx/view) | Earlier cyan/red candidate push-up row |
| [`reference-1959-forehead-chin-comparison.webp`](https://drive.google.com/file/d/18zROV44S5Lxz1yMmVWqHXn0SoIANh-bY/view) | Historical original versus earlier push-up row |
| [`reference-existing-pike-farside-shading.webp`](https://drive.google.com/file/d/1fiQVgpDgfIZCDlaAWOezqWUvBkDrZ8U5/view) | Earlier pike candidate and 10% darker far-side treatment |
| [`reference-1959-film-montage-forehead-0832.webp`](https://drive.google.com/file/d/1-Lh2Kb8aDa_d0S_4R6rei8_MGjcoUOx6/view) | 1959 source-film key poses, first forehead moment |
| [`reference-1959-film-montage-forehead-0835.webp`](https://drive.google.com/file/d/1YE1C4NJmB9UDfnlv2cFkuFGR5JjmVFwY/view) | 1959 source-film key poses, alternate forehead moment |
| [`candidate-forehead-pike-photo-guided-v2.png`](https://drive.google.com/file/d/1-DpynvTovobEC2AMwO-Fhrp4nNAO-P6M/view) | Source-guided individual pike candidate; no exact-contact signoff |
| [`candidate-ninepose-1959-film-to-sprite.png`](https://drive.google.com/file/d/18V_VlUk-iu7tYh6tSFKcj5zVZUdcwtWa/view) | Source-guided nine-pose card; not an approved strip |
| [`reference-test-transition-closeup-v2.mp4`](https://drive.google.com/file/d/1_6Vea5SP8Ieaw5mjALgh1aPk3uRF_Smb/view) | Provided motion comparison, 13.33 s, 1280x720 at 24 fps; not visually audited |
| [`reference-test-transition-stitch.mp4`](https://drive.google.com/file/d/1k0SrnP9RpDbt2wpM_hM-sdKOYuNqdaMI/view) | Provided motion comparison, 123.92 s, 1280x720 at 24 fps; not visually audited |

All listed links are user-owned Drive reference assets and may require the authorized account. They are **not** production art under `sprites/library/index.json`.

## New production lessons and prompt constraints

1. **Historical source is movement authority.** When text and the 1959 frame conflict, inspect the exercise's own original frame first. The generic concept of a modern push-up was the cause of the forehead-pike prompt error. The actual booklet wording remains authoritative for exercise identity, counts and intent; film frames help disambiguate visible geometry.
2. **Appearance and pose are separate inputs.** Use the existing cyan/red Sprite Boy as appearance reference only; keep the film's support points, joint angles, hip angle, and contact phase. Preserve age-appropriate body shape and truly loose gym shorts.
3. **Avoid ballet-style pointed toes for jumps.** Prompt: *"Use the original film frame's ankle/foot articulation. Athletic sneakers with realistic ankle angle; toes and feet remain neutral or naturally flexed unless that source frame specifically depicts plantarflexion. No ballet, en pointe, exaggerated toe point, dainty legs, or shortened shins."* Natural plantarflexion at takeoff is not automatically wrong; reject only unsupported/exaggerated posing.
4. **Choose view angle per movement.** Start by testing a slight oblique/three-quarter angle rather than exact profile or an arbitrary 45° angle when it exposes hip depth, thigh overlap, and shoe orientation more clearly. A useful trial range is roughly **15–30° away from a pure side view**, not a locked standard. Preserve a consistent view within one motion strip unless a transition is deliberate. For outside-the-foot toe touches, prefer **near-frontal** view so the hand's landing outside each shoe is visible. Final view depends on visibility of required form, not aesthetic preference.
5. **Treat camera depth separately from anatomical identity.** For scissor movements, explicitly specify physical left/right foot tracking and near/far occlusion at hip/shorts seam. An appealing frame with near trailing thigh does not prove a correct alternating cycle. Avoid rewording alone as a substitute for physical source or tracked landmarks.
6. **Use a staged rendering experiment.** User reports that high-resolution/anatomically accurate source images followed by posterization and then cartoonization have produced better prior sprites. Make this a controlled three-stage test: geometry-first high-detail render → review/accept pose → posterize → cartoonize. Compare against a direct-to-cartoon rendering from the same film still. **The current run was prompted to prioritize anatomy first but did not physically generate and validate three separate stage files; do not claim that pipeline is tested.**
7. **Keep an alternate realism test separate.** Later, test a more anatomically detailed/realistic posterized sprite (similar to the original runner) against the current simplified character on exactly the same source still, pose prompt, camera and acceptance metrics. Do not quietly change the canonical avatar until explicitly selected.
8. **Use single-pose validation before assembling sheets.** Nine-figure generation can copy leg geometry and overlook depth switches. Approve the difficult figure against the historical frame first, then assemble a sheet and verify that the approved pose actually survived compositing.
9. **No fade ghosting.** Existing 5BX experiments found crossfades can duplicate limbs; maintain no-fade single-body review unless a tested motion interpolator passes the same anatomy gate.

## Suggested pose-transfer prompt template

> **Pose authority:** Render the actor from `[exact 1959 frame path and timestamp]`. Copy source frame's visible shoulder/hip/knee/ankle angles, support points, and relation to the floor. Keep the exact exercise phase; do not substitute a common modern exercise.
>
> **Appearance authority:** Replace the actor with the canonical Sprite Boy wearing a cyan sleeveless tank, loose red gym shorts, white socks, and blue athletic sneakers. Retain age-appropriate natural athletic thighs and shins, compact dark spiky hair, black outlines, and magenta background.
>
> **Camera:** Match the source viewpoint, or test a slight off-axis view if needed to see depth. For outside-the-foot touches, use near-frontal. Keep the same camera across a motion cycle unless approved.
>
> **Feet in jumps:** Athletic footwear, natural neutral/flexed ankles matching the film. Do not force pointed ballet toes or en-pointe shoes. No unnatural shin shortening or toe stretching.
>
> **Rendering order:** Establish anatomically credible high-detail geometry and verify it; then simplify into posterized cartoon shading without moving the joints or changing contact points. Avoid extra figures, text, props, line-of-ground or shadows.
>
> **Test:** Check head/hands/feet support, near/far overlap and limb ownership, toe articulation, unclipped silhouette, loose shorts, and source-frame similarity before calling the frame accepted.

## Next comparison and approvals

- [ ] Individually validate exact forehead floor contact and show a side-by-side source/frame comparison.
- [ ] Re-render one jump from the 1959 film with natural sneaker/ankle geometry, compare directly against the pointed-toe failure.
- [ ] Generate the same scissor endpoint from pure profile versus slight three-quarter; review foreground trailing-hip outline and physical leg identity.
- [ ] Repeat the outside-left/right-foot toe touch with near-frontal viewpoint; validate floor contact beyond shoe.
- [ ] Compare geometry-first → posterize → cartoonize against a direct cartoon and a more realistic posterized avatar, same source pose.
- [ ] Human reviewer signs off on individual source-matched poses **before** contact sheet approval and before video.

**Change scope:** This document is a reference and process-learning record only. Its presence in GitHub or Drive does not constitute form approval, release approval, a replacement avatar decision, or a deployed sprite/video change. Keep the production control plan's human review gates intact.
