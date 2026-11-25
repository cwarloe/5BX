# Requirements: Bright Boy pose and chart workbench

Status: **Draft — awaiting Charles's confirmation and approval**
Owner: Charles
Last updated: 2026-11-25

## Problem

The existing [5BX Workout Mixer](../../sprites/kit/demo/page.html) is a useful interactive visual layer viewer, but the exercise producer now needs to compare **individual poses** and inspect the newer realistic middle-school photographic test cards without confusing those unapproved experiments with the original production Sprite Boy. The viewer currently plays pose cycles, changes the chart/exercise, recolors the cartoon cut-outs, and toggles scenery/props; it cannot directly step to a pose or show the 2026-11-25 photographic review catalog.

**Identification to confirm:** Charles remembers a tool once called **5BX Bright Boy**. The best repository match is `sprites/kit/demo/page.html` (**5BX Workout Mixer**) with its generator at `sprites/kit/make_demo.py`, built to the separate `sprite-boy-demo` branch and served at `workout-mixer.pages.dev`. This proposal deliberately does not assume it is the same tool until Charles confirms.

## Intended first increment

Make the existing viewer a **controlled pose-and-chart review workbench** with (a) exact pose stepping/scrubbing for selected production Sprite Boy strips, and (b) read-only links/previews of the newer photographic contact cards with explicit review status. Keep visual editing of articulated joints, generating new photos, and avatar replacement separate until a distinct proof-of-concept is approved.

## Out of scope for this increment

- No direct skeletal joint dragging, limb deformation, IK, or 3D rigged animation. Flat generated photographs are not editable body rigs.
- No AI image/video generation or consumption of credits from the browser.
- No replacement or silent approval of the original cyan/red/magenta Sprite Boy production avatar.
- No change to `data/5bx-charts.json` exercise definitions, counts, timing, or approved form.
- No import of rejected/generated raw image binaries into Git, and no background or workout app service-worker change.
- No Cloudflare deployment or merge until Charles reviews the new UI and explicitly approves release.

## Requirements

### R1. Preserve the existing working mixer

**User story:** As the 5BX producer, I want the existing chart previews, layer toggles, palette changes, and playback preserved, so a better review interface does not damage working production behavior.

**Acceptance criteria**

1. WHEN the user selects a built chart/exercise, THE SYSTEM SHALL show the same current production Sprite Boy assets and layer composition, subject to the controls that already work.
2. The system SHALL preserve play/pause, speed, all layer/prop toggles, and shorts/shoes/tank hue presets.
3. WHEN source art is not restored locally, THE BUILD SHALL state which preview media are missing rather than generate replacements or pretend a chart is complete.
4. The system SHALL read chart names and slot availability from the existing generated data derived from `data/5bx-charts.json` and `sprites/config/strips.json`.

### R2. Pose-by-pose control

**User story:** As the reviewer, I want to stop animation on any exact pose and compare the nearby poses, so foreground/background leg order, elbow position and support contacts are easy to audit.

**Acceptance criteria**

1. WHEN the user selects **Inspect poses**, THE SYSTEM SHALL pause automatic playback and display a clearly numbered pose selector and Previous/Next controls for the current exercise.
2. Selecting a pose SHALL draw that exact existing cut-out (not crossfaded with its neighbor), with a visible index such as `Pose 2 of 4`.
3. WHEN the user returns to **Play cycle**, the original timing and stage rendering SHALL resume; pose inspection SHALL NOT modify source data or asset selection.
4. The same controls SHALL be usable by keyboard and on a touch-width screen, including a visible focus state.
5. A test SHALL prove pose stepping has stable order for at least one normal exercise and one cyclic/reversing exercise.

### R3. Separate production and photographic review

**User story:** As the producer, I want to see the current photographic middle-school tests alongside the older sprite work, so I can compare them without accidentally treating an experiment as approved art.

**Acceptance criteria**

1. The viewer SHALL clearly distinguish **Production Sprite Boy** and **Photographic experiments** as separate profiles/sections.
2. The photographic section SHALL provide chart/exercise filters and a list of records with their exact numbered review IDs, statuses (`PASS` / `CANDIDATE` / `DIAGNOSTIC` / `REVIEW` / `REJECT`), source title, and links to original/prompt evidence.
3. It SHALL use a lightweight metadata manifest based on the existing 54-card dated review index. Raw experimental images SHALL stay in the user-authorized Drive archive; a private Drive link SHALL NOT be assumed to be a public embeddable image URL.
4. The photographic section MAY preview a user-selected local file inside the browser session. Such imports SHALL never upload, overwrite, or implicitly approve any source image.
5. IF an image is unavailable for inline display, THE SYSTEM SHALL show an informative link or local-import option, not a broken placeholder or false success.

### R4. Explain color control limits

**User story:** As the producer, I want to experiment with outfits while preserving normal skin and anatomy, so clothing choices do not distort the character.

**Acceptance criteria**

1. Existing shorts/shoes/tank hue controls SHALL remain active on the *transparent cartoon sprite layer* only.
2. The photographic contact-card section SHALL NOT apply global hue shifts to whole photos that would recolor skin, background, or track.
3. If photo recoloring is desired later, the UI SHALL describe it as a separate mask-based image-edit requirement and shall not label it a working feature.

### R5. Review traceability without changing approval state

**User story:** As the producer, I want to know which pose or photo I am looking at and its documented limitations, so approval decisions are evidence-based.

**Acceptance criteria**

1. Each photographic record SHALL link to the original high-resolution file and the exact prompt/QA document when accessible.
2. Visual status color SHALL include readable text; an assistant `PASS` SHALL be labeled **provisional until Charles reviews it**.
3. The workbench SHALL NOT write to `sprites/library/index.json` or mark an asset `chosen`/`expert_reviewed` merely because a user views or selects it.
4. The interface SHALL preserve explicit `near/far limb identity unknown` caveats where recorded, instead of simplifying a diagnostic marker success into form approval.

### R6. Static and testable delivery

**User story:** As the maintainer, I want a simple deployable tool and repeatable tests, so experiments are easy to review without disturbing the installed workout app.

**Acceptance criteria**

1. Existing demo assets SHALL continue to be generated by `sprites/kit/make_demo.py`; the workbench SHALL remain a static site with no new backend or login required for its basic functions.
2. Browser checks SHALL cover pose selection, play/pause handoff, chart switching, hue reset/presets, missing media, status labels, and offline/local import behavior where implemented.
3. Existing `sprites/tests` SHALL still pass, and a full regression check SHALL preserve the original stage and source status.
4. Build and deployment instructions SHALL distinguish the GitHub `main` source from the generated `sprite-boy-demo` branch and manual Cloudflare Pages deployment; updating source alone SHALL NOT be represented as a live update.

## Current grounded baseline

- Repo: `cwarloe/5BX`, branch `main`, initially inspected at `ab217f784ca8d07d1383c75d7ab376b0c5eafb4a`.
- Source UI: `sprites/kit/demo/page.html`; generator: `sprites/kit/make_demo.py`; build instructions: `sprites/OVERVIEW.md`.
- `python3 sprites/kit/line.py status`: 29 registered strips, 32 prompt recipes, 33 library records, 0 structural errors; Chart 1–3 have 6/6 mapped slots, Chart 4 has 4/6, Charts 5 and 6 have 5/6. Those are mappings/records, **not human form approvals**; source PNGs are archived outside the checkout.
- Existing sprite unit tests: 43/43 passed during investigation; resource warnings about unclosed files in `build.py` remain unrelated to this scope.
- Photographic tests: November 25 review has 54 numbered visual records (53 AI-generated outputs + one mechanical montage); individual raw assets and exact prompts are in the dated Google Drive experiment folder, and master identity remains separate from the old Sprite Boy avatar.

## Questions for Charles before design/code

1. **Is this the right tool?** The source's current name is **5BX Workout Mixer**; is it the earlier **5BX Bright Boy**, or are you remembering a different articulated modeler?
2. **What does “change poses” mean for the first update?** Recommend **select/step/scrub already-created poses** now. If you mean **drag a hand/knee/foot to change the actual anatomy**, that needs a separate articulated-rig workstream.
3. **What should the default opening mode be?** Recommend keeping **Production Sprite Boy** as the default, with **Photographic experiments** clearly selectable and unapproved.
4. **What name should appear in the UI?** Recommend **5BX Pose Workbench** with a small “Workout Mixer” subtitle, or retain the current name.

Approval of this requirements document will authorize the next repository-prescribed steps: `design.md`, `tasks.md`, incremental implementation in a feature branch, regression testing, and a preview PR for Charles. It will **not** by itself authorize production art replacement, a merge, or Cloudflare deployment.
