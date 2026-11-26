# Test 29B — fixed palm-line position diagnostic (targeted edit)

Date: 2026-11-26 UTC. ONE built-in `image_gen.imagegen` edit only. Exact edit prompt/reference roles: [`29B_C3_PalmLine_ExactEditPrompt.md`](29B_C3_PalmLine_ExactEditPrompt.md). Source untagged image: [`29_C3_EX4_ChinForehead_FourPhase_35mm_DIAGNOSTIC.png`](29_C3_EX4_ChinForehead_FourPhase_35mm_DIAGNOSTIC.png).

**Output:** `29B_C3_ChinForehead_FixedPalmLine_DIAGNOSTIC_REJECT.png`, 1536×1024. SHA-256 `f1bd0be5e8e49d80167efd6ae8a8081e4ddfe8235d7a2282e42bdcdac31c8481`.

## Hypothesis and controlled change

The 29 original card showed a reasonable youthful pike, but could not prove that the forehead moved **behind the planted hands** as the booklet requires. The edit introduced a **fixed yellow tape line on the track at the palm X-coordinate** in every tile and specified for right-facing side view:

- B chin target to SCREEN-RIGHT of fixed palm line (forward).
- C forehead target to SCREEN-LEFT of fixed palm line (rearward/toward feet).
- Both palms and both toes fixed; no longer arms, extra joints, increased height, new age or different outfit.

## Observed visual result

| Panel | Palm-line control | Head relationship | Verdict |
| --- | --- | --- | --- |
| A up plank | Yellow vertical track tape starts immediately beneath planted near palm and continues to lower edge; palms remain same X. | Face to screen right of palm line as expected for plank. | **PASS marker/pose.** |
| B chin-down | Same fixed ground stripe aligned to near palm in rightward-facing low plank. | Chin/face well to SCREEN-RIGHT of line, in front of hands. | **PASS chin-side control.** |
| **C forehead pike** | Stripe aligned to near palm X, visibly at about image tile local X~538; hand seems stationary. | Forehead/hair front remains about 50–70 px to **SCREEN-RIGHT** of line, not left; head reaches track IN FRONT of hands again. Body pose is essentially carried forward from 29 with no actual backward head crossing. | **CRITICAL FAIL:** marked test definitively exposes missing in-front vs behind reversal. |
| D return plank | Stripe aligned with planted palm, same high body silhouette as A. | Face to screen-right of line as expected. | **PASS marker/pose.** |

### What did and did not change

- **Marker placement succeeded:** no band teleportation, each thin yellow line belongs to the track *under the hands*, not to a shoe or wrist. It makes the ambiguous relation measurable at a glance.
- **Geometry correction did NOT succeed:** image model added the diagnostic track-line but preserved the original pike with forehead in front of hands, despite explicit opposite-side language. The line is not simply drawn to the right of head; its x is correctly tied to the hands. This is a genuine topology failure, not a mislabelled diagram.
- **Body/identity protected:** same realistic middle-school boy in four coherent photos, no elongated hands/feet or hyperextension, reasonable hip lift and both toe/palm support, same blue-charcoal outfit and static track. Far elbow still partly occluded in pike. Exactly four related tiles; no giant muscular adult.
- **Reference issue:** original 1959 film frame itself may not unambiguously show behind-hand contact due adult profile geometry. The **booklet wording** remains the formal check; a picturesque pike is not automatically correct 5BX.

## Final disposition and transferable lesson

**REJECT 29B for strict Chart 3 instructional video.** It is a better diagnostic than the unmarked result because it cleanly proves *which* movement relation the generator did not satisfy. Do not publish this as an approved chin–forehead push-up or send it to Flow. A still cannot certify actual ground touch or moving fixed contacts.

**What failed:** a visible fixed line plus strong verbal instructions did **not** force the model to move the forehead behind the hands. The generator obeyed the easier *marking* task while ignoring the structural head-to-wrist positional change. A future controlled image edit would likely need a **verified real or drawn child-proportion pike reference where the forehead lies left of a stationary hand line**, or skeletal pose guide with hand/head coordinates, followed by identity replacement. Avoid distorting the child's shoulders or height to force contact. This is an inference, not a demonstrated remedy.

No retry was made, no Google Flow credits spent, no Drive/GitHub external writes, no human form approval inferred.
