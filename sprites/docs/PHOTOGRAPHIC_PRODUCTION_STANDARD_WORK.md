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

## Kanban-lite flow control — no new board to maintain

Treat the seven stations above as a **pull system**, with one tracked unit per
*chart/exercise and exact revision*. Do not assume that a collection of
experimental cards is an approved or active release job. The traveler may
summarize flow and blockers, but must **derive** them from the existing index,
inventories and versioned QA notes, rather than introducing another writable
status ledger or letting operators click an approval button.

| Traveler label | Evidence required | What it does **not** imply |
| --- | --- | --- |
| READY | A specific exercise, movement range, view, identity reference and intended output are recorded | Production has started |
| GENERATING | A numbered controlled output or generation attempt is linked with the exact submitted prompt | The anatomy has passed |
| TECHNICAL QC | An intake result on that exact asset is recorded | Form or identity approval |
| FORM QC | An independent anatomy/occlusion/movement assessment is recorded | Charles has approved the result |
| NEEDS EYES | A concrete, unresolved owner question and matching asset link exist | A human decision has already occurred |
| VIDEO QC | A **playable video** and a one-cycle motion/loop review are recorded | A still, card, or first frame is a full video |
| APPROVED | Named owner decision for the exact asset plus all required prior gates | Approval transfers to a later revision |
| HOLD / REWORK / REJECT | A named defect or stop condition exists | A worker can bypass the hold with a new internal PASS |
| UNKNOWN / EXPERIMENTAL | Evidence cannot establish a current release stage | It is safe to invent the missing stage |

These are **display concepts**, not a promise that all states can already be
resolved automatically. An absent, contradictory or stale source entry must
appear as `UNKNOWN` or an explicit hold until clarified. Show the output and
exact source link beside any state so the reviewer can audit its provenance.
If a later QA note rejects a version, do not display an older favorable note
as the current verdict. Never collapse an experiment into the production lane
solely because its exercise number appears in an inventory.

**Register before displaying:** some newer experiments have a complete QA
note but have not yet been linked from the canonical mobile index or a chart
inventory. For example, the Chart 2 prone back-extension
[`C2BE01` pilot](photo_batches/2026-11-26/chart2_prone_back_extension/C2BE01_QA_Lessons_and_VideoPrompt.md)
has direct still links and an explicit `CONDITIONAL STILL / NOT VIDEO-APPROVED`
finding, but is not yet indexed as a numbered current output there. The
producing agent should first add its exact revision, linked output type,
existing QA path and provisional verdict to the canonical index/inventory;
then regenerate the traveler. Until that happens, the traveler is a view of
**indexed evidence**, not a claim to inventory every new agent experiment.
Do not create a competing entry database or infer approval from its absence.

**Definition of Ready (release lane):** a chart/exercise identity; the
historically correct motion and safe allowed range; camera/near-far labels;
avatar identity master; an exact prompt or controlled generation plan; and a
clear named check that determines whether the output can advance. Otherwise
keep the job in discovery/experiment or on hold.

**Definition of Done (one exercise):** the exact revision and all inputs are
traceable; still anatomy and owner form judgment are recorded; a playable
one-cycle video has been checked throughout for limb lineage, movement,
appearance and seamless loop; the final video has an explicit named approval;
and the output/decision is linked from the existing QA record. None of these
criteria may be satisfied by an image-model assertion alone.

The initial release-lane WIP limit of **two exercises** is an *operating rule*,
not yet an automatically enforced lock. Pull the next ready exercise only
after a slot is freed; a worker can perform independent `EXPERIMENTAL`
research without claiming a third release slot. When blocked, display the
reason and next required action; count blocked release jobs against WIP rather
than hiding them. A small, output-first board should show both WIP and blocker
age **only if** dated evidence exists. No inferred dates, artificial deadlines,
or ceremonial daily stand-ups are needed. A short asynchronous change note
with the output and blocker is sufficient.

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

### Measurement contract (start with completeness, not a dashboard claim)

Capture these fields *when the event happens*, alongside the numbered
generation/QA entry already being written: exercise ID; version; UTC
timestamp; source/model; output link or hash; prompt/reference version;
attempt number for a named defect; defect code; independent technical and
form verdicts; measured credits; measured human touch minutes; and the exact
video-review and human-approval events when present. Preserve `unknown` for
cost, elapsed time, model details or a verdict that was not captured.
The folder name, batch date or Markdown document modification time is **not**
proof of when each stage began or ended. For instance, Flow test 20 has a
recorded 18-credit generation, but remains an unverified motion/loop; those
credits are a known pilot expense, not credits per approved video.

| Measure | Reliable calculation | Required caution |
| --- | --- | --- |
| First-pass yield | Number of first attempts passing the **defined same quality gate** / number of first attempts assessed at that gate | No estimate from the number of links, thumbnails or labels |
| Rework rate | Assessed attempts needing correction / assessed attempts | Separate a new defect from rework of the same defect |
| Repeated-defect count | Distinct defect identities that recur on a later revision | Compare a defined defect, not just generic `FORM` labels |
| Cycle time | Time between two timestamped process events on the **same** exercise/revision | Do not treat a Markdown page edit date as generation time |
| Human touch time | Sum of measured owner/worker hands-on minutes per accepted exercise | Missing minutes make the denominator incomplete |
| Credits per approved exercise | Measured credits across attributable attempts / explicitly approved exercises | Cannot be computed before genuine approvals; report total known pilot credits separately |

Show the observation count and data coverage beside each metric, and
distinguish a genuine measured zero from **not measurable**. In particular,
the current photographic pilot has no final human-approved exercise videos;
there is therefore no defensible cost-per-*approved*-exercise number yet.
Use the metrics to locate the current constraint, not to reward a model for
generating more candidates or passing weak checks.

### Learning cadence: one exercise, one short retrospective

After an exercise is released, or when a repeated defect is escalated, spend
approximately **5–10 minutes** reviewing its existing record. Answer four
questions: What output passed? Where was time or money spent? What specific
defect mechanism mattered? What single prevention test or standard-work change
should the *next exercise* verify? Record the decision **inside that exercise's
existing versioned QA note**, with the reference image/video and a named
owner. Mark the countermeasure `PROPOSED`, `TESTED`, or `CONFIRMED`; do not
claim an improvement until it survives the next relevant batch. A worked
mini-template and an illustrative high-knee example appear in
[the release retrospective guide](PHOTO_RELEASE_RETROSPECTIVE.md).

This gives us the useful part of Agile (small increments and feedback),
Kanban (explicit states, pull and WIP), and Lean Six Sigma (defect evidence,
constraint measures, verified countermeasures), **without** adding Scrum
ceremonies or requiring Charles to maintain a separate project board.

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
