# 5BX Chart 4–6 high-knee stationary run — combined wrist/ankle ownership trial

**Test IDs 34A (marked diagnostic) and 34B (clean still)** · 2026-11-26 · production-stage model self-QA only. **Not approved video or human-observed continuous gait.** Original strong conditional 34 V3 established alternating knees but looked like the same near arm swung backward in both peaks; 34A explicitly targeted that failure, without changing leg geometry.

## Inputs and exact reproducibility

- **Approved appearance authority:** `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`. Normal fair/soft 13–14yo boy, blue tank, charcoal shorts, dark socks, gray/yellow sneakers, black wristband; no adult shoulder/quadriceps muscularity.
- **Edit target / successful leg-position authority:** `artifacts/parallel_batch_20261126/chart4_run/34_C4_HighKneeStationaryRun_V2_ORANGE_TEAL_DIAGNOSTIC.png`. Previous orange-near and teal-far ankle proof.
- 34A exact submitted imagegen prompt: [`34A_WRIST_ANKLE_DIAGNOSTIC_PROMPT.md`](34A_WRIST_ANKLE_DIAGNOSTIC_PROMPT.md); output [`34A_C4_HighKneeCoupledWristAnkle_TAGGED_DIAGNOSTIC.png`](34A_C4_HighKneeCoupledWristAnkle_TAGGED_DIAGNOSTIC.png), 1199×1312.
- 34B exact imagegen edit prompt: [`34B_REMOVE_ALL_BANDS_EXACT_PROMPT.md`](34B_REMOVE_ALL_BANDS_EXACT_PROMPT.md); output [`34B_C4_HighKneeCoupledArms_CLEAN_CONDITIONAL.png`](34B_C4_HighKneeCoupledArms_CLEAN_CONDITIONAL.png), 1199×1312. The original 34A marked card was the **edit target**, v2 only visual wardrobe authority.
- Standard built-in imagegen tool, one generated output per prompt (two calls), no CLI. Both source images and failed original V1 remain untouched. No Drive/GitHub/video writes by this subtask.

## Physical chain audit

Each wrist/ankle color belongs to ONE physical side across all panels: ORANGE near-side arm and leg, TEAL far-side arm and leg. Orange near wrist has adjacent permanent small black wristband. Color appearance alone would not suffice: reviewer also followed the actual shoulder→elbow→wrist chain and hip→knee→ankle→shoe chain, with front/back occlusion.

| Panel | Expected anatomical movement | Marked 34A observation | Clean 34B observation |
| --- | --- | --- | --- |
| **A top-left** | Near orange right knee up to own waist, far teal left foot planted; **near orange arm BACK**, **far teal arm FORWARD** | Orange wrist/fist by rear hip, teal wrist/fist anterior to chest. Orange raised ankle linked to flexed near thigh, teal planted shoe fully grounded. **PASS** | Same near arm behind and far arm ahead, near raised shoe/far planted shoe; bands gone. **PASS** |
| **B top-right** | Orange knee descending, no teleport; arms passing naturally | Near orange forearm/hand returns closer waist; far teal forearm forward. Orange ankle enters near-ground, teal far support shoe planted, partial natural foot blur. **CONDITIONAL** | Same apparent limb positions, neutral socks; no extra foot. **CONDITIONAL** |
| **C bottom-left** | Far teal left knee up to own waist, near orange right support planted; **near orange arm FORWARD**, **far teal arm BACK** | Orange wrist/fist is now distinctly **in front of tank** attached to near shoulder; teal wrist/fist behind body; teal tagged raised ankle linked to far bent thigh, orange near shoe flat track. This reverses A's arm pose and knee pose. **PASS** | Forward near black-wristband arm retained, other bare-wrist arm behind, far knee up/near shoe planted. **PASS** |
| **D bottom-right** | Far teal knee descending, near leg ready for next cycle, arms return toward A | Both knees pass down; orange wrist nearer waist/back and teal far wrist forward, near planted support. **CONDITIONAL**; still can't prove timing from four photos. | Same, dark socks and one black wristband, no colored remnants obvious. **CONDITIONAL** |

**Primary result:** unlike original untagged 34 V1 and leg-only V2/V3, the 34A four-band diagnostic now visibly controls and demonstrates **both opposite knees and reciprocal opposite arm swing**. 34B clean version retains those A↔C counter-swings while removing all orange/teal temporary markers. That is a **conditional still-photo improvement**, not a biomechanically verified gait animation.

## Appearance/quality and regression caveats

- Same boy across all four tiles; blue/charcoal/gray-yellow shoes and static track/lawn/trees broadly consistent. Boy reads plausible older middle-school, not grown adult or elementary child, with smooth pale skin, no obvious armpit/body hair.
- **Subtle identity drift:** hair is a little curlier/full than approved v2 master and C foreground upper arm/deltoid is slightly firmer than neutral-stance v2. Upper leg/thigh silhouette does NOT conspicuously grow from frame to frame, but still-image generator could change subtle contour; prioritize softness in a separate future identity-only edit rather than touching this new successful reciprocal pose.
- The generated 34A and 34B have 1199×1312 vertical 2×2 dimensions rather than the old 1672×941 landscape layout. All four shoes/fingers are inside frame; no crop disaster.
- The generative 34A→34B cleanup is NOT pixel-mask exact. Whole-card ImageMagick RMSE ≈ **0.03028** normalized (~3.03%). This is consistent with colored rings removal and possible incidental light/texture changes, not proof all other pixels remained fixed. Direct visual QA, not RMSE alone, supports preservation of limb placement.
- Running direction reads screen-right; the requested ~25–30° toward-camera oblique is still effectively close to a side profile, so depth lineage can be harder to independently infer **once marks are removed**. Retain 34A permanently as diagnostic provenance.
- Some B/D foot blur and contact/arm timing may be altered by future video interpolation. The four stills are not measured time intervals. Exact gait frequency, ground reaction, non-sliding support, ankle trajectory, loop seam, and no frame reversal are unverified.

## Actionable next acceptance gate

Preferred single-anchor starting still is clean **34B panel A**. In a future Google Flow or Grok trial, explicitly require an upright non-traveling run at waist-high knees; one full alternating step cycle with **near leg up/far arm forward/near arm back → far leg up/near arm forward/far arm back**, camera fixed, natural shoe orientation, unchanged fair soft middle-school identity, no jumps or bodybuilder shoulder definition. Avoid asking the model to automatically interpolate all four as discrete slides if it tends to reverse phase order. Inspect the actual video normal speed and frame-by-frame joint ownership before granting motion pass; compare with diagnostic 34A.

**Disposition:** 34A **FOUR-LIMB DIAGNOSTIC PASS**; 34B **PREFERRED CLEAN CONDITIONAL STILL**; original 34 V3 preserved as fallback; actual video **NOT TESTED**. No need for human approval until short video exists or the child's specific arm-swing comfort is uncertain.
