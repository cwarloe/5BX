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
*Sprite Art 5BX Workout*; `ART.md` lists the file names. The four production
archives are now also available as individually browsable PNGs under Drive's
`Production Art` folder. Restore only the needed `sheets/`, `assets/` and
`library/images/` paths into this folder without renaming them; a ZIP step is
not required. `kit/build.py --bake` redraws the sprite PNGs from `sheets/` if only
those are missing, but the imported backdrop pictures (`assets/backgrounds/`) are art and cannot be redrawn: the
build stops with a message naming the `assets` zip if they are absent.

## Fixes made while moving it in

Review of the move found three bugs in the kit's `build.py` (all fixed here, and worth sending back to the kit's
own history): cached sprite and backdrop records were trusted even when their PNGs were absent; the cache key for
composed frames hashed an image's path but not its contents; and exercise 5 reserved one jump window more than the
plan emits, so it ran 12 s short (now 360 s of the 360 s allotted at chart 1, level A).

## The 5BX Workout Mixer demo page

Live at https://workout-mixer.pages.dev/ (a Cloudflare Pages project called `workout-mixer`). It used to be served from the
`knowledge-harvest` repo and then from this repo's GitHub Pages; both copies are down.

The demo is about 57 MB of generated pictures and clips, so it is **not on `main`**. The built site is kept on its own
orphan branch, `sprite-boy-demo`, as a store; Cloudflare is not connected to it, so nothing deploys by itself. To refresh it:

1. Restore the art zips into `sprites/` (see above) and run, from `sprites/`:
   `python kit/make_demo.py --data ../data/5bx-charts.json --out ../_demo --reel`
2. Copy your clips into `_demo/clips/` (`chart4-exercises.mp4`, `chart5-exercises.mp4`, `chart6-exercises.mp4`; made with
   `kit/build.py ... --chart N --only ... --preview`).
3. Deploy the folder: `npx wrangler pages deploy _demo --project-name workout-mixer --branch main` (needs `wrangler login`
   once; Wrangler 4 needs Node 22, Wrangler 3 works on Node 20).
4. Commit the contents of `_demo/` as a single new commit on the `sprite-boy-demo` branch (replace its history, do not stack
   57 MB per refresh) and push it, so the branch matches what is live.

The full chart 1 video is a GitHub release asset (`sprite-boy-videos-2026-11-21`), linked from the page; videos are not in Git.

## Motion diagnostics and research (2026-11-24)

The current Chart 1 scissor-jump proof of concept has a [source-grounded diagnostic record](docs/SCISSOR_JUMP_DIAGNOSTIC_RECORD.md) covering original multi-angle video, character transfer, failed anatomical shoe marking, wrong pose order, motion interpolation, confirmed successes, and unresolved tracking/depth questions. Read it before commissioning another scissor-jump take or changing the motion pipeline. The [user-supplied pose/depth research guide](docs/research/limb-swap-depth-fix-guide.md) is preserved with [applicability cautions](docs/research/README.md); sample scripts and parameter values have not been validated against 5BX.

This is documentation only. Raw recordings and rejected media still belong in Drive, and the proposed source-identity gate does not replace the pending approvals in the [production requirements](../specs/sprite-production-line/requirements.md).
