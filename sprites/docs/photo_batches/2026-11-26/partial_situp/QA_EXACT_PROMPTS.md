# 5BX Chart 1 Exercise 2: Partial Sit-up — photographic four-phase card

## Output and source

- **Date:** 2026-11-26 UTC.
- **Tool:** Built-in image generation, one generated image with one appearance reference.
- **Identity authority:** `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`. Its four standing views determine actor/outfit, **not exercise form**.
- **Movement authority:** `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md` Chart 1 Exercise 2: back lying, feet six inches apart, arms at sides; rise just far enough to see heels.
- **Output:** `01_CANDIDATE__Chart1_PartialSitup_FourPhase_35mm.png` (1199×1312, 2×2 grid).
- **Output SHA-256:** `c7abe60bc7aa7719d6b9c1636ca143d777372a5682a567e96bbc86ccaf5c8830`.
- **Status:** **CANDIDATE**, assistant visual inspection only; no video tested or Charles approval.

## Exact submitted prompt (verbatim)

```text
Use case: photorealistic-natural.
Asset: one high-resolution 35mm documentary-photography FOUR-PHASE CONTACT SHEET for the authentic 5BX Chart 1 Exercise 2 PARTIAL SIT-UP, a school fitness instructional reference.
Input Image 1: the supplied four-angle character-master sheet is the sole authority for the boy's identity, recognizable 13–14-year-old face, eyes, nose, ear shape, naturally messy modest dark-brown hair, fair skin, normal slightly soft undeveloped body, exact BLUE sleeveless athletic tank, CHARCOAL running shorts, dark ankle socks, gray/yellow sneakers, black wristband, and outdoor red school track with grass and trees. Its standing poses are NOT exercise pose references. Keep this identical boy in every new panel.
Make ONE photorealistic 2×2 grid of four coherent still photos in chronological order, with narrow white dividers, same fixed tripod camera at low slight side-oblique angle (~20 degrees, allowing both feet to be seen), same distance, framing, lighting, boy's scale and surrounding track/field. Head toward IMAGE LEFT and shoes toward IMAGE RIGHT in all panels. Entire head to shoes within every panel, generous safe margin, shoes and hands not cropped. Real skin and fabric microtexture, authentic gray-yellow running-shoe details, soft outdoor daylight, not a cartoon or painterly/airbrushed render.
STRICT BOOKLET MOVEMENT: Chart 1 PARTIAL SIT-UP, NOT THE LATER FULL SIT-UP. START LYING SUPINE, feet approximately SIX INCHES APART, LEGS FULLY EXTENDED and both heels planted; BOTH ARMS AT HIS SIDES beside hips with hands resting on the red track. He must lift only his HEAD, SHOULDERS and UPPER BACK slightly, just enough so his eyes can see his own heels. His lumbar spine, pelvis, legs and heels remain in contact with the track throughout, with no sitting upright and no reaching to toes.
Panel TOP LEFT START: boy rests face-up fully supine, shoulders/head down, arms along sides, shoes to right and heels down.
Panel TOP RIGHT EARLY RISE: neck and upper shoulders begin curling off track only a little, chin gently toward chest, abdomen relaxed, arms still alongside torso, heels motionless.
Panel BOTTOM LEFT MAXIMUM PARTIAL SIT-UP: small modest controlled crunch, shoulder blades now a little above track, approximately 20–30 degree upper-back lift, neck comfortable, gaze downward along straight legs toward heels; pelvis and low back remain down, both arms still low and parallel to the body. This is distinctly NOT vertical sitting.
Panel BOTTOM RIGHT RETURN: fully supine again, head and shoulders settle back to the EXACT START, arms remain at sides, shoes/heels same positions. No change of boy's identity, haircut, clothes, camera, horizon, or scale.
Absolute anatomy rules: one believable ordinary middle-school boy with only two arms, two legs, two hands, two feet; same nonmuscular shoulders and non-sculpted waist all panels, no stretched torso/neck or adult abdominal definition, no pelvis lifting, no bent or floating knees, no feet leaving track, no extra limbs or duplicated body, no camera shift, no exercise text labels, no fading/ghosting, no overdone gym crunch, no grown-up gymnast.
```

## Assistant visual QA

| Check | Observation | Verdict |
| --- | --- | --- |
| Booklet-specific movement | Shows supine, mild shoulder rise, approx. 20–30° partial curl, fully supine return. Does **not** do Chart 2+ full sit-up. | PASS provisional |
| Feet / legs | Both legs extended, heel contact appears stable, shoes in the same approximate positions. Exact six-inch separation cannot be confirmed from projected 2D perspective. | PASS with caveat |
| Arms | Both hands remain near hips alongside body; slight natural sliding during curl. No extra arms. | PASS |
| Age / body | One fair, plausible 13–14-year-old with normal waist and undeveloped arm/shoulder definition; not babyish or adult muscular. | PASS provisional |
| Outfit / scene | Blue tank, charcoal shorts, dark socks, gray/yellow shoes, black wristband, red track/tree line are constant. | PASS |
| Camera | One visibly fixed scene and horizon per four poses; margins ample. Subject small in frame due broad landscape, reducing facial pixels. | PASS with fidelity tradeoff |
| Face | Face resembles v2 in all visible panels, but low panel resolution limits detailed identity verification. | REVIEW |
| Motion | Still contact card only; temporal interpolation, loop seam and pelvis/heel registration untested. | NOT TESTED |

## Lessons / next smallest test

1. Naming the **Chart 1 partial** range and explicitly forbidding full vertical sitting avoided the common full sit-up pose leakage.
2. Four synchronized phases jointly preserved wardrobe and camera better than individually unrelated stills; do not extrapolate this to video until tested.
3. The face is small in the full-card tiles. Before a production Flow test, generate or extract **one more detailed, well-registered neutral supine opening frame** directly from the approved identity master; don't chain from an earlier generated video.
4. Flow next test: single start image; 0–1 s flat; 1–3 s lift head/shoulders only far enough to see heels, feet/pelvis grounded; 3–6 s fully lower to identical start. Fixed camera, actual continuous motion, no ghost/reverse frame ordering.

## Second generation — detailed single opening frame

- **Why:** four-phase 1199×1312 contact-card tiles allocate only ~600 pixels each in width. A single well-framed native 16:9 photo could preserve face/hair/shoe pixels when subsequently used for Flow video.
- **Output:** `02_CANDIDATE__Chart1_PartialSitup_SupineStart_35mm.png`, 1672×941. High-resolution realistic starting supine pose; boy occupies much more of the frame, while leaving vertical headroom and full foot margin.
- **Output SHA-256:** `d4c4844204e28835357211aee01ea29509a3e89632995338e81ca6e6400f2394`.
- **Input image 1:** same approved master v2, **identity authority**.
- **Input image 2:** the just-generated 4-phase contact card, **pose/scene authority only**, top-left frame.
- **QA:** PASS provisional on realistic clothing detail, face/shoulder/leg proportions, flat start posture, two heels grounded and both arms at sides. The far arm is partly hidden, appropriate to side view. Age appears about 13–14. No motion test yet. This is not a substitute for the original master as the identity authority.

### Exact second submitted prompt

```text
Use case: photorealistic-natural.
Asset: SINGLE high-detail, full-width cinematic 35mm photographic START FRAME for 5BX Chart 1 partial sit-up video, one boy and one scene, not a grid.
Reference image 1 (four-angle master): STRICT authoritative boy/wardrobe identity. Keep the exact same recognizable fair-skinned 13–14-year-old middle-school boy, natural moderately messy dark-brown hair, slightly soft undeveloped shoulders/arms and normal waist/chest/thighs, BLUE athletic sleeveless tank, loose CHARCOAL running shorts, dark socks, light gray/yellow running shoes, black wristband. No older or younger replacement, no new muscles, no different nose or face.
Reference image 2 (joint four-phase card): POSE/SCENE authority ONLY. Use its TOP-LEFT fully supine position and consistent outdoor red running track/grass/tree line as the composition source, not its lower phases.
Create ONE unlabelled 16:9 landscape photograph in a fixed static camera, low about 20-degree side-oblique view. The same boy lies FLAT ON HIS BACK on the red track, head toward IMAGE LEFT, shoes toward IMAGE RIGHT, both extended legs straight and placed six inches apart; both heels rest on the track, feet at neutral natural ankle angle. Arms straight comfortably at his sides, palms resting lightly on track beside his hips, head/shoulders/back/hips entirely resting on track, neutral breathing. Entire head to both shoes visible with safe space at image ends and room above for later partial curl. Boy should occupy a useful width of the image (roughly 75% of frame width), but full body never cropped. Consistent photographic track/field/forest background, soft outdoor daylight, sharp recognizable face, individual natural hair strands, genuine cotton shirt wrinkles and realistic cloth stitching and sneaker materials, unretouched normal skin details. No text, logos, arrows, dividing lines, second person, hallucinated limbs, airbrushed cartoon appearance, hyper-developed arms, torso lifted, feet sliding, adult face, camera pan/zoom or artistic bokeh that obscures exercise geometry.
```

### Ready-to-paste next single-frame Flow test (PROPOSED, not executed)

```text
One uninterrupted 6-second locked-off 35mm documentary video, starting exactly with the attached full-body supine photograph of the same boy and ending in that exact posture. Keep the same 13–14-year-old face, hair, soft nonmuscular body, blue tank, charcoal shorts, gray/yellow sneakers, red track/green field and fixed camera. Perform exactly ONE Chart 1 PARTIAL SIT-UP (mini-crunch), NOT a full sit-up: 0–1 seconds lie flat on back, both arms at sides, legs straight and both heels planted about six inches apart. 1–3 seconds slowly lift only the head, shoulders and upper shoulder blades 20–30 degrees, just high enough to look toward his own heels, while lower spine/pelvis/legs and feet remain fully grounded. 3–6 seconds slowly lower upper back, shoulders and head until entirely supine again with hands still at sides and both heels planted, matching frame one. No sitting upright, reaching toward toes, bending knees, lifting feet, sliding hips, camera movement, shrinking subject, clothing changes, crossfades, extra arms, reversal of image sequence, loops that finish partly raised, dialogue or text.
```

