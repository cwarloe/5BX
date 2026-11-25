# Tasks: Workout Mixer photographic review prototype

Status: **Implementation complete, pending Charles's visual approval — 2026-11-25**

- [x] **T1: Inline photographic media review.** Add an isolated, accessible
      chart/exercise picker and browser-local image/video import/preview to
      `sprites/kit/demo/page.html`, preserve existing cartoon controls.
- [x] **T2: Transparency and backdrop proof.** Add three background scenes,
      alpha-versus-opaque feedback, and no-regeneration status copy; verify
      standing/kneeling alpha candidates without registering them in Git.
- [x] **T3a: Automated logic regression.** Check selection, local media,
      alpha detection, backgrounds, video, text-safe labels, no upload writes,
      and missing inventory; all four dependency-free checks pass.
- [x] **T3b: Full Chromium regression.** GitHub-hosted Playwright Chromium
      exercised the actual page, legacy controls, local image/video preview,
      and 390-pixel mobile layout; all four browser checks passed. Human visual
      acceptance is a separate review gate.
- [x] **T4: Review handoff.** Run existing tests, document demo/build limits,
      push to draft PR, and leave merge/deploy for Charles's approval.
- [x] **T5: Independent review fixes.** Improve blank-stage contrast, guard
      asynchronous image/video status, add per-exercise clear with URL cleanup,
      and identify imported videos accessibly; re-review and regression passes.
- [x] **T6: Dated review index and private-link hygiene.** Reconcile all 54
      numbered cards and four video QA observations, publish a sanitized
      status-only repository index, and label private Drive sources accurately
      without broadening their sharing permissions.
- [x] **T7: CI browser visual gate.** GitHub Actions run 45713407036 passed
      the four Playwright checks plus four DOM checks and archived desktop/mobile
      fixture screenshots; existing sprite preflight run 45713407062 also passed.
- [x] **T8: Real-build reel repair.** Rebuild the demo with registered sprites,
      fix FFmpeg caption escaping, verify a complete reel and chart clips,
      and record exact unregistered movement gaps.

The 54-card dated archive and the two alpha candidates remain outside Git.
No task may mark experimental photographic art production-approved.
