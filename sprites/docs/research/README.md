# Research references for 5BX motion diagnostics

This folder preserves research inputs separately from tested 5BX standard work.

## Limb swapping and depth ordering

- [`limb-swap-depth-fix-guide.md`](limb-swap-depth-fix-guide.md): user-supplied research guide, archived **as received** on 2026-11-24. It surveys pose extraction/temporal label repair, ControlNet/OpenPose, depth and 3D controls, prompt design, multi-view consistency and QA. It includes a small Python example that operates on **per-frame pose JSON, not MP4**.
- [`../SCISSOR_JUMP_DIAGNOSTIC_RECORD.md`](../SCISSOR_JUMP_DIAGNOSTIC_RECORD.md): 5BX-specific observations, successful experiments, failures, source evidence, unanswered questions, and a proposed one-cycle test.

**Reading rule:** The guide contains links to third-party vendor articles, GitHub projects, research papers, model settings and examples. Inclusion is **not verification or endorsement** of every claim, license, API, threshold, or sample script. Treat all code and parameters as untested until inspected and applied in a disposable test. Do not turn a recommended model setting into a project requirement without a matched test result.

**Critical distinction:** Anatomical left/right remains fixed for the person. Near/far is relative to the camera and may change during motion; image-left/right changes when the person faces the camera. A color assigned by screen position is not reliable leg identity.

Raw recording and rejected media stay in the Drive archive indexed by [`ART.md`](../../../ART.md); these Markdown files contain documentation, not replacement media.

## Other identified animation research and failure records (2026-11-24)

- [`5bx-animation-repo-scout-rigby2d.md`](5bx-animation-repo-scout-rigby2d.md) preserves the [user-owned Grok Build / Repo Scout memo](https://docs.google.com/document/d/1WwEc2idsoYsw9EHDjJenNv1EtIkfe9mNxOJcYe2fVdc/edit), a combined write-up of **two separate read-only research reports**: a survey of Charles's repositories and a survey of external animation/rigging tools, papers, licenses, and visual QC options. It suggests a Rigby2D pilot but ran **none** of the named tools. This is research inventory, **not** tested 5BX production guidance; any historical prices, popularity, licenses, tool statuses, and project links require re-checking before use.
- [`5bx-animation-unbuilt-failure-brief.md`](5bx-animation-unbuilt-failure-brief.md) preserves [the earlier user-owned failure statement](https://docs.google.com/document/d/1uKSIYUezociFfpmhmdz-_6sAcg4M6UFqpiqrWBiTfZY/edit): redrawing a new person, numerical-pose tests passing while pixels were wrong, and wrong-form assets assigned to the wrong chart. It is historical diagnosis and explicitly cautions against silently editing `video/design/NOTES.md`.
- [`../FOREGROUND_TRAILING_EXERCISE_AUDIT.md`](../FOREGROUND_TRAILING_EXERCISE_AUDIT.md) applies the demonstrated occlusion lesson to **every 5BX chart and exercise** and identifies which four prompt recipes need conditional treatment.

**What is actually archived:** one user-supplied technical limb/depth research guide; one combined document containing two Repo Scout research reports; one separate historical failure brief. If Charles meant other animation reports not represented by these exact sources, they still need to be supplied or located; do not invent their contents.
