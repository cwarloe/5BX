# 5BX: project instructions

Everything 5BX lives in this repo. Do not start a new 5BX repo or copy 5BX
material into another one.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `app.js`, `sw.js`, `styles.css` | The workout app (PWA). Stays at the repo root so existing home-screen installs keep working |
| `data/5bx-charts.json` | **Single source of truth** for every rep count, step target, time and chart description. The app, the game and the video builder all read it |
| `figures/` | Booklet exercise illustrations |
| `tests/` | End-to-end tests for the workout app (`npm test`) |
| `video/` | Chart video builder (`video/chart.py`) |
| `game/` | The arcade game (TanStack/Vite). Its own instructions: `game/AGENTS.project.md` |
| `sprites/` | The sprite kit: builds the exercise video from pose strips, makes the ChatGPT/Grok prompts and batches, keys sheets, checks backgrounds. Start at `sprites/OVERVIEW.md` |
| `sprites/qc-line/` | A second, smaller pipeline (sheet QC, cut-out manifest, he/she prompt tokens, mats drawn in code). To be ported into the kit, then deleted |
| branch `sprite-boy-demo` | The built 5BX Workout Mixer demo page (generated; about 57 MB, not on `main`). Hosted on Cloudflare Pages at https://workout-mixer.pages.dev/, not on GitHub Pages; how to refresh it is in `sprites/OVERVIEW.md` |
| `specs/` | Feature specs (see below) |
| `.github/workflows/pages.yml` | Publishes the app at `/5BX/` and the game at `/5BX/game/` |

Large raw art (ChatGPT batches, rejected takes, source sheets) does not go in
this repo. It lives in the Google Drive folder **Sprite Art 5BX Workout**; see
`ART.md` for the index. Only art the app, game or video actually uses is
committed here.

## Rules

- Never type chart numbers from memory; read `data/5bx-charts.json`.
- `sw.js` ignores everything under `./game/`. Keep it that way, or a visit to
  the game overwrites the workout app's offline home page.
- After any change to app files, bump `CACHE` in `sw.js`.

## Spec-driven development

Use a spec for features that take more than one sitting, touch several files,
or have testable behavior. Small fixes skip it.
Full guide: https://github.com/cwarloe/lessons-learned/blob/main/SPEC_DRIVEN_DEVELOPMENT.md

- Specs live in `specs/<feature-slug>/` (requirements.md, design.md, tasks.md).
  Start a new one by copying `specs/_template/`.
- Before writing code for a feature, read its spec. If there is no spec and the
  change qualifies, write `requirements.md` first and wait for Charles to
  approve it, then design, then tasks.
- Work one task at a time; check it off in the commit that completes it.
- If the code needs to differ from the spec, update the spec first.
- A feature is done when every acceptance criterion maps to a passing test or a
  named manual check.
