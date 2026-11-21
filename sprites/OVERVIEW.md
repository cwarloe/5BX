# Sprites: what is here

Two toolkits for the 5BX exercise sprites and stage backgrounds, moved here from `cwarloe/knowledge-harvest`
so everything 5BX lives in one repo.

| Folder | What it is | Status |
|--------|------------|--------|
| `/` (this folder: `kit/`, `config/`, `prompts/`, `docs/`, `tests/`, `README.md`) | **The sprite kit.** Builds the video from pose strips; makes prompts and batches; keys sheets; checks backgrounds against the stage. Snapshot of `knowledge-harvest` branch `sprite-kit/batch-d` at commit `66f3f6c` (2026-11-20 19:52 -0700) | **The main tool** |
| `qc-line/` | A second, smaller pipeline built in parallel: sheet QC (figure count, pixel clearance, floor line, lift, character palette), cut-out manifest with feet pivot and lift, `he`/`she` prompt tokens, mats drawn in code, a defect log with first-pass yields | **To be ported into the kit, then deleted** |

## How they overlap

Both write prompts from a character file, both cut sprites out of a magenta sheet, and both check backgrounds.
The kit does each of those better (it is wired to the video builder, grounds every exercise in the booklet
drawing, and its keyer copes with the drifting background and the purple ground shadow). `qc-line` has four
things the kit lacks:

1. **Sheet QC**: `qc-line/pipeline/qc.py` scores a returned sheet for figure count, true pixel clearance between
   figures, floor line, jump height and whether the character's colours are still right.
2. **Cut-out manifest**: `qc-line/pipeline/cut.py` writes each sprite with its feet pivot and a `lift_px` offset, so a
   jump stays in the air when placed on a stage.
3. **Pronoun tokens**: `qc-line/pipeline/gen.py` fills he/his/him from the character file. The kit's `prompts/strips.json`
   hard-codes "his", so a girl character would still be called "his".
4. **Defect log and yields**: `qc-line/LESSONS.md`.

## Port plan (not done yet)

1. Add `kit/qc_sheet.py` from `qc-line/pipeline/qc.py` and `sheetlib.py` (it needs only numpy, Pillow and OpenCV).
2. Add the pivot and lift output to the kit's strip import.
3. Replace "his/him/he" in `prompts/strips.json` with tokens and fill them from `config/character.json` (add `pronouns`).
4. Move the useful parts of `qc-line/LESSONS.md` into `docs/` and delete `qc-line/`.

## Two corrections to `qc-line/LESSONS.md`

Written before the kit's batch C review (`batches/2026-11-20-C/REVIEW.md`) was read:

- **Gaps.** D-01 and rule `R-GAP` treat narrow gaps as a defect. The review measured that every sheet still
  separates into the right number of figures, so only touching matters. The kit's prompts say exactly that.
- **Retakes.** D-12 guessed that attaching the failed sheet anchors the tool to its mistakes. The batch C
  results support it, and the kit now attaches the booklet drawing instead of the failed take (`kit/make_batch.py --remake`).

## Art

Raw art does not live in Git (see `/ART.md`). The images that used to sit next to this code (strip sheets, the
sprite library, baked assets, batch folders, exports and the demo) are in the Drive folder
*Sprite Art 5BX Workout*; `ART.md` lists the file names. The kit's `build.py` reads `sheets/` and `library/`, so
download those zips back into this folder to build a video.
