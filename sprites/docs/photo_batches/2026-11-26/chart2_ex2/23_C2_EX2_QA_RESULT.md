# Test 23 — Chart 2 full sit-up, independent panel-level QA

**Result:** **STRONG CONDITIONAL still candidate**. No owner review, Flow video or historical-form sign-off. One imagegen call, no corrective edit.

**File:** `23_C2_EX2_FullSitup_FourPhase_35mm_CANDIDATE.png` · **1199×1312** PNG · SHA-256 `71c109f381be2ec311096f885de08525bfdd4b48619b5f294de593fb823195c1`.

**Historical target:** `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`, Chart 2 Exercise 2: *Back lying, feet 6" apart, arms at sides; sit up to vertical position, keep feet on floor even if necessary to hook them under a chair.* This is intentionally DIFFERENT from Chart 1's partial sit-up, which stops once the heels can be seen.

## Four panels, actual visual QA

| Panel | Torso and head | Legs/shoes | Arms / contact | Assessment |
| --- | --- | --- | --- | --- |
| A upper-left | Back, shoulder blades and head flat on red track. | Both long legs straight; heels touching track; shoe toes point naturally upward; shoes complete. | Both arms alongside body, one dark wristband. | **PASS start**. |
| B upper-right | Shoulders and trunk lifted roughly 40–50°; gaze forward, no dramatic neck hyperflexion. | Both knees nearly straight, ankles and heels apparently unmoved; no floating feet. | Hands slide beside thighs, not visibly grasping. | **PASS rising midpoint**. |
| C lower-left | Torso nearly vertical above seated pelvis, a real full sit-up rather than a shallow curl. | Extended legs and both heels remain on track; shoes stay near identical scene x-position. | Hands at sides near hips; palms touch track and *could* be giving minor support, impossible to exclude from still. | **PASS full vertical range; CONDITIONAL palms**. |
| D lower-right | Controlled lower at roughly 35–45°, head/chest still raised. | Long legs and heels still grounded, neither knee drawn inward. | Arms alongside thighs. | **PASS return**. |

## Strengths

1. Clear range progression A→B→C→D; C is actually upright. This avoids the common error of accidentally generating another Chart 1 partial sit-up.
2. Consistent sky-blue tank, charcoal shorts, gray/yellow trainers, dark socks, fair untanned skin, ordinary undeveloped early-teen body. No visible abdominal definition, excessive leg hair, facial hair or conspicuous armpit hair.
3. Entire body visible with adequate headroom and shoe margins; no duplicated limbs, extra wrists/feet, warped waist or extreme flexibility.
4. The boy’s feet do not visibly rise when his torso rises. Heel contact appears sustained in all four tiles; foot anchoring remains a **visual inference**, not a tracked physical proof.
5. Red track, green field, trees, static general scene; frame scale sufficiently close for still-reference tests.

## Limitations and caution

- **Camera angle FAIL versus request:** Generated approximately 90° side profile, not the requested 20–30° side-oblique. Two legs largely overlap, although both shoe tips are visible. This is acceptable for judging a basic sagittal sit-up but limits near/far identity checks.
- **Hands at vertical apex:** C palms lie visibly on track at hips. They might be passive or assisting; the still alone cannot establish whether he pushes himself up. No claim of hands-free mechanics.
- **Precise registration:** Similar but not pixel-identical shoes, shadows, trees and head geometry across separately synthesized frames. Never directly use the 2×2 card as ordered video frames without registered full-resolution starts.
- **Identity:** Slightly fuller profile hair and a somewhat more defined upper arm in B/C than the approved master v2. Small but watch in cross-exercise clips. His proportions remain credible for 13–14.
- **Prompt correction for next test:** The submitted prompt incorrectly demanded the *full soles* remain down while also asking for legs flat/supine. In the realistic pose only **heels or rear shoe edges** contact track, with shoe toes naturally up; future wording should say “heels remain grounded and feet do not rise,” not “full soles planted.”
- No human 5BX movement verification, no animation or loop QA.

## Status / suggested next gate

**KEEP as photographic four-phase candidate for Test23**, with a conditional flag for possible hand-supported vertical apex. If animating, prefer a separately generated full-resolution *supine A* frame from the approved v2 identity, lock static camera, request one continuous A→B→C→D→A full sit-up and explicitly keep heels anchored. Inspect the actual MP4 frame by frame for heel lifting and torso swing before claiming success. Reuse exact prompt in `23_C2_EX2_ExactPrompt.md`.
