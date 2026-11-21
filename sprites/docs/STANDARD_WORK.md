# 5BX video production — one-page standard work

**Working unit:** one exercise movement × one avatar, not one chart level. The 12
levels of a chart reuse its exercise artwork; `data/5bx-charts.json` supplies
the counts and timing. Keep movement definitions independent of appearance so
another avatar can reuse the specifications and renderer (not necessarily the
same pose pixels).

| Station | Do this | Pass/hold decision |
|---|---|---|
| 1. Brief | Check booklet text, `data/5bx-charts.json`, reference, camera, pose order and common wrong forms. Edit the canonical `prompts/strips.json`, not an old generated prompt. | **Hold** if exercise meaning or reference is ambiguous. |
| 2. Generate | Pin the character reference; make a *small* named set of poses/takes. Save raw and rejected art in the Drive archive from `ART.md`, not Git. | Keep the original source and the reason for each rejection. |
| 3. Mechanical QC | Inspect pose count, separation, transparency/key, floor contacts and jump/lift. Existing `qc-line/pipeline/sprite.py qc` can help; it is not anatomy review. | **Gate A:** fix a failed sheet before cutting or animating. |
| 4. Human form review | Compare *every pose* with the booklet and movement specification. Grade the exact asset in the existing sprite library. | **Gate B:** named human reviewer, form grade **4 or 5**, selected revision recorded. “Chosen” alone is insufficient. |
| 5. Cut and animate | Key and cut transparent sprites; use the primary `sprites/kit/build.py` to preview **only that exercise/cycle** at its actual timing. | **Hold** for sliding, ghosting, limb changes, cropping or cadence errors. |
| 6. Assemble | Reuse approved strips, timing, theme and avatar settings for chart/level/format variants. Full render writes its input-hash build record. | Run `release-check` before a candidate is called ready for publication. |
| 7. Publish and learn | Watch the **full** video (including on a phone), confirm exercise labels, duration and movement, then publish. Log the defect type and one correction. | **Gate C:** final human playback and decode check; not covered by the artwork check alone. |

## Three practical commands

From the repo root:

```bash
python3 sprites/kit/line.py status                  # mapping and review backlog
python3 sprites/kit/line.py check                   # structural mistakes; safe on a clean clone
python3 sprites/kit/line.py release-check --chart 2 # strict art gate; needs restored source sheets
```

The final command **holds** if any chart slot is unmapped, there is not exactly
one chosen asset, its actual sheet bytes differ from the library's recorded
hash, its source sheet is absent, or its named human form grade is below 4.
It verifies **artwork readiness only**, not automated mechanical-QC evidence or
the final rendered video. The normal `check` deliberately allows unfinished
charts and missing Drive art as warnings.

To record a genuine human form approval (after inspection), use the existing
library rather than editing review flags by hand:

```bash
python3 sprites/kit/library.py grade ASSET_ID --form 5 --by Charles --expert --notes "matches booklet and all poses"
python3 sprites/kit/library.py choose ASSET_ID
```

Copy that exact chosen sheet into `sprites/sheets/`, point its `file` in
`sprites/config/strips.json` at it, and run a single-exercise `--preview`
before building a whole chart. A new version needs a new review.

## Current audit and next constraint (2026-11-21)

- **Existing:** prompt generation, two overlapping sprite/QC implementations,
  pose extraction, incremental preview/full render, and build input records.
  `sprites/kit/` is the primary production path; `video/chart.py` is older.
- **Backlog:** 32/36 chart slots mapped, four unmapped; 29 registered strip
  types. No chosen asset has a recorded passing named human form review yet.
  Chart 1 scissor jumps are **held for redesign** pending additional references.
- **Next controlled experiment:** compare one approved movement/cycle using
  Sprite Boy and one second approved avatar. Reuse the same movement spec,
  timing and scene. Measure how much pose work actually must be repeated.
- **Limit waste:** no new tracker, bulk retakes, new renderer or paid model
  tests until a one-exercise pilot shows that they solve the bottleneck.
  Work on at most two pilot exercises at once. For each batch record just
  **first-pass approvals / new attempts**, **manual minutes per approved
  exercise**, and the **recurring defect reason** in the existing lessons log.

For deeper rationale and future work, see
[`PRODUCTION_CONTROL_PLAN.md`](PRODUCTION_CONTROL_PLAN.md) and
[`specs/sprite-production-line/tasks.md`](../../specs/sprite-production-line/tasks.md).
