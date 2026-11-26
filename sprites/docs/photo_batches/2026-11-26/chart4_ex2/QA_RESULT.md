# ID30 — 5BX Chart 4 Exercise 2 photographic contact sheet

**Status: CONDITIONAL KEEP — good exercise mechanics, useful test candidate; not a finalized animation reference.**

## Source of truth

Booklet `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`, Chart 4 Exercise 2: “Back lying, legs straight, feet together, arms straight overhead. Sit up and touch the toes keeping the arms and legs straight. Use chair to hook feet under only if necessary.”

## Generated artifact

- `30_C4_Ex2_ToeTouchSitup_FourPhase_35mm_CANDIDATE.png`, 1199 × 1312 pixels, PNG.
- One 2×2 card; top-left supine start, top-right 45-degree rise, bottom-left toe reach, bottom-right return/recline.
- Prompt and ordered source references recorded verbatim in `30_C4_Ex2_ExactPrompt.md`.

## Visual QA

| Check | Result | Notes |
| --- | --- | --- |
| Character continuity | PASS | Same face, hair, age band, blue shirt, charcoal shorts, dark socks, gray/yellow trainers across the four frames. |
| Middle-school anatomy | PASS | Ordinary soft 13–14-year-old proportions, no added abs or muscular bulk, fair skin. |
| No artificial hyperflexibility | PASS | Straight-leg seated toe-reach achieved without visibly growing arms or torso or contorting shoulders. |
| Straight legs | PASS | Both legs appear straight in all four panels. |
| Straight arms | PASS WITH MINOR CAVEAT | Arms extended in all four panels; bottom-left may show a very mild natural elbow softening, acceptable. |
| Feet / heel anchoring | PASS WITH MINOR CAVEAT | Footwear stays close to the track at each phase; toe tips angle upward naturally. Mid-rise image has slightly ambiguous sole contact because feet overlap at side angle, but no large floating heels. |
| 35mm photographic quality | PASS | Realistic daylight track/field and consistent static framing; enough edge safety margin for whole body. |
| Exact booklet top-end | PASS | Seated reaching toward the toes, realistic flexibility. |
| Four sequential phases | PASS | Supine → sit-up arc → toe touch → recline; last panel shows a near-supine return, not flat-rest start. |
| Extra limbs / anatomical artifacts | PASS | No clear duplicate hands/legs, no major malformed limbs or severe proportion drift. |

## Remaining caution

1. This is a four-panel card, not four independently aligned footage keyframes. Future animation should avoid asking a video engine to interpolate strictly through all four as unordered input, as it can reverse movement.
2. The exact side-on angle makes the foot silhouettes overlap slightly. A future separate-frame test could use around 20° oblique angle and ensure both heels remain visibly anchored during the upward arc.
3. Overall visual resolution is good for testing and mobile review, but single-panel crops are limited by the 1199-pixel card width.

**Recommendation:** Keep ID30 as a successful controlled pose-generation test. Do not claim a production-quality video without movement validation.
