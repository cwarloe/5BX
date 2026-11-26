# Tasks: photographic video-first exercise playback

Requirements: [requirements.md](requirements.md); design: [design.md](design.md)

Each checkbox is completed in the commit that supplies its acceptance
evidence; all engineering tasks follow Charles's requirements approval on
2026-11-26. Final exercise video admission/release is a distinct owner gate.

- [x] 1. Implement typed empty registry, exact action/chart/exercise identity,
      canonical SHA URL and full-repeat slot timing (R1.1–5, R2.3, R2.6).
- [x] 2. Implement invisible-before-validation video lifecycle, strict
      metadata/clock sync, pause/skip/error/reduced-motion cleanup (R2.1–7, R3.4).
- [x] 3. Integrate dev-flag-only photographic preview with explicit HOLD
      states and **zero sprite renders/preloads**; preserve production (R3.1–3).
- [x] 4. Add negative-path and simulated DOM lifecycle regression tests;
      integrate into Game CI test command, typecheck and development build
      (R1–R3). Real browser network/decode remains manual task 6.
- [x] 5. Confirm independent public-build artifact guard on final combined
      code; default empty registry means no new public MP4 (R1.1, R1.5,
      R3.1). Verified with `VITE_PHOTO_PLAYER_PREVIEW=1 npm run pages` and
      `node game/scripts/assert-approved-media.mjs --app-root game/public
      --app-root game/dist-pages --site-source .`; historical byte-pinned
      root-site animation reference remains outside photographic player.
- [x] 6. Review acceptance mapping; record explicit named pending browser/mobile
      checks when real browser unavailable (R1–R3). See `verification.md`:
      PHOTO-BROWSER-01/02/03 are **PENDING**, not acceptance PASS.

## Future release gate — outside this engineering PR

7. **Owner-gated video release only:** authenticated exact-video approval,
   action-specific canonical QA, byte-verified delivery and revocation before
   any nonempty registry (R1.3–5). This work remains HOLD and is not counted
   toward engineering task completion.
