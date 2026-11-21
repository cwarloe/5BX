# 5BX sprite-to-video production control plan

Status: **Draft standard work / proposed controls**, 2026-11-21. See [the proposed requirements](../../specs/sprite-production-line/requirements.md). This document does not claim that proposed automation has shipped.

## Purpose

Treat exercise-video creation as a repeatable manufacturing process: **make the right movement once, confirm it early, reuse approved components, measure defects, improve the constraint**. Avoid producing attractive but anatomically wrong video, unnecessary paid retakes, and bulk re-renders after a local change.

## Product family: separate what changes

| Independent input | Authoritative/current home | Intended reuse boundary |
|---|---|---|
| 5BX plan and timing | `data/5bx-charts.json` | All avatars, formats, themes and levels |
| Movement semantics, source booklet reference, pose/check list | `sprites/prompts/strips.json`, booklet refs; **canonicalization proposed** | All avatars |
| Chart slot, cycle, anchors and pose files | `sprites/config/strips.json` | Video assembly and derived consumers |
| Avatar identity, outfit, pronouns and palette | `sprites/config/characters/` plus approved image reference | A single character's art generation |
| Selected pose sheets and transparent sprites | Raw art in Drive; wired assets / library records under `sprites/` | Every chart/level/output that uses the exercise and avatar |
| Backgrounds, props, text and format | `sprites/config/theme.json`, `sprites/config/scene.json` | Independent of art generation |
| Render and provenance | `sprites/kit/build.py`, `kit/builds.py`, build manifests | Reproducibility and targeted re-render |

**Economic reality:** swapping a character profile reuses specifications and assembly, but not necessarily the character's actual pose pixels. Avoid claiming a no-cost avatar swap until the second-avatar experiment measures it. A smooth, articulated animation is likewise distinct from the current crossfaded pose cycle.

## Proposed value stream and quality gates

| Stage | Standard work | Pass evidence / stop condition | Status today |
|---|---|---|---|
| 0. Release the exercise brief | Identify exercise/chart, booklet geometry, camera, cycle, pose list, rep/step cadence | Stable exercise ID, source and explicit 'must not' errors | Prompt/spec files exist; definitions overlap |
| 1. Release the avatar brief | Select profile and pinned appearance reference | Approved look, clothes, colours, pronouns, compatible key colour | Sprite Boy locked; another real avatar unproved |
| 2. Generate controlled candidates | Make a named job/batch with exact input references; retain every returned take | Job ID, prompt version, references, model/cost, source file | Kit prompts/batches and library partially support this |
| 3. Mechanical inspection | Check count, separation, key/alpha, palette, floor and lift; reject objectively faulty inputs early | QC result linked to asset ID; FAIL goes to correction | `qc-line` checks available but not integrated into kit |
| 4. Human form inspection | Compare *every pose* to the exercise contract and booklet | Named reviewer, verdict and defect reason; no unreviewed release | Batch reviews exist; library `expert_reviewed` not complete |
| 5. Cut, key and locate sprites | Convert accepted sheets to transparent poses with explicit contact anchors/lift | Pose sequence, pivot, transparency and consistent scale | Both pipelines implement overlapping pieces |
| 6. One-cycle assembly | Preview only the affected exercise at its planned cadence | No slide, wrong pose, crossfade ghost, cut-off limb, timing error | Kit supports `--only` and `--preview`; gate formalization proposed |
| 7. Final render and release check | Read timing from data; render, decode-check, inspect mobile view | Build/input hashes, duration, selected asset versions, final approval | Kit build records and decode check exist |
| 8. Close the learning loop | Log every defect; update the smallest rule/test that prevents recurrence | Defect category, correction, owner, before/after outcome | `qc-line/LESSONS.md` begins this practice |

### Stop-the-line rules

- Incorrect or ambiguous exercise form, contact point or limb geometry: **hold** the affected exercise, even if it looks attractive.
- Wrong or mixed avatar identity, missing source reference, wrong chart slot, or unapproved take: **do not publish**.
- Keying/splitting/anchoring fails or changes the motion: **repair one affected asset** and retest that cycle before any full render.
- A code/configuration change fails regression or an artifact cannot be recovered: **do not delete the previous working line**.
- A generated model cannot satisfy a geometric constraint after repeat attempts: **change the input diagram/view or technique**, not merely the wording of the same prompt.

## Defect prevention: fix at the source

1. **Check the specification before asking for a retake.** The Chart 3 chin/forehead push-up failure came partly from a prompt contradicting the booklet. Correct the contract, then retake.
2. **Use one neutral character appearance reference, and the booklet/geometry references for movement.** Failed poses used as references have reintroduced errors. Batch C and E already document this.
3. **Code the exact geometry.** Mats, numeric overlays and HUD layouts belong in code, not repeated generative-image requests.
4. **Fix locally and preserve approved work.** A bad pose should not trigger six new charts or a completely new video. A visual edit must be re-inspected because it can redraw untouched regions.
5. **Do not edit generated batch prompts as the only source.** Move successful Batch E instructions back to the generator's canonical definitions before new batches.
6. **Record both successes and rejects.** A rejected take and the reason prevent repeating the same failed production attempt.
7. **Make one improvement per experiment.** Compare the changed and baseline approach using the same exercise, avatar, quality rubric, and outcome measurements.

## Pilot work-in-process policy

Limit active improvement to **two exercises** initially: Chart 1 knee push-up (relatively simple and stable) and Chart 1 scissor jumps (camera/shading and limb-side ambiguity). First run them on the approved Sprite Boy, then on one newly approved avatar. Keep normal shipped assets frozen while conducting the trial. Do not start a whole-chart or whole-avatar paid batch until these two demonstrate acceptable form, traceability, and assembly.

## Minimum job and asset traveler

Each attempt should be traceable with the following fields, in a machine-readable record or a temporary review sheet until automation is implemented:

| Field | Example / rule |
|---|---|
| Job and asset ID | Stable exercise ID + avatar ID + attempt/revision, not an ambiguous `final2.png` |
| Specification | Exercise contract version, chart slot and required pose order |
| Inputs | Exact character reference, booklet image, geometric diagram, prompt revision/hash |
| Production | Tool/model, settings, creation time, attempts, credits/cost (unknown if unavailable) |
| QC | Measured findings, human reviewer, verdict, defect codes, link to evidence |
| Location | Source art archive, selected asset path, content hash |
| Disposition | Candidate / rejected / approved / superseded, and why |
| Downstream use | Chart registry entry, build ID, video output version |

## Measures and operating review

| Metric | Definition | Why it matters |
|---|---|---|
| First-pass yield | New approved jobs without correction / all new completed jobs in the batch | Basic process quality; separate from retake yield |
| Retake yield | Corrected jobs accepted / corrected jobs completed | Whether the correction method improves outcomes |
| Credits per accepted exercise | Total attributable generation/edit credits / accepted exercise assets | Real marginal production cost |
| Manual touch time | Human minutes for prompting, grading, hand-fixing, locating files and recovery | Eliminating operator waste |
| Lead time | First released brief to approved asset or release-ready video | Throughput and bottleneck detection |
| Repeated defect count | Recurrences of the same defect type after countermeasure | Whether corrective actions actually work |
| Change-to-preview time | Time from one changed asset/config to verified one-cycle preview | Whether incremental builds really pay off |
| Escaped defect rate | Defects found after release / released assets, by severity | Final protection of the viewer |

Historical baseline (one small overnight sample, **not** process capability): new sprite sheets 7/11 first-pass accepted (64%); first-pass acceptance of retake jobs 2/7 (29%), as recorded in `qc-line/LESSONS.md`. Preserve exact denominators and record who reviewed. Before/after experiments must use a comparable rubric.

After each batch, review the highest-frequency form defects and the longest wait/touch step. Make the smallest change that prevents a repeat, attach a regression test or named review check, and record the next batch's results. Do not generate a lengthy report unless the data changes a decision.

## Current integration risks to close before scaling

1. **Two processing implementations:** `sprites/kit/` is primary; the `qc-line/` checks, anchor/lift export, pronoun tokens and metrics need parity tests and selective porting before retirement.
2. **Recipe drift:** Batch E's improved scissor/back-extension instructions live in a batch file and review; `prompts/strips.json` still contains earlier retake directions. `library/index.json` has the chosen assets, but the expert-review fields are still false.
3. **External recoverability:** `ART.md` has most Drive IDs and instructions, but at least one Chart 4–6 archive is marked pending. Verify it before calling the pipeline recoverable from a clean environment.
4. **Coverage and duplicates:** Review missing Chart 4–6 slot mappings and decide whether `video/chart.py` is a compatibility artifact or an active alternative; do not maintain two authoritative video producers accidentally.
5. **Motion quality:** Current pose cycling/crossfades are deterministic but not full anatomical in-between animation. Test a controlled interpolation/rig approach on the pilot before committing to a new full-series production method.

## Approval and change control

- **Charles:** approves requirements, a new avatar's identity/look, any change to what the exercise means, and adoption of a materially different video style.
- **Production operator/automation:** owns repeatable generation, file identity, mechanical checks and build evidence.
- **Named form reviewer:** owns the exercise-accuracy verdict (a model's self-review is not an expert verdict).
- **Version control:** keep existing working outputs and build manifests; use reviewed PRs and acceptance evidence for changes.

Next action after approval: write the spec's `design.md`, then `tasks.md`; deliver the integration in small tested commits. No pipeline deletion, paid generation, or deployment is authorized by this documentation plan.
