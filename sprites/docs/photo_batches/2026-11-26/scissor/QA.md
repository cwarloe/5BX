# Chart 1 scissor-jump photographic batch, 2026-11-26 (UTC)

**Overall verdict: REJECT as video/complete scissor cycle.** Two imagegen calls produced useful diagnostic stills but did not establish a physically alternating near/far-leg sequence. No Flow video was requested because the still cycle failed the motion gate. No owner exercise-form approval claimed.

## Immutable inputs

- PRIMARY character/wardrobe authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`, explicitly approved for image identity. Four-view 13–14yo soft, fair, blue tank/charcoal shorts/gray-yellow shoes.
- SECONDARY pose-only authority: `artifacts/parallel_tests/scissor_jump_leg_depth/frame_01_near_trailing.png`, a previously credible foreground-trailing running pose. Explicitly NOT authoritative for the face, camera, clothing or age.
- Booklet/source wording: Chart 1 scissor jumps, opposite arm/leg forward, jump to exchange before landing, arms at approximately shoulder height; `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`.
- Prior diagnosis: `repo_5bx_brightboy/sprites/docs/SCISSOR_JUMP_DIAGNOSTIC_RECORD.md`, which expressly warns that mixed opposing A/B pose sheets repeatedly collapse to the same lead leg and that a source-grounded physical leg ID is missing.

## Test 1 — jointly generated four-phase photo card

**File:** `scissor_joint_card_V1_REJECT_same_leg.png`.
**Exact verbatim prompt:** `PROMPT_V1.md` (the entire block from `Use case:` through the end). Built-in image generator, two referenced PNGs.

### Observations

- PASS photo / appearance: same general 13–14yo face, blue tank, charcoal shorts, gray-yellow shoes, four full-body panels, stable background style, no ballet feet, natural modest stride/shorts.
- FAIL exercise sequence: top-left and bottom-left grounded panels both show **the same forward/rightward leg depth/silhouette**. The distinctive camera-near trailing / camera-near leading hip overlap does **not** invert. Top-right and bottom-right airborne panels also closely repeat a similar near-leg-leading knee-lift. Thus no physical opposite-leg landing is demonstrated.
- FAIL arm/leg phase: hands are below shoulder height, arm/leg opposition is not anatomically traceable, wristband arm continuity ambiguous.
- Minor camera identity: the model mostly preserves facing right and image style; some relative head/body scale and scene features shift across panels, meaning frames not registered for direct animation.

**Verdict:** **REJECT** as source for video. This is an exact recurrence of earlier mixed A/B-sheet failure even with approved photo master and explicit right/left hip depth wording.

## Test 2 — isolated inverse trailing-leg endpoint

**File:** `scissor_near_trailing_V2_ISOLATED_CANDIDATE.png`.
**Exact verbatim prompt:** `PROMPT_V2_INDEPENDENT_ENDPOINT.md` (the full block from `Use case:`). Built-in image generator, same two reference PNGs.

### Observations

- PASS isolated photo: believable documentary sharpness and full-body scale; fair teen identity / palette generally tracks master; legs unbroken, toes neutral, two feet grounded, moderate split stance, no age-distorting extreme jump.
- PARTIAL depth geometry: the trailing leg appears closer to the camera and front leg appears farther, similar to the accepted depth exemplar. However **physical anatomical right/left identity cannot be verified** from one independently generated pose, and the visible shorts crossing remains camera-angle-dependent.
- FAIL cross-frame registration: alternate independent render has different background, face/hair microgeometry, figure placement/camera distance from V1. Cannot splice these as registered animation frames.
- FAIL unambiguous arm identity: the black wristband is on the rearward arm, despite prompt assigning right wrist/arm forward. Do not infer correct physical limb mapping from natural-looking hands.

**Verdict:** **CONDITIONAL DIAGNOSTIC CANDIDATE ONLY**, not usable video endpoint or final form approval.

## Lesson / next best test (no automatic regeneration from word-only prompts)

1. Jointly generated current photorealistic identity cards appear strong for appearance but **still reproduce repeated same-leg scissor topology**. More negative prompt text did not solve it.
2. Isolated near-trailing output can be visually plausible but lacks verified physical right/left identity and differs in photographic registration. Do not pretend two plausible independent stills constitute an alternating cycle.
3. Next cost-effective controlled test is to use the owner's original **120-fps scissor-jump video** with a visible physical-leg marker or source frame/skeleton trace to identify the actual anatomical near/far limb in A and B, then provide both explicitly labeled source frames as **pose authority only** while using v2 as separate **appearance authority**. Distinguish tracking, pose generation and animation stages.
4. Camera stays static and full figure visible, no toe-pointing, no fades/interpolation ghosts. Do not submit video generation until both opposing body positions pass the hip-depth and physical-leg-identity gates.

No repository/Drive writes, no Flow credits spent, and no approved production asset changed in this task.

## Follow-up — authenticated original human source video recovered, but no defensible physical-leg pair

**Original Google Drive file:** [VID_20261123_213002.mp4](https://drive.google.com/file/d/1z9mmCui_0FQKlDPOL_6FI_Drij-fPCr8/view), exact size **179,593,650 bytes**. Authenticated raw Drive fetch succeeded; downloaded into this isolated scratch batch as `source_human_120fps_20261123.mp4`. SHA-256 `1f9152bb82f0b73d71ad47ba77bdc64c642f9dd28e4e7675697e73ead216738e`. ffprobe reports H.264, 1920×1080, duration 90.133211 seconds, nominal 120/1 frame-rate base, variable average frame rate reported; do not infer that every displayed frame is sharp 120-fps capture.

**Four documented static-angle windows inspected** using timestamped 2 fps montages:

- Angle 1, facing left/near-profile: **12.0–20.5 s**, `reference_pass1_CONTACT.jpg`.
- Angle 2, facing right/slight three-quarter: **32.0–40.5 s**, `reference_pass2_CONTACT.jpg`.
- Angle 3, facing left/three-quarter: **47.5–56.0 s**, `reference_pass3_CONTACT.jpg`.
- Angle 4, facing right/near-profile: **70.0–78.5 s**, `reference_pass4_CONTACT.jpg`.

**Closer diagnostic:** 10 fps crop sequence for **33.0–35.0 s** in `pass2_temporal_CONTACT.jpg` and constituent source frames. Two visually plausible movement phase candidates were extracted at original 1920×1080 resolution: `pass2_t33p5.png` (33.50s) and `pass2_t34p0.png` (34.00s), shown in `source_pair_33p5_34p0_UNVERIFIED.png`. Additional candidate left-oblique pair at 49.0/50.0s is in `pass3_A_B_UNVERIFIED.png`.

### Diagnostic findings

- The original is now **accessible and fully preserved** locally; a missing or inaccessible file is no longer the blocker.
- All four camera passes repeatedly **crop shoes/toes at the lower frame edge** during the action, with occasional frame-to-frame motion blur and near/far lower-leg occlusion. This was already identified in the earlier project diagnostic report and is confirmed again from the authenticated source.
- The 33.5/34.0s pair does show changing arm trajectories and grounded split stance, but **the actual anatomical right/left leg identity through the crossing cannot be traced unambiguously** from those two stills. The 49/50s left-oblique pair looks quite similar, not a defensible inverse endpoint. Two different timestamps are not proof of a valid leg exchange.
- The source athlete is an adult demonstrating the movement. His face/build/outfit are never appearance authorities for the photographic schoolboy, only movement geometry.

**Final physical-leg provenance verdict: INSUFFICIENT / UNVERIFIED.** Do **not** describe either pair as two verified opposite-leg endpoints and do **not** generate new AI scissor art or Flow video based on a claimed swap. A source with an actual same-foot marker (e.g., contrasting wrist/ankle/sock band on one physical limb) and full shoes in frame, or independently labeled anatomy/skeleton with a justified occlusion resolution, is the missing control. Existing source remains valuable for cadence/arm swing and modest stride amplitude, but not certification of near/far ownership.
