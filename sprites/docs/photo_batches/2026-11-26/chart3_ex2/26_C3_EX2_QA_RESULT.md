# Test 26 — Chart 3 hands-behind-head full sit-up: visual QA

**2026-11-26 UTC. Status: CONDITIONAL STILL; not strict-booklet or video approved.** One imagegen call, no retry, with approved v2 character as primary appearance reference and Chart 2 23B full sit-up as pose-only secondary reference. Exact submitted prompt: `26_C3_EX2_ExactPrompt.md`.

**Output:** `26_C3_EX2_HandsBehindHeadSitup_FourPhase_35mm_CANDIDATE.png`, 1199×1312 PNG, SHA-256 `0e055b2a7639176e9075ac9419c5194995a4cf02331d74d0aff84df86c98189e`. No Flow/other video generated; no Google Drive/GitHub writes by this agent.

## Booklet authority

Chart 3 Ex2, `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`: Back lying, feet 6 inches apart, **arms clasped behind head**; knees may bend **slightly**; sit up **to vertical** and keep feet on floor. Foot hook/chair may be used if necessary, but none was introduced.

## Four panels inspected

| Panel | Relevant visual fact | QA |
| --- | --- | --- |
| **A upper-left** | Back and head almost against red track; torso prone/supine correctly, both elbows laterally splayed, both hands plausibly behind lower head; both gray/yellow shoes on track. | **PASS posture**, with **CAUTION** deep knee bend. |
| **B upper-right** | Torso raised to ~40–50°, arms bent around nape, two outward elbows, no visible palm pressing track, pelvis supported, shoe soles grounded. | **PASS pose**, clasp details occluded. |
| **C lower-left** | Torso upright near 85–90° from floor, seat planted, both hands still at back of skull, elbows out, shoes planted; no pushing on ground. | **PASS full upright position**, knees bent much more than booklet's 'slightly'. |
| **D lower-right** | Controlled recline around 30–40° with hands still near/behind skull, pelvis supported, both shoes resting. | **PASS return still**, movement and contact continuity not video proven. |

## Independent constraints

- **Major success:** The model did not copy Chart 2's arms-at-sides; it preserved the distinct Chart 3 hands-behind-head support in all four phases. The boy's torso reaches genuine vertical, unlike Chart 1 partial curl, and does not grow, twist or sprout extra arms. Blue tank, charcoal shorts, dark socks, gray/yellow shoes, fair soft undeveloped early-teen anatomy, dark messy hair and track setting remain generally consistent across panels.
- **Main strict-form concern:** The knees bend substantially (visually around a right angle at the knee), not just *slightly*. This may be a sensible easier variant for a 13–14-year-old, but should not be reported as faithful to the booklet's limited knee allowance without Charles's judgment. The feet are roughly a few inches apart in side projection, but 6-inch transverse spacing and bilateral heel loading cannot be independently measured from the image.
- **Clasp evidence:** Hands are hidden behind head/neck as they naturally would be from this view. Both elbows/arms can be traced, but interlocked fingers are **not actually visible**, so the specific clasp is apparent, not conclusively certifiable. No extra fingers or limbs are visible.
- **Camera angle:** Despite explicit 25–30° oblique instruction, output is predominantly strict side view, again obscuring far heel/hand and authentic 3D contact. Intra-card camera horizon/scene are stable; geometry/face small differences from the original master remain generator reconstruction, not pixel identity.
- **No video verification:** This four-panel contact sheet cannot prove an unassisted sit-up with both heels fixed during transitions, no bouncing, frame registration or a seamless loop.

**Verdict / next test:** Useful **conditional pose reference** with a clear full sit-up and hands staying behind the head. It is **not yet an approved strict Chart 3 form source**. If this pose is advanced, one targeted iteration should decrease flexion to approximately 20–35° knees while preserving two planted heels, both hands behind skull and full vertical apex, then verify real child's capacity and foot mechanics. Do not force extra limb length or abdominal definition to satisfy the booklet. No further regeneration in this one-test assignment.
