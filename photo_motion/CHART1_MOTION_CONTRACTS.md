# Chart 1: additional photographic movement contracts

**Development-only request specifications. No new photos or videos were generated or approved by adding these files.** The source wording is `data/5bx-charts.json` and `sprites/docs/CHARTS-2-6.md`. The common photographic identity, fixed-camera requirements and original experimental evidence remain in the existing QA documents. The original cartoon remains legacy and is not used here.

## Why four contracts were added

| Chart 1 exercise | Required physical sequence | Prior experiment that this corrects |
| --- | --- | --- |
| Ex1 toe touching | Arms up → simple forward fold **between feet** → rise arms up → modest backward reach → original arms-up stance | The 43R photo had natural reach but unresolved color/identity drift and no animation. Do not misapply the harder outside-shoe reach in Charts 3–6. |
| Ex2 partial sit-up | Supine, straight legs, arms at sides → lift head and shoulders **only high enough to see heels** → return supine | Earlier Flow 08 was a *full* sit-up and cannot certify Chart 1's smaller motion. |
| Ex3 alternate leg raise | Prone/rest → lift head and physically orange-tracked leg → rest → lift head and physically teal-tracked leg → rest | Previous unmarked cards repeated the same apparent physical leg; colored-band experiments helped track anatomy within generated stills, but did not prove source-video anatomical left/right. |
| Ex5 stationary low run | Alternating contact from persistent physical orange/teal feet with reciprocal arms, about four-inch low foot lifts; first/last contact pose matched | Existing Flow Video 20 lacked independently decoded frame-by-frame motion verification; a plausible thumbnail is not evidence of alternation. Avoid accidentally using Chart 4's waist-high-knee style. |

Existing Ex4 kneeling push-up and Ex5 *interspersed scissor jump* contracts remain in their original `photo_motion/specs/` files. **Ex5 deliberately has two movement contracts**: the running form cycle and separate scissor jump. The workout controls when to switch based on 5BX timing/step data; these video contracts do not encode the 75-step transition.

## Important timing interpretation

The 6-second running example has 17 contact samples at 0.375-second intervals, alternating physical orange/teal foot contact and ending where it began. This is a **repeatable illustration** (~8 returns of the same tracked foot per 6 seconds), *not* a fixed required cadence for every 5BX level. The source counts an anatomical **left** foot touching the ground. Orange is only a generated near/camera-side identifier, **not independently proven to be anatomical left**, so the sampled video must not be used as a validated left-step counter until the real demonstrator's limbs are tracked.

All timings are targets, not claims that a generator performed the specified motion. A passing JSON contract cannot validate foot sliding, actual support, head/shoulder clearance, camera movement, face continuity, or ghosts in an MP4; those remain video QA and human review tasks.

## Reproducing these checks

```bash
python3 -m photo_motion validate photo_motion/specs/*.json
python3 -m unittest discover -s photo_motion/tests -p 'test_*.py' -v
python3 -m photo_motion prompt photo_motion/specs/chart1-alternate-leg-raise.json
```

`photo_motion/extended_contract.py` contains the exercise-specific checks for these four types. It composes the original structural validator, and `photo_motion/__main__.py` routes them to the same CLI used by the earlier two contracts. The extended tests deliberately break leg tracking, heel support, natural toe-reach range, recovery and running-knee height and assert that these errors are rejected.

## Scope boundaries

- No automatic video model calls, generation credits, camera effects, crossfades or old cartoon assets.
- No new form approval. Source stills 43R, alternate-leg marked 04/clean 05–06, and Flow 20 remain candidates/diagnostics until actual-video review and Charles's decision.
- A single immutable chart-master photographic identity remains the source for the entire chart; do not chain pose identity from one generated video into another.
- If an existing visually plausible output conflicts with a strict movement gate, preserve both the failed result and explanation. Changing the gate requires source/form evidence, not just a model's ability to produce that result.
