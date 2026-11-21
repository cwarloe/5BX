# Tasks: Lean sprite-to-video production line

Design: [design.md](design.md)

Rules: make small tested commits, update this list in the same commit that completes a task, and avoid adding systems without a measurable benefit.

## Increment 1 — useful immediately

- [x] 1. Add a dependency-light `kit/line.py` production status and structural check (R1, R2, R3, R6, R7)
- [x] 2. Reconcile the two Batch E lessons in the canonical prompts without changing approved pose art (R1, R7)
- [x] 3. Make new-avatar prompts grammatically reusable and regression-test them (R4)
- [x] 4. Add unit tests, a lightweight CI check, and the one-command operator instructions (R1–R4, R7)
- [x] 5. Run what can be tested from a clean clone, record limitations accurately, and open a reviewed PR (#18 merged)

## Increment 1.5 — release control without a new system

- [x] Audit the seven stations against existing kit, QC, library, build records and old video builder
- [x] Add a strict on-demand artwork release check: chosen revision hash, restored sheet, mapped slots, named human review and positive form grade
- [x] Publish one-page operator standard work and regression tests; leave existing WIP assets untouched

## Later increments — only after the first proves useful

- [ ] 6. Port the unique image QC, contact/pivot and lift checks from `qc-line/` into the main kit, using parity fixtures before retiring duplication (R3, R5)
- [ ] 7. Resolve archive restore gaps and align chosen asset IDs with the build registry (R2, R6)
- [ ] 8. Run the Chart 1 knee-push-up and scissor-jump pilot with a second approved avatar; measure yield, touch time, credits and errors (R4, R7)
- [ ] 9. Test controlled intermediate motion only if the existing pose-cycle animation fails the agreed clarity bar (R3, R5)
- [ ] 10. Make generated `PROMPTS.md`/`prompts.json` snapshots reproducible from a clean clone without misleading art-availability labels (R1, R6)

## Increment 2 — Chart 2 read-only visual traveler + incoming QC

- [x] Generate a six-card chart review HTML directly from the existing registry,
  library, original booklet references and Drive recovery index (no new ledger).
- [x] Display selection IDs, selected-vs-render source, immutable hash matches,
  named human form review status, and incomplete/missing artwork honestly.
- [x] Integrate the kit's own keyer/segmenter into technical intake checks:
  source format, magenta/transparency, figure count and spacing, edge margin,
  configurable floor/airborne geometry and character palette.
- [x] Pilot Chart 2 with restored sheets; retain the source art and approval data
  unchanged. Add isolated synthetic tests and CI for the image-dependent checks.
- [ ] Finish task 6's cut-out pivot/lift manifest comparison and parity tests
  before deleting or retiring any of `qc-line/`. The new QC explicitly adapts
  the overly strict old magenta threshold to the production keyer's tolerance.

2026-11-21 pilot note: the Chart 1 knee-push-up one-exercise previews rendered
and exposed a backdrop-restore dependency and crossfade ghosting (D-14 in
`sprites/qc-line/LESSONS.md`). Comparing `--no-fade` needs human playback/form
review; an approved second avatar and new scissor references are still pending.
Thus task 8 remains open. No new motion generation is authorized by this note.
Update (Charles, 2026-11-21): he authorized trying pinned-frame loops (first and
last frame pinned on an approved pose); the knee push-up pilot is a pilot, not a
binding constraint, and crossfade is retired as the default. See LESSONS section 11.

2026-11-21 workflow follow-up: `kit/line.py status/check` now flags an absent
chart-specific image backdrop as an archive-restore warning (task 7 partial).
Charles selected `--no-fade` for the knee push-up. Artwork/video generation is
paused while another bot revises the generation instructions; do not duplicate
that work. The wider archive recoverability audit remains open.
Clarification (Charles, 2026-11-21): the "other bot" is the artwork bot itself
(5BX Sprite Animator), which is exempt from the pause and cleared to generate.

Tasks 6–9 are intentionally *not* being implemented in this first increment. This is a prioritized queue, not authorization for unattended paid media generation.
