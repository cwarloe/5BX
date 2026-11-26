# Photographic 5BX — release and defect retrospective

**Purpose:** close the loop on **one exercise or escalated defect** in about
5–10 minutes. This is a copy-ready *section template*, **not** a new log,
approval system, tracker or separate file required for every exercise.
Put the completed section in the **existing versioned exercise/batch QA
record** under `photo_batches/2026-11-26/`, then link that source from the
mobile review index when it changes the current outcome. The read-only
traveler should reflect the source record automatically.

For recurring defects and proposed prevention controls, the optional
[`5bx-learning` in-note comment](PHOTO_DEFECT_LEARNING.md) can be validated
without creating a second tracking system or inferring exercise approval.

## Copy into the existing QA note

```markdown
### Release / defect retrospective — Chart __ Exercise __ / revision __

- Outcome: RELEASED / HOLD / REJECT / ESCALATE / EXPERIMENTAL
- Evidence: [exact still/card](URL), [actual video](URL or not available), [QA](path)
- Owner's form verdict: named reviewer + timestamp + exact revision, or **not obtained**
- Gate evidence: technical __; independent form __; full video/loop __
- Constraint / most costly delay: observed stage and reason, or **unknown**
- Attempts assessed: __ first-pass / __ total; named recurring defect(s): __
- Measured credits: __ or **unknown**; human touch minutes: __ or **unknown**
- Root cause / lesson (evidence, not guess): __
- One preventive countermeasure: __
- Verification at next relevant batch: test __; owner __; status PROPOSED
- Follow-up finding: TESTED / CONFIRMED / REJECTED with exact output link, or pending
```

Do not write `APPROVED` when only a contact card or a model-produced
technical PASS exists. The final owner approval of exact video revision is
an additional independent release decision. If timestamps, credit totals or
touch minutes were not actually measured, enter `unknown`, not a plausible
estimate. First-pass comparisons require the **same** defined quality gate.

## Illustrative example — Chart 4 high-knee 34B–34K (NOT a release)

- **Outcome:** `EXPERIMENTAL / NEEDS EYES`; the 34K card is a review
  candidate, with no approved video.
- **Observed defect:** the far/background upper arm looked implausibly long.
  Earlier hand edits introduced or preserved fist/hand orientation problems.
- **Specific mechanism:** requiring the far hand to remain visible in a
  three-quarter view contradicted natural occlusion. The later 34J–34K tests
  hid the far wrist/hand behind the torso and reduced the far elbow contour.
- **Proposed prevention test:** before requesting more edits to a far limb,
  label foreground/background ownership and decide which segments should
  be **hidden** at the chosen camera angle. Compare the changed crop, but
  recheck that leg exchange and near-arm swing remain intact.
- **Verification:** compare 34K against the preceding revision and the
  camera-correct physical reference at the next form review. Status remains
  `PROPOSED`, not `CONFIRMED`, until reviewed.
- **Measurement:** repeat attempts exist, but source records do not establish
  the full measured time and credits needed to calculate cycle time or cost
  per approved exercise. Report those as `unknown`.

References: [current mobile review index](photo_batches/2026-11-26/MOBILE_REVIEW_INDEX.md)
and [production standard work](PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md).

## What deserves a permanent process change?

Promote a countermeasure into standard work only when the next relevant
exercise or batch shows that it prevented the **same named defect**, with
evidence. If the result is mixed, preserve the test outcome and iterate.
This prevents rediscovering an error while avoiding a growing library of
unverified rules.
