# 5BX round 7 — occlude the far left arm instead of forcing a visible hand

Experimental 35mm photographic still, not human-approved for animation.

## Controlling human insight

The user reviewed the preceding 34I-type high-knee card and accepted that it was an improvement but still looked unnatural: the **far upper arm remained too exposed/long** for a shoulder positioned in the background. The repeated effort to render a visible far hand was likely forcing an impossible camera silhouette. The user proposed a more plausible composition: **tuck the far arm behind the torso, possibly showing only the elbow**, rather than requiring a full hand.

## 34J controlled test

- Source: the exact user-selected image, preserved as `34I_UserSelected_ExactEditBase.png`.
- Change ONLY lower-left panel C's trailing background/left arm; physically hide its forearm/wrist/hand behind torso and hip. Leave a small natural rear elbow bulge behind lower rib/waist.
- 34J visually removes the downward hanging hand and most of the implausibly long far upper arm. It no longer reads as a second foreground/right fist. The source boy, other panels, clothes and legs remain comparable. The near/foreground right arm is still raised forward in C and swung behind in upper-left A.
- **Still uncertain:** whether the remaining visible rear elbow is ideal for a moving high-knee keyframe and whether a video system will infer a natural hidden arm rather than popping a limb into view. Needs human review and later video test.
- **State:** 34J **REVIEW CANDIDATE** (photographic pose only). Prior 34H/34I are preserved as diagnostics; do not silently promote either.

## Production lesson

**Occlusion is an anatomical feature, not a rendering failure.** At a three-quarter profile, a far-side arm can disappear behind torso and seat. Forcing both complete arms/hands to be visible can create duplicated handedness, implausibly long upper arms, and a poor silhouette. In prompts, specify `the far forearm and hand are hidden behind the torso; only a slight far elbow may show`, then test temporal continuity. Avoid trying to repair an occluded limb by lengthening it or twisting the wrist toward the camera.

## Files

- `34I_UserSelected_ExactEditBase.png` — exact user-provided edit source
- `34J_FarElbowOnly_Occlusion_Review.png` — candidate
- `34I_vs_34J_Occlusion_MobileCompare.jpg` — focused comparison
- `34J_ExactSubmittedPrompt.md` — verbatim prompt

No new video has been generated in this round.
