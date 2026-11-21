# Requirements: Lean sprite-to-video production line

Status: Draft — awaiting Charles's approval
Owner: Charles
Last updated: 2026-11-21

## Problem

5BX can already generate pose sheets, cut sprites, and assemble timed workouts, but the work is not yet one controlled, repeatable production line. Two overlapping sprite toolkits, separately maintained exercise instructions, incomplete recipe updates, and review evidence scattered across files create avoidable inspection, retakes, and risk of an incorrect exercise reaching a video. The next goal is to produce many correct videos, across exercises, avatars, levels, and presentation styles, with predictable cost and minimal rework.

## Objective and customer

Build a **repeatable, auditable process** that starts with an approved 5BX movement and an approved character specification and ends with reproducible exercise animations and release-ready videos. A new character or visual theme should reuse approved movement definitions, timing data, quality checks, and assembly logic; only genuinely character-dependent art should need creation.

The customer is the person following an exercise demonstration on a phone or larger screen. **Correct form comes before visual appeal and production throughput.**

## Scope and constraints

- `cwarloe/5BX` is the home for 5BX source, specifications, tooling, and shipped assets. Do not create another 5BX repository.
- `data/5bx-charts.json` remains the sole source for chart descriptions, counts, timing, step and jump intervals. Do not hard-code a generic repetition duration.
- Keep raw/rejected/generated media outside Git, in the Drive folder documented in `ART.md`. Keep only media required by the app, game, or shipped videos in Git.
- Maintain the existing workout app, game, published Sprite Boy demo, and working video builder during any migration. Preserve the app's service-worker behavior and cache rules.
- Keep existing approved/reviewed art and decisions (including the Sprite Boy's cyan tank, red shorts, and blue shoes) unless an explicit review changes them.
- This PR is **requirements and process documentation only**: no video generation, paid image calls, renderer changes, source-asset deletion, pipeline deletion, or deployment. Per `CLAUDE.md`, approval of this requirements document precedes implementation design and tasks.

## Definitions

- **Exercise contract:** Avatar-independent exercise identity, source reference, pose/transition order, contact geometry, camera/view constraints, and human-review checklist.
- **Avatar profile:** Character-specific identity, body proportions, appearance, outfit, palette, pronouns, references, and approved look.
- **Job:** One uniquely identified attempt to produce or repair one asset, with recipe, inputs, outputs, cost, and outcome.
- **Approved asset:** A versioned asset that passed mechanical QC and named human form review; a 'chosen' artistic take alone is not approval.
- **Build record:** A manifest tying one video to exact chart data, approved assets, renderer settings, code revision, and output hash.
- **First-pass yield (FPY):** The fraction of new jobs accepted without a corrective generation/edit or manual repair; count retakes separately.

## Requirements

### R1. Canonical movement and product definitions

**User story:** As a producer, I want to specify an exercise once, so that different avatars and outputs cannot silently disagree about the movement.

**Acceptance criteria**

1. Every exercise used in production SHALL map to a stable exercise ID and its authoritative booklet/`data/5bx-charts.json` reference.
2. The exercise contract SHALL describe required poses, their order, contact points, permitted camera view, cycle type, and measurable or human-reviewed form constraints independently of any avatar's outfit or appearance.
3. Prompt generation, mechanical checks, and video assembly SHALL consume the canonical contract or generated projections of it; conflicting hand-maintained exercise definitions SHALL be identified and resolved before rollout.
4. IF a chart slot lacks a valid, approved movement asset, the build SHALL report the specific missing slot and SHALL NOT silently substitute an incorrect exercise.

### R2. Traceable work and controlled asset state

**User story:** As a producer, I want to know exactly what created each image and why it passed or failed, so that I can reuse good work and stop repeating failed attempts.

**Acceptance criteria**

1. Every new generation, edit, and import SHALL receive a unique job/asset identifier and an explicit state: requested, generated, automatic-QC-pass/fail, human-review-pass/fail, approved, superseded, or rejected.
2. Each candidate SHALL preserve its exercise ID, avatar ID, source prompt version, reference-art identifiers, tool/model, relevant settings, file location, hash, and reviewer/reason; paid calls SHALL record reported credits/cost when available.
3. An approval SHALL identify the exact asset revision; an edited or regenerated revision SHALL NOT inherit the old approval automatically.
4. The process SHALL preserve rejected takes and their defect reasons in the raw-art archive, without treating them as production assets.

### R3. Quality gates and stop-the-line rules

**User story:** As someone relying on exercise demonstrations, I want both measurable image quality and correct exercise form verified before publication.

**Acceptance criteria**

1. Every pose sheet SHALL pass available automated checks for pose count, separation/no touching, usable key/alpha, character-palette consistency, floor/contact alignment, and configured jump/lift requirements before being cut for a release.
2. Every exercise SHALL receive a documented human form review against its source exercise contract, including limbs, contacts, direction, range of motion, and consistency across poses. Mechanical QC SHALL NOT be described as anatomical validation.
3. A form failure, missing source/reference, missing asset, or unreviewed exercise SHALL block release; the producer SHALL see an actionable defect and the affected exercise/asset ID.
4. A representative animation cycle SHALL be checked for anchor/scale stability, correct pose order, legibility, seamless looping, and timing **before** a full workout render.
5. A release video SHALL be checked for correct chart/level content, timing, counter labels, decode integrity, and mobile legibility, with a named human review where required.

### R4. Avatar and presentation reuse

**User story:** As a producer, I want to change who performs the movement or how the video looks without redesigning the exercise itself.

**Acceptance criteria**

1. Each avatar SHALL have its own profile and approved appearance reference; prompt generation SHALL substitute pronouns and character-specific rules without leaking the existing boy's descriptors.
2. Adding an avatar SHALL NOT require hand-editing the exercise form definitions, counts, chart data, timing, or compositing logic.
3. Appearance or background/HUD changes SHALL rebuild only affected assets or render segments when technically possible; unrelated approved source art SHALL remain unchanged.
4. The pilot SHALL compare one simple exercise (Chart 1 knee push-up) and one difficult exercise (Chart 1 scissor jumps) across Sprite Boy and one subsequently approved second avatar. A passing prompt substitution test alone SHALL NOT count as avatar-production validation.

### R5. Repeatable incremental assembly

**User story:** As a producer, I want the same approved inputs to produce the same intended workout, and a small change to cost only a small rebuild.

**Acceptance criteria**

1. The established `sprites/kit/` builder SHALL remain the primary assembler; overlapping QC functionality SHALL be migrated with regression tests before `qc-line/` is retired.
2. The producer SHALL be able to render and inspect one exercise/cycle independently of rendering a complete workout.
3. Approved pose cycling SHALL remain supported. Any proposed smooth in-between motion SHALL be a separate, measured pilot and SHALL NOT introduce incorrect anatomy, sliding contacts, or uncontrolled character drift.
4. A full build SHALL record exact input versions/hashes and pass the existing full-decode check before being marked complete.

### R6. Artifact availability and recovery

**User story:** As the next operator, I want to resume production without searching chats and old repositories for the correct asset.

**Acceptance criteria**

1. A clean-checkout recovery check SHALL identify all required source-art archives, their stable locations, expected contents/hashes, and restore instructions; unavailable files SHALL be reported rather than replaced with lookalikes.
2. The selected production strip and its approved source SHALL be traceable from the chart registry to the asset record and Drive archive.
3. No migration SHALL delete or overwrite the existing working pipeline, original art, rejected takes, or archived-repository evidence until parity and restore checks pass and Charles approves retirement.

### R7. Quantified improvement and feedback

**User story:** As the process owner, I want visible defect and cost trends so that improvements target the major causes of rework.

**Acceptance criteria**

1. Each batch SHALL record new jobs, first-pass acceptances, retakes, approved outputs, repair touches, measured effort/cost when available, and defects by category; missing measurements SHALL be labeled unknown, never estimated as zero.
2. The process SHALL calculate FPY with an explicit denominator and separate retake yield, cost per approved exercise, cycle/lead time, and recurring defects.
3. Every recurring defect SHALL get an owned corrective action, a regression check or explicit manual gate, and a before/after measurement. Prompt-rule changes SHALL record which defect they address.
4. The process owner SHALL review a brief defect Pareto and bottleneck summary after every production batch and update only the relevant standard work.

## Proposed rollout sequence (not yet implementation tasks)

1. **Baseline and source reconciliation:** Inventory active vs archived pipeline functions; reconcile Batch E recipes, chosen-asset status, chart-slot coverage, and Drive manifest gaps.
2. **Single controlled line:** Port useful QC, anchors/lift offsets, pronoun handling, and defect metrics into `sprites/kit/` with parity tests; avoid dual maintenance.
3. **Traceability and gates:** Join asset/job records with build manifests and introduce mechanical/human/release gate checks.
4. **Two-exercise, two-avatar pilot:** Measure correctness, first-pass yield, manual touch time, marginal credits, and rebuild time.
5. **Motion improvement experiment:** Compare approved pose-cycle playback against a controllable interpolation/rigging method; adopt only if form and cost targets improve.

## Baseline observations requiring verification in design

- `sprites/OVERVIEW.md` explicitly identifies the main kit and the overlapping `qc-line/` functions still to port.
- `sprites/qc-line/LESSONS.md` reports a small first-run sample: 7/11 new sprite sheets accepted (64%), 2/7 retakes accepted (29%). These are indicative, not process capability estimates.
- `sprites/batches/2026-11-21-E/REVIEW.md` says its improved prompts were not yet placed in `prompts/strips.json`; as of this draft, that file still includes older scissor-jump retake directions, while `sprites/library/index.json` includes Batch E chosen records. The chosen records still show `expert_reviewed: false`.
- `ART.md` indexes the external source archives, but labels the Charts 4–6 sheets archive upload pending. Check actual availability before depending on it.
- `sprites/config/strips.json` has only partial Chart 4–6 slot mappings. Establish intended reuse versus real gaps; do not silently fill them.
- The original `video/chart.py` and the newer `sprites/kit/build.py` both remain. Preserve the former as historical/compatibility behavior until equivalence is understood.

## Open questions for approval/design

1. Who is the named final movement-form reviewer for the pilot (Charles, a qualified exercise reviewer, or both)?
2. Which second avatar should be the real pilot? The existing example girl profile is a prompt/test fixture, not approved production art.
3. Which actual artifact locations and restore tools are available to a clean build operator? The Drive manifest is the current index.
4. What minimum visible improvement justifies investing in skeletal tweening/intermediate animation rather than retaining accurate keyed-pose playback?

No code or existing assets should change on the basis of this draft alone. After Charles approves requirements, write `design.md`, then `tasks.md`, with a test or named manual check for every criterion.
