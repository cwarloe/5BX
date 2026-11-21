# Project instructions: 5bx-video-game

`AGENTS.md` is the App Builder platform contract and is left as shipped. This
file covers what is specific to this repo. Where they differ, this file wins.

## Spec-driven development

This repo uses spec-driven development for features that take more than one
sitting, touch several files, or have testable behavior. Small fixes skip it.
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

## Source of truth for 5BX numbers

Exercise counts, step targets, timings, and chart wording come from
`data/5bx-charts.json` in the `cwarloe/5BX` repo, transcribed from the 1965 RCAF
booklet. Do not type chart numbers by hand from memory.

## Sprite frame rule

Frame counts per action follow the beats in the chart text and the original
RCAF figures (see the HARD RULE comment in `src/lib/levels.ts`). Never pad or
truncate an exercise to a fixed frame count.
