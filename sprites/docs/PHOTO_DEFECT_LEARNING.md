# Photographic production: defect-to-prevention control

**Purpose:** Stop repeated expensive retries without turning every visual
experiment into a management ceremony. This is a lightweight Lean Six Sigma
*failure mode, containment, correction, verification* record. It does **not**
replace [the photographic standard work](PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md),
the owner handoff, the release retrospective, or the existing QA note.

## One source of truth

Add an optional, **single** `5bx-learning` JSON comment to the **existing**
photographic exercise QA Markdown note, alongside its regular prose and
`5bx-production` comment if present. The learning comment records repeatable
evidence about a *named defect*; it is **not** a new status ledger, active job,
Kanban board, review decision, or replacement for the historical input/output
evidence. Keep the numbered generations, exact submitted prompts, media links,
technical verdicts and human feedback in that same QA file as usual.

The check is deliberately backward compatible: a note with no learning comment
passes. The richer annotation becomes useful when a defect recurs or a new
countermeasure could prevent similar rework on another exercise.

## Copy-ready example, contained within the existing QA file

This example is an **illustrative, unconfirmed** scissor-jump defect record.
Do not paste it as factual history unless the named attempts and links have
been independently verified; correct its evidence links for the exact outputs.

```markdown
<!-- 5bx-learning
{
  "schema_version": 1,
  "defects": [
    {
      "id": "C1-E5-LIMB_ID-near-far-exchange",
      "code": "LIMB_ID",
      "symptom": "Opposing endpoints appear to show the same physical leading leg",
      "first_seen_revision": "V1",
      "first_seen_evidence": "sprites/docs/photo_batches/2026-11-26/scissor/QA.md",
      "risk": {
        "impact": "CRITICAL",
        "detection": "HUMAN_REVIEW",
        "consequence": "The exercise would demonstrate an incorrect physical leg exchange",
        "containment": "Reject the candidate as a production motion source"
      },
      "mechanism": {
        "confidence": "HYPOTHESIS",
        "finding": "A screen-left/right description may not preserve physical ankle ownership"
      },
      "corrections": [
        {
          "revision": "V2",
          "method": "PROMPT_ONLY",
          "changed_variable": "Near/far leg depth instruction",
          "outcome": "FAIL",
          "evidence": "sprites/docs/photo_batches/2026-11-26/scissor/QA.md"
        }
      ],
      "countermeasure": {
        "description": "Use markers that stay on the same physical ankles through all poses",
        "prevention_test": "Trace each marker through hip, knee, ankle, and shoe in every phase",
        "status": "PROPOSED"
      }
    }
  ]
}
-->
```

### Data rules

| Field | Meaning | Guardrail |
| --- | --- | --- |
| `id` | Stable *specific* defect identity (exercise + code + mechanism) | Same unresolved problem across revisions retains its original ID; a different failure gets a new ID. |
| `code` | One of `FORM`, `LIMB_ID`, `HAND`, `OCCLUSION`, `IDENTITY`, `FRAMING`, `CONTACT`, `LOOP`, `RECOVERY`, `SOURCE` | The broad code is **not** sufficient to establish recurrence. |
| `risk` | Qualitative effect, detection route, and immediate containment | `CRITICAL/HIGH/MEDIUM/LOW` are triage judgments, **not** invented numerical probabilities or RPN scores. |
| `mechanism` | Suspected mechanism, and its evidential status | `HYPOTHESIS` means not demonstrated; use `EVIDENCED` only with a supporting source locator. |
| `corrections` | Exact revision, one intended changed variable, method, outcome, evidence | A convincing-looking still or a model assertion cannot become a form PASS. An `INCONCLUSIVE` outcome is honest. |
| `escalation` | Why retries stopped, evidence, and qualitatively different next method | Required after two unsuccessful corrections **of the same still-unresolved defect**; another prose-only retry is not a different method. |
| `countermeasure` | Proposed prevention test and current validation state | Must be validated on a later relevant batch before it becomes confirmed standard work. |

The first appearance of a defect is recorded in `first_seen_revision`; entries
in `corrections` describe subsequent **correction attempts**, not the original
defective generation. If a fix produces an unrelated defect, give the new
problem its own ID. `PASS` on a correction describes that **specified test**
only; it does not mean the exercise, video, anatomy or release passed.

### Two failed corrections: change methods, not adjective counts

After two failed corrections of the *same unresolved defect*, add:

```json
"escalation": {
  "reason": "Two revisions failed to change the physical leg-exchange evidence",
  "alternative_method": "Tag specific physical ankles in the source reference",
  "evidence": "sprites/docs/photo_batches/2026-11-26/scissor/QA.md"
}
```

Stop additional prompt-only retries for **that defect**. Other experiments
and unrelated production can continue. The validator checks that a distinct
alternative is named; it cannot determine whether the alternative will work.

### Countermeasure maturity

1. `PROPOSED`: a plausible prevention rule exists, with a specific test. It is
   not standard work yet.
2. `TESTED`: a test has an explicit result and exact evidence. Success on the
   original repaired asset is *not* sufficient to claim generality.
3. `CONFIRMED`: a later **independent relevant batch** passed the prevention
   test. Supply `verification.result: PASS`, `verification.independent_batch`,
   and `verification.evidence`. This means the process-control hypothesis has
   repeat support, **not** human fitness-form approval.
4. `REJECTED`: the proposed control failed a verification test. Supply
   `verification.result: FAIL` and preserve why it failed.

Never declare an improvement because a prompt sounds better, because one image
looks attractive, or because an unreviewed video passed a codec inspection.
For safety-critical movement questions, the review/risk guide and release gate
remain authoritative; this record only supports engineering learning.

## Run the checker without modifying assets

```bash
python3 sprites/kit/photo_defect_learning.py --repo-root . --all
python3 sprites/kit/photo_defect_learning.py sprites/docs/photo_batches/2026-11-26/scissor/QA.md
python3 -m unittest sprites.tests.test_photo_defect_learning
```

The command scans existing photographic Markdown files, validates annotated
schema/locators, prints a small JSON summary, and exits nonzero on violations.
It does not make paid requests, open private media, delete or rewrite files,
make release decisions, or invent missing history. A missing annotation is not
evidence that defects have disappeared; report coverage separately.

## Keep 6S lean

- **Sort:** Preserve rejected generations as evidence, but label them as
  rejected rather than treating them as source masters.
- **Set in Order:** Link each precise defect ID and attempted correction from
  the already-authoritative QA note.
- **Shine:** Check malformed annotations and obsolete evidence references before
  they become production inputs; a path's syntax alone does not prove its file
  or linked video still exists.
- **Standardize:** Give recurrent failures the same ID, code and prevention test
  without conflating an arm defect with a leg defect.
- **Sustain:** Promote only next-batch-verified countermeasures into controlled
  regression checks; recheck after a provider/model change.
- **Safety:** Critical form/identity failures stop that candidate, not the
  entire 5BX line. No agent can make the owner's final `DONE` decision.

The goal is fewer **repeated causes**, not more QA paperwork. If an annotation
doesn't alter a test, a prompt standard, a containment action, or a useful
future decision, leave it in ordinary narrative rather than over-structuring.
