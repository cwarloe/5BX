# Requirements: Complete Chart 1 and add Charts 2–3

Status: Draft
Owner: Charles
Last updated: 2026-11-20 (moved into cwarloe/5BX)

## Problem

The game offers only three levels (Chart 1: D-, D, D+), so a user outgrows it
in a few weeks. The 5BX plan has 12 levels per chart, and the age-group targets
for most adults sit on Charts 2–3. Sprites for several Chart 2–3 movements
already exist in this repo but are not reachable.

## Out of scope

- Charts 4–6.
- Saving workout history or automatic level-up (separate spec: progression).
- The run/walk alternatives (½ mile run, 1 mile walk, etc.).

## Requirements

### R1. Every level of Charts 1–3

**User story:** As someone following 5BX, I want every level from Chart 1 D-
through Chart 3 A+, so that I can keep using the game for months instead of
weeks.

**Acceptance criteria**

1. THE SYSTEM SHALL offer 36 levels: D-, D, D+, C-, C, C+, B-, B, B+, A-, A, A+
   for each of Charts 1, 2, and 3, in that order.
2. THE SYSTEM SHALL use, for each level, exactly the reps for exercises 1–4 and
   the steps for exercise 5 given in `data/5bx-charts.json` (repo root).
3. THE SYSTEM SHALL keep the per-exercise times at 2:00, 1:00, 1:00, 1:00, and
   6:00 on every chart.
4. THE SYSTEM SHALL label each level with its chart and level (for example,
   "Chart 2: C+").

### R2. Chart-correct exercises

**User story:** As a user on Chart 2 or 3, I want the exercise names, cues, and
animation to match my chart, so that I do the right movement.

**Acceptance criteria**

1. WHEN a level is selected THE SYSTEM SHALL show that chart's exercise names
   (for example, Chart 3 exercise 4 is "Chin-forehead push-up").
2. WHEN the stationary run reaches each 75-step mark THE SYSTEM SHALL cue the
   chart's interval movement: scissor jumps (Chart 1), astride jumps (Chart 2),
   or half knee bends (Chart 3), 10 per interval.
3. WHEN an exercise has a chart-specific sprite set THE SYSTEM SHALL animate
   with it, using the frame count that matches that movement's beats.
4. IF a chart-specific sprite set does not exist for an exercise THEN THE
   SYSTEM SHALL <see open question 1> rather than silently showing a different
   movement.

### R3. Existing users keep their place

**User story:** As someone already using the game, I want my saved level to
still work after the update.

**Acceptance criteria**

1. WHEN a stored level from the current version ("D-", "D", or "D+") is loaded
   THE SYSTEM SHALL select the same level on Chart 1.
2. IF the stored level value is missing or unrecognized THEN THE SYSTEM SHALL
   select Chart 1 D-.

### R4. Choosing a level on a phone

**User story:** As a user on a phone, I want to pick from 36 levels quickly.

**Acceptance criteria**

1. THE SYSTEM SHALL let the user choose chart and level separately (or an
   equivalent control) without scrolling through a 36-item list.
2. THE SYSTEM SHALL remember the last selected chart and level between visits.

## Open questions

1. **Missing sprites.** Chart 2 needs new art for the full sit-up, both-leg
   back extension, and full push-up. Chart 3 needs the hands-behind-head sit-up
   and hands-behind-back extension. Until that art exists, should the game:
   (a) reuse the closest Chart 1 sprite and show the correct name and cue
   (recommended; ships sooner), (b) hide Charts 2–3 until the art exists, or
   (c) make the art part of this spec?
2. **Data sharing.** Now that the game lives in the same repo as
   `data/5bx-charts.json`, should the game import it directly at build time
   (recommended: one copy, no drift) or keep a typed copy with a test?
3. **Sprite folders `c3-toe` and `c4-toe`.** Are these drafts of Chart 3/4 toe
   touching that replace `toe-multi`, or leftovers to delete?
