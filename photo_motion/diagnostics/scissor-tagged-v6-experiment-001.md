# Predeclared photographic scissor-jump diagnostic — C1-EX5-001

**State:** PREPARED / NOT GENERATED / HOLD FOR CHARLES'S FINAL VIDEO APPROVAL
**Intent:** one falsifiable, minimal-cost Google Flow *actual moving-video* experiment, not a production release. The separate process advisor retains control of travelers and Kanban.

## Hypothesis and change being tested

With the V6 photo card's *single tagged starting pose* as image input, can the current video model maintain orange/teal ankle-and-wrist **physical** limb ownership through **two** distinct scissor-jump flights and return to the exact start stance in a six-second real-photographic film?

If the clip is beautiful but it only shows one flight, it **fails** this experiment. Markers cannot simply jump to a different physical limb between camera positions. The source image's color-near/far tracking is **not proof of anatomical left/right**.

## Frozen reference inventory (verify again before using)

| Role | Immutable source | Known full-file SHA-256 | Caveat |
| --- | --- | --- | --- |
| Movement starting still | V6 tagged scissor contact card, 2×2, 1536×1024, existing Drive reference `1C9HMa4xwg4CkpDiNo7N8Ue5MqUW_sxWs` | `4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2` | Source bytes independently verified. Upper-left panel A clean half-open crop **(4,4,764,508)** is **760×504**; crop SHA must be captured before generation. |
| Visual identity master | Chart 1 approved v2 master, existing Drive reference `1kS-KxLMAoH1eDa2__XYajM5E3fr58HGT` | `e305b5b7787df0bacaafad70f02e4f7a2d96535893680b78ddc3b7c6860fb28d` | Appearance comparison only; not a substitute for tagged pose and not an automatically authorized derived identity. |
| Motion definition | `photo_motion/specs/chart1-scissor-jump.json` and original Chart 1 Exercise 5 booklet text in `data/5bx-charts.json` | Calculate exact Git blob/file SHA at reservation time | The original 1959 demo excerpt does *not* depict this exact Chart 1 jump. |
| Human demonstrator | Existing 120 fps adult scissor movement reference `1z9mmCui_0FQKlDPOL_6FI_Drij-fPCr8` | `1f9152bb82f0b73d71ad47ba77bdc64c642f9dd28e4e7675697e73ead216738e` | Cropped/occluded shoes mean anatomical left/right still unproven. |

Only the single actual panel-A image should be the generation start-frame input in this test. Keep the v2 master outside the prompt's ingredient slot as a comparison standard, to isolate the model's ability to preserve source-frame limbs. Preserve the original card, lossless crop coordinates/bytes, and submitted prompt as separate evidence. Never adopt a new video frame as the identity master by default.

**Framing constraint discovered on direct pixel inspection:** Panel A has an approximately **3:2** aspect ratio, while Flow's observed default output is **16:9**. A naive 16:9 cover-crop can cut off the head and shoes. Prepare an explicit framing method that preserves *every* limb and ground contact (e.g. measured side extension/letterboxing), hash the exact prepared 16:9 input, and record any padding or outpainting as a separate transformation. Do not stretch the person or assert a 760×504 panel is a native 1280×720 reference. This unresolved framing choice is a **pre-spend technical gate**.

## Exact proposed prompt v1 — DRAFT ONLY

The following is a prepared candidate, **not** yet a claim about what was submitted to Flow. The `photo_motion.experiments` run record must capture the actual verbatim prompt text if/when used.

> Generate one uninterrupted SIX-SECOND REAL PHOTOGRAPHIC VIDEO from the attached single start photograph. Its first frame matches that source image. One ordinary softly proportioned 13–14-year-old boy; the same face, dark hair, natural pale skin, light-blue athletic tank, charcoal shorts, dark socks, gray/yellow running shoes, red running track, grass, trees, daylight and fixed full-body side-on tripod composition. Realistic documentary 35 mm color photography, never a cartoon or sprite.
>
> TWO distinct original RCAF 5BX scissor jumps occur in this *one continuous take*. Track these same four PHYSICAL limbs across all frames. In starting panel A, the ORANGE wrist marker is on the *forward* arm while its ORANGE ankle marker is on the *back* leg; TEAL is on the *back* arm and *forward* ankle. These colors pair opposite-moving arm and leg for tracking; they do **not** establish that the wrist and ankle are on the same anatomical side. Every marker stays attached to its original wrist or ankle, even when screen positions cross.
>
> 0.0s A: orange leg BACK, teal leg FORWARD, orange arm FORWARD and teal arm BACK, both entire shoes planted. Arms almost straight and shoulder-high. Around 1.4s B: FIRST genuine AIRBORNE exchange, with both whole shoes visibly clear of the ground as the physical limbs exchange fore/aft positions. Around 2.5s C: opposite landing, orange leg FORWARD, teal leg BACK, orange arm BACK, teal arm FORWARD, both shoes planted. Around 3.8s D: SECOND separate AIRBORNE exchange, both shoes visibly clear again and arms reverse again. By 6.0s E: original grounded A stance and shoe positions, same physical orange and teal limbs, same arm angles and camera framing. There must be a visible opposite landing BETWEEN two separate airborne exchanges.
>
> Gentle attainable youth warm-up amplitude, natural feet and joints, long shoulder-high opposing arms, not bent running elbows or a high split. All limbs remain connected and correctly sized through every frame. No teleporting legs or marker migration, fading, static pose slideshow, ghost bodies, duplicated shoes, cuts, changes of face or clothing, camera moves, scenery warp, audio, captions, or music. End naturally registered to the opening frame for a repeatable loop.

The six-second checkpoint times are engineering *targets*, not historical prescribed jump cadence. The generated MP4 must be reviewed between these timestamps, not merely at them.

## One-attempt cost and provenance gate

1. Confirm the current Flow account/model/quote. Account showed **852 Flow credits** before this workstream's paid attempts; that is a point-in-time observation, not guaranteed future balance. Charles authorized **up to 200 total Flow credits** for this development workstream, with conservation as the default.
2. The historical six-second Omni 1.2 Flash pilot rate was **18 credits**, but this is **not** a current quote. Use one output only. Do not assume an unspecified model or quote. If source input, model, exact charge or output count cannot be verified, remain PREPARED.
3. Before charging, initialize a private `photo_motion.experiments` ledger capped at 200 for provider `Google Flow`; write the exact final prompt and hash-verified lossless panel-A crop; reserve that actual quoted estimated charge with a unique attempt key. Keep all private media and prompt/ledger records outside Git.
4. Generate **one** actual clip and retain the Flow ID, timestamp, source refs, source-crop hash, model/parameters, balance-before/balance-after observations, quoted versus actual charge, raw MP4 and SHA-256. Record even a failed or partially billed run rather than silently reclaiming its reservation.
5. Do not automatically retry. First review the failure category; a second run must change one explicit hypothesis/parameter and use a fresh attempt key. Never promote to production without Charles's specific video approval.

## Predeclared evidence and reject codes

| Code | Required observation | Reject if |
| --- | --- | --- |
| `FLIGHT_2` | Two separate intervals with complete shoes airborne, with grounded C between | Only one exchange, one hidden crossing, or no daylight under both shoes |
| `POSE_A_C_A` | Physical leg/arm order A → opposite C → original A | Same limb leads both landings, or initial pose cannot be recovered |
| `LIMB_OWNER` | Each orange/teal wrist/ankle remains on the same physical joint chain | A marker swaps sides, disappears or attaches to another limb |
| `ARM_FORM` | Extended opposite arms near shoulder height | Bent pumping-run elbows or extreme/unattainable pose |
| `CONTACT_SEAM` | Opening and final planted shoes occupy comparable track marks | Foot slips/float or obvious discontinuity at wrap |
| `PHOTO_CONTINUITY` | Fixed camera, same recognizable youth, outfit and background | Face/clothes/scenery change, camera pans or scale drifts |
| `VIDEO_CONTINUITY` | Continuous 24-fps-class real temporal movement | A still-card dissolve, ghost, cut, freeze or detached/duplicate anatomy |

Run `python3 -m photo_motion validate photo_motion/specs/chart1-scissor-jump.json`, inspect the actual MP4 with a fresh output directory, and run the temporal and annotated-contact tools only where their assumptions apply. Suggested review frames: 0.000s, 1.400s, 2.500s, 3.800s and approximately 5.958s; also step through *all* intervening frames, particularly both shoe liftoffs and landings.

Exploratory flags (not owner-approved acceptance thresholds): change in original grounded shoe locations over about 2% of frame width or background-registration movement over about 1% should trigger human review. No automatic metric can approve real exercise form, historical anatomical side, or publication.

**Approval boundary:** Experimental generation can proceed within the 200-credit authority once the exact start-image handling and current quote are verified. This document makes **no** declaration that a generated exercise video is final; Charles retains that decision.
