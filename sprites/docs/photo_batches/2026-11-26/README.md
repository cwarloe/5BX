# 5BX photorealistic Charts 1–2 parallel test batch

**Mobile review starts here:** [`MOBILE_REVIEW_INDEX.md`](MOBILE_REVIEW_INDEX.md) for two direct Google Drive contact sheets, tests 15–25 and Flow video 20. Technical inventories: [`REVIEW_INVENTORY.md`](REVIEW_INVENTORY.md) for Chart 1, [`CHART2_PILOT_INVENTORY.md`](CHART2_PILOT_INVENTORY.md) for Chart 2. The independent checks and [color-marker pose-control playbook](COLOR_MARKER_POSE_CONTROL_PLAYBOOK.md) record both successes and failed experiments.

**Owner instruction:** Generate/evaluate autonomously; bring back only decisions requiring Charles's human judgment. This batch is experimental; no asset is publicly approved merely because image generation succeeded.

## References and invariants

- Chart 1 movement text: `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md` (derived from the original booklet data).
- Primary identity: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` (approved v2).
- Verified Drive copy of approved blue/charcoal master: https://drive.google.com/file/d/1kS-KxLMAoH1eDa2__XYajM5E3fr58HGT/view (local SHA-256 `e305b5b7787df0bacaafad70f02e4f7a2d96535893680b78ddc3b7c6860fb28d`).
- Documentary 35mm photographic appearance, blue tank, charcoal shorts, dark socks, gray/yellow running shoes, black wristband; ordinary fair-skinned 13–14-year-old with soft unmuscular physique and natural messy hair.
- **One chart-wide identity and wardrobe.** Distinct later charts may intentionally use a different boy/outfit, including the reserved olive/gray alternate.
- **Static camera, no pan/zoom/track.** Keep enough room for the running and hop sequence; face detail should be maximized *within* necessary full-body framing.
- Generate each exercise's complete 3–4-frame still card *jointly*. When testing video, use one checked start photograph, not all card panels as forced keyframes.

## Independent assignments

| Directory | Exercise | Defining mechanics | Agent |
| --- | --- | --- | --- |
| `toe_touch/` | C1 Ex1 | Forward toe touch; stand and modest backward stretch, no outside-foot 6-inch rule | `chart1_toe_touch` |
| `partial_situp/` | C1 Ex2 | Partial rise **only enough to see heels**, arms by sides, heels down | `chart1_partial_situp` |
| `alt_leg/` | C1 Ex3 | Prone, palms under thighs, **alternate one straight leg** and head lift | `chart1_alt_leg` |
| `knee_pushup/` | C1 Ex4 | Knees and hands planted; both elbows bend, soft straight shoulder-to-knee body | `chart1_knee_pushup` |
| `low_run_video/` | C1 run | Alternating stationary low run; feet rise about **four inches**, no hop in this single test | `low_run_video` |
| `scissor/` | C1 jump | Opposing leg/arm scissor with unambiguous near/far leg swap, athletic shoes | `chart1_scissor` |

## Independent QA gates

1. **Movement:** Compare requested phase/joint/limb semantics against the *correct chart*; reject a visually plausible move copied from a harder chart or gymnast.
2. **Grounded mechanics:** Track exact planted palms, knees, feet and pelvis across panels; preserve near/far limb ownership; no duplicated limb, floating support, leg reversal, hyperextension or extra growth.
3. **Identity:** Check all frames against master face, apparent age, hair, softness, proportions and same outfit/color. Note any subtle drift separately from mechanism errors.
4. **Photographic clarity:** Detail of face, hair, cloth, shoe; real textures; stable horizon; entire figure visible. The wider static camera is intentional for running/jump; do not mark it alone as a defect.
5. **Video, if present:** True motion rather than crossfade, start/end pose registration, no loop seam, camera lock, no ghosting, no clothes/person change; require exercise form separately from smooth animation.

## Follow-on Chart 2 tests

IDs **21–25** cover (in production numbering) back extension, astride jumps, full sit-up, standard push-up, and the one-press toe touch. Each exercise's current preferred image is **conditional/provisional still only**. Separate exact prompts and QA are archived in `chart2_ex3/`, `chart2_astride/`, `chart2_ex2/`, `chart2_ex4/`, and `chart2_ex1/`. `CHART2_INDEPENDENT_QA.md` provides a second skeptical check against original booklet movement; among the hardest residuals are far-elbow/leg occlusion in strict side views, an invisible extra bounce, and arm height during astride jumps. All five retain static camera and same blue/charcoal identity; no Chart 2 video has yet been produced.

## Record per experiment

- Exact, unedited prompt submitted to model; reference filenames and roles; model/tool and settings if known.
- Generated file path and SHA-256, test number, QA grade per gate: **strong candidate**, **conditional**, or **reject**, with precise defect.
- If retrying, specify exactly one intentional variable change.
- Distinguish assistant QA from Charles's final form approval; only the latter can promote to `APPROVED`.
- Preserve rejected lessons; do not automatically publish generated pictures to a public repo.
