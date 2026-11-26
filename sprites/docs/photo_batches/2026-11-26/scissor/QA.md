# Chart 1 scissor-jump photographic batch, 2026-11-26 (UTC)

**CURRENT ROLLING VERDICT (through V7): V6 MARKED 5BX STRAIGHT-ARM FORM DIAGNOSTIC PASSES AGENT VISUAL QA; V7 CLEAN VERSION PASSES THE SAME AGENT VISUAL QA CONDITIONALLY; BOTH AWAIT HUMAN REVIEW AND ARE NOT RELEASE/VIDEO APPROVED.** V1 repeated the same lead leg; V3 correctly alternated physically tagged legs but not arms; V4 correctly alternated color-tracked arms and legs but used bent ~90° runner's arms; V5 removed tags but inherited that **original-5BX straight-arm form failure**. V4/V5 remain valuable only as natural-running-arm anatomy/ownership diagnostics. The booklet instructs extended arms to approximately shoulder height in opposition to legs. **V6 corrects that arm form while maintaining the colored physical-limb identities; V7 removes markers while retaining the V6 straight-arm geometry.** Camera still tends toward near side-profile. No Flow video generated, no owner exercise-form approval claimed. Older per-test diagnostic verdicts below should be interpreted within their stated scope.

## Immutable inputs

- PRIMARY character/wardrobe authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`, explicitly approved for image identity. Four-view 13–14yo soft, fair, blue tank/charcoal shorts/gray-yellow shoes.
- SECONDARY pose-only authority: `artifacts/parallel_tests/scissor_jump_leg_depth/frame_01_near_trailing.png`, a previously credible foreground-trailing running pose. Explicitly NOT authoritative for the face, camera, clothing or age.
- Booklet/source wording: Chart 1 scissor jumps, opposite arm/leg forward, jump to exchange before landing, arms at approximately shoulder height; `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`.
- Prior diagnosis: `repo_5bx_brightboy/sprites/docs/SCISSOR_JUMP_DIAGNOSTIC_RECORD.md`, which expressly warns that mixed opposing A/B pose sheets repeatedly collapse to the same lead leg and that a source-grounded physical leg ID is missing.

## Test 1 — jointly generated four-phase photo card

**File:** `scissor_joint_card_V1_REJECT_same_leg.png`.
**Exact verbatim prompt:** `PROMPT_V1.md` (the entire block from `Use case:` through the end). Built-in image generator, two referenced PNGs.

### Observations

- PASS photo / appearance: same general 13–14yo face, blue tank, charcoal shorts, gray-yellow shoes, four full-body panels, stable background style, no ballet feet, natural modest stride/shorts.
- FAIL exercise sequence: top-left and bottom-left grounded panels both show **the same forward/rightward leg depth/silhouette**. The distinctive camera-near trailing / camera-near leading hip overlap does **not** invert. Top-right and bottom-right airborne panels also closely repeat a similar near-leg-leading knee-lift. Thus no physical opposite-leg landing is demonstrated.
- FAIL arm/leg phase: hands are below shoulder height, arm/leg opposition is not anatomically traceable, wristband arm continuity ambiguous.
- Minor camera identity: the model mostly preserves facing right and image style; some relative head/body scale and scene features shift across panels, meaning frames not registered for direct animation.

**Verdict:** **REJECT** as source for video. This is an exact recurrence of earlier mixed A/B-sheet failure even with approved photo master and explicit right/left hip depth wording.

## Test 2 — isolated inverse trailing-leg endpoint

**File:** `scissor_near_trailing_V2_ISOLATED_CANDIDATE.png`.
**Exact verbatim prompt:** `PROMPT_V2_INDEPENDENT_ENDPOINT.md` (the full block from `Use case:`). Built-in image generator, same two reference PNGs.

### Observations

- PASS isolated photo: believable documentary sharpness and full-body scale; fair teen identity / palette generally tracks master; legs unbroken, toes neutral, two feet grounded, moderate split stance, no age-distorting extreme jump.
- PARTIAL depth geometry: the trailing leg appears closer to the camera and front leg appears farther, similar to the accepted depth exemplar. However **physical anatomical right/left identity cannot be verified** from one independently generated pose, and the visible shorts crossing remains camera-angle-dependent.
- FAIL cross-frame registration: alternate independent render has different background, face/hair microgeometry, figure placement/camera distance from V1. Cannot splice these as registered animation frames.
- FAIL unambiguous arm identity: the black wristband is on the rearward arm, despite prompt assigning right wrist/arm forward. Do not infer correct physical limb mapping from natural-looking hands.

**Verdict:** **CONDITIONAL DIAGNOSTIC CANDIDATE ONLY**, not usable video endpoint or final form approval.

## Lesson / next best test (no automatic regeneration from word-only prompts)

1. Jointly generated current photorealistic identity cards appear strong for appearance but **still reproduce repeated same-leg scissor topology**. More negative prompt text did not solve it.
2. Isolated near-trailing output can be visually plausible but lacks verified physical right/left identity and differs in photographic registration. Do not pretend two plausible independent stills constitute an alternating cycle.
3. Next cost-effective controlled test is to use the owner's original **120-fps scissor-jump video** with a visible physical-leg marker or source frame/skeleton trace to identify the actual anatomical near/far limb in A and B, then provide both explicitly labeled source frames as **pose authority only** while using v2 as separate **appearance authority**. Distinguish tracking, pose generation and animation stages.
4. Camera stays static and full figure visible, no toe-pointing, no fades/interpolation ghosts. Do not submit video generation until both opposing body positions pass the hip-depth and physical-leg-identity gates.

No repository/Drive writes, no Flow credits spent, and no approved production asset changed in this task.

## Follow-up — authenticated original human source video recovered, but no defensible physical-leg pair

**Original Google Drive file:** [VID_20261123_213002.mp4](https://drive.google.com/file/d/1z9mmCui_0FQKlDPOL_6FI_Drij-fPCr8/view), exact size **179,593,650 bytes**. Authenticated raw Drive fetch succeeded; downloaded into this isolated scratch batch as `source_human_120fps_20261123.mp4`. SHA-256 `1f9152bb82f0b73d71ad47ba77bdc64c642f9dd28e4e7675697e73ead216738e`. ffprobe reports H.264, 1920×1080, duration 90.133211 seconds, nominal 120/1 frame-rate base, variable average frame rate reported; do not infer that every displayed frame is sharp 120-fps capture.

**Four documented static-angle windows inspected** using timestamped 2 fps montages:

- Angle 1, facing left/near-profile: **12.0–20.5 s**, `reference_pass1_CONTACT.jpg`.
- Angle 2, facing right/slight three-quarter: **32.0–40.5 s**, `reference_pass2_CONTACT.jpg`.
- Angle 3, facing left/three-quarter: **47.5–56.0 s**, `reference_pass3_CONTACT.jpg`.
- Angle 4, facing right/near-profile: **70.0–78.5 s**, `reference_pass4_CONTACT.jpg`.

**Closer diagnostic:** 10 fps crop sequence for **33.0–35.0 s** in `pass2_temporal_CONTACT.jpg` and constituent source frames. Two visually plausible movement phase candidates were extracted at original 1920×1080 resolution: `pass2_t33p5.png` (33.50s) and `pass2_t34p0.png` (34.00s), shown in `source_pair_33p5_34p0_UNVERIFIED.png`. Additional candidate left-oblique pair at 49.0/50.0s is in `pass3_A_B_UNVERIFIED.png`.

### Diagnostic findings

- The original is now **accessible and fully preserved** locally; a missing or inaccessible file is no longer the blocker.
- All four camera passes repeatedly **crop shoes/toes at the lower frame edge** during the action, with occasional frame-to-frame motion blur and near/far lower-leg occlusion. This was already identified in the earlier project diagnostic report and is confirmed again from the authenticated source.
- The 33.5/34.0s pair does show changing arm trajectories and grounded split stance, but **the actual anatomical right/left leg identity through the crossing cannot be traced unambiguously** from those two stills. The 49/50s left-oblique pair looks quite similar, not a defensible inverse endpoint. Two different timestamps are not proof of a valid leg exchange.
- The source athlete is an adult demonstrating the movement. His face/build/outfit are never appearance authorities for the photographic schoolboy, only movement geometry.

**Final physical-leg provenance verdict: INSUFFICIENT / UNVERIFIED.** Do **not** describe either pair as two verified opposite-leg endpoints and do **not** generate new AI scissor art or Flow video based on a claimed swap. A source with an actual same-foot marker (e.g., contrasting wrist/ankle/sock band on one physical limb) and full shoes in frame, or independently labeled anatomy/skeleton with a justified occlusion resolution, is the missing control. Existing source remains valuable for cadence/arm swing and modest stride amplitude, but not certification of near/far ownership.

## Test 3 — colored-ankle physical ownership, one 2×2 generation (new targeted diagnostic)

**File:** `scissor_2x2_V3_orange_teal_DIAGNOSTIC.png`, 1536×1024 photorealistic generated card. **Exact verbatim submitted prompt:** `PROMPT_V3_ORANGE_TEAL_DIAGNOSTIC.txt`. **References in declared order:** approved photographic `identity_sheet_v2_hair_arm_refinement.png` (identity); successful `04_C1_EX3_AlternatingLegRaise_OrangeTealDiagnostic.png` (physical-color-tracking convention ONLY); `scissor_near_trailing_V2_ISOLATED_CANDIDATE.png` (initial leg geometry ONLY). One built-in imagegen call, one candidate, no further revision and no video.

### Independent visual QA, four panels

| Tile | Orange camera-near physical leg | Teal camera-far physical leg | Full shoes/contact | Arm relation |
| --- | --- | --- | --- | --- |
| A, top-left | Trailing (screen-left) | Leading (screen-right) | Both full shoes grounded | **FAIL:** same near/black-wristband arm remains rearward instead of forward opposite teal-leading leg |
| B, top-right | Leading (screen-right), airborne | Trailing (screen-left), airborne | Two full shoes visible; modest athletic jump, front toe points somewhat downward but not ballet | Near arm rearward, plausibly opposite orange-leading leg |
| C, bottom-left | Leading (screen-right), grounded | Trailing (screen-left), grounded | Both full running shoes visible | Near arm rearward, plausible opposite orange-leading leg |
| D, bottom-right | Trailing (screen-left), grounded | Leading (screen-right), grounded | Both full running shoes visible | **FAIL:** visually same arm arrangement as A/C, not the required reverse swing |

**CRITICAL LIMB OWNERSHIP: PASS as diagnostic.** Exactly one small orange band and one teal band are visible in all tiles. Orange is attached to the apparent near anatomical thigh/shin/shoe chain: trailing A, leading B/C, trailing D. Teal visibly follows the complementary far leg. They do not change ankles or merely recolor the same front shoe between endpoints. Unlike V1, the A/C leg positions genuinely alternate. This is strong *model-output* evidence, not retrospective validation of anatomical identity in the adult source video.

**CAMERA / CLOTHES / AGE: PARTIAL PASS.** Stable red track/tree setting, photographic face and normal early-teen proportions, blue sleeveless top, dark-gray shorts, gray/yellow shoes, complete body, fairly fixed scale and no extra limbs. Camera reverted close to pure 90° profile instead of requested 25–30° oblique, which obscures some hip-depth verification. Some slightly different hair/calf detail between panels, minor relative to main objective.

**AUTHENTIC EXERCISE ARMS: FAIL.** The near-side black-wristband arm remains rearward and the opposite arm remains forward in essentially all four tiles. At A/D (orange near leg trailing, teal far leg leading), the near arm should be forward and the far arm rearward. Thus arms did not switch in opposition as required for the RCAF scissor jump, despite text explicitly requiring it. The apparent correct arm-leg relationship in B/C happens only because the legs exchanged, while arms did not.

**OVERALL VERDICT: OWNERSHIP DIAGNOSTIC SUCCESS, FULL 5BX SCISSOR CARD REJECT FOR PRODUCTION.** No marker teleport, correct near/far leading-leg swap, shoes/grounded endpoints intact; nevertheless A/D incorrect opposite arms prevents a valid complete four-phase exercise reference. Do not use for a Flow sequence yet. This is a useful rigid-leg-identity control for the next one-shot revision. Future tests could also physically tag NEAR/FAR WRISTS independently (two small wrist tags) and demand arm trajectory swaps without confusing markers with leg positions; a clean no-band card remains a later, separately verified step.

No GitHub/Drive writes, no video generation, no human approval inferred.

## Test 4 — physical ankle + wrist coupling, one 2×2 joint diagnostic

**New output:** `scissor_2x2_V4_ankle_wrist_COUPLED_DIAGNOSTIC.png`, 1536×1024. **Full verbatim prompt:** `PROMPT_V4_ANKLE_WRIST_PHYSICAL_COUPLING.txt`, containing no omitted follow-up. **References:** (1) approved photographic v2 identity master; (2) V3 scissor colored-ankle diagnostic as leg-pose authority, explicitly NOT as arm-pose authority. One imagegen generation only. Nothing edited on Drive/GitHub; no video made.

### Strict independent panel tracking

| Panel | Orange camera-near physical ankle & shoe | Orange same-side physical wrist & hand | Teal camera-far ankle & wrist | Fore/aft arm-leg opposition |
| --- | --- | --- | --- | --- |
| **A** top-left grounded | Trailing screen-LEFT, complete grounded shoe | **Forward screen-RIGHT**, band at bent fist near shoulder | Teal ankle forward RIGHT; teal wrist backward LEFT | **PASS** |
| **B** top-right airborne | Leading screen-RIGHT, complete shoe off track | **Backward screen-LEFT**, tagged wrist behind torso | Teal ankle trailing LEFT; teal wrist forward RIGHT | **PASS** |
| **C** bottom-left grounded opposite stance | Leading screen-RIGHT, complete grounded shoe | **Backward screen-LEFT** | Teal ankle trailing LEFT; teal wrist forward RIGHT | **PASS** |
| **D** bottom-right return grounded | Trailing screen-LEFT, complete grounded shoe | **Forward screen-RIGHT** | Teal ankle leading RIGHT; teal wrist backward LEFT | **PASS** |

**LIMB OWNERSHIP AND MARKER COUPLING: PASS (DIAGNOSTIC).** Both orange bands consistently remain on the apparent camera-near side's wrist and ankle, and both teal bands on the far side's wrist and ankle. Colors do not migrate from one shoe to another or relabel a stationary forward hand: wrists genuinely swing to opposite positions A/D versus B/C, with shoulders/elbows changing accordingly. Exactly two wrist and two ankle tags per panel. The former black wristband is replaced temporarily by colored marker, without a third black wristband. Leg hip-to-shoe chains also alternate, retaining V3's genuine orange-trailing / orange-leading reversal.

**CROSS-OPPOSITION TRACKING: PASS, BUT HISTORICAL ORIGINAL-5BX ARM FORM: FAIL (independent later review).** A/D: near orange leg BACK, near orange hand FRONT; far teal leg FRONT, far teal hand BACK. B/C: near orange leg FRONT, near orange hand BACK; far teal leg BACK, far teal hand FRONT. This fixes V3's same-arm-in-front error, but the **bent ~90-degree runner's elbows and hands near chest/waist are not the booklet's extended near-shoulder-height arms**. All full shoes visible; A/C/D grounded; B airborne with both shoes off track. B front toe points mildly downward within normal athletic running footwear, not exaggerated ballet pointed toes.

**IDENTITY / ENVIRONMENT: PASS CANDIDATE.** Similar 13–14-year-old v2 photorealistic appearance, fair skin, unmuscular limbs, messy dark hair, same plain blue tank/dark-gray shorts/gray-yellow trainers, same red track/trees, consistent panel scale and no extra limbs or duplicated fingers. The boy remains ordinary early teen. A/D and B/C appear largely identical pose pairs as requested; D genuinely returns to A.

**VIEWPOINT: PARTIAL / LIMITATION.** Despite repeated explicit oblique-angle instructions, the lens remains near a strict side-on angle rather than requested 20–30° view. Marker linkage is highly legible, but there is less independent photographic depth evidence for shoulder/hip near/far attachments than ideal. Thus this verifies the model can render tagged cross-opposition reliably in a visually plausible card, not that a real anatomical source skeleton has been proven frame-by-frame.

**HISTORICAL VERDICT (REVISED): FOUR-LIMB OWNERSHIP DIAGNOSTIC SUCCESS; ORIGINAL 5BX SCISSOR EXERCISE FORM FAIL.** Joint ankle/wrist markers solve the prior arm/leg identity problem, but the incorrectly flexed running arms disqualify this card as authentic Chart 1 scissor form. It is retained solely as a limb-tracking reference, never production-approved.

**New prompt lesson:** Binding *each physical arm to its same-side physical leg using two persistent visual identifiers* and expressing the alternating fore/aft wrist/ankle X relationships in all four tiles was materially more effective than bare instructions to “swing opposite arms.” The previous V3 never switched arms, despite repeatedly mentioning opposite-arm swing; V4 visibly switches both physical wrists while holding the leg exchange intact.

## Test 5 — clean marker-removal edit, first pass retained (no retry)

**Output:** `scissor_2x2_V5_clean_NO_BANDS_CANDIDATE.png`, 1536×1024. **Exact verbatim imagegen edit prompt:** `PROMPT_V5_CLEAN_BAND_REMOVAL.txt`. **References in order:** V4 four-band scissor diagnostic as pose/composition authority; v2 four-view identity master for natural socks/wristband. One edit call; no second attempt needed after visual QA.

### Strict comparison to marker-verified V4

| Check | Observed V5 result | Verdict |
| --- | --- | --- |
| A top-left | Near leg trails, far leg leads; **black wristband on near-forward arm**, far-rear wrist bare | **PASS** visual pose/owner preservation |
| B top-right | Near leg leads airborne, far leg trails airborne; **black wristband on near-backward arm**, far-forward wrist bare | **PASS** visual pose/owner preservation |
| C bottom-left | Near leg leads on track, far leg trails; **black wristband on near-backward arm**, far-forward wrist bare | **PASS** visual pose/owner preservation |
| D bottom-right | Near leg trails again, far leg leads; **black wristband on near-forward arm**, far-rear wrist bare | **PASS** visual pose/owner preservation |
| Band removal | Orange and teal ankle/wrist bands gone from all four tiles; two naturally charcoal socks and ONE unobtrusive dark wristband, consistently on near physical arm | **PASS** |
| Four-panel registration | Identical 2×2 white gutters, static track/trees/lane marks, same boy and clothing; shoes and heads uncut | **PASS visually**; minor photo texture/details changed |
| Athletic anatomy | Body not stretched, no altered limb count, modest normal shoe/heel orientations, full grounded and airborne footwear | **PASS visually** |
| Camera-angle goal | Essentially right-angle side view rather than requested 20–30° oblique | **PARTIAL; unchanged limitation** |

The generated clean candidate is VERY closely registered to V4; `magick compare -metric MAE V4 V5 null:` returned **1367.78 / 0.020871 normalized** (roughly 2.1% average pixel-channel difference), which is consistent with retouching and incidental texture regeneration. The numerical difference does **not** independently prove motion or anatomical correctness; the qualitative four-panel limb/black-wristband trace above is the decisive check.

**HISTORICAL QA OUTCOME (REVISED): CLEAN NATURAL-RUNNING-ARM OWNERSHIP DIAGNOSTIC PASS, ORIGINAL 5BX ARM FORM FAIL.** V4's color-coupled physical arm/leg alternation survives removal of tags, as far as static side-on images permit inspection. The black wristband is an unobtrusive near-arm ownership cue: forward A/D, rearward B/C. **However, its elbows remain substantially flexed and hands too low to depict booklet-prescribed extended arms near shoulder height. Thus V5 must not be called a 5BX production candidate** despite excellent clean-edit registration. Keep V4 alongside V5 only as an auditable marked/clean limb-identity pair.

**Production lesson:** A marked four-limb topology card can support a very tightly specified small-region edit, yielding a clean photographic result with correct apparent opposition and high registration. If future V5 animation reveals reversals or drift, retain V4 markers as the reference truth and fix motion before generating another clean image. Never infer motion success from this still comparison alone.

No external uploads, no repo writes, no Flow video, and no final human approval.

## Independent booklet-form correction discovered after V5

The two tag-tracked cards V4/V5 genuinely solved physical limb-ownership but **did not meet original Chart 1 scissor-jump arm form**. Independent verification of `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md` identifies the instruction to extend one arm and opposite leg forward with other arm and leg back and hold arms around shoulder height. V4/V5 instead depicted a more common modern running-pump with elbows bent around 90° and rear hands low. They must remain archived as *natural running-arm mechanics tests only*, not 5BX exercise references. Do not erase their useful positive color-owner tracking results, but do not promote them to video.

## Test 6 — corrected straight extended arms at shoulder height (colored four-limb diagnostic)

**Generated image:** `scissor_2x2_V6_TAGGED_STRAIGHT_ARMS_DIAGNOSTIC.png`, 1536×1024, one imagegen edit of V4 tagged card using approved v2 identity sheet as secondary reference. **Exact submitted prompt:** `PROMPT_V6_5BX_STRAIGHT_SHOULDER_ARMS_TAGGED.txt`.

| Element | Four-tile evaluation | Status |
| --- | --- | --- |
| Near camera-side orange leg | Trails A/D, leads B/C, same orange ankle band/shoe lineage | **PASS diagnostic** |
| Far teal leg | Leads A/D, trails B/C, teal ankle remains with far physical leg | **PASS diagnostic** |
| Near-side orange arm | **Long and essentially straight at shoulder height**, forward A/D and rearward B/C; orange wristband follows near anatomical arm | **PASS diagnostic** |
| Far-side teal arm | Long and straight near shoulder height, rearward A/D and forward B/C; teal wristband follows far anatomical arm | **PASS diagnostic** |
| Arms/legs opposition | A/D orange wrist on RIGHT with orange ankle LEFT; B/C orange wrist LEFT with orange ankle RIGHT; teal reciprocal | **PASS diagnostic** |
| Ground and airborne timing | A/C/D normal complete shoes appear on track, B both shoes off track in measured modest jump | **PASS visual** |
| Youth identity, anatomy | Fair 13–14yo with soft arms/legs, same face/hair, blue top, charcoal shorts, normal shoe shape; no extra limbs | **PASS visual** |
| Camera/viewpoint | Constant track/trees and complete heads/shoes, BUT lens remains mostly true side profile rather than requested 20–30° oblique | **PARTIAL** |

**Verdict V6: TAGGED 5BX FORM DIAGNOSTIC PASS, HUMAN JUDGMENT PENDING.** The high extended straight-arm line now differs decisively from V4/V5, and color markers indicate anatomically consistent opposing arm/leg ownership across all four panels. Backward arm extension is high at the shoulder and should receive a human biomechanics sanity check; the model must not be credited as proof of what all middle-schoolers comfortably achieve. Nonetheless no visually evident dislocated elbow or duplicate arm. This warranted the authorized clean edit V7.

## Test 7 — clean edit preserving V6 straight-arm 5BX geometry

**Generated image:** `scissor_2x2_V7_CLEAN_5BX_STRAIGHTARMS_CANDIDATE.png`, 1536×1024, one imagegen edit with V6 tagged card as primary pose authority and approved v2 identity master second. **Exact submitted prompt:** `PROMPT_V7_CLEAN_5BX_STRAIGHTARMS.txt`.

**Band-removal QA:** All eight ankle bands and eight wrist bands from four panels removed. Each tile now has two plain charcoal socks and exactly one subtle dark/black wristband on the camera-near physical arm. No orange or teal cuff residue. Black near wrist is **forward in A/D** along with trailing near leg, and **rearward in B/C** along with leading near leg. Far arm remains bare and reciprocally opposite. Both arms still extended long and essentially horizontal at approximately shoulder height in EVERY tile, not the bent running-pump V5 posture. Near/far hips, knees, shoes and opposing positions are visually unchanged; B jump remains modest and A/C/D grounded. Same fair teenage face, hair, clothing, static 2×2 camera, green field/red track and full shoes/head framing. No visible extra limbs or ballet toe points.

**Registration check:** ImageMagick normalized mean absolute per-channel pixel difference V6→V7 = **0.0169184 (~1.69%)**, consistent with local colored-band replacement and minor generative texture differences. This numerical correlation is supplementary: visual limb trace is the actual exercise-form gate.

**Verdict V7: CLEAN 5BX STRAIGHT-ARM CANDIDATE — AGENT VISUAL PASS, NOT APPROVED.** V7 appears to preserve V6's meaningful improvement over V4/V5 and may be presented to the owner for form judgment. Camera near strict side-view and potentially ambitious rear shoulder extension remain open review points; this static card has not yet been motion-tested. Keep V6 tagged side by side with V7 clean as the auditable anatomy pair. Do not create Flow video or claim owner approval automatically.

**Lesson now confirmed:** Movement-specific **booklet form** and physical limb identity are separate QA gates. Persistent wrist/ankle color markers solved topology; enforcing near-straight shoulder-height fore/aft arms then solved the historically missed 5BX instruction, and a subsequent marker-removal edit kept those arms. All three gates—identity/ownership, actual source exercise form, clean edit—must pass independently before video.

No repository or Google Drive writes, no external video generation, and no human approval inferred.
