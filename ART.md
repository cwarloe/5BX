# 5BX art: where everything lives

**Rule:** art the app, game or video actually uses is committed in this repo.
Raw and in-progress art (ChatGPT batches, rejected takes, source sheets, clips
that aren't shipped) lives in Google Drive, never in Git.

**Drive folder:** [Sprite Art 5BX Workout](https://drive.google.com/drive/folders/1x7ZrBMan7-jSXgYnZeOZzmEc_of0sRzE)
(owner: Charles; maintained by Claude; Charles does not edit it by hand).

**Browsable production inputs:** [Production Art](https://drive.google.com/drive/folders/17LK1ric6Y1tQ0adA-UkJuYNvaCffzDmN).
The four indexed production-input ZIPs have also been extracted here as
individual PNGs (124 files): `sheets/`, `assets/` and `library/images/`.
Folders preserve the paths the sprite kit expects, so a file can be viewed or
restored by itself. The original ZIPs remain in the parent folder as backups.

For newly produced files, use the stable asset-ID naming rule below. Dated
`YYYY-MM-DD_<source>_<what-it-is>.<ext>` names identify historical transfer
bundles; keep the original names of extracted production assets unchanged.

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
ZIPs are optional snapshots, not a required production format. Store **working
source art as individual Drive files**. Keep the preserved relative paths under
`Production Art` for existing files; add new art in its appropriate folder and
record its Drive ID in `direct_files` in the recovery index. Create a ZIP only
when a batch backup or transfer actually calls for one. Do not add another
packaging step to the normal artwork process.

### Find exactly what to restore

The read-only recovery index at `sprites/config/art-archive-index.json` supports
**direct Drive files first** (including the extracted production inputs) and
records the verified contents, Drive IDs and SHA-256 of four historical
source/baked-asset ZIPs as fallback.
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
| `2026-11-24_video-game-5bx_chart1-corrected-cadet-frames/` (folder, 11 JPGs, 3.1 MB) | `cwarloe/video-game-5bx` `assets/sprites/chart1-corrected/` (commits of 2026-11-24, after the repo was meant to retire) | Cartoon cadet Chart 1 key frames redrawn from the rewritten 5BX prompts: stretch (arms up, floor, backbend), partial sit-up up/down, back raise each leg, knee push-up up/down, low run, scissor. Historical cartoon reference; the photographic Mark is the current direction | [`1XAMTfojs-3Kgn_81hV4uNTBt4Jze4Mc3`](https://drive.google.com/drive/folders/1XAMTfojs-3Kgn_81hV4uNTBt4Jze4Mc3) |

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

## Reference-only art: accepted running depth depiction (2026-11-24)

| Drive file | Status / permitted use | Drive ID |
|---|---|---|
| [`2026-11-24_near-trailing-leg-running-reference-4poses.png`](https://drive.google.com/file/d/1lSzvp-SjsNDOClhmQquGk7tqUAmb1HAh/view) | User-confirmed **foreground-trailing-leg hip occlusion** for a right-facing running figure. Illustrative source/QA reference only; **not** accepted scissor-jump form, canonical character replacement, or shipping art. See [portable rule](sprites/docs/FOREGROUND_TRAILING_LEG_RULE.md). | `1lSzvp-SjsNDOClhmQquGk7tqUAmb1HAh` |

## Scissor-jump inverse endpoint experiments (2026-11-24; reference only)

All files below remain **unapproved as exercise-form or released art** in the existing *Sprite Art 5BX Workout* Drive folder. On 2026-11-24 Charles accepted the **near-trailing six-pose sheet for depth/silhouette only**; that is not a completed exercise or animation approval. None replaces an entry in the sprite library.

| File | Experiment and disposition | Drive ID |
|---|---|---|
| [`2026-11-24_scissor-near-leading_6pose-experiment.png`](https://drive.google.com/file/d/1kHIR9Lg5R2MCPpcFmj96fHW-zn9W5_Aw/view) | Six separate right-facing **near-leg-leading** variations; candidate inverse hip occlusions; not human approved | `1kHIR9Lg5R2MCPpcFmj96fHW-zn9W5_Aw` |
| [`2026-11-24_scissor-paired-depth_same-overlap-failure.png`](https://drive.google.com/file/d/1tRxbi4nNx94FmKJnIUpmPP8kG_owggQW/view) | Six-pose paired A/B request **failed**: both columns have near-identical hip/shorts topology despite explicit inversion instruction; keep for failure diagnosis | `1tRxbi4nNx94FmKJnIUpmPP8kG_owggQW` |
| [`2026-11-24_scissor-near-trailing_6pose-experiment.png`](https://drive.google.com/file/d/10-yl-i3xjLPJulv7tImmCAW4QP_-DJJ3/view) | Six right-facing **near-leg-trailing** variations. **Charles approved the foreground-trailing hip overlap only** (2026-11-24); form, anatomical leg continuity, avatar replacement and released art remain unapproved | `10-yl-i3xjLPJulv7tImmCAW4QP_-DJJ3` |


## 1959 RCAF film-to-sprite reference test (2026-11-24)

All **10 files** below are verified in the user's existing [Sprite Art 5BX Workout / 2026-11-24 film-to-sprite experiment folder](https://drive.google.com/drive/folders/1_xuq2ZA8rGe1d750EDxP8pcPPg8ejgJO). The 1959 film's original stills already have their own committed reference copy in [`docs/reference/rcaf-1959-stills/`](docs/reference/rcaf-1959-stills/). This new batch is supplementary user-supplied comparison art, two **unapproved** candidate generations, two supplied test videos, and the dated lessons log. Experimental data stays in Drive; do **not** add it to the shipping sprite library or direct-file production restore index merely because it is listed here.

| Asset in Drive | Role | Direct Drive ID |
|---|---|---|
| [`reference-existing-sprite-pushup-and-pike-row.webp`](https://drive.google.com/file/d/1qxOM1cRtwtNhM4OMG7s-ltyC5omrxmWx/view) | Previously generated cyan/red push-up and pike row | `1qxOM1cRtwtNhM4OMG7s-ltyC5omrxmWx` |
| [`reference-1959-forehead-chin-comparison.webp`](https://drive.google.com/file/d/18zROV44S5Lxz1yMmVWqHXn0SoIANh-bY/view) | Historic film compared with an earlier sprite row | `18zROV44S5Lxz1yMmVWqHXn0SoIANh-bY` |
| [`reference-existing-pike-farside-shading.webp`](https://drive.google.com/file/d/1fiQVgpDgfIZCDlaAWOezqWUvBkDrZ8U5/view) | Existing pike with about 10% darker far-side shading | `1fiQVgpDgfIZCDlaAWOezqWUvBkDrZ8U5` |
| [`reference-1959-film-montage-forehead-0832.webp`](https://drive.google.com/file/d/1-Lh2Kb8aDa_d0S_4R6rei8_MGjcoUOx6/view) | 1959 RCAF film reference frame montage | `1-Lh2Kb8aDa_d0S_4R6rei8_MGjcoUOx6` |
| [`reference-1959-film-montage-forehead-0835.webp`](https://drive.google.com/file/d/1YE1C4NJmB9UDfnlv2cFkuFGR5JjmVFwY/view) | Alternate forehead frame montage | `1YE1C4NJmB9UDfnlv2cFkuFGR5JjmVFwY` |
| [`candidate-forehead-pike-photo-guided-v2.png`](https://drive.google.com/file/d/1-DpynvTovobEC2AMwO-Fhrp4nNAO-P6M/view) | Film-guided individual forehead-pike **candidate**, exact contact unverified | `1-DpynvTovobEC2AMwO-Fhrp4nNAO-P6M` |
| [`candidate-ninepose-1959-film-to-sprite.png`](https://drive.google.com/file/d/18V_VlUk-iu7tYh6tSFKcj5zVZUdcwtWa/view) | Film-guided nine-pose **candidate**; not approved for animation | `18V_VlUk-iu7tYh6tSFKcj5zVZUdcwtWa` |
| [`reference-test-transition-closeup-v2.mp4`](https://drive.google.com/file/d/1_6Vea5SP8Ieaw5mjALgh1aPk3uRF_Smb/view) | User-supplied 13.33 s / 24 fps test clip; motion not reviewed here | `1_6Vea5SP8Ieaw5mjALgh1aPk3uRF_Smb` |
| [`reference-test-transition-stitch.mp4`](https://drive.google.com/file/d/1k0SrnP9RpDbt2wpM_hM-sdKOYuNqdaMI/view) | User-supplied 123.92 s / 24 fps test clip; motion not reviewed here | `1k0SrnP9RpDbt2wpM_hM-sdKOYuNqdaMI` |
| [`5BX-film-to-sprite-pose-transfer-lessons-2026-11-24.md`](https://drive.google.com/file/d/1LiWokOiRDVpwJ7A6suD0guwcKe2xCeBs/view) | Archived process notes; canonical proposed repo copy at [`sprites/docs/FILM_TO_SPRITE_POSE_TRANSFER_2026-11-24.md`](sprites/docs/FILM_TO_SPRITE_POSE_TRANSFER_2026-11-24.md) | `1LiWokOiRDVpwJ7A6suD0guwcKe2xCeBs` |

The [lesson record](sprites/docs/FILM_TO_SPRITE_POSE_TRANSFER_2026-11-24.md) specifies source-film authority, what worked, failure modes, no-ballet-foot and camera-angle rules, high-detail → posterize → cartoonize as an **untested** comparison, a proposed realistic-posterized avatar A/B test, and required human form review.
