# 44 — Chart 1 scissor-jump oblique viewpoint proof

**Verdict: DIAGNOSTIC ONLY, REJECT AS VIDEO ANCHOR.** The 20° off-profile view adds arm/hip depth but does not solve the airborne exercise mechanic; fixed-camera headroom remains inadequate.

## Inputs
- Image 1: `scissor_2x2_V7_CLEAN_5BX_STRAIGHTARMS_CANDIDATE.png` (prior side-profile clean candidate).
- Image 2: `scissor_2x2_V6_TAGGED_STRAIGHT_ARMS_DIAGNOSTIC.png` (orange/teal anatomical wrist/ankle tracking).
- Image 3: v2 middle-school identity sheet.

## Observed frames

| Frame | Intended | What appeared |
|---|---|---|
| A top-left | Near leg trailing / far leg leading, near arm forward | Planted side-stride with arms extended shoulder height; mild shoulder depth and normal thigh/calf proportions. |
| B top-right | Airborne exchange of near/far legs and arms | Both feet airborne and sneakers not ballerina-pointed, but foreground knee bends strongly like a sprinting leap. **Not a convincing extended-leg scissors flight.** |
| C bottom-left | Reversed lead-foot landing | Reverse depth is plausible but occlusion makes independent leg ownership hard to certify without in-card markers. |
| D bottom-right | Original grounded stance | Mostly same as A, frame-to-frame clothing and body roughly maintained. |

## Geometric and identity QA

- **Arms:** all remain roughly shoulder high and naturally near-straight. Black wristband appears on forward (A/D) vs trailing (B/C) arm, **consistent with a possible physical arm swap**, but no tagged version of 44 confirms anatomical wrist ownership.
- **Legs:** no implausibly narrow ballerina thighs; reasonable femur/tibia length and shoes in all four panels. B front knee roughly right-angle bent, reducing resemblance to 5BX's straight-arm/straight-leg scissor motion.
- **Feet:** running shoes not pointed like ballet; both shoes airborne in B.
- **Age/body:** plausible soft middle-school boy; some arm/shoulder definition, mild face angle differences, no overt bodybuilding or leg-hair.
- **Perspective:** a shallow 20° profile rotation shows more of both shoulders and hips than V7, helpful for depth, but near/far assignment still cannot be proven unambiguously by clean stills alone.
- **Composition:** head in A/B is about 2–3% from top of frame, leaving inadequate room for a higher jump in video and risk of cropped head.
- **Track:** straight static boundary generally consistent. No measured optical registration test yet.
- **Motion:** no video; only four generated stills.

## Decision and next control

Keep V7 and V6 diagnostic as the lead-pose/limb-ownership authority. Do **not** feed 44 to Flow as a video anchor. Next scissor iteration should either retain V6 orange/teal anatomical wrist/ankle markers while transforming the viewpoint **or** use a real 30° angle still from the user's recorded exercise footage. Lock knee extension and camera headroom before band removal. Two checks must independently pass: physical near/far leg swap and readable scissor flight (no running stride reinterpretation).

## Local artifacts
- `44_C1_ScissorOblique20_Diagnostic_ONLY.png`
- `V7_vs_44_ScissorOblique_MobileCompare.jpg`
- `44_ExactPrompt.md`

## Direct mobile review

- [44 full 4-panel oblique diagnostic](https://drive.google.com/file/d/1uuTsZHyaITRF6enRLnzlBZ95uLUORvIH/view)
- [V7 side-view versus 44 oblique comparison](https://drive.google.com/file/d/10Op8hYF7tTKllft8T86G0bkjW5F_ud96/view)
