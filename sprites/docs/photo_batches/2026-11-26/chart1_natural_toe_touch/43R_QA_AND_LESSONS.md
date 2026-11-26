# 43 / 43R — Chart 1 Ex1 toe-touch, natural-range pilot

**Status: 43 REJECT FOR VIDEO ANCHOR (overhead crop margin); 43R CONDITIONAL STILL REVIEW.** Not human-accepted and not video tested.

## Inputs and intent

- Character identity: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`.
- Earlier Chart 1 four-panel pose sheet: `artifacts/parallel_batch_20261126/toe_touch/C1_EX1_toetouch_backstretch_4phase_v1_REVIEW.png`.
- Best overhead start frame `artifacts/parallel_batch_20261126/toe_touch/03_CANDIDATE__Chart1_ToeTouch_ArmsUpStart_Headroom35mm.png`.
- User's principle: Do not elongate arms or grant 99th-percentile flexibility merely to touch six inches beyond the outer foot. A realistic teenager stopping near the lateral shoe is preferable.

## Frames and motion intent

| Panel | Intended phase | Observed |
|---|---|---|
| Top left | Arms straight overhead, comfortable stretch | 43R passes full hands/headroom; top margin ~11% of cell. |
| Top right | Partial forward hip hinge, downward arms | Hands near kneecaps, not as low as desired mid-shin but plausible intermediate. |
| Bottom left | Deepest realistic reach | Fingers stop next to lateral shoes; head down; knees mildly bent; hands not stretched 6 inches past shoe. **Promising natural range.** |
| Bottom right | Return upright, arms passing shoulder height | Upright with straight arms forward; plausible recovery but standing more erect than strict halfway. |

## Independent QA gates

| Gate | Verdict | Evidence/caveat |
|---|---|---|
| Full 4-phase in one frame | PASS | Four sequential poses, white gutters, same outdoor track/field/treeline. |
| Anatomical reach | PASS (visual) | Arms retain typical length; no fingertip-floor miracle or outside-foot extension. |
| Legs / shoes | PASS (visual) | Both feet stay on track, similar wide stance, realistic knee flex. |
| Headroom | 43 FAIL; 43R PASS | First top-left hands nearly touch upper edge; edit adds clear space (~11%). |
| Body proportions | CONDITIONAL | Soft middle-school physique preserved; some face/head-size drift across quadrants, minor. |
| Wardrobe luminance | **COLOR DRIFT REVIEW** | Independent optical check found largest blue-tank median RGB varies: A (60,142,227); B (28,83,140); C (92,166,242); D (57,133,214). B substantially darker; could be pose-specific shading but must be evaluated before final use. |
| Track camera registration | PASS (limited) | Independent optical check found track boundary spread 0 px across quadrants. |
| Orientation | PASS | Nearly front-on, consistent with prior finding that this movement is clearest almost frontal. |
| Movement/time | NOT TESTED | Still contact card; no Flow/Grok video or verified frame interpolation. |
| 5BX precision | NOT CERTIFIED | A safe, plausible adapted demonstration. Literal historical six-inch outside-foot target intentionally relaxed; not strict proof of exact official form. |

## Repeatable lesson

A strict numeric extremity target can create counterfeit anatomy. In prompting, replace it with: **'reach toward the outer shoe; stop when normal hamstring flexibility and unchanged arm length permit.'** Preserve upper-body and lower-body geometry, not fingertip goal achievement. Make wide headroom a first-generation constraint: contact sheets often crop the overhead hands even when a separate start-frame reference has enough headroom. Favor 8–12% vertical margin for video input.

**Do not overlook photometric drift when poses pass.** Darker fabric in a bent-forward tile may be shadow, but it must be compared under stable illumination or corrected before producing a four-frame video anchor.

## Files

- `43_C1_ToeTouch_NaturalReach_V1_HEADROOM_HOLD.png`
- `43R_C1_ToeTouch_NaturalReach_Headroom_CONDITIONAL.png`
- `43_vs_43R_NaturalToeReach_MobileCompare.jpg`
- `43R_ExactPrompt.md`

## Direct mobile review

- [43R full four-panel card](https://drive.google.com/file/d/1nqTbpFMqRddF0UhZY7vQN0u9Mh_E8dhu/view)
- [43 vs 43R before-and-after](https://drive.google.com/file/d/12Fw76nJg4NW9V2Ba4w45B_nvLf0mHGA-/view)
