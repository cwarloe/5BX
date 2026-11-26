# 5BX photographic production — current standard work

**Scope:** photographic middle-school-character experiments, stills, short motion
tests and release decisions. The older cartoon sprite pipeline remains available
for regression; it is **not** the current creative target. The working image
references, exact submitted prompts, QA verdicts and Drive links already live
under `sprites/docs/photo_batches/2026-11-26/`. Keep them authoritative; do
not create a second spreadsheet, status ledger or separate review database.

## Single route through the line

| Station | Minimum evidence | Stop or advance |
| --- | --- | --- |
| 1. Brief | Chart/exercise, original 5BX movement, exact allowed range, fixed view and avatar identity master | Hold unclear exercise meaning or contradictory reference poses. |
| 2. Controlled still | One numbered job, exact prompt, identity and pose references, direct source output and revision | Reject wrong limbs, impossible anatomy, wrong age or an untraceable source. |
| 3. Automated intake | Image dimensions, frame completeness, source hash when available, count/spacing and format | Technical PASS is **not** a form approval. |
| 4. Independent form inspection | Anatomical left/right and near/far lineage, hands/fingers, occlusion, supports, contacts and historical movement | Preserve named reasons for HOLD/REJECT and do not silently promote earlier grades. |
| 5. Human exception review | Only the unresolved output, an enlarged before/after when useful, one concrete question | Charles's judgment is captured in the existing QA note; an assistant review remains provisional. |
| 6. One-cycle video | Complete movement, no fade/ghost, fixed camera, anatomy, stable identity and seamless start/end | A coherent contact card or first video frame does not prove this gate. |
| 7. Release and learn | Approved exact asset, input/version links, full playback review, lessons and next preventive test | No unreviewed media is described as instructional or released automatically. |

The [photographic review traveler](../README.md#review-grid--incoming-image-inspection)
is the **read-only viewing surface** for the same evidence. It shows current
refinements and an exception queue, and distinguishes a contact card from an
actual standalone still or video. When the owner gives feedback, record it in
the same versioned QA note; regenerating the traveler reflects that record.

## Two-attempt escalation rule — a pilot control, not a universal law

Track the **same unresolved defect**, not the number of variants overall.

1. **First correction:** change one variable in the prompt or source target;
   compare the exact changed region with the previous candidate.
2. **Second correction of that same defect:** isolate the anatomy with a
   reference crop, physical left/right markers, a clearer camera angle or a
   better movement diagram. Recheck the entire body for collateral changes.
3. **If it still fails:** stop prompt-only retries for that defect. Record
   `ESCALATE`, the two failed references, the suspected mechanism and a
   different test approach (physical reference, explicit geometry/occlusion,
   pose-controlled edit, or accept a safe natural range). Do not keep paying
   to restate the same prompt. A model change is an experiment, not a pass.

The 34B–34K high-knee sequence is a useful example: the apparent arm-length
problem was partly hand orientation and eventually the requirement to display
a hand that should be **occluded**. Fixing the viewpoint constraint was more
promising than repeatedly lengthening or rotating the far arm. Preserve the
successfully tracked leg exchange when repairing the hand/elbow. A variant
with a new defect begins a *new* defect investigation; it does not reset the
original unresolved defect or grant approval.

Use short defect codes consistently in the existing QA narrative: `FORM`,
`LIMB_ID`, `HAND`, `OCCLUSION`, `IDENTITY`, `FRAMING`, `CONTACT`, `LOOP`,
`RECOVERY`, `SOURCE`. Each code needs a concise finding and a candidate
version. `PASS` from an automated image check never means owner-approved form.

## Limit active release work, and measure the constraint

- Keep **at most two release-validation exercises active** initially: Chart 1
  scissor jump and kneeling push-up. Independent photographic exploration may
  continue elsewhere, but label it `EXPERIMENTAL` until it enters this line.
- Finish one scissor-jump cycle from the photographic master, verify physical
  leg ownership, trace every key frame, play on a phone, then obtain a named
  human form verdict. Reuse the tested route for the other four Chart 1 moves.
- The production agent collects attempted generations, defect code, exact
  tool/model, measured credits if available, manual touch minutes, result and
  output hash/URL in the **existing** experiment record. Use `unknown` where a
  provider does not expose a cost or duration; do not invent estimates.
- Review each small batch for first-pass yield, retake yield, credits per
  accepted exercise, human minutes per approval, repeated defect count and
  time from changed asset to tested one-cycle preview. Treat the current
  numbers as exploratory until the sample and grading rule are stable.

## Output and decision vocabulary

- **CONTACT CARD:** multiple phase images in one file, even if the whole file
  is advertised as *full resolution*. Not an independent high-resolution frame.
- **STANDALONE STILL:** a single native-resolution camera frame. A crop of a
  small contact-card panel is not new source detail.
- **VIDEO:** a playable motion clip, not a card or an unverified model preview.
- **COMPARISON / DIAGNOSTIC:** evidence for an edit or identity test, never an
  automatically selected production master.
- **CANDIDATE / NEEDS EYES:** can be shown for review, not used for release.
- **HOLD / REJECT / SUPERSEDED:** preserved for lessons; not passed downstream.
- **APPROVED:** only an explicit named human form verdict on that exact
  revision after the relevant still/video gates.

The traveler is intentionally read-only and does not offer a fake Approve
button. Its exception queue is an inbox of **questions**, not a substitute for
recording the actual answer and exact asset identity in source-controlled QA.

## Concurrency and ownership

- Image-generation agents own their outputs, exact prompts and anatomy QA.
- The traveler/process work owns the viewing logic, tests and standard work.
- Do not rewrite or replace a concurrent agent's image, Drive file or active
  draft; review with the current remote repository before merging.
- Changes to the release definition, exercise meaning or avatar master still
  require Charles's explicit judgment. Existing approved outputs remain frozen.
