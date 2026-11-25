# Tasks: Workout Mixer photographic review prototype

Status: **In progress — approved first increment, 2026-11-25**

- [x] **T1: Inline photographic media review.** Add an isolated, accessible
      chart/exercise picker and browser-local image/video import/preview to
      `sprites/kit/demo/page.html`, preserve existing cartoon controls.
- [x] **T2: Transparency and backdrop proof.** Add three background scenes,
      alpha-versus-opaque feedback, and no-regeneration status copy; verify
      standing/kneeling alpha candidates without registering them in Git.
- [x] **T3a: Automated logic regression.** Check selection, local media,
      alpha detection, backgrounds, video, text-safe labels, no upload writes,
      and missing inventory; all four dependency-free checks pass.
- [ ] **T3b: Full Chromium regression.** The browser test exists and checks
      the actual page, phone layout, and legacy controls, but this environment
      has no usable Chromium executable; download is blocked (403). Run it on
      a host with Playwright Chromium before declaring full visual acceptance.
- [x] **T4: Review handoff.** Run existing tests, document demo/build limits,
      push to draft PR, and leave merge/deploy for Charles's approval.
- [x] **T5: Independent review fixes.** Improve blank-stage contrast, guard
      asynchronous image/video status, add per-exercise clear with URL cleanup,
      and identify imported videos accessibly; re-review and regression passes.
- [x] **T6: Dated review index and private-link hygiene.** Reconcile all 54
      numbered cards and four video QA observations, publish a sanitized
      status-only repository index, and label private Drive sources accurately
      without broadening their sharing permissions.

The 54-card dated archive and the two alpha candidates remain outside Git.
No task may mark experimental photographic art production-approved.
