# 5BX pose and identity QA: next-stage experiments

**2026-11-26 | assistant engineering proposal + one executed offline pilot.** Intended for the 35mm/photo-based middle-school character, not the legacy cartoon. These are **proposed process gates**, not clinically validated biomechanics or evidence that generated video motion is correct. Original 5BX booklet/1959 film remains the exercise-form source; the user-approved [v2 character sheet](../character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png) remains appearance source.

## Five experiments worth testing

1. **Anatomical state ledger before each card: a tiny motion “unit test.”** Write one line per phase and *physical* limb: body-side identity, joint chain (hip→knee→ankle or shoulder→elbow→hand), contact state (`planted / airborne / touching body / occluded`), torso orientation, and frame-edge clearance. Pre-specify the expected opposite-side transition. Fail the card if a B/C swap repeats a limb or if a required hand/contact disappears, even if the picture looks beautiful. This is stronger than merely putting labels A/B/C/D on tiles. **Gate:** all critical limb/ground/contact predicates must be demonstrably true in each intended phase; unknown occlusions remain `CONDITIONAL`, never pass by inference.
2. **Machine-readable temporary marker telemetry.** Keep orange/teal ankle/wrist bands for hard crossovers, *then quantify their connected-pixel centroids per panel* and compare the required order. This does not replace tracing the band through the correct thigh/shoulder, but quickly catches same-side repetitions and mislabeled cards before expensive cleanup/video. **Gate for waist-high run:** each color marker must have a clear component, in A the orange ankle is above the teal by at least ~10% of tile height, and in C the teal above orange by the same amount. This threshold is an *initial heuristic*, not a validated error bound. **Clean edit:** the marker probe should become unobservable; compare the clean card against the tagged version manually for preserved physical joint paths. Do not run this height test blindly on bent-knee sit-ups (a knee can rise with a planted ankle).
3. **Background fiducial registration.** Use the red-track/green-field boundary as a stationary scene ruler. Compute its row position independently in A/B/C/D; flag if its spread exceeds *3% of tile height*. This catches some unintended camera/scale shifts and moving scenery before video. Track-lane lines could be a second, independent fiducial. **Gate:** both scene ruler and person scale/head-to-hip envelope must remain coherent; a coherent horizon alone does not prove that the camera is truly locked, and the 3% bound needs calibration.
4. **Two-axis identity lock: structural vs surface appearance.** Do **not** penalize a shoulder merely for changing highlights under load. Compare an exercise card with the *same viewing-angle class* of the v2 reference and independently ask: **(a)** segment lengths, chest/waist/thigh girths and joint endpoints unchanged? **(b)** deltoid/quadriceps separation, hard shadows, hair volume, nose/ear shape, skin shade look older/more athletic? Correct *surface definition only* first, preserving thigh circumference, ordinary waist/chest and normal exercise loading. **Gate:** no changed limb ancestry/contact or proportion after an appearance edit, and a second reviewer must reject cosmetic changes that make the child thinner, longer, muscular, younger, or more flexible. Raw pixel-difference/SSIM is a change-locality aid only, **not** proof of identity.
5. **Motion checkpoint test before full video batch.** For difficult high-knee, clap, chest-slap and twist cases, produce an explicit *mid-interval pose* (two hands clearly off track; torso rotated opposite; one knee lowered before the other rises) to expose discontinuities before spending video credits. Then video-test **single high-quality start anchor** versus optional additional endpoint as an A/B experiment, rather than assuming three frames are better. **Gate:** sampled actual video frames obey the anatomical state ledger; phase direction, support/contact transitions, fixed camera, boy's age/build and first→last loop must pass independently. A still frame cannot certify temporal biomechanics.

## Executed pilot: marker + camera checks

Created reusable read-only analysis script [`marker_component_ledger.py`](marker_component_ledger.py). It examines each quadrant of a 2×2 card, isolates bright orange and teal components in HSV color space, reports their centers, and optionally checks marker-height exchange and red-track boundary consistency. It **never alters the source** and uses no model calls. Dependencies: Pillow, NumPy, SciPy. Usage:

```bash
python artifacts/next_batch_20261126/marker_component_ledger.py --run-knee-check --track-check artifacts/parallel_batch_20261126/chart4_run/34_C4_HighKneeStationaryRun_V2_ORANGE_TEAL_DIAGNOSTIC.png
```

### Observed numbers

| Input | Relevant observed metric | Diagnostic output | Interpretation / limitation |
| --- | --- | --- | --- |
| **34 V2 marked waist-high run** | Tile A orange ankle band y≈358.8, teal y≈524.4. Tile C orange y≈527.0, teal y≈351.7. A opposite-band gap **165.6 px**, C opposite-band gap **175.3 px**, each above initial **65.6 px** threshold. | `MARKED HEIGHT EXCHANGE` | Pixel evidence of the requested **marker-height reversal** across A/C. Human still must trace both colors ankle→knee→hip and the opposite support shoe. These blobs cannot by themselves prove complete anatomy. |
| **34 V3 clean** | Teal marker absent in A/C after edit; orange skin/shoe false positives remain. | `NO MARKED HEIGHT PROOF` | **Expected**, because diagnostic bands were removed. It does *not* mean the clean posture is wrong. Preserve the V2→V3 parent-child relationship and compare silhouettes. |
| **34 V2 static scene** | Red-track edge y by tile: **[489, 490, 490, 490] px**, spread **1 px** vs 19.7 px heuristic tolerance. | `TRACK EDGE COHERENT` | Useful stationary-background evidence, not proof of identical camera focal length or child scale. |
| **35R marked twisting sit-up** | Track edge **[545, 543, 538, 545] px**, spread **7 px** vs 19.7 px tolerance. Orange and teal have multiple wrist/ankle blobs; height alone does not test a bent knee. | `TRACK EDGE COHERENT`; marker components require joint-specific manual tracing | Explicitly **do not** use waist-high run centroid heuristic as a twist verifier. The proper check is B teal LEFT knee bent with ORANGE RIGHT elbow reaching across, and C orange RIGHT knee bent with TEAL LEFT elbow crossing. No literal elbow contact proved. |
| **32R softened wide-hand push-up** | Track edge **[300, 299, 311, 300] px**, spread **12 px** vs 15.4 px tolerance; original→R1 all-pixel normalized MAE **≈2.02%**, top-background MAE **≈1.06%**. | `TRACK EDGE COHERENT`; visually subtle edit | Supports modest apparent camera/background continuity, but *does not* prove the shoulders really match v2 or that hand mechanics survived. Original and revised still need side-by-side human/second-agent anatomy QA. |

This pilot uses the output's *generated marker pixels* and a simple reddish-background classification; thresholds are tuned to these sample colors, and small skin/shoe/blue-shirt fragments can be false positives. It is a **screening tool**. Do not promote `MARKED HEIGHT EXCHANGE` to `ANATOMICAL PASS` automatically. No sample videos were inspected in this experiment.

## Copy-ready prompt blocks for the next controlled image test

**Identity surface lock, append to every pose:**

> Image 1 is the immutable v2 appearance reference: the same ordinary fair-skinned 13–14-year-old American middle-school boy with short naturally messy brown hair, gentle non-muscular shoulders/arms/thighs, natural waist and chest, normal ears/button-like nose, smooth skin without mature body hair, medium-blue tank, charcoal shorts, dark socks, gray/yellow running shoes and black wristband. Do not enlarge or narrow shoulders, waist, thighs or height, alter face/age, increase visible deltoid/quadriceps muscle separation, or make him a smaller child. Exercise loading may alter shadows but must not manufacture new muscle mass. Preserve full body in a locked red-track camera.

**Paired anatomical state, for limb swap or twist:**

> This is one four-panel 35mm photographic sequence with fixed camera and unchanged boy. Give the physical camera-near RIGHT ankle/wrist narrow ORANGE diagnostic bands and physical far LEFT ankle/wrist narrow TEAL bands, permanently attached to their own hip→knee→ankle and shoulder→elbow→wrist chains. State each panel's support, lifted limb, torso rotation and opposite elbow explicitly. Bands cannot jump to the other anatomical limb. Show all joints/feet and natural, child-achievable range. Keep all four panels related, do not independently redesign his face/physique.

**Cosmetic softening edit, *only after* mechanics pass:**

> Edit target: this already mechanically validated card. Change **only** surface modeling of deltoid, triceps, quadriceps and chest: reduce hard muscular striations and bodybuilder-like shadows modestly, retaining a normal gently soft middle-school appearance. Keep identical upper-arm width, thigh circumference, natural waist/chest, limb lengths, all joint endpoints, grounded shoes/hands, face, hair, clothing, camera, ground plane, and A/B/C/D phase topology. Do not make the child thinner, fatter, shorter, taller or more flexible. If the edit would distort mechanics, leave the original anatomy untouched.

**Mandatory reviewer ledger per phase:**

`phase | physical limb ID | hip/knee/ankle or shoulder/elbow/hand chain | planted/airborne/contact | torso rotation | visible/occluded | body-scale/age | pass/uncertain/fail`.

## Next actual experiment to run

Test the **34 high-knee** and **35R twist** under two conditions each: existing clean four-card (baseline) versus four-card with **explicit mid-motion state** added as a fifth frame. Keep identity, model, reference images, camera, palette and prompt wording fixed except for that added state. Judge physical leg/arm continuity and video animation separately. Avoid overprompting for perfect 5BX form when an average middle-school body cannot perform it comfortably; an honest near-touch is preferable to elongated limbs.

**Do not promote until independently inspected:** Running marker-height reversal is now automatically observable; torso twist, elbow contact, thigh softness and true animation remain human/model-visual QA judgments.
