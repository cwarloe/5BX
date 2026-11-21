# 5BX art: where everything lives

**Rule:** art the app, game or video actually uses is committed in this repo.
Raw and in-progress art (ChatGPT batches, rejected takes, source sheets, clips
that aren't shipped) lives in Google Drive, never in Git.

**Drive folder:** [Sprite Art 5BX Workout](https://drive.google.com/drive/folders/1x7ZrBMan7-jSXgYnZeOZzmEc_of0sRzE)
(owner: Charles; maintained by Claude; Charles does not edit it by hand).

File names in Drive: `YYYY-MM-DD_<source>_<what-it-is>.<ext>`, where the date is
when the art was made and `<source>` is the repo or tool it came from.

## In this repo

| Path | What it is |
|---|---|
| `game/public/sprites/<action>/<n>.png` | Game sprites, one folder per movement; frame counts follow the chart beats (see `game/src/lib/levels.ts`) |
| `figures/c{chart}e{exercise}.png` | Booklet exercise illustrations used by the workout app |
| `video/sheets/`, `video/design/` | Pose sheets and design notes for the chart video builder |
| `sprites/` (code, docs, config, `prompts/refs/` booklet references) | The sprite kit and its prompts. Its strip sheets, sprite library, baked assets, batch folders and exports are art, so they are in Drive (below); `sprites/OVERVIEW.md` says how to put them back to build a video |

## In Drive

| File | From | What it is | Drive ID |
|---|---|---|---|
| `2026-11-19_video-game-5bx_chart1-sprites-4frame-padded.zip` | `cwarloe/video-game-5bx` `public/sprites/` | Chart 1 sprites padded to 4 frames each. Superseded: they break the frame-count rule; kept for reference | `1JOrpcqu0AJ14qBgk0gB2yeG-7mJ5qerK` |
| `2026-11-19_video-game-5bx_cadet-video-to-sprite-pipeline.zip` (63 MB) | `cwarloe/video-game-5bx` `assets/sprites/video2dsprite/cadet/` | Grok video-to-sprite run: raw and cleaned frames (145 each), sprite cycles, prompt and pipeline notes | `1GQExE2GQUE8Ys23Czmozv3QK9-GHL78Q` |
| `2026-11-19_video-game-5bx_exercise-film-clips-mp4.zip` (16 MB) | `cwarloe/video-game-5bx` `public/video/` | Eight exercise film clips (toe, sit-up, back, push-up, run, scissor, cadet run) and their index page; film mode was not ported to the game | `1sd05XQ2nQk5JbrwXz54S4wLTL3E0YaE6` |

## Waiting for Charles to drag into Drive

Zips are made and sit in `Desktop\overnight\for-drive\` on Charles's PC (none is committed). Each was made so that
unzipping it inside `sprites/` puts the files back where the kit expects them. Fill in the Drive ID here after upload.

| File | From | What it is | Drive ID |
|---|---|---|---|
| `2026-11-21_knowledge-harvest_sprite-kit-library.zip` | `knowledge-harvest` `sprite-kit/batch-d`, `sprites/library/` | The chosen sprite takes and backgrounds (25 files) | pending |
| `2026-11-21_knowledge-harvest_sprite-kit-sheets.zip` | same, `sprites/sheets/` | Strip sheets the build reads (21 files) | pending |
| `2026-11-21_knowledge-harvest_sprite-kit-assets.zip` | same, `sprites/assets/` | Baked sprites and backdrop layers; `kit/build.py --bake` can rebuild them (90 files) | pending |
| `2026-11-21_knowledge-harvest_sprite-kit-batches.zip` | same, `sprites/batches/` | Reference images attached to each ChatGPT batch (27 files) | pending |
| `2026-11-21_knowledge-harvest_sprite-kit-exports.zip` | same, `sprites/exports/` | Layer-pack exports (28 files) | pending |
| `2026-11-21_knowledge-harvest_sprite-boy-demo.zip` | `knowledge-harvest` `docs/sprite-boy-demo/` | The phone demo: reel, strips and per-chart sprites; rebuildable with `kit/make_demo.py` | pending |
| `2026-11-20_chatgpt-overnight_passing-sprites-and-backgrounds.zip` | `qc-line` review | The 18 outputs that passed review, plus the mats drawn in code | pending |
| `2026-11-20_chatgpt-overnight_reference-images.zip` | overnight batch | The 14 sprite and 4 background reference images the prompts name | pending |
| `2026-11-20_chatgpt-overnight_returned-sheets-part1.zip`, `..._part2.zip` | overnight batch | Everything ChatGPT returned in run 1 (51 files), including rejected takes | pending |

Large uploads: Claude can send at most ~3 MB per file to Drive; anything bigger is handed to Charles to drag in, then checked here by file size.
