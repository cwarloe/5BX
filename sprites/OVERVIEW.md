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

### Photographic review panel (prototype; not deployed)

The source page at `kit/demo/page.html` now includes a **Photographic exercise
review** section. It is intentionally separate from the original cartoon
Sprite Boy animation and its clothing hue controls:

1. Pick the chart and exercise; the options come from the generated
   `data.json` inventory.
2. Choose local PNG/JPG/WebP stills or MP4/WebM videos. Multiple files selected
   for the same movement appear as an ordered, clickable media list, so a
   three- or four-position card can be reviewed without rebuilding the site.
3. A cutout PNG with true alpha can be shown over the track-color, light-studio,
   or dark-stage backgrounds. Opaque photos/videos keep their own original
   scenery. The feedback says which state was detected.
4. Files are never uploaded; selections persist only for the current browser
   session. Importing an image does **not** register or approve it as production
   art, and changing a background does **not** edit the source file.

See `specs/bright-boy-workbench/` for scope and tests. Quick checks:
`node --test sprites/tests/test_photo_review_unit.cjs` (dependency-free
preview logic) and `node --test sprites/tests/test_photo_review.cjs` (full
Chromium checks when a browser is installed). Current source builds do **not**
embed the 2026-11-25 photographic cards or videos: use the linked review
archive or local file picker. Production source art must still be restored for
`kit/make_demo.py`; source changes do not update the Cloudflare site.

## Motion diagnostics and research (2026-11-24)

The current Chart 1 scissor-jump proof of concept has a [source-grounded diagnostic record](docs/SCISSOR_JUMP_DIAGNOSTIC_RECORD.md) covering original multi-angle video, character transfer, failed anatomical shoe marking, wrong pose order, motion interpolation, confirmed successes, and unresolved tracking/depth questions. Read it before commissioning another scissor-jump take or changing the motion pipeline. The [user-supplied pose/depth research guide](docs/research/limb-swap-depth-fix-guide.md) is preserved with [applicability cautions](docs/research/README.md); sample scripts and parameter values have not been validated against 5BX.

This is documentation only. Raw recordings and rejected media still belong in Drive, and the proposed source-identity gate does not replace the pending approvals in the [production requirements](../specs/sprite-production-line/requirements.md).

## Approved conditional near-trailing-leg reference (2026-11-24)

Charles approved the near/far **hip-overlap depiction** in a [four-pose running card](https://drive.google.com/file/d/1lSzvp-SjsNDOClhmQquGk7tqUAmb1HAh/view): when the camera-near leg trails to screen-left while the character faces right, that trailing thigh must overlap **in front of** the camera-far leading thigh at the shorts. See [the portable foreground-trailing-leg prompt and QA rule](docs/FOREGROUND_TRAILING_LEG_RULE.md). Apply it conditionally to other exercises/poses with the same depth assignment; this is **not** acceptance of a scissor-jump animation or a new default rule for every frame.

## All-chart foreground-leg audit and research (2026-11-24)

The [exercise-by-exercise depth applicability audit](docs/FOREGROUND_TRAILING_EXERCISE_AUDIT.md) checks all six charts and identifies four reusable affected prompt recipes. Required inverse sagittal foot-switches occur in Chart 1 scissor jumps and Chart 4 semi-squat jumps; low stationary runs (Charts 1–3) and high-knee runs (Charts 4–6) need depth checks **only when the camera-far limb actually leads**. Their source prompts now state this conditional rule. No production sprites or timing changed. The [research index](docs/research/README.md) now points to the user-supplied limb/depth guide, the two read-only animation Repo Scout reports (in one archival source), and the earlier observed failure brief, with implementation/verification caveats.


## Historical film-to-sprite pose transfer (2026-11-24)

The [1959 RCAF film-to-sprite experiment and lessons](docs/FILM_TO_SPRITE_POSE_TRANSFER_2026-11-24.md) records source-grounded reference prompts, a failed straight-body instruction for Chart 3's forehead-contact **pike**, promising corrections using film frames for body geometry and Sprite Boy only for appearance, toe-pointing/ballet failures in jumps, exercise-specific camera choices, and what remains unverified. It includes a pass/fail evidence table, prompt template, film timestamps, follow-up comparison plan, and links to the archived experimental images and supplied videos.

**No production changes:** these are reference candidates, not approved exercise form, sprite library replacements, timing changes, or an animation release. Experimental images and videos stay in the [Drive art archive](https://drive.google.com/drive/folders/1_xuq2ZA8rGe1d750EDxP8pcPPg8ejgJO), indexed in [ART.md](../ART.md), under the existing raw-art policy. Recheck every difficult pose against the 5BX booklet and historical film with named human review before making video.
