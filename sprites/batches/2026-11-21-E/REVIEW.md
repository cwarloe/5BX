# Batch E review (rewritten prompts, ChatGPT, 2026-11-21)

Two jobs from batch D that were still not right (scissor jumps, back extension) were rewritten and run again.
Reviewed by Claude against each job's check list, by eye at full size and with the sheet checks in
`../../qc-line/pipeline/` (`sprite.py qc sheet`). The four returned sheets are in Drive (see `/ART.md`), not in git.
Grok was not run (optional). `BATCH-E-sprites.md` holds the prompts exactly as sent.

| Job | Sheet | Verdict | Notes |
|---|---|---|---|
| 01 scissor jumps | JOB-01-open-hands | **Keep** | Stance A has the light shoe in front, stance B the dark shoe in front (the batch D failure). Both arms horizontal at shoulder height in both stances. Jumps clearly off the floor (14% of sheet height). Caveats: front knee bent more than "slightly", jump arms hang diagonally instead of crossing, still a side view |
| 01 scissor jumps | JOB-01-sheet | Same drawing, fists | Closed fists; open hands were requested, so use the other file |
| 02 back extension | JOB-02-optional-start-edit | **Keep** | The one-figure edit of the batch D alternate: START now flat with head down and chin on the floor; LIFTING is a clear middle step; TOP has a visible gap between the thighs and the hands. Figures 2 and 3 look unchanged by eye (not compared pixel for pixel) |
| 02 back extension | JOB-02-sheet | Weaker | START still has the head raised and the feet lifted |

Measured: the sheet checks pass on all four (a spacing warning at 2.9-3.0% on two, still clear). They cannot judge
poses, so the verdicts above are by eye. The kit's own rule applies: the figures only need to not touch.

## What worked (applies to every character)

- **State a left/right difference through shade, not geometry.** The tools never produced the three-quarter front
  view that batch D asked for, but "near side normal, far side darker; light shoe in front in A, dark shoe in
  front in B" was followed.
- **Give lift heights as angles** (0, about 15, about 30 degrees) and say where the shoes rest in START, not "lying flat".
- **A one-figure edit of a near-good sheet can work** (JOB-02). Edits have re-rendered whole images before, so check
  the other figures.

## Not done

- The batch E prompts are hand-written. They are not yet in `prompts/strips.json`, which the kit regenerates its
  prompts from, so `kit/make_batch.py` will not reproduce them.
- The accepted sheets are not logged in the kit's library (`kit/library.py add`).
