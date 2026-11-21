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

## In Drive

| File | From | What it is | Drive ID |
|---|---|---|---|
| `2026-11-19_video-game-5bx_chart1-sprites-4frame-padded.zip` | `cwarloe/video-game-5bx` `public/sprites/` | Chart 1 sprites padded to 4 frames each. Superseded: they break the frame-count rule; kept for reference | `1JOrpcqu0AJ14qBgk0gB2yeG-7mJ5qerK` |

## Not yet in Drive

| What | Where it is now | Why |
|---|---|---|
| Cadet video-to-sprite pipeline (raw/clean frames, 63 MB) | `cwarloe/video-game-5bx` `assets/sprites/video2dsprite/cadet/` | Too large for a single upload from Claude; awaiting a decision |
| Exercise film clips (8 MP4s, 16 MB) | `cwarloe/video-game-5bx` `public/video/` | Same |
| Sprite-boy playbook, ChatGPT batches, 84 sprites, strips, reel | `cwarloe/knowledge-harvest` branches `ccr-f07b2184-lqmygq`, `add/exercise-sprite-video-playbook`, `gh-pages` | Still being worked on; moves in the second consolidation PR |
| Sprite/video lessons learned | `cwarloe/lessons-learned` branch `ccr-f07b2184-lqmygq` (`AI_SPRITE_VIDEO_LESSONS.md`) | Same |
