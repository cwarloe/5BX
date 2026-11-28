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
| `tools/video_finish/` | Turns a white-background clip into a looping gym video at the reference proportion: loop finder, measuring, person cut-out, placement, checks. Settings and per-clip data in its `config.json`; order of steps, rules and known mistakes in its `README.md` |
| `tools/gravity_check/` | **TEST ONLY.** Measures how floaty an AI-generated jump is (apparent gravity from the pelvis's arc) and retimes airborne frames to 9.81 m/s². Not wired into any pipeline; first test used a legacy outdoor-track clip. See its `README.md` |
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

Use a full spec where shared design and acceptance evidence materially reduce
rework: substantial cross-component or user-facing changes, risky behavior,
or multi-agent handoffs needing more than a PR description. For small,
reversible, preauthorized changes, a clear PR and reproducible tests are
sufficient even when several files change or the behavior is testable.
Full guide: https://github.com/cwarloe/lessons-learned/blob/main/SPEC_DRIVEN_DEVELOPMENT.md

- Specs live in `specs/<feature-slug>/` (requirements.md, design.md, tasks.md).
  Start a new one by copying `specs/_template/`.
- Before writing code for a feature, read its spec. If there is no spec and the
  change qualifies, write `requirements.md` first. For a new, unapproved feature,
  wait for Charles to approve the requirements before design and implementation.
  For a feature already inside an **explicitly approved workstream**, an agent
  may continue through design, tasks, tests and a low-risk engineering PR without
  repeating that approval ceremony. Record the approved scope and acceptance
  evidence in the spec or PR; new material scope changes still require approval.
- Dependent tasks run in order. Independent tasks may run in parallel when file
  ownership and integration are clear; check each task off in its completion
  commit.
- If the code needs to differ from the spec, update the spec first.
- A feature is done when every acceptance criterion maps to a passing test or a
  named manual check.

This procedural exception never overrides `AGENTS.md`: Charles still accepts
each final exercise video, and historical motion/safety, avatar identity,
paid usage, private-data access and public release decisions retain their
separate approval boundaries. A passing test or an agent's assertion cannot
stand in for the owner decision.
