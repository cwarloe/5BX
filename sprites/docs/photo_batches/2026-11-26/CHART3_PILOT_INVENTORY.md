# 5BX Chart 3 — photographic tests 26–29

2026-11-26 UTC. **Assistant-reviewed still photographs, not approved exercise animations.** Source of exercise truth: original 5BX Chart 3 text; source of character identity: approved v2 soft, fair 13–14-year-old boy with blue tank/charcoal shorts/gray-yellow shoes. All tests use a static track camera.

## Mobile gallery

- [**00-C3 — Chart 3 four-exercise mobile overview, including rejects**](https://drive.google.com/file/d/1eqWJDLNBOqAWZJ69cMcH7rjAG80xaN1R/view) — 279 KB.
- [**26B — hands-behind-head sit-up, CONDITIONAL DIAGNOSTIC**](https://drive.google.com/file/d/1Df-zN6-IvOQ_c8eaaX_NcalYq_-TJrEi/view). Hands stay behind head and torso reaches upright, but knees still flex about 40–50° versus booklet's *slightly*, and shoes nearly touch tile edge. Avoid video anchor until re-framed.
- [**27 — prone back extension, hands clasped behind back, STRONG CONDITIONAL**](https://drive.google.com/file/d/1XDzwrfTJmbAuY_dGSI8qL12yTsWDXk3q/view). Head/chest and both legs appear to rise modestly; strict profile obscures far-leg proof.
- [**28D — half-knee bends with raised heels, STRONG CONDITIONAL**](https://drive.google.com/file/d/1xjo-YCk631ZcHlhjqL8VJFTYHtGek1O1/view). Better roughly 110–120° included knee angle at A/D, both heels raised upright at C; exact angle/motion not yet independently measured.
- [**29E — chin-to-forehead push-up four-pose card, STRONG CONDITIONAL**](https://drive.google.com/file/d/1j6L2nOUHSxBZgYlbTOjrylG50vmTZCmq/view). Chin ahead of planted palm line, forehead behind, full-body shape proportional, widened B face/shoe clearance; actual contact and video continuity untested.
- [29C — breakthrough standalone forehead-pike pose authority, STRONG PROVISIONAL](https://drive.google.com/file/d/1EQ5jOF2Okxp_C2FnffekpmrHodRt13Ti/view) and [29D — first correct but tight-margin four-pose card](https://drive.google.com/file/d/10lyY-czvi_zPCmat_4M86IzzTKkFYPpI/view). Original 29/29B cards were **REJECTED**, retained in local experiments but not used for animation.

## QA and exact reproducibility

| ID | Preferred local file | Main pass | Remaining gate |
| --- | --- | --- | --- |
| 26B | `chart3_ex2/26B_C3_EX2_SlightKneeBend_35mm_CANDIDATE.png` | Hands behind head and grounded-looking feet all four phases; upright torso. | Knees overly bent, nearly clipped shoes, far heel/actual hands clasp obscured. Original 26 had worse ~90° bend. |
| 27 | `chart3_ex3/27_C3_EX3_BackExtension_HandsClasped_FourPhase_35mm_CANDIDATE.png` | Hands physically interlocked lumbar region; chest and apparently both straight legs modestly lift, pelvis grounded. | Side view overlaps far leg; motion unverified. |
| 28D | `chart3_jump/28D_C3_HalfKneeBends_110Knee_HeelRaise_PREFERRED_CANDIDATE.png` | Feet together, hands hips, improved bent/straightened position, BOTH heels off ground with forefeet planted (not a jump). | 2D knee angle approximate; four revisions required to separately solve heel rise and starting bend. |
| 29E | `chart3_ex4/29E_C3_ChinForehead_FourPhase_Headroom_CANDIDATE.png` | A/D plank, B chin LEFT/front of palms, C pike forehead RIGHT/behind palms, normal teen anatomy. | Near-contact, not literal verified touch; static card pixels aren't animation; some 10–25px contact registration differences, side angle hides far elbow. |

**Critical new lesson:** A marker is not automatically a pose controller. Test29B's bright stationary palm-line marker correctly appeared, yet the generator **still kept the forehead on the wrong side**. A real 1959 RCAF forehead-pike photograph plus a previously near-correct middle-school image, with v2 as separate appearance authority, generated 29C correct *standalone* head-behind-hands anatomy. That guided joint card 29D, then one careful margin edit 29E. Do not describe the method as a validated video or a guarantee in other models. The [independent Chart3 QA](CHART3_INDEPENDENT_QA.md) checked each outcome without claiming human approval.

**Exact prompts and rejects:** `chart3_ex2/26_C3_EX2_ExactPrompt.md`, `26B_SlightKneeBend_ExactEditPrompt.md` and their QA; `chart3_ex3/PROMPT_EXACT.md` / `QA_RESULT.md`; `chart3_jump/28_C3_HalfKneeBends_QA_RESULT.md` and each V1–V4 submitted prompt; `chart3_ex4/29_C3_ChinForehead_QA.md` and exact prompts for 29, 29B, 29C, 29D, 29E, with before/after QA. None of the four Chart3 exercises has a verified final Flow/Grok video in this pilot.
