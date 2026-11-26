# Test 41 QA — Chart 6 Exercise 4, chest-slap push-up

**Candidate:** `41_C6_EX4_ChestSlapPushup_FourPhase_35mm_CANDIDATE.png`  
**Date:** 2026-11-26 UTC  
**Status:** **CONDITIONAL KEEPER / technically convincing diagnostic, not yet video-validated.** Four distinct movement states with the uncommon double chest-slap represented. The unsupported torso at the slap apex may be raised too high for a typical soft middle-schooler; this must be fast and transient in video.

## Source and semantic requirement

The original booklet's Chart 6 Exercise 4 specifies: **front lying with palms under shoulders; push off floor, slap chest, return to start**. This is a true **chest slap**, not a clap between hands and not a supported pose with one hand still on floor.

## Four-panel independent QA

| Panel | Intended | Observed | Result |
| --- | --- | --- | --- |
| A top left | Low straight-body push-up | Two hand contacts on track, flexed elbows, shoulders/hips/knees/ankles aligned, knees up | **PASS** |
| B top right | Both arms release from floor | Both separate hands and all visible fingers hovering above track, no supporting hand, toe areas grounded | **PASS** |
| C bottom left | Double slap of upper chest during brief flight | Two hands visibly apart and laid against opposite regions of blue tank near the chest. Neither hand on ground. Not clapping palm-to-palm. Both arms connect to shoulders without apparent phantom support | **PASS core pose**, **CAUTION**: hands could read as holding/touching shirt rather than a fast slap in a static still; elevation and time spent aloft must be minimized in motion |
| D bottom right | Recover high support | Both palms flat under shoulders, elbows straight, toe support, long plank | **PASS** |

## Key failure-mode checks

- **Extra limbs:** none evident; exactly two arm chains in each panel, including C. Far hand in C is partly occluded by near hand/torso, so exact ten-digit counts are not independently possible.
- **Ground-contact mistake:** C does *not* leave a hidden or visible supporting hand on ground, unlike a common generation failure. Both toes remain at track, no floor-supported knee.
- **Target correctness:** C hands touch two separated points on chest/blue shirt, *not* each other. The two-palm chest slap is semantically achieved.
- **Body alignment:** no extreme pike or obvious spine collapse. C torso is inclined high relative to ground, a realistic short explosive crest only for a fit person; a typical 13–14-year-old without prominent upper-body strength may struggle with such height. Avoid freeze/hold or slow-motion treatment.
- **Adolescent realism:** somewhat more defined shoulders than desired in B/C, but no adult musculature or V-cut abs, strong chest hair or facial hair. Approximate middle-school appearance and pale skin retained.
- **Identity and scene:** face, hair, light blue tank, dark charcoal shorts and gray/yellow shoes are consistent enough across card; track/grass/tree horizon coherent. A and D are close in support pose. Static ~25–30° oblique reveals both arms.
- **Cropping and registration:** full body largely captured with margins; the boy's projected body height changes naturally with pose, but background/camera framing is not pixel-perfect between tiles.

## Decision

**Keep Test41 as a pose-generation success and an animation experiment candidate**, but **do not approve as final instructional video** on this still alone. Preferred future improvement: **smaller release amplitude and lower chest-slap apex**, hands contacting the shirt briefly and then immediately replanted. If animation turns C into a long hold, morphs fingers/forearms, or suggests unsupported hovering, reject the video and try the grounded high-support starting frame only, as the project has previously found more stable for video generation.

## Reproducibility

- **One imagegen call**, two referenced local image files, no attempts to patch the generated image.
- Exact full prompt: `41_C6_ChestSlapPushup_ExactPrompt.md`.
- PNG: 1536×1024, sRGB.
- SHA-256: `07d4dec7dba68822a965156f727ddddd60336135d1a59ac0555fc2685c0b0cdc`.
- No video generation, Google Drive/GitHub write or other external publishing.

