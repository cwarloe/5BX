# Risk-based safety and independent-review control — photographic 5BX

**Design note; not a new approval ledger.** The existing exercise QA note,
`5bx-production` handoff, original booklet, photographic identity master,
canonical mobile index, and `photo_motion` contracts remain authoritative.
This document defines how to assess risk before spending credits, how to
calibrate independent visual reviews, and when to stop *one affected job*.
It does not certify any exercise, video, model, or person as safe.

## Failure-mode review (qualitative FMEA pilot)

Use severity and detectability to decide the inspection *before* generation.
Do not invent risk priority numbers, defect probabilities, sigma levels, or
control limits from the current small, selectively generated sample.

| Failure mode | Severity / detection concern | Prevention and detection | Containment |
| --- | --- | --- | --- |
| Wrong exercise range or an invented historical instruction | Critical; attractive movement hides wrong source | Pin the applicable Chart 1+ contract and original booklet movement; reject conflicting sources before generation | Hold the exercise and resolve the specific movement authority |
| Wrong physical leg/arm ownership through a crossing | Critical; a nice-looking pose can hide the error | Trace each near/far joint chain through **actual video**, use marked references as diagnostics but do not treat their colors as verified anatomical identity | Reject this revision; no clean/production inheritance from a marked still |
| Implausible support, contact, elbow or shoulder loading | Critical; automated pixel checks cannot determine safe form | Independently inspect hands, feet, knees, shoulder/elbow and actual motion at normal speed and sampled frames | Quarantine this candidate; escalate unanswerable source/safety ambiguity |
| Face, age, proportions or clothing change within a clip | High; frame-level changes can evade first-frame review | Immutable approved identity master; inspect sampled *and intermediate* frames against it, do not seed master from a previous generated clip | Rework specific identity defect; preserve prior successful geometry |
| Camera/loop or motion interpolates by fades, ghosts or teleports | High; a contact sheet cannot prove temporal continuity | Inspect decoded MP4, phase timing and seam; diagnose zero/duplicate frames separately from actual holds | Keep experimental; do not label video QC passed |
| Incorrect provenance or stale/fabricated QA evidence | High; false confidence and no reproducibility | Bind exact video SHA, model, submitted prompt and inspection evidence; reject malformed or contradictory current handoffs | `INVALID` or `BLOCKED`, never READY/DONE |
| Agent overspends, retries forever, exposes private raw footage | High; paid and privacy impacts persist beyond a run | Approved per-run/provider limits, two-attempt same-defect escalation, controlled private review archive and no secrets in logs | Stop affected provider/job; preserve unrelated work |

Risk-based inspection is **not** a claim that inspection can prove zero harm.
Publication of exercise demonstrations still depends on Charles's acceptance
of the exact reviewed video. AI reviewer text or a valid JSON field cannot
impersonate a human decision.

## Independent reviewer calibration

Independent form/motion review needs more than a second agent name. Until a
reviewer has demonstrated reliable judgments, use this rubric with known
rejected and conditional examples. Do not call earlier conditional cards
`ground truth`; they are training examples for recognizing failure modes.

For one candidate, record an explicit `PASS`, `FAIL`, or `UNKNOWN` for each:

1. Correct chart, exercise, movement amplitude and *temporal* phase order.
2. Exactly two physical legs and arms; trace hip→knee→foot and
   shoulder→elbow→wrist continuously, including occluded spans.
3. Foreground/background roles agree with the source contract; no screen-left
   relabeling, mirrored anatomy or color-marker swapping.
4. Required contact points and grounded/airborne transitions occur at the
   right phases, without impossible body loading.
5. No hyperextended limb, distorted torso, mature bodybuilder physique,
   ballet-like toe extension or unsafe artificial range.
6. Same approved photographic identity, clothing, scene and camera throughout.
7. No ghost limbs, fades, freeze-as-transition, instant teleport, unexplained
   cuts or camera reframing.
8. Complete start→movement→return cycle and independently inspected seam.
9. Output is the **actual decoded MP4** bound to the source and QA hashes,
   not a frame still, contact card or attractive browser preview.

The reviewer must name the *observed frames/timestamps and evidence* for each
`PASS`, and name the defect or limitation for `FAIL`/`UNKNOWN`. A missing
critical observation stays `UNKNOWN`, never silently becomes `PASS`.
For the initial pilot, have two independent reviews of several contrasting
known-defect clips (e.g. same-leg scissor, frozen running arm, false support,
drifting identity), then discuss disagreements to improve the rubric.
Report simple agreement and disagreements; do not infer statistically
validated reviewer accuracy from a handful of clips. If a reviewer repeatedly
misses a critical defect, it cannot be the sole non-owner form gate.

Reviewer independence recorded as a distinct name is a **minimum structural
guard**, not cryptographic identity verification. The production scanner
rejects case/spacing aliases of the named producer; it cannot prove who wrote
an attestation or whether the private MP4 has the claimed form. Where an
external human record is required, preserve the actual attributable decision
URL rather than authoring a plausible-looking assertion in JSON.

## Stop-the-line (jidoka) with bounded WIP

- **Immediate hold of the affected candidate** for form safety, source
  contradiction, untraceable limb identity, unapproved paid usage or private
  media access. The entire repository does not stop; unrelated experiments
  and the other registered WIP slot continue.
- **Two corrections of the same defect without a demonstrated remedy:** cease
  prompt-only retries; preserve both failures and change the test method.
  A new prompt or provider name does not erase the original defect lineage.
- **Review evidence contradiction:** an `INVALID` handoff still consumes its
  *declared* active WIP position until corrected. Bad metadata must not
  create a phantom free production slot.
- **READY_FOR_REVIEW** only for the exact playable, inspected, linked MP4,
  with named independent form/motion evidence. It is not an owner decision.
- **DONE** only after a separately attributable, timezone-stamped ACCEPT by
  Charles referring to the exact video hash. The scanner can validate the
  recorded fields but cannot authenticate remote actors or exercise form.

## Sustaining checks (digital 6S)

Before a provider/model change, replay an unchanged easy exercise, the
scissor-jump limb-continuity challenge, and a planted-contact push-up test.
Track input/contract hashes, provider/model, generation settings, actual
credits, phase defects and reviewer disagreements beside the **existing**
QA evidence. A reference whose identity or prompt changed is a **new test**,
not a comparable historical control.

Start with simple descriptive trends and per-defect recurrence, including
unknown observations. Add statistical process-control limits only after a
stable measurement definition and sufficient comparable sequential results.
Do not confuse fewer generated failures with improved quality when sampling
or the acceptance gate has changed.
