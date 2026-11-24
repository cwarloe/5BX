# Research references for 5BX motion diagnostics

This folder preserves research inputs separately from tested 5BX standard work.

## Limb swapping and depth ordering

- [`limb-swap-depth-fix-guide.md`](limb-swap-depth-fix-guide.md): user-supplied research guide, archived **as received** on 2026-11-24. It surveys pose extraction/temporal label repair, ControlNet/OpenPose, depth and 3D controls, prompt design, multi-view consistency and QA. It includes a small Python example that operates on **per-frame pose JSON, not MP4**.
- [`../SCISSOR_JUMP_DIAGNOSTIC_RECORD.md`](../SCISSOR_JUMP_DIAGNOSTIC_RECORD.md): 5BX-specific observations, successful experiments, failures, source evidence, unanswered questions, and a proposed one-cycle test.

**Reading rule:** The guide contains links to third-party vendor articles, GitHub projects, research papers, model settings and examples. Inclusion is **not verification or endorsement** of every claim, license, API, threshold, or sample script. Treat all code and parameters as untested until inspected and applied in a disposable test. Do not turn a recommended model setting into a project requirement without a matched test result.

**Critical distinction:** Anatomical left/right remains fixed for the person. Near/far is relative to the camera and may change during motion; image-left/right changes when the person faces the camera. A color assigned by screen position is not reliable leg identity.

Raw recording and rejected media stay in the Drive archive indexed by [`ART.md`](../../../ART.md); these Markdown files contain documentation, not replacement media.
