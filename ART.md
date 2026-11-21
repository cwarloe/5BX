# 5BX art: where everything lives

**Rule:** art the app, game or video actually uses is committed in this repo.
Raw and in-progress art (ChatGPT batches, rejected takes, source sheets, clips
that aren't shipped) lives in Google Drive, never in Git.

**Drive folder:** [Sprite Art 5BX Workout](https://drive.google.com/drive/folders/1x7ZrBMan7-jSXgYnZeOZzmEc_of0sRzE)
(owner: Charles; maintained by Claude; Charles does not edit it by hand).

File names in Drive: `YYYY-MM-DD_<source>_<what-it-is>.<ext>`, where the date is
when the art was made and `<source>` is the repo or tool it came from.

## Name new assets consistently; keep the old ones working

The **stable identity** is the existing sprite-library asset ID (for example
`c1-ex4-w1` or `c3-ex4-03`), **not** a descriptive filename. Do not invent a
second revision number outside the library. For new art, use that exact ID as
the prefix, lowercase names, and underscores between fields:

| Artifact | Example new filename |
|---|---|
| Source pose sheet | `c1-ex4-02_knee-push-up_sprite-boy_sheet.png` |
| Individual transparent pose | `c1-ex4-02_knee-push-up_sprite-boy_pose-02.png` |
| Optional backup bundle | `2026-11-21_5bx_sprite-boy_chart1-sheets_b02.zip` |

Use a new, unique library ID for every changed source revision (existing `w1`
IDs remain valid); `b01`, `b02` distinguish archive batches. Never name a take
`final`, `final2`, or `approved`: approval and selection belong in
`sprites/library/index.json`, with a review attribution and content hash.
A second avatar gets a new avatar ID, not a new exercise definition.

**Do not bulk-rename legacy files or move the existing ZIPs.** Their exact
paths are already referenced by the builder, library and archived batches.
The ZIPs were convenient batch snapshots, not a required production format.
Store **new working source art as individual Drive files**, and record their
Drive IDs in `direct_files` in the recovery index; make an immutable ZIP only
when a batch backup is useful. No deeper folder tree is needed yet. If the
Drive folder later becomes crowded, separate working files and archive backups
into two shallow folders rather than nesting every chart and revision.
The `direct_files` list starts empty: existing art remains in its verified ZIPs.
There is no reason to extract and re-upload that history just to populate it.

### Find exactly what to restore

The read-only recovery index at `sprites/config/art-archive-index.json` supports
**direct Drive files first** (for new work) and records the verified contents,
Drive IDs and SHA-256 of four historical source/baked-asset ZIPs as fallback.
It is an index of **where files are**, not an approval record.
For a clean clone, run:

```bash
python3 sprites/kit/line.py restore-plan --chart 1 --only ex4
python3 sprites/kit/line.py restore-plan --chart 6
```

The command groups only *missing* sources by direct Drive link or the exact
historical ZIP, showing the expected paths relative to `sprites/`. Restore
those files without renaming or overwriting approved local art. A new file not
yet uploaded/indexed is marked `UNINDEXED`; record its **direct Drive ID** after
uploading it. This does **not** download or alter anything automatically.

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

## In Drive: moved in from knowledge-harvest and the overnight run (uploaded 2026-11-21)

Each zip unpacks inside `sprites/` to put the files back where the kit expects them. These 10 zips are in the same Drive folder as the three above.

| File | From | What it is | Drive ID |
|---|---|---|---|
| `2026-11-21_knowledge-harvest_sprite-kit-library.zip` | `knowledge-harvest` `sprite-kit/batch-d`, `sprites/library/` | The chosen sprite takes and backgrounds (25 files) | `16_B_GPtk4xoSOUCw0Iu4dcxb-d5csDCn` |
| `2026-11-21_knowledge-harvest_sprite-kit-sheets.zip` | same, `sprites/sheets/` | Strip sheets the build reads (21 files) | `14mp9wVwDaE1blkT8aVB6g686hu-xVb5H` |
| `2026-11-21_knowledge-harvest_sprite-kit-assets.zip` | same, `sprites/assets/` | Baked sprites and backdrop layers; `kit/build.py --bake` can rebuild them (90 files) | `1t0jXOlfMULJ12W199ck0AX7_AcUJHB0i` |
| `2026-11-21_knowledge-harvest_sprite-kit-batches.zip` | same, `sprites/batches/` | Reference images attached to each ChatGPT batch (27 files) | `1QP80QlP_Bx7hzkgFsehI06CJM0aP8VRZ` |
| `2026-11-21_knowledge-harvest_sprite-kit-exports.zip` | same, `sprites/exports/` | Layer-pack exports (28 files) | `16Il-ym3zjZrY_LKxVn1OfQxTUaz5wpIN` |
| `2026-11-21_knowledge-harvest_sprite-boy-demo.zip` | `knowledge-harvest` `docs/sprite-boy-demo/` | The phone demo: reel, strips and per-chart sprites; rebuildable with `kit/make_demo.py` | `1Yo8yZwWdJ1q26R9DD_DBM0PVpOGU_A77` |
| `2026-11-20_chatgpt-overnight_passing-sprites-and-backgrounds.zip` | `qc-line` review | The 18 outputs that passed review, plus the mats drawn in code | `1HznihJiHM1MoAhiJC-8eIyVs81o4I-z0` |
| `2026-11-20_chatgpt-overnight_reference-images.zip` | overnight batch | The 14 sprite and 4 background reference images the prompts name | `1jmrAUkCQr_y2z8ss2pxggz7TTAkC9vsD` |
| `2026-11-20_chatgpt-overnight_returned-sheets-part1.zip`, `..._part2.zip` | overnight batch | Everything ChatGPT returned in run 1 (51 files), including rejected takes | `1o-mH3ZgDL8DaEg28k079kfgIeSw64WzL` (part 1), `114jAaCNnlE_0Rb7by4rn7s5d_HFqpSDA` (part 2) |
| `2026-11-21_chatgpt-batch-e_scissor-and-back-extension-sheets.zip` | `sprites/batches/2026-11-21-E/` | The four returned sheets (two kept: `JOB-01-open-hands`, `JOB-02-optional-start-edit`) | `1PtDD3tXPD2E8lLlIakwiv-hAFk2EQHMl` |
| `2026-11-21_sprite-kit-sheets-batch-e.zip` | `sprites/sheets/`, `sprites/library/images/` | The two batch E sheets now wired into `config/strips.json` (`e-scissor-jumps-c1.png`, `e-back-extension-c2.png`) and their library copies | `1DokiIilRLf75Dbh1ZG_tDhCatU3EsL0e` |
| `2026-11-21_sprite-kit-sheets-charts-4-6.zip` | `sprites/sheets/` | The nine reviewed overnight sheets now wired into `config/strips.json` for charts 4 to 6 (`ov-*.png`; the two back-extension sheets are flipped so the boy faces right) | `1-jniVN3VE17GI4P5tJTwzzJCKld1N_uV` |

Large uploads: Claude can send at most ~3 MB per file to Drive; anything bigger is handed to Charles to drag in, then checked here by file size.
