# Test 29C — realistic isolated forehead BEHIND palms endpoint, independent assistant QA

Date: 2026-11-26 UTC. **One** built-in `image_gen.imagegen` generation, not a retry of 29B track-line edit and not a complete four-phase card. Exact prompt and source-role provenance in [`29C_C3_ForeheadPike_Standalone_ExactPrompt.md`](29C_C3_ForeheadPike_Standalone_ExactPrompt.md).

**Preferred output:** `29C_C3_ForeheadPike_BehindPalms_Standalone_CANDIDATE.png`, native **1672×941**, SHA-256 `fd605f1dc30b34510d331c21f05a38c0d937e8d0121221fb319ced67316d12ee`.

## Why this test differs

- **29 original** included a plausible pike but head stayed in front of palm line in a right-facing four-card.
- **29B explicit track-line edit** painted the marker correctly but still left forehead in front, thus failed the Chart3 wording despite improved diagnostic certainty.
- **29C changed the pose authority, not the boy:** a previously nearly correct **screen-left-facing teen pike** (`artifacts/parallel_tests/v_pushup_realistic/02_almost_there.png`) and authentic 1959 RCAF forehead frame (`artifacts/restore_build_20261125/build_source/docs/reference/rcaf-1959-stills/ex4-c3-forehead-08m32s0.png`) supplied the actual **behind-palms topology**. The approved v2 image remained appearance authority. Output was **ONE isolated new photograph**, with the same left-facing orientation as its two pose references.

## Pose anatomy by explicit visual audit

| Gate | Observation | Verdict |
| --- | --- | --- |
| **Critical forehead side** | Boy faces SCREEN LEFT; planted near palm is around screen X~250–320, far palm around X~200–290. Forehead/face lowest point lies around X~430–520, **screen RIGHT of both palm contacts**, i.e. **BEHIND hands toward the feet**. Head ground projection is visibly separated from hand line, unlike 29/29B. | **PASS key fixed-palm topology**. |
| **Toe and palm supports** | Both hands are flat on track to left of head; two shoes on toe caps remain on track at image right; knees airborne and mostly straight; hips form V apex. Neither hands nor toes float. | **PASS single still**. |
| **Child-feasible range** | Elbows flex naturally, shoulders not hyperextended or dislocated, torso and legs retain human proportions; moderate pike with forehead/hair near track rather than forceful deep compression. Heels slightly raised naturally inside sneakers. | **PASS/STRONG**, no sudden growth. |
| **Exact forehead skin touch** | Hairline/forehead comes within a few centimeters of track; precise skin contact and neck pressure are not objectively provable. | **NEAR CONTACT only**, allowed by realism brief. |
| **Anatomical count** | Both arms appear attached to shoulders, two hands and two running shoes visible, no spider third limb/duplicate elbow or stretched forearm. Far elbow has partial body overlap but no obvious artifact. | **PASS visible structures**, not 3D certainty. |
| **Identity and outfit** | Blue sleeveless tank, charcoal athletic shorts, dark socks, gray/yellow running shoes, black near wristband, fair ordinary adolescent skin and limbs. Hair slightly curly/full and face is obscured by pose, so exact v2 face-match remains unverified. Some shoulder contour but not overt muscular adult. | **CONDITIONAL identity**. |
| **Framing/photographic quality** | Single high-detail 35mm-style side-view track photo, entire palms/toes/shoes visible with room from frame edges, real lighting/textures, no markers/captions. | **PASS still**. |

## Correct inference / limitation

**STRONG PROVISIONAL STANDALONE POSE ENDPOINT, NOT APPROVED ANIMATION.** Unlike 29 and 29B, this photo visually satisfies the booklet's unusual forehead-BEHIND-hands relationship without six-inch growth or impossible shoulders. It is strong pose reference to use in a future *joint* four-phase sequence or a controlled substitution of boy identity, not itself evidence of chin→forehead dynamic transitions, hand/toe stationary registration, or final exercise form. User may prefer near-contact rather than perfect forehead skin touch given normal middle-school flexibility.

The improvement is associated with providing **pose photographs already containing the correct limb/head topology** and switching to their left-facing viewpoint, after word-only and marker edit failed. Since both reference quality AND direction changed together, **do not claim either variable alone is causally proven**. This supports a general rule: for rare anatomically difficult poses, first establish a correct standalone single endpoint against a real photo, then compose a card, rather than repeatedly editing a four-panel card whose key body topology is wrong.

## Suggested next gate (not executed)

If continuing, use 29C **pose-only** plus approved v2 identity to attempt a new *joint* four-phase card at the same LEFT-facing static 35mm camera: A normal plank, B chin near ground *in front* of palms (SCREEN LEFT), C 29C forehead near ground *behind* palms (SCREEN RIGHT), D return plank. Both palms and toes must stay at same track coordinates. Use temporary fixed palm-line marker only to verify, not as an artwork goal; do not let the generator reintroduce right-facing pose or conflate chin/forehead contact. Compare age/hair/shoulders to immutable master across four phases, and treat resulting card as conditional until human biomechanics and video motion QA.

No video, Flow credits, Google Drive or GitHub writes in this agent task. **No human approval inferred.**
