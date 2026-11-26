# 5BX evidence-only production metrics

This is a read-only measurement view on the **existing** photographic QA
records. It is not a second Kanban board, approval database, or video generator.
Do not add invented timestamps, model names, credits, form passes, or owner
approvals merely to make a dashboard look complete.

## Record what happened, when it happened

Append one optional machine-readable comment to the exercise's **existing
detailed QA note** when a measured attempt occurs:

```markdown
<!-- 5bx-metric id=C1-E5-video-v08 chart=1 exercise=5 stage=video gate=motion trial=2 quality=fail provider=Google_Flow model=Omni-1.2-Flash credits=18 start=2026-11-26T22:00:00Z end=2026-11-26T22:04:00Z manual_minutes=0 defect_code=LIMB_ID defect_id=C1-E5-near-far-switch -->
```

That line is **illustrative only**, not a real test or spend record. Producers
must replace it with observed values and keep the descriptive defect narrative,
prompt, actual media link/hash, and QA rationale in the same QA file.

Required fields: `id`, `chart` (1–6), `exercise` (1–5), `stage`, `trial` (positive
integer). An absent `quality` becomes `unknown`, never `pass`. Stage choices:
`brief`, `still`, `intake`, `form_qa`, `human_review`, `video`, `release`.

Optional fields:

| Field | When to record | Safeguard |
| --- | --- | --- |
| `gate` | The quality criterion assessed, e.g. `technical`, `motion`, `form`, `identity`, `loop`, `contact` | Compared separately from stage. If omitted, defaults to stage; do not combine unlike gates into one yield. |
| `quality` | `pass`, `fail`, `hold`, `unknown` | Internal gate verdict only, **never Charles's approval**. |
| `provider`, `model` | Exact displayed generation provider and model | Omit if unavailable; a guessed model is worse than unknown. Replace spaces with quoted values using shell-like syntax. |
| `credits` | Measured native provider credits consumed | `0` is measured zero; `unknown` is unmeasured. Credits across providers are incompatible units and never summed. |
| `cost_usd` | Actual dollar charge attributable to this attempt | Never convert Google Flow credits or prepaid balance into assumed USD cost. |
| `manual_minutes` | Timed human/worker touch minutes for this attempt | Missing is unknown, not free labor. |
| `start`, `end` | Actual timezone-aware ISO-8601 event times | Time may not be inferred from the directory name or file modification time. |
| `defect_code`, `defect_id` | A documented finding | Use existing standard-work codes. Keep a stable `defect_id` for the **same** unresolved root defect across revisions; see the existing QA narrative for evidence. |
| `reviewer` | Independent named form/motion reviewer | A `form` or `motion` gate may not claim `quality=pass` without a named reviewer. This field cannot itself prove genuine independence. |

`trial` counts attempts for the same exercise and stage. Each `(chart,
exercise, stage, gate, trial)` should be unique for an assessed quality gate.
Conflicting first-attempt numbers are excluded from the yield denominator
rather than guessing which result should win. An attempt may have multiple
separate assessed gates; identify them explicitly with `gate=`.
When that same attempt ID is assessed at multiple gates, identical recorded
credits/US-dollar costs are counted **once**. Conflicting charges or provider
attribution for the same ID are excluded with a warning; use a unique attempt
ID for genuinely distinct, separately billed operations.

## Current reporting interface

```bash
python3 sprites/kit/photo_metrics.py --repo-root . --out artifacts/production-metrics.json
python3 sprites/kit/photo_metrics.py --repo-root . --chart 1
```

The existing photographic traveler and GitHub Actions artifact consume this
same report. New read-only sections:

- `gate_breakdown`: first-pass yield and sample size at each distinct
  `stage/gate` combination.
- `provider_breakdown`: measured attempts, model coverage, provider-specific
  credits, measured dollar charges, and quality yield by gate.
- `defect_breakdown`: counts by existing defect code and exact repeated stable
  defect IDs. Repeated broad codes **do not** prove one defect recurred.
- `instrumentation`: coverage of recorded timestamps, credits, US-dollar
  charges, provider/model identity, explicit gates, stable defect IDs, and
  manual touch time.

Overall first-pass yield remains `null` when records contain incomparable
gates. Overall documented credits remain `null` if multiple providers have
credit measurements; use the individual provider totals instead. Measured
actual USD costs can be totaled, but represent a **known subset** while any
attempt lacks a cost field. Missing observations remain `null`, not zero.

`credits_per_approved_video` and `human_minutes_per_approval` remain `null`
until an exact, genuinely owner-accepted video has a complete attributable
history. An attractive still, technical PASS, or internal review-ready packet
cannot create an approved denominator.

## Lean feedback loop

1. Capture an attempt's actual prompt, provider/model, media hash and one
   metric marker in the existing QA record.
2. Capture a specific defect with its stable identity; do not infer that
   matching category names describe the same cause.
3. Fix one variable; compare against the original exact asset and check for
   collateral defects. After two failed corrections of the same defect, change
   approach rather than paying for a third prompt-only retry.
4. Run the same defined gate on the corrected version and preserve rejected
   evidence. Promote a successful preventive rule only after it is tested
   again on another relevant job.
5. Use the metrics as **constraint signals**, with documented sample coverage;
   do not infer statistical process control or a Six Sigma capability level
   from a handful of non-comparable experimental video generations.

No generation, status transition, media approval, or publication is performed
by the measurement CLI.
