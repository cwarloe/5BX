# Design: Lean production preflight (first increment)

Status: Approved for first implementation increment (Charles, 2026-11-21)
Requirements: [requirements.md](requirements.md)

## Approach

Use the repository's existing JSON registry, sprite library and video kit. **Do not introduce a project-management database, a new web app, or a second image-quality engine.** This increment is a read-only, standard-library preflight command plus two focused prompt-generation corrections. The existing image QC under `sprites/qc-line/` remains available until an independent parity-tested move is justified.

This is a *working first station*, not a claim that all seven requirement groups are complete. Batch generation, human movement review, and full video output remain the later stations. A person who knows the movement, including Charles, may perform the practical form check; no external certification scheme is required.

## Components and files

| File | Change | Requirements |
|---|---|---|
| `sprites/kit/line.py` | Read-only `status` / `check` commands; inventory registry, recipe and selected-art coverage, show missing slots and unreviewed picks | R1, R2, R3, R6, R7 |
| `sprites/prompts/strips.json` | Reconcile the two successful Batch E retake lessons into the reusable scissor-jump/back-extension prompt recipe; preserve historical take notes | R1, R7 |
| `sprites/kit/prompt.py` | Apply avatar pronoun substitutions to movement text while preserving original behavior for Sprite Boy | R4 |
| `sprites/config/characters/_template.json` | Declare an optional pronoun map for new avatars; avoid changing the existing boy | R4 |
| `sprites/tests/test_line.py`, `sprites/tests/test_prompt.py` | Dependency-light unit tests for contract validation, warnings and avatar substitution | R1–R4, R7 |
| `sprites/README.md` | One-command operator entry point, without duplicating the full process manual | R5, R7 |

## Data and state

- `line.py` reads only `data/5bx-charts.json`, `sprites/config/strips.json`, `sprites/prompts/strips.json`, and `sprites/library/index.json`. It does not mutate files or require raw source art or image processing packages.
- `status` reports each chart's six expected slots, mapped/missing slots, selected candidate count, form-review backlog and missing local art. It distinguishes **missing locally (stored in Drive)** from **not yet mapped**.
- `check` exits nonzero only on structural defects: chart referring to an unknown strip, unknown pose in a cycle, invalid pose or chart IDs, or missing prompt for a registered strip. It reports operational gaps and unequal prompt/registered pose counts as WARN until explicitly reconciled. An intentional extra pose in Chart 2 toe touch is a known example.
- Existing `library/index.json` remains the artifact ledger. No parallel spreadsheet or statuses database is created. A chosen take is not automatically a human-reviewed one.
- A new character may set `pronouns` to a simple map (`he`, `him`, `his`, `himself`, `boy`); the default remains the existing boy. Substitutions occur **only when rendering new prompts**, never in the stored exercise definitions. Preserve case of whole-word matches.

## Operator flow

1. Run `python3 sprites/kit/line.py status` to see what's mapped and what needs attention.
2. Run `python3 sprites/kit/line.py check` before starting a batch or merging a registry/prompt change.
3. If a definition is faulty, fix it at its canonical source. If an illustration is at fault, keep the approved assets and change only its job/pose.
4. Use existing `kit/make_batch.py`, `kit/library.py`, and `kit/build.py --only ... --preview` for the work itself; do not duplicate their abilities in `line.py`.
5. Attach a named human movement review to the selected art before promoting an entire new exercise video to release. The producer need not be a certified trainer, but an AI-generated verdict is not the same as a human check.

## Failure handling and tradeoffs

| Case | Behavior | Why |
|---|---|---|
| New clone lacks Drive art | WARN, not failed code check | Art intentionally lives outside Git |
| Chart 4–6 slot not yet made | Listed as MISSING, not fatal to other charts | Support incremental coverage |
| Registered strip has more poses than its intended prompt | WARN with both counts | Existing Chart 2 toe touch has an extra accepted rebound pose |
| Chosen art lacks a human form reviewer | Clearly list REVIEW NEEDED; never mark it reviewed automatically | Keep form review proportional, explicit and honest |
| Bad cycle index or unknown strip | ERROR and nonzero exit | Prevent a wrong/missing movement entering assembly |
| No extra avatar approved yet | Test substitution with a synthetic girl profile only | No paid generation or speculative identity choice |

## Testing and release criteria for this increment

| Criterion | Verification |
|---|---|
| R1.1–R1.4 | `test_line.py`: known/unknown strip, pose-count warning, cycle failure, missing chart slots |
| R2.2, R3.2 | `test_line.py`: chosen-unreviewed take remains in review queue |
| R4.1–R4.2 | `test_prompt.py`: male default unchanged and female pronouns/noun applied without leakage |
| R7.3 | `test_prompt.py`: Batch E remediation wording appears in generated fresh/remake prompts |
| No regression of existing builder | `line.py check` on current repo; run existing relevant tests when dependencies/art are available |

The next increment after this is to integrate *only* the unique `qc-line/` functions into the main kit with parity fixtures. We deliberately do not delete `qc-line/`, add a dashboard, or purchase new image generation in this increment.
