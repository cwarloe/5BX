# Test 33 — Chart 4 semi-squat jump: photo-card QA

**Date:** 2026-11-26 UTC. **Image:** `33_C4_SemiSquatJump_FourPhase_35mm_CANDIDATE.png`, 1199×1312, SHA-256 `f3741701ed1d317f75bb67303a71efa275192bc76afeb539769ec4e749545598`. One `image_gen__imagegen` generation, no follow-up or Flow video. Source: approved v2 identity sheet, and `ex5-c4-squat-bottom-09m49s0.png` from 1959 RCAF exercise film as pose reference only.

**Important prompt audit:** The model was actually sent exactly `33_SUBMITTED_PROMPT_VERBATIM.txt`. The originally designed prompt in `33_C4_SemiSquatJump_ExactPrompt.md` is nearly the same but the call extracted a file slice incorrectly: it omitted the first `Use case` line and inadvertently included a trailing Markdown fence/tool footer. Preserve this distinction for cross-model reproducibility.

## Panel audit against exact 5BX wording

| Tile | Required semantics | Visible evidence | Verdict |
| --- | --- | --- | --- |
| **A top-left** | Half crouch, straight arms with hands on knees, near/far feet modestly staggered, palms/soles not airborne | Both hands rest on knees with nearly straight elbows; knees flexed into plausible half crouch; two shoes firmly on track with an offset. Back tilts but is reasonably straight. | **PASS, CONDITIONAL**: exact anatomical right-foot ownership from this angle not independently proved. |
| **B top-right** | Launch toward upright, both feet clearly leave track, no pointed-toe ballet foot | Two complete shoes float above track by a modest distance, slight knee bend, hands move off knees and down beside torso. Ankles remain within normal running-shoe range. | **PASS** as early airborne phase. |
| **C bottom-left** | Straight upright body in air, both feet off track, normal shoes | Torso almost vertical, knees close to straight, both shoes visibly off track, forefeet not exaggerated into pointed position; arms hang naturally. | **PASS, CONDITIONAL**: small jump height and slight toe-down foot tilt, but not balletic and fully legible. |
| **D bottom-right** | Land and return to original half crouch, hands on knees, right foot modestly ahead | Both complete shoes grounded, bent knees, same approximate crouching geometry as A and hands again on knees. | **PASS, CONDITIONAL**: body/pose location shifts between tiles; no registration proof of same landing spot. |

## Cross-panel gates

- **Photorealistic identity: PASS CANDIDATE.** Face, fair skin, messy hair, soft normal 13–14yo build, light/medium blue tank, charcoal shorts, dark socks, gray/yellow sneakers remain similar in all four. Minor expression/hair texture variation, not a newly younger child or muscular adult. Figure scale subtly varies by panel, as generative contact sheets do.
- **Anatomy: PASS VISIBLE.** No extra fingers/arms/feet; both knees flex naturally in crouch and unbend in flight. No unnaturally long bones, contorted joints, extreme leap or underage visual inconsistencies.
- **Camera/background: CONDITIONAL.** Approximately 25–30° front-side view preserves stagger leg silhouette, stable red track/green grass/trees and documentary 35mm look. Plant positions and tree registration vary a little; this is a pose reference, **not a registered animation plate**.
- **Biomechanics: STRONG CONDITIONAL.** Distinguishes true grounded crouch vs airborne midphase; supports realistic child form without ballet toes. The exact prescribed **right** foot ahead of **left** is visually plausible but physical foot identity cannot be certified from stills alone. A full video needs to be tested for landing trajectory, changing hand position and foot ownership.
- **Video: NOT RUN.** No interpolation, loop seam, frame-level foot/toe or age consistency has been tested. No Charles human exercise-form approval.

**Verdict: STRONG CONDITIONAL STILL-IMAGE CANDIDATE, not an approved video.** For an eventual single-frame Flow test, choose A as grounded start and keep the jump small, both athletic shoes unpointed, no tracking camera. Before production, verify original foot stagger and actual soft landing in the rendered motion. If mechanical fidelity is uncertain, recover a more complete filmed source showing the exact right/left foot from the 1959 film or owner's own demonstration.
