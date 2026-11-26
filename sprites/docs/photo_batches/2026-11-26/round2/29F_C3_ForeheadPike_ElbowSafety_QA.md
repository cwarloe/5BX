# Chart 3 5BX forehead-pike: user-reported elbow geometry concern and 29F diagnostic

**2026-11-26 UTC · assistant visual QA only, not medical or human form certification.** The user correctly called attention to a neglected acceptance criterion: some deep V/forehead-push-up pictures force the forehead close to hands/track by drawing cocked or implausibly contorted elbows. Previous self-QA called 29E's elbows "natural" without independent visible-joint scrutiny; that positive assessment is **withdrawn** pending a qualified movement review.

## Files and evidence

- Original `artifacts/parallel_batch_20261126/chart3_ex4/29E_C3_ChinForehead_FourPhase_Headroom_CANDIDATE.png`: left-facing four-phase card A/B/C/D. Panel C pike has forehead almost on track, shoulder/upper-arm arching around head, strong near-elbow bend, far elbow/forearm partly hidden. 29E's correct **head-behind-hands** topology is *not* sufficient to call it a safe/normal demonstration.
- Original accepted identity master `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` — appearance only.
- Older less-deep `artifacts/parallel_tests/v_pushup_realistic/02_almost_there.png` — comparatively less compressed elbow/shoulder shape, a reasonable *pose-reference* but not itself form-certified.
- Original adult RCAF 1959 still `artifacts/restore_build_20261125/build_source/docs/reference/rcaf-1959-stills/ex4-c3-forehead-08m32s0.png` — historical movement authority, **not** the permitted mobility envelope of a typical 13–14yo.
- New `29F_C3_ForeheadPike_ShallowHead_NaturalElbow_DIAGNOSTIC.png`: ONE built-in imagegen edit of 29E with v2 identity + less extreme pike + original still as separate reference roles. Exact submitted input order and prompt in `29F_SUBMITTED_PROMPT_VERBATIM.md`.

## Strict panel comparison

| Gate | 29E | 29F observed | Verdict |
| --- | --- | --- | --- |
| Head-to-track distance in C | Forehead/hair appears effectively in contact/very near track | Forehead/hair now visibly **above** track by several centimeters; no forced touch | **Improved** |
| Physically clear near elbow in C | Upper arm sweeps back/over head, near elbow strongly flexed near face; forearm almost vertical | Near elbow still similarly strongly flexed and its upper-arm/forearm junction remains compressed around head; not an obvious new hinge geometry | **NOT corrected convincingly** |
| Far elbow and two distinct arm chains | Far elbow overlaps near arm/head, cannot independently trace shoulder→elbow→wrist | Still partly occluded, not confidently traceable independently in 2D | **UNVERIFIED** |
| Head behind fixed palms | Yes, correct screen-depth relationship | Yes, preserved with shallower forehead approach | **PASS for still topology** |
| Upper/body and child age | Same soft blue/charcoal middle-school boy, no obviously added limbs | Same approximate body, hair, face, shoes and track | **Conditional pass** |
| A/B/D and margins | Good four-phase framing | Positions mostly preserved; normal generative changes across background and fabric | **Conditional pass** |

Normalized per-tile pixel RMSE 29E→29F (not a skeletal similarity metric): A **2.93%**, B **2.83%**, C **4.97%**, D **3.50%**. This confirms C changed more than other tiles but **does not establish elbow improvement**. Imagegen still re-synthesized non-target pixels.

## Disposition

**29E: DOWNGRADE / HOLD FOR ELBOW ANATOMY; not approved as video/instructional master. 29F: DIAGNOSTIC ONLY / NOT A VERIFIED ELBOW FIX.** It improved the overly deep head position, but visible elbows still look compressed, and the far joint remains hidden. The prior “strong conditional keeper” label on 29E in the mobile index was based on head/palm location and composition; this new adverse user report supersedes that earlier incomplete QA.

Do not stretch, hyperflex or rotate a child's elbows/shoulders merely to mimic a highly flexible adult from archival footage. We cannot infer actual injury risk or diagnose hypermobility from a 2D generated image; we **can** reject a pose whose joints cannot be confidently interpreted as normal. A qualified exercise/form reviewer should review a clear-angle reference before instructional publication.

## Next controlled experiment recommendation (not yet attempted)

Break the error pattern by starting from the older `02_almost_there.png` relaxed V **as the pose target**, rather than asking an image editor to repair the deep 29E pike. Generate one full-resolution standalone profile or mild 15–20° oblique with shoulder→elbow→wrist on *both sides plainly visible*. Keep hands/shoes fixed, hips raised moderately, forehead **10–20 cm above track**, elbows soft or moderately bent naturally, all skin/face/age from the approved v2. Then independently inspect elbow hinges, wrists under forearms, shoulder movement and face distance *before* building a new A/B/C/D card. A visually convincing shallower pike is preferred to an exact forehead touch that requires joint distortion.

Potential prompt line: “Do not optimize for forehead contact. For an ordinary middle-school boy, stop the pike descent as soon as both arms still display clear, relaxed shoulder–single elbow–wrist continuity; leave a natural head clearance. Show the far arm clearly and reject any crossed elbows, inverted joint bend, shoulders rolling behind forearms or missing palm.”

**No video, GitHub, Google Drive or production changes were performed by this agent.** Original image files were not overwritten.
