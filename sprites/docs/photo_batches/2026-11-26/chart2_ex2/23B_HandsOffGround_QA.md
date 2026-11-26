# Test 23B — Chart 2 full sit-up hand-support correction

**Verdict: PASS targeted form correction, STRONG CONDITIONAL still candidate overall.** One built-in imagegen edit, no retry. No human form approval or video.

- **Input 23:** `23_C2_EX2_FullSitup_FourPhase_35mm_CANDIDATE.png`, SHA `71c109f381be2ec311096f885de08525bfdd4b48619b5f294de593fb823195c1`.
- **Edited 23B:** `23B_C2_EX2_FullSitup_HandsOffGround_35mm_CANDIDATE.png`, SHA `b6ea85310ac705cc65e80521a95e34e62ff43744ce4c97c5b88c3b76857708d3`, 1199×1312 PNG.
- **Exact prompt:** `23B_HandsOffGround_ExactEditPrompt.md`. Inputs: original 2×2 edit target first, v2 identity master second.

## Visual changes and preservation

- **Lower-left C, changed as requested:** Both hands are now visibly off the red running-track surface, relaxed alongside/atop the upper thighs. The black wristband remains near-side; elbows and forearms still physically attach normally. One forearm/hand rests against gray shorts rather than strictly hovering in air, which is a minor difference from the requested wording but **removes the ambiguous floor-pushing posture**. No hand appears planted or supporting weight.
- **Critical torso/leg geometry preserved:** Full nearly vertical seated torso; pelvic seat on ground, long legs nearly straight, both heels down, shoes fully visible, no lifting or twisting. No new limbs, extra hands, changed elbow direction, or abnormal waist curvature.
- **Other three panels:** Start, rising, and lowering poses visually still match their original actions and angles. No obvious scene/camera/framing shifts or age/wardrobe changes in those tiles.
- **Image identity:** Same fair skin, soft unmuscular early-teen figure, modest messy dark hair, blue tank, charcoal shorts, gray/yellow shoes and dark socks. No adult musculature or child-like facial drift.

## Pixel/registration check

ImageMagick normalized mean absolute RGB difference (original 23 vs edit 23B) is **0.0166031**, about 1.66% mean channel change across the whole 1199×1312 image. Quadrants A/B/C/D respectively: **0.0154981 / 0.0148801 / 0.020382 / 0.0156476**. This confirms panel C changed *more* than the others, but it also shows **generative microchanges in all three supposedly immutable panels**. Do **not** claim the edit literally preserved every original pixel; visual registration is excellent but not exact.

## Remaining limitations / next gate

1. The camera is still virtually 90° profile rather than requested 20–30° side-oblique; far leg overlaps near one.
2. The real boy's exact arm/heel mechanics in a video remain untested. He appears hands-free at apex in still C, but an image is not motion proof.
3. Because 23B changed microtexture throughout, do not rely on pixel-aligning panel centers as an exact animation sequence; use one strong high-resolution start anchor and a static camera.
4. The historical Chart 2 *full* sit-up differs from Chart 1 *partial* sit-up; preserve that designation in any video prompt.

**Recommendation:** Prefer 23B over 23 as the photographic four-phase pose card, still marked **strong conditional**. No further card edits needed until human/video review.
