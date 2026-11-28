# 5BX photographic pilot: mobile production traveler

## Chart 1 working traveler

**[Open the Chart 1 video production traveler](chart1.html)** for the practical five-exercise, six-movement handoff. Each expandable section links the current source/reference card, individual high-resolution PNGs, clean copyable prompt(s), available white motion proof, and returned-video handoff. Retired diagnostic visual candidates are folded under Archive in the traveler and moved one level down to the exercise's Drive `archive` folder.

**[See the Chart 1 production workflow diagram](CHART1_WORKFLOW.md)** for the reference → white motion proof → integrated static gym render → three-repetition loop → editable HTML title/timer → QA/review sequence.

The current prompts in Drive and the traveler are proposed **gym-pass** prompts unless an exact historical Flow submission is explicitly evidenced; neither a saved prompt nor a review clip is automatic movement approval. The page works as one standalone HTML file, including from disk. It stores returned handoff links only in browser-local storage and does not upload videos. The older gallery (`index.html` + `data.json`) remains the independent photographic pilot archive.

## Why this exists

The photographic tests had a detailed GitHub markdown archive and many Drive images, but on a phone the user had to guess which numbered file was current. This page makes one **read-only, mobile-first station** for all six charts, current conditional candidate/rejected status, direct Google Drive art and comparisons, prompts, and a separate footer of full-resolution starting stills.

## Data contract

- `index.html` is a dependency-free static page; responsive cards, chart/status filters and search; links open Drive/Flow directly (no ZIP or GitHub download required).
- `data.json` is the curated source. One object per numbered photographic test; the `status` vocabulary is `candidate`, `conditional`, `hold`, `reject`, or `video-unverified`.
- `driveId` is the high-resolution contact-sheet asset; `url` is used only for external Flow video when a Drive ID is unavailable. `stills` and `variants` preserve direct source/diagnostic links.
- `prompt` references exact archived prompts where available. Absence of a prompt link **does not** imply an approved/reproducible take.
- `note` is the honest exercise-specific defect/next review criterion. Nothing is automatically approved based on technical color/registration checks.

To view locally (do not open as `file://`, because the page fetches `data.json`):

```sh
cd photo-traveler
python -m http.server 8000
```

Visit `http://localhost:8000/`. Published from the 5BX repo root, its intended path is `/5BX/photo-traveler/` on GitHub Pages; verify the actual deployed site rather than assuming it is live immediately.

## Update standard work

1. After a new photo batch, **retain** its high-resolution Drive image and exact generation prompt; never overwrite a rejected take.
2. Add or revise the corresponding `cards` entry in `data.json` with stable test ID, chart, current disposition, one primary link, note, compare/diagnostic variants and stills.
3. Do not infer human form approval from an assistant self-review or machine image-QA PASS. If a pose has unsafe elbow/knee angles, mark `hold`; explicit user-rejected takes remain accessible only as variants.
4. Run `node photo-traveler/test_traveler.cjs` before publishing.
   Run `node photo-traveler/test_sw_exemption.cjs` if the root PWA service-worker navigation rules change.
5. Open the traveler at mobile width, test a direct full-resolution Drive link, a prompt link, the status filter, and any new thumbnail fallback. Thumbnail previews may be blocked by Google account permissions; the direct full-resolution Drive link is authoritative.
6. Once the companion [card consistency checker](../sprites/docs/photo_batches/2026-11-26/card_consistency_qa/README.md) emits a structured QA result for a new card, the result may be added as separate evidence, **never as automatic human approval**.

This initial ledger includes **28 photographic pilots** across all six charts, plus variant comparisons and individual high-resolution still references. It is deliberately not a second app, sprite-asset registry or animation generator.

## Production PWA cache boundary

The root workout app registers an offline-first `sw.js`. It originally exempted only the sibling arcade game. A same-origin navigation to `/photo-traveler/` would otherwise be cached under the root workout `./index.html` key, risking a wrong offline home screen. Release `5bx-v20` adds a narrow `photo-traveler/` route exemption for the gallery page and manifest; the existing workout page, assets and game paths retain their original behavior.

The app home now has a single non-disruptive link beneath **Today's targets** reading **Explore experimental photo exercise poses**. It opens the gallery separately and does not alter workouts, progress data or pose assets.
