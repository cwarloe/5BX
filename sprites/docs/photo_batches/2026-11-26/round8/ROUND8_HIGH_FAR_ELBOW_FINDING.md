# 34K — High far elbow, behind-torso occlusion

- Base: 34J exact four-panel card, uploaded by user as `01-generated-image.png` (1199×1312).
- Target: lower-left panel (raised background leg), visible far/background elbow; user point x=21.8%, y=65% (full image).
- Correction: raise **far elbow visibly above the near/foreground elbow** and shorten apparent far upper arm. Keep far forearm, wrist, and hand fully hidden behind blue tank/torso. Do not create another hand or extend arm behind hips just to reveal it.
- All four poses remain on the same contact sheet for identity consistency.
- Acceptance criteria: far elbow top and tip higher (image y smaller) than near elbow; plausible shoulder-to-elbow length; no doubled/hyperextended arms, age/face/muscle or palette drift.
- Visual QA: 34K appears improved over 34J in lower-left panel; far elbow rises ~15–30 px in crop and no far hand is exposed. This remains a **candidate pending user visual approval**.
- Artifacts: `34K_HigherFarElbow_Review.png`, `34J_vs_34K_FarElbow_MobileCompare.jpg`.

## Lesson

For near-profile high-knee running, the far arm should often be almost fully occluded. Explicitly showing the far hand can force a model to lengthen the upper arm or create the wrong hand. Specify shoulder depth, a small higher elbow silhouette, and far forearm occlusion. Compare **joint heights** before judging merely whether a hand is visible.

