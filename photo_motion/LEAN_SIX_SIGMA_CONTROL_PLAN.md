# Photographic 5BX: Lean 6S and Six Sigma control plan

**Status:** Engineering design / candidate standard work. No change to exercise form,
owner approval, provider spending authority, or the active Google Flow workstream.

The operating objective is a dependable **cost per owner-accepted exercise**, not
the highest volume of generated images. The plant produces one correctly
demonstrated, inspectable, reproducible photographic movement at a time and
reuses proven controls across Chart 1 before expanding to other charts.

## Authority and single sources of truth

| Concern | Existing authority | Evidence it does **not** provide |
| --- | --- | --- |
| Historical movement | Original 5BX booklet, `data/5bx-charts.json`, `photo_motion/specs/*.json` | A generator correctly executed the motion |
| Character | Approved original photographic identity master and its hash | A later model output retained that identity |
| Current production state | Current detailed photographic QA note's `5bx-production` marker, indexed by the existing traveler | A real person has approved a candidate merely because CI passes |
| Model/input lineage | Exact submitted prompt, ordered input hashes, model and settings in `photo_motion.experiments` | Deterministic regeneration of stochastic model output |
| Paid generation authority | Provider-specific, immutable budget policy and paid-attempt reservation | Live provider quota, a permission to spend with another provider, or a provider bill |
| Output evidence | Direct private playable MP4, verified SHA-256, media inspection and independent human form/motion review | Automatic owner acceptance or publication |

Do **not** introduce a second project board, mutable approval ledger, separate
metrics database, or an asset folder that competes with the existing Drive
archive and photographic review index. Derived reports are disposable views.
The consumer Grok/Flow interfaces and their subscriptions do not imply
unattended API access or interchangeable API credits.

## Digital 6S: the production workcell

| S | Prevention control | Automatically verifiable signal |
| --- | --- | --- |
| **Sort** | Mark reference masters, diagnostic tags, provisional poses, failed experiments, and reviewable videos as different classes; never silently promote a rejected card | Every input has an explicit role, hash, status and exercise binding |
| **Set in order** | Keep exactly one versioned motion contract, detailed current QA marker and linked mobile review index per active exercise; stable revision IDs | No unresolved duplicate active marker or broken referenced artifact |
| **Shine** | Run repeatable intake, stale/missing metadata and broken-link diagnostics; preserve rejects instead of deleting provenance | No undecodable media, unresolved hashes, orphan receipts or unregistered review link |
| **Standardize** | Pin input order, camera, physical near/far lineage, output duration, form thresholds and machine-readable preflight | Contract and request schema validation passes before credit reservation |
| **Sustain** | Turn each confirmed recurring defect into a guard/test, and requalify after provider/model/prompt changes | Regression/canary results with exact baseline and candidate digests |
| **Safety** | Block dangerous form, missing physical lineage, privacy leakage, unapproved spend and unsupported owner approvals | Five named QA checks before `READY_FOR_REVIEW`; owner-only exact-video acceptance for `DONE` |

**Separation of duties:** producing agents may generate, repair and inspect;
independent reviewers inspect form and motion; the owner alone chooses whether
to use the exact version. Automated checks must never report `FORM_PASS` on
the strength of a visually appealing first frame or text-only contract.

## Pull flow, quality at source and stop-the-line

1. **READY / first-article preflight (free):** Verify historical exercise,
   versioned motion contract, approved identity anchor, ordered input assets,
   locally verified source hashes or clear evidence limitations, exact proposed
   settings, available provider-specific budget and a named QA gate. Record
   `HOLD` with a specific reason if an input is unqualified. No generation yet.
2. **RESERVED:** Record the *actually submitted* prompt and immutable attempt
   fingerprint, reserve only this provider's authorized expected credits.
   Repeated identical calls are idempotent; true retries use new attempt keys.
   An estimated cost is not an actual charge. No extra generation can proceed
   while a spending constraint is breached.
3. **GENERATING:** Invoke an explicitly configured provider adapter only when
   the separate provider credential and approved cap exist. Persist provider
   run ID and actual charges; unreported charges remain pending, **not zero**.
4. **TECHNICAL QC:** Verify actual playable MP4 bytes, SHA-256, codec, duration,
   frame extraction, output locator, source provenance and start/end evidence.
   Any source/codec/geometry mismatch is `REWORK` or `HOLD`, not `PASS`.
5. **FORM + MOTION QC:** Independently trace physical limbs through *all*
   relevant phases; check supports/contact, exercise range, uninterrupted
   airborne transitions when required, camera and identity, then full loop.
   Failures get a named defect and attributed revision. An automated similarity
   score alone is not a safety certification.
6. **READY_FOR_REVIEW:** Only an exact MP4 with inspection hashes, full QA
   evidence, linked existing mobile inventory and a concise owner question
   enters the owner buffer. This frees an active agent-production slot.
7. **DONE / release decision:** Only Charles's explicit decision for the same
   MP4 SHA moves that revision to `DONE`. No implied acceptance, publishing,
   or automatic cross-revision inheritance.

Keep **at most two active release exercises**. A critical defect stops *that
unit* (and optionally a suspect model/provider), not unrelated ready work.
Use an Andon-style blocker only for a genuine access, safety, spending or
requirements decision; an ordinary failed generation stays inside agent-owned
rework. This avoids making the owner's inbox a production station.

## Risk-first FMEA-lite and concrete error-proofing

Treat these as preliminary **ordinal priorities**, not calculated RPNs or
statistical failure probabilities. Re-rank after measured production evidence.

| Failure mode | Initial priority | Prevention / detection / containment |
| --- | --- | --- |
| A scissor jump repeats one anatomical lead leg or teleports a foot marker | Critical | Explicit physical near/far chains in spec; framewise lineage check; preserve tagged reference; quarantine if untraceable |
| Model makes an attractive but historically incorrect exercise | Critical | Independent booklet-to-motion form check separate from photographic quality; stop affected unit |
| Identity anchor is replaced by a descendant AI frame | High | Pin approved original image digest; reject lineage substitution and changed clothes/face/body without owner direction |
| One airborne phase is omitted or a push-up contact point drifts | High | Exercise-specific support and phase invariants; sample full video, not just start/end |
| A change in model, prompt, source order or provider degrades output | High | Canonical generation manifest; golden canaries and explicit requalification rather than inherited PASS |
| Agent spends repeatedly on an ineffective correction | High | Two-attempt same-defect escalation; change evidence or method, not merely rephrase prompt |
| Credits are underquoted, overcharged, or settled as fake zero | High | Provider-specific reservations, actual-charge receipts, immutable unresolved states; manual spend approval boundary |
| Output has no independent source hash, is not playable, or lacks owner link | High | Fail-closed review packet/QA validator and direct private MP4 link |
| Agent fabricates a review verdict or owner decision | Critical | Owner acceptance bound to exact SHA and external genuine decision evidence; separate agent-reviewed and owner-approved states |

## Shift/drift control: qualify the process before trusting the batch

Build a **small, immutable golden-test pack** with three deliberately different
failure surfaces, using previously verified source/contract digests:

1. Chart 1 scissor jump: physical near/far limb exchange, **two** distinct
   airborne exchanges, extended opposing arms and return to the same contacts.
2. Chart 1 kneeling push-up: planted knees and palms, chest-floor low point,
   full down/up recovery and contact stability.
3. Chart 1 toe touch: stable face/outfit, camera framing, realistic ordinary
   flexibility and complete endpoint recovery.

A change to provider/model/version, generation settings, reference hash,
prompt version or inspection thresholds should produce a **requalification
flag** before new high-volume paid generation. Where the supplier cannot pin
model versions, record the exact displayed name, generation date and settings,
and treat silent changes as a known uncertainty. Compare model and input
**fingerprints**, then inspect actual image/video content independently.

Canary comparison is an *engineering signal*, not a substitute for inspecting
a fresh actual clip. A failed critical form canary quarantines that candidate
and blocks promotion; a benign text/model metadata change requests review,
not automatic `FORM_FAIL` or false `FORM_PASS`. Requalifying one provider must
not overwrite the baseline or approval state of a different provider.

## Closed-loop corrective action, not endless prompt retries

Track a defect by `(exercise, revision lineage, mechanism, affected body part)`.
Codes such as `LIMB_ID`, `FORM`, `CONTACT`, `OCCLUSION`, `IDENTITY`, `LOOP`,
`SOURCE` and `COST` name symptoms; the QA note also records a suspected cause.

- First correction: isolate and change **one** causal variable; check adjacent
  geometry for collateral drift and retain a before/after comparison.
- Second correction of the *same* defect: require a stronger input such as
  physical color marking, source-frame tracing, a camera change or a controlled
  reference crop. Do not reset the attempt count by renaming the version.
- Still failing: mark `ESCALATE` within the same QA note; propose a different
  method or an owner-only historical-form question if truly unresolved.
- When a correction succeeds: state one explicit *countermeasure*, link its
  test, and mark `PROPOSED`, `TESTED` or `CONFIRMED`. A change is only confirmed
  after it passes an independent applicable subsequent exercise or canary.

Do not confuse countermeasure verification with a retrospective story. Failed
examples are permanent regression fixtures where they can be shared safely.

## Measurement integrity and iteration cadence

Instrument at the point of production, inside existing timestamped QA notes
and immutable cost/asset receipts. Required fields: chart/exercise, revision,
attempt identity, UTC event time, provider/model, prompt/source digests,
defect code and root-cause note, measured charge, human touch minutes, gate
verdict, output SHA/link and next action. Mark missing evidence **unknown**,
not zero. Existing `photo_metrics.py` may derive read-only views.

Initial scorecard:

1. **First-pass yield at an explicitly named gate**, with denominator/coverage.
2. **Rework per assessed candidate** and recurrence of *the same defect*.
3. **Known spent credits per owner-accepted video** (not computable before
   accepted outputs; report pilot costs separately until then).
4. **Measured human intervention minutes** per accepted video.
5. **Critical defect escapes** past internal QA and cost/time to recover.

Do not draw control limits from sparse, non-stationary experiments or treat
different exercise types as one statistical process. Begin with timestamped
run charts and defect Pareto counts; use formal SPC only after a consistent
measurement system and an adequate sequential baseline. Periodically sample
independent reviewer agreement before trusting yield comparisons.

### Measurement-system check before optimizing a model

Quality scoring is itself a process that can drift. Take a small, deliberately
mixed sample of accepted-looking, borderline and known-rejected clips; have
two independent reviewers inspect the **same frame-identified evidence** using
the same movement-specific rubric, preferably without knowing the provider.
Record where they agree or disagree on physical limb ownership, contact,
identity and loop. An unresolved disagreement is `NOT_ESTABLISHED`, not a
majority-vote safety PASS. Recalibrate the rubric against authoritative source
material before trusting provider rankings or process yield. Never make the
owner an obligatory reviewer of early experimental drafts.

### Fair supplier experiments: do not optimize price per attractive clip

When the current Flow test is finished and an independently approved provider
budget exists, qualify alternatives in matched blocks:

1. **Use the same movement contracts and original identity authority** for
   each supplier. Translate the contract into provider-native language where
   necessary, but record the exact submitted prompt and settings separately.
2. **Block by exercise difficulty:** simple toe touch, planted-contact kneeling
   push-up and two-exchange scissor jump are separate strata. Do not compare a
   provider doing only easy exercises against one doing scissor jumps.
3. **Repeat and randomize** the order where practical. One beautiful output
   cannot estimate first-pass yield from a stochastic generator. Preserve all
   attempts, including failures and actual billed credits.
4. **Score blinded to provider where practical** with the same rubric and
   independent form/identity/loop gates, not the supplier's self-assessment.
5. **Compare observed cost per qualified output, human intervention and
   critical escape rate**, not published price per video second. Mark unknown
   costs and unresolved form judgments explicitly; a sample too small for a
   rate is a pilot observation, not a quality-capability claim.

This is a compact design-of-experiments pilot rather than a prematurely formal
Six Sigma capability study. The goal is to establish which *operating route*
is stable enough to scale before spending on unattended bulk generation.

**Cadence:** Each new accepted exercise or escalated repeated defect triggers
a 5–10 minute asynchronous retrospective in its existing QA note: what passed,
where waste occurred, probable mechanism, one countermeasure, and a named
next verification. No Scrum ceremonies or compulsory owner stand-ups.

## Integration order and constraints

1. Introduce fail-closed preflight and evidence-completeness checks before
   any new provider adapter can reserve paid credits.
2. Introduce digest-driven canary requalification and a small independent
   reviewer rubric; retain current photographic masters and legacy rejects.
3. Convert known recurring defects into tests/operating constraints rather
   than repeated exploratory prompts.
4. Derive source-backed cost, yield and cycle-time metrics from existing
   records; no second reporting database.
5. Only after a provider, actual credentials, explicit spend cap, private
   asset archive and supported unattended API are in place should issue #47's
   production runner submit paid jobs. Its dry-run mode must work without any
   credentials or network access.

No change here authorizes using third-party services, paying for API calls,
moving private media, shipping a video or accepting exercise form. The current
Google Flow agent retains ownership of its active assets and experiments.
