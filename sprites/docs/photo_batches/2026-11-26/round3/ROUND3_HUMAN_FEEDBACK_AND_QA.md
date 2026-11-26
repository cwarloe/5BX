# 5BX round 3: human anatomy/arm-swing corrections

2026-11-26 UTC. Experimental **photographic stills**, not validated motion or safe exercise instruction.

> **Superseded by round 4 human review:** **34C is REJECTED** because its foreground arm freezes between alternating knee poses. **29H/29I/29J are production REJECTS** because of forced extreme elbow/head geometry. See `../round4_human_feedback/ROUND4_HUMAN_FEEDBACK_AND_QA.md`; retain this report only as historical QA/provenance.

## Controlling human review

The user reviewed the current cards and reported:

- **29H V/forehead pike:** Better but the visible elbow is **still hyperextended**. This human review supersedes the prior internal 29H *geometry pass*. **29H now SAFETY HOLD; do not animate.**
- **24R standard push-ups:** Look pretty good. Freeze pose and character unless a concrete later issue emerges.
- **32R/32S wide push-ups:** Look better. Do not automatically throw away usable mechanical frames because of modest exercise-load shading; retain source options.
- **34B high-knees:** Near/far leg placement is excellent, but the arm trailing behind the boy looks unnatural. Fix rear arm locally, **do not regenerate the successful legs**.

## Controlled edit outcomes

| Variant | Target/change | Current observation | Gate |
| --- | --- | --- | --- |
| **29I** | 29H elbow local edit, unlocked 15–25° | The result remains extremely close to 29H, with elbows nearly straight. A prettier frame is **not** an observable form correction. | **HOLD / diagnostic only** |
| **29J** | 29I with more visible ~30° normal bend, head clearance allowed | The follow-on human review found the elbow/head anatomy still visibly wrong despite modest bending. | **REJECT for production**; historical diagnostic only |
| **34C** | 34B with A/C rearward arms bent | **Failed temporal QA:** the foreground arm stops alternating between the raised-knee frames, even though its isolated positions can look natural. | **REJECT**, not conditional |

## QA priorities

1. **Human anatomical veto overrides assistant internal labels.** Revoke the 29H geometry pass status; retain the image as provenance, not video input.
2. No forced forehead contact. Judge near and far **shoulder → elbow → wrist** individually; if far elbow is occluded, mark **uncertain**.
3. A small visible bend might still be abnormal if it is on the wrong side of the joint. Do not infer safety from a numeric angle specified in a prompt.
4. Preserve **34A (wrist+ankle marked) → 34B clean → 34C rear-arm edit** lineage so the physical limb alternation is not lost. The clean photo alone does not prove which overlapping leg is foreground.
5. Keep the same ordinary 13–14yo soft body (not thinner), blue tank/charcoal shorts, pale skin, naturally messy hair, gray-yellow shoes, fixed red-track camera. Reject edits that make him look older or add deltoid/thigh bulk.

## Files

- `29I_VPike_SlightElbowFlexion_DIAGNOSTIC.png`, `29I_VPike_ExactSubmittedPrompt.md`
- `29J_VPike_VisibleElbowBend_DIAGNOSTIC.png`, `29J_VPike_ExactSubmittedPrompt.md`
- `29H_vs_29I_Elbow_Compare.jpg`, `29I_vs_29J_Elbow_Compare.jpg`
- `34C_HighKnee_NaturalRearArm_CONDITIONAL.png`, `34C_HighKnee_ExactSubmittedPrompt.md`, `34B_vs_34C_ArmSwing_Compare.jpg`

Every still is versioned and the source variants remain unchanged. **No new video has been generated or reviewed in this round.**
