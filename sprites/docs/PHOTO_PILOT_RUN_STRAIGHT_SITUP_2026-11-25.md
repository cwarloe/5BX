# 5BX photographic pilot — straight-leg sit-up — 2026-11-25

Status: **REVIEW / still frames**, not an approved animation. This tests a specific failure of the two prior photographic videos: they reached forward but **never returned supine**, so they could not form a complete movement loop.

## Source and generated output

- Identity authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`. One pale, naturally soft, unmuscular 13–14-year-old middle-school boy, blue tank/charcoal shorts/dark socks/gray-yellow shoes, fair skin, short modest messy dark hair.
- Starting photographic anchor: `artifacts/autonomous_batch_2026-11-25/flow_anchors/04_straight_situp_supine_35mm_CANDIDATE.png`.
- Historical movement source: 1959 RCAF 5BX film `ex2-c4-start-10m39s6.png` and `ex2-c4-mid-10m34s0.png`; **pose source only**, not adult anatomy.
- Unified 2×2 photographic sheet SHA-256: `3ab9058b6f2a430ddf2c3c7162d5ac35a3a7aa6fd8ff015a822be58592a525f8`.
- Sequence: top-left **lying with straight legs and arms overhead** → top-right **halfway up, arms raised** → bottom-left **seated, reaching to shins** → bottom-right **fully lying again**, arms overhead. Same track, rightward feet, head to image left, fixed slight oblique viewpoint.

## Still-image QA

**What worked:** Entire movement sequence was generated together; repeated fully-supine start/end is visibly present; legs remain extended and shoes on track, without ballet toes or unrealistic flexibility. The reach stops at his shins rather than stretching to the far ends of his shoes. Camera, outfit, face, and approximate scale remain stable. Compared to earlier videos this card supplies an explicit recovery endpoint.

**Review questions:** The near shoulder in the forward reach may have slight extra definition; the hair shape and facial angle vary with posture. Because hands and arms are partially occluded in the bottom-left frame, exact two-arm tracing needs a close review. A four-phase still cannot guarantee any video generator will return to the starting position; the existing `10adbef1.mp4` and `f502709a.mp4` still need to be labeled PARTIAL. Do not use their end frame for an automatic loop.

## Full-card prompt

> One unified, high-fidelity 35mm photographic 2×2 contact sheet of the same normal fair-skinned 13–14-year-old boy as in the supplied identity image, in bright blue tank, charcoal shorts, dark socks and gray/yellow shoes, modest dark messy hair, soft unmuscular natural body, no body hair. Fixed camera at a slight oblique angle on the outdoor red running track, identical grass and trees in every panel, white gutters. Use the supplied supine youth photo to lock floor, scale and direction: head LEFT, shoes RIGHT, legs fully straight. The 1959 RCAF 5BX picture illustrates movement mechanics, not adult appearance. Top left lying flat, both arms overhead behind head. Top right halfway up, straight arms reaching diagonally upward as torso curls up, both legs on track. Bottom left seated, arms forward with fingertips naturally near shins/ankles, no forced extreme toe touch or limb elongation. Bottom right **fully returned flat onto his back, same as first frame**, arms again overhead. Same face, same clothing and physically possible youth anatomy throughout; exactly two arms and legs, no added muscles, no bent knees, no captions or collage styling besides the four panels.

## Next Google Flow video prompt — not yet executed

> A single continuous five-to-six-second photorealistic 35mm documentary shot on the same school running track, fixed camera at a slight side angle. The same ordinary fair-skinned 13–14-year-old boy from the **single provided fully-supine start frame**, with blue tank/charcoal shorts, dark modest messy hair and naturally soft shoulders, completes **one entire straight-leg sit-up**. Start flat on back, both straight legs resting on track, arms stretched back overhead. He slowly curls shoulders and torso up while arms sweep forward, briefly reaches naturally toward shins without distorting spine, knees, arms or waist, and then **lowers all the way back onto the track** with head and shoulders touching ground and arms returned behind head by the final second, matching the uploaded starting frame exactly. Feet and leg lengths stay fixed, school track/trees/shadows unchanged. No camera move, mirrored image, crossfade, extra arms, exaggerated abs, bent knees, cut, sudden body growth or stop-at-the-reach ending. One coherent opaque boy, no audio or titles.

**Video acceptance:** Both start and ending must be supine with head/shoulders on track, all motions natural and smooth, feet/legs fixed, face/age unchanged, no frame blending or limbs swapping. Upload ONLY the top-left supine frame as a start image. The complete card is for human/reference QA, not a 4-keyframe video input. A new generated AI video is **not** included with this test because the connected video engine was unavailable on its current plan.

Mobile review: [5BX Video Review](https://drive.google.com/drive/folders/1W9dWViCZENv2UvoZ_k0EME8h9xRUWNKY). This card remains a `REVIEW` candidate until Charles approves the specific artifact.
