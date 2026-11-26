# 35S / 35T — Exact image generation/edit prompts

## 35S Diagnostic — edit original 35R color-band four-card

```text
Use case: identity-preserve precise photographic pose edit. Input image 1 is the EDIT TARGET: the exact 2-by-2 color-band diagnostic four-phase Chart 5 twisting-sit-up card, same photographic early-teen boy on red running track. Refine only poses B (top right) and C (bottom left) to show a REAL modest CONTRALATERAL TORSO ROTATION and clearer opposite ELBOW TOWARD BENT KNEE. Preserve all leg positions, limb identity markers, body/face/age, identical blue tank, charcoal loose shorts, gray/yellow shoes, dark socks, forest/track, cropped camera, panel labels A/B/C/D, and panel A and D completely unchanged.

COLOR MARKERS ARE ANATOMICAL OWNERSHIP, NOT DECORATION: ORANGE always on his own RIGHT elbow and RIGHT ankle, CYAN/TEAL always on his own LEFT elbow and LEFT ankle. Maintain two arms and two legs, connected anatomically, one pair of each markers per panel.

Panel B: The teal-ankled LEFT knee is bent and raised in the BACKGROUND, while orange-ankled RIGHT leg stays extended in FOREGROUND, heel in same place. Rotate chest/shoulder slightly TOWARD that raised teal-left knee. Bring his ORANGE RIGHT elbow FORWARD diagonally across front of chest, aimed at the bent TEAL LEFT KNEE, within an easy short distance of knee, even if not touching. His other cyan LEFT elbow stays behind/above, hand gently at side of head. Do not raise legs further, do not lengthen upper arm or shorten torso.

Panel C: The ORANGE RIGHT knee is bent and raised FOREGROUND, while teal LEFT leg remains straight in BACKGROUND. Rotate chest/shoulder in opposite direction TOWARD that raised orange-right knee. Bring his CYAN LEFT elbow diagonally FORWARD across the front of his chest toward the bent ORANGE RIGHT KNEE, visibly a different elbow ownership than B. The orange RIGHT elbow stays back and hand gently at side of head. Natural reach, elbow can remain a few inches short.

No muscular definition, washboard abs, tan, armpit or leg hair, adult growth, elongated limbs, extra limbs, elbows twisted backwards, hyperflexibility, footwear or color drift. He looks like an ordinary non-athletically-developed pale 13-14 year-old boy with short imperfect messy brown hair, slight button nose, unchanged moderately sized ears. Preserve full four-panel contact card and side-to-slight-30-degree-oblique viewpoint. Photorealistic natural daylight 35mm sports photography, static background. This is a subtle exercise-mechanics correction, not new choreography.
```

## 35S Clean — strip orange/teal limb-ownership bands

```text
Use case: precise-object-edit. The input is the newly generated photorealistic 2x2 four-panel Chart 5 twisting-sit-up reference contact sheet, labeled A, B, C, D. Remove ONLY the temporary orange and cyan/teal color bands wrapped around the boy's elbows and ankles in ALL four panels; replace with continuous matching natural pale skin at elbow/upper-arm locations and the existing ordinary dark charcoal/gray socks over ankles. No colored bands may remain. Treat all four exercise poses, elbow-to-opposite-knee relationships in B and C, every elbow/knee position, anatomical left-right ownership, age, face, short messy brown hair, blue tank, charcoal shorts, gray/yellow running shoes, body proportions, hand placement, track, field, trees, fixed camera framing and panel letters as LOCKED. No visible wristbands added. Do NOT change movement form, face, clothing, muscles, knees, arms, finger count, room, or art style. Natural 35mm photo of a pale average American 13–14-year-old boy, nonmuscular soft youth anatomy, no tan/body hair. The ONLY edit is cleanly removing the orange and teal limb-tracking bands and restoring skin/sock texture.
```

## 35T Clean — deepen the C left-elbow-to-right-knee motion

```text
Use case: identity-preserve precise single-panel photorealistic pose edit in a 2x2 contact sheet. Image 1 = EDIT TARGET, the clean four-panel twisting sit-up photo card labeled A B C D. Image 2 = ANATOMY/TRACKING REFERENCE, the same poses with orange RIGHT elbow and RIGHT ankle and teal LEFT elbow and LEFT ankle marks that define arm ownership. Maintain all original image 1 pixels as much as possible; modify ONLY the posture of the boy's upper chest and LEFT ARM in the LOWER LEFT PANEL C.

Panel C is lifting the boy's anatomical RIGHT knee in FOREGROUND (orange ankle in tracking reference), while his LEFT leg stays straight in background (teal ankle). His anatomical LEFT elbow (teal elbow in tracking reference), currently close beside his LEFT ear and upper chest, should rotate modestly FORWARD and DOWN toward the raised opposite RIGHT KNEE. Rotate his shoulders and ribcage a modest extra 10–15 degrees toward that right knee and gently draw the LEFT ELBOW in front of chest so its tip points at the front of raised RIGHT kneecap, coming visibly closer but NOT forced to touch if uncomfortable. Keep LEFT HAND gently behind/near left ear; left forearm and upper arm natural two-segment lengths, elbow flexed 80–100 degrees, never hyperextended. His anatomical RIGHT elbow stays back, hand near RIGHT ear, and must NOT become the reaching elbow. It is contralateral LEFT ELBOW toward RIGHT KNEE, not same-side. Exactly one upper and forearm per shoulder and two hands total. Because a 13–14-year-old may not reach elbow to knee, stop at a plausible gap.

Maintain every joint and foot location in panels A, B and D EXACTLY, and lower-left C both hips/knees/ankles/shoes/ground geometry exactly. Keep full four-panel 2x2 grid, labels, background, photo style, pale ordinary undeveloped middle-school boy's same face, ears, short dark messy hair, blue tank, charcoal shorts, dark socks and gray/yellow shoes, no muscle increase, no puberty/body hair and NO color tracking bands in final output. Original 35mm photo natural light, static camera. Do not move bent knee toward elbow, lengthen arms, twist spine unnaturally, invent a third hand, or swap right/left ownership.
```

## Input lineage

1. 35R marked anatomical reference: `artifacts/parallel_batch_20261126/chart5_ex2/35R_C5_EX2_TwistSitup_ColorTracking_35mm_DIAGNOSTIC_PASS.png`.
2. 35S diagnostic: `35S_ContraElbow_ColorDiagnostic_CANDIDATE.png`.
3. 35S clean: `35S_ContraElbow_Clean_CANDIDATE.png`.
4. 35T clean: `35T_ContraElbow_CrossBody_Clean_CANDIDATE.png`; used 35S clean as edit target and 35S marked diagnostic as anatomical ownership reference.

All outputs were generated with built-in image generation. No video generation or externally approved form validation.

