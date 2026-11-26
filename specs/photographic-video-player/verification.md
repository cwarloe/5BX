# Photographic player engineering verification (2026-11-26)

**Engineering status:** synthetic/CI checks pass; named real-browser checks below
are **PENDING**, not passed. **Photographic footage release: HOLD.** Charles's
chat requirements approval is not an authenticated exact-video approval. No
Flow credits, actual exercise media, owner evidence, or registry entries are
included here.

## Requirement-to-evidence map

| Requirement | Engineering evidence | Deliberately unverified / release boundary |
| --- | --- | --- |
| R1.1–2 empty registry, no sprite fallback | `photo-video.test.ts`; synthetic DOM missing/invalid/error tests; combined `assert-approved-media` passes | Any actual workout clip remains HOLD |
| R1.3–4 provenance and exact chart/exercise/action/revision/SHA | Pure tests reject wrong chart/exercise/action, null or malformed registry, wrong revision/hash, forged interval; running and scissor have separate keys | Authenticated Charles owner event and action-level canonical QA are **not implemented**; future trusted registry-generation/release step |
| R1.5 strict origin and bytes | Pure URL tests reject off-origin, arbitrary paths, traversal and digest/name mismatch; Pages/public artifact scan rejects unapproved videos | The browser cannot prove response-byte identity. Future deployment gate must hash *served* bytes against owner-accepted digest and support revocation |
| R2.1–3 time and segments | Simulation-derived 40s jog/5s scissor slots and frame/metadata tests; no autoplay before validation, pause/seek loop; 6s jump rejected | Real browser decoder and A→C→A visual review await footage |
| R2.4–6 invisible until full-loop admitted | Synthetic DOM tests: hidden before metadata, 5.05s rejected, seek-before-reveal, source removal on error/unmount/segment; pure timing tests reject 5.01s, 5.05s, 6s, 4.95s, accept exact 5.00s as **duration-only** | Actual decoded playable duration and seam quality require later per-asset motion QA; exact 5.00s alone never admits a clip |
| R2.7 drift and lifecycle | Runtime seeks when clock deviates by more than 1/FPS; 13 jsdom tests cover StrictMode, pause/segment switch, error, reduced motion, pending `play()` AbortError, rejected browser play promise, stale seek completion after the last simulation tick, and a seek-in-flight frame-visibility guard | Real Chrome/Safari decode/seek, background/resume, phone timing pending manual check |
| R3.1 production isolation | `import.meta.env.DEV && VITE_PHOTO_PLAYER_PREVIEW === "1"`; `VITE_PHOTO_PLAYER_PREVIEW=1 npm run pages` succeeds; production JS contains no photographic player strings | Public default sprite experience intentionally unchanged until media release |
| R3.2 no photo-preview sprites | Source audit: `new Image()` preload and upcoming HUD `<img>` strictly behind `!photoPreview`; synthetic DOM has no sprite fallback; independent reviewer corroborated | Actual browser Network panel `/sprites/` count is **PENDING MANUAL** |
| R3.3–4 accessible HOLD/opt-in | Labeled video and status/HOLD, keyboard-operable button, live reduced-motion toggle/opt-in/reset DOM tests | Mobile layout, keyboard/assistive-tech smoke pending manual |

## Repeatable engineering commands (repo root unless indicated)

1. `cd game && npm ci --no-audit --no-fund && npm test && npm run typecheck && npm run build:dev`
2. `cd game && VITE_PHOTO_PLAYER_PREVIEW=1 npm run pages`
3. `node game/scripts/assert-approved-media.mjs --app-root game/public --app-root game/dist-pages --site-source .`

The Game CI workflow repeats the test, typecheck, dev build, Pages build and
media gate. Pages deployment independently checks the assembled `_site` before
upload. The root site retains only the separately byte-pinned *historical*
animation-reference exception; no photographic clip exception exists.

## Named PENDING real-browser smoke checks

**PHOTO-BROWSER-01 — Empty-registry dev preview, desktop/mobile:** In actual
Chrome and Safari with a development build, set
`VITE_PHOTO_PLAYER_PREVIEW=1`, start workout, skip across exercise 5's jog and
scissor segments. Check unavailable text, no video or cartoon frames, and
DevTools Network **zero `/sprites/` requests** (including preloads and upcoming
HUD). Check widths 320px/375px, no clipping, 44px control targets, keyboard
focus, screen-reader status and reduced-motion opt-in. Neither local executor
nor its Playwright wrapper currently has a working browser binary.

**PHOTO-BROWSER-02 — Real decoder with isolated synthetic fixture:** In a
controlled local dev test harness only, provision a synthetic, non-exercise
test MP4 with a matching *test-only* registry. Assert no visible frame or
`.play()` before trusted admission + metadata + clock-aligned seek; exercise
pause/resume, 40s/5s swap, skip, background/resume, live reduced-motion
toggle, `play()` rejection and unmount. Confirm every prior source is unloaded.
No fixture is added to the shipped empty registry or public output.

**PHOTO-BROWSER-03 — Production flag denial:** In production/Pages build with
`VITE_PHOTO_PLAYER_PREVIEW=1`, confirm a query string cannot enter photographic
preview and normal published workout remains unchanged. Automated production
bundle inspection already verifies the player is absent from JS, but browser
visual comparison is pending.

## Real-browser attempt record — 2026-11-26 (BLOCKED)

The independent post-merge reviewer attempted the prescribed local browser QA
without user involvement or publishing any media:

1. `cd game && VITE_PHOTO_PLAYER_PREVIEW=1 npm run dev -- --host 127.0.0.1 --strictPort`
   started Vite successfully and reported `http://127.0.0.1:8080/`. The dev
   server was stopped after this attempt.
2. `cd game && node scripts/browser-smoke.mjs http://127.0.0.1:8080/ /workspace/screenshots/5bx-photo-dev.png`
   exited **1** before opening a page: Playwright reported that its
   `chromium_headless_shell-1248` executable was missing from the local browser
   cache. Neither desktop nor mobile screenshots or browser verdicts were
   produced. The system `chromium` command was also an unusable launcher: its
   expected Chromium executable was absent. No usable `agent-browser` or
   Firefox executable was found.
3. A separate cloud Chrome browser attempted the same loopback URL and
   returned `net::ERR_HTTP_RESPONSE_CODE_FAILURE` rather than the local Vite
   app. That browser does not share the executor's loopback server.

No browser package/OS installation, network tunnel, permission override,
sign-in, public deployment, synthetic or actual MP4 upload, or paid service
was used to work around the blocker. **PHOTO-BROWSER-01/02/03 all remain
PENDING**: no live visual/layout, sprite network, video decoding/playback, or
production UI behavior was observed. Existing pure/DOM tests and production
bundle checks are separate evidence and do not constitute real-browser PASS.
To complete these checks, provision an authorized Chrome/Playwright headless
binary in the same executor as the dev server (and Safari separately for the
specified platform coverage), then rerun the named checks above.

## Lessons retained for the next iteration

- StrictMode rehearses effect cleanup/setup without replacing the DOM video;
  an admitted source removed in rehearsal must be restored safely and still
  revalidated before visibility/playback.
- An outstanding browser `play()` Promise may reject *after* an intentional
  pause; invalidate obsolete attempts so that expected interruption does not
  permanently HOLD a valid clip. A genuine current rejection still HOLDs.
- A seek requested for an earlier workout tick can complete after the final
  newer tick, such as when a tab is backgrounded or a workout pauses. The
  `seeked` event now aligns the video to the latest clock before revealing a
  frame; synthetic DOM regression evidence is not a real-browser verdict.
- No full-loop or SHA-looking metadata is proof of exercise-form quality,
  owner decision, or served bytes. Keep release authority outside the player.
