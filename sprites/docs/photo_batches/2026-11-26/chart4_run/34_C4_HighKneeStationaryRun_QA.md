# Test 34 — Chart4–6 waist-high stationary high knees (2026-11-26 UTC)

**Test V1 verdict: REJECT as proof of alternation.** Built-in imagegen photographic 2×2 card `34_C4_HighKneeStationaryRun_V1_REJECT_SameKnee.png`; only reference approved identity sheet `identity_sheet_v2_hair_arm_refinement.png`. Full exact prompt in `34_C4_HighKneeStationaryRun_ExactPrompt.md` (block under code fence). Static imagegen generation, no video or external files. The image visually includes unwanted film-border numbering and phase labels despite explicitly requesting no text.

## Panel-by-panel skeptical QA

| Tile | Observed | Pass/fail |
| --- | --- | --- |
| A upper left | Both feet together planted, arms down, camera nearly frontal rather than 25–30° off side. | Plausible *idle*, but not requested peak A; phase specification failure. |
| B upper right | One bent knee lifted to waist; support foot on track. Foreground wristband arm held back. | Good realistic high knee; neutral athletic shoe. |
| C lower left | Transitory stepping foot positions, one shoe close to track, arms moving. | Plausible transition, somewhat different scale/camera distance. |
| D lower right | Bent knee appears **same side, same screen position, same foreground calf/shoe and same near wristband arm arrangement as B**. Label claims opposite knee but not anatomically visible; generator may have simply replicated B. | **FAIL physical alternate-leg lineage.** Unverified near/far swap; no defensible right-vs-left ground support. |

**Other gates:** Appearance close to v2 (normal softly undeveloped mid-school figure, blue tank/charcoal shorts and gray/yellow shoes), no gross extra limbs, at least one realistic waist-height knee; full shoes visible. However face subtly ages/sharpens between frames, and camera view approaches 0° frontal not a depth-readable oblique. Fake Kodak branding and output labels are unnecessary/inaccurate. Body seems slightly more muscular at shoulder in B/D. Four related panels are not pixel-registered (track lines/trees vary). Camera intended to be static, not proven as four source frames.

## Next controlled test

Use **physical-leg color identity** from the Chart1 alternate-leg/scissor workflow: a small ORANGE band on the physical camera-near ankle and TEAL on camera-far ankle, persistent across all 2×2 panels, with corresponding thigh-to-shoe lineage. Require A orange foreground knee up with teal foot down and C teal far knee up with orange foot down, with B/D passing phases. Set no labels or border. Use 2×2 joint generation before cleaning. If successful, remove ankle markers in a *separate* one-variable edit; do not infer video motion from stills. This is a diagnostic hypothesis, not guaranteed.

## V2 orange/teal physical-leg diagnostic — PASS (stills), with caveats

**Artifact:** `34_C4_HighKneeStationaryRun_V2_ORANGE_TEAL_DIAGNOSTIC.png`, 1199×1312. Exact prompt: `34_C4_HighKneeStationaryRun_V2_ExactPrompt.md`. Image inputs in declared order: approved v2 identity master; Chart1 alternate-leg orange/teal diagnostic precedent. The latter was authority only for *marker technique*, not the prone pose. This is NOT a final clean wardrobe asset.

| Frame | Distinguishing visual evidence | QA |
| --- | --- | --- |
| A top left | Bright **ORANGE** ring is visibly on elevated bent-knee ankle/shoe at waist-height; **TEAL** ring is visibly on grounded straight support leg. Both thighs/shins/shoes stay distinct. | **PASS** near/front-leg peak and far support. |
| B top right | Orange-ankle shoe lowers and overlaps near the planted teal shoe. Both tagged physical limbs remain visible. Slight speed blur belongs to moving orange shoe. | **PASS** grounded passing, though knees/feet are crowded. |
| C bottom left | Opposite **TEAL**-ankle knee rises to boy's natural waist, its entire teal leg connected to raised gray/yellow shoe. **ORANGE** support leg plants on track, orange band and shoe plainly visible. | **PASS** tracked opposite physical leg / near grounded support. |
| D bottom right | Teal foot descends behind/adjacent to planted orange foot; both ankle markers persist on correct shoes. | **PASS** return passing phase. |

**Additional gates:** No textual labels. Blue tank, charcoal loose shorts, gray/yellow shoes consistent; genuinely photographic and reasonably representative of average 13–14yo. Camera more side-facing (~three-quarter side) than V1, helps thigh overlap. All support shoes contact track at peaks; torso stays upright. No dancer-pointed shoes or extreme jump, no six-inch height growth, no anatomical extra limbs. Each panel is almost stationary with minor generator background/scale drift typical of independently synthesized panel regions. **Remaining shortcoming:** near/far arm swing does not convincingly reverse from A to C; foreground watchband arm stays predominantly behind, far arm forward. This may need controlled wrist markers before deriving an entire video. Frame C peak reads as nearly the same knee silhouette but different *tracked physical* teal leg; this is why permanent marker audit is important. The generated still is visual evidence of distinct source colors/leg placement, not a proof that an animation interpolator will maintain knee lineage.

## V3 clean ankle-marker removal — CONDITIONAL KEEPER for photographic pose card

**Artifact:** `34_C4_HighKneeStationaryRun_V3_CLEAN_CANDIDATE.png`, 1199×1312; exact prompt: `34_C4_HighKneeStationaryRun_V3_CleanNoBands_ExactPrompt.md`. Source references in declared order: V2 tagged diagnostic as pose authority; v2 master as identity-only authority. **Single semantic edit:** Orange/teal ankle rings removed and replaced by plain charcoal socks. ImageMagick V2-to-V3 normalized mean absolute error = **0.0184152**, compatible with near-identical geometry but not a pixel-perfect copy. Source and clean remain the same dimensions.

V3 preserves A foreground high knee/far grounded support and C background high knee/foreground grounded support established by V2 markers; all feet and arms remain complete. Both peaks reach approximate natural waist height with realistic trailing shins and neutral footwear, torso and track camera broadly consistent. No posterized/cartoon quality or gratuitous age exaggeration. Plain charcoal socks restore final wardrobe. **Caveat:** once colored markers are removed, ankle ownership is harder to audit from a single clean sheet; keep V2 tagged diagnostic beside V3 as provenance. In C, raised thigh has less unambiguous three-dimensional crossing than desired, and counter-swing arms look nearly repeated instead of fully exchanging opposite the leg. Therefore **keeper for the initial still image prototype, not yet approved as a keyframed motion/video master**. Recommend video using a single strong up position if frame interpolation starts reversing legs; specifically check full arm exchange, track stability and age identity in motion.

**Disposition:** V1 REJECT; V2 PASS physical-leg diagnostic; V3 CONDITIONAL KEEPER clean photographic pose card. No Flow video, no Google Drive/GitHub external write, no user-review approval implied.
