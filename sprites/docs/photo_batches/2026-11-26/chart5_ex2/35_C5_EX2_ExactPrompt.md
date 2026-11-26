# ID35 — Chart 5 Exercise 2: alternating twisting sit-up

## Generation request (verbatim)

Generate ONE premium, high-resolution 2×2 photographic contact sheet (four panels labeled only A, B, C, D) showing the SAME American middle-school boy performing the original 1959 RCAF 5BX Chart 5 Exercise 2 *twisting sit-up*. Each panel is a distinct carefully posed 35 mm film-quality sports photograph, same locked tripod camera and same outdoor red running-track location, grass and soft woodland behind. Each panel fully shows him head to shoes; natural daylight; clear, unobscured joint anatomy. This is a precise physical-education movement analysis, not a glamour or bodybuilding picture.

CHARACTER IDENTITY: Match the supplied primary reference identity sheet, not the other movement references. Identical approximately 13–14-year-old boy in all four panels: fair/pale untanned Caucasian skin; softly proportioned, normal not thin or heavy, age-appropriate undeveloped arms/shoulders/legs with little visible muscle definition, no body or facial hair, smooth youthful oval face, modest button nose, unchanged ear shape/size, open eyes; slightly messy short dark-brown hair with a little volume on top, not fluffy and not a shaved fade. Same navy/medium blue athletic sleeveless shirt, charcoal shorts, neutral grey athletic shoes with muted yellow accents, dark ankle socks, plain dark wristband. Do not turn him into an adult, bodybuilder, younger child, or cartoon. He has exactly two arms, two hands, five fingers per hand, two physically distinct legs, two feet, coherent joints. Preserve his face and outfit identically across all phases.

CAMERA: A single stable camera at a modest 25–30° oblique angle relative to the axis of his body, essentially side-on but high enough to see which knee moves forward and which elbow crosses his midline. Same distance, lens, lighting and framing all four panels. The boy's head is on the LEFT of each frame and feet toward the RIGHT. During sit-up the boy turns his torso, but the camera does not move, mirror, zoom or cut. Athletic mat or dry flat track underneath, realistic contact shadows, green trees and soft grass in the background. Leave space around every elbow and shoe; keep left and right anatomy legible. Four equal panels with thin white gutters, no explanatory lettering besides A B C D.

EXERCISE FORM: Starting position is supine, back on ground, BOTH legs straight and together, heels supported, BOTH HANDS interlaced/clasped behind the head; elbows separated naturally. A twisting sit-up is performed by flexing the trunk and simultaneously bending ONE knee up toward the chest and rotating the torso toward that raised knee. Critically, the elbow and bent knee must be OPPOSITE SIDES of the body: right elbow toward left knee (contralateral), then left elbow toward right knee. The arm never sprouts an additional forearm, the hand never leaves the back of the head to touch the knee. An anatomically honest near-touch is acceptable; do not distort the length of limbs or spine just to create contact. The non-lifting leg stays long and extended on ground. Feet are flexed or naturally relaxed, not dancer-pointed.

PANEL A — Neutral start: lying naturally supine with torso and head down, knees straight together, feet together; BOTH hands clasped behind head, elbows splayed. Full body, head left, shoes right.

PANEL B — RIGHT ELBOW / LEFT KNEE: from lying, chest curling up and torso rotating across centerline toward his anatomical LEFT knee, which alone bends upward; the anatomical RIGHT elbow moves diagonally toward the cap of the lifted anatomical LEFT knee. His anatomical RIGHT leg is still extended straight along the ground. His hands remain interlaced behind head. The knee visibly originates from the LEFT hip, the extended leg visibly originates from the RIGHT hip; no crossover cheating or mirrored limb, no elbow touching same-side knee. RIGHT-ELBOW-TO-LEFT-KNEE is the single diagnostic requirement for this panel.

PANEL C — LEFT ELBOW / RIGHT KNEE, REVERSE REP: a distinct reverse-side sit-up with his anatomical RIGHT knee alone bent and raised and his anatomical LEFT leg fully extended on the ground. His anatomical LEFT elbow sweeps toward his anatomical RIGHT knee while his chest and shoulders rotate ACROSS his midline in the opposite direction from B; hands remain behind his head. The bent knee originates at the RIGHT hip and extended leg at the LEFT hip. Do NOT copy B then only exchange which leg is up; actually reverse the spinal/shoulder twist and targeting elbow. LEFT-ELBOW-TO-RIGHT-KNEE is the single diagnostic requirement here.

PANEL D — Return to supine neutral: both legs extended together, feet relaxed; hands still interlaced behind head; torso down, same framing as A. A and D visually bookend two alternate-side repetitions, not sequential impossible movement. Do not depict both knees bending simultaneously, a bicycle crunch with feet flying, a regular straight sit-up, or a yoga pose.

Visual character consistency is as important as biomechanics. Shutter-speed-sharp 35mm photographic realism, modest 1990s-style track sports photography, fine natural skin texture, soft light, slight film grain, no painterly/cel shading. Four realistic shots of exactly one persistent boy with credible unforced flexibility. Preserve full complete limbs, normal finger count, visible hip-to-knee-to-ankle topology, distinct shoe per foot.

## Reference input order and roles

1. `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` — canonical character appearance, same boy.
2. `artifacts/parallel_batch_20261126/chart3_ex2/26B_C3_EX2_SlightKneeBend_35mm_CANDIDATE.png` — supporting full-body and hands-behind-head shape, not identity.
3. `artifacts/parallel_batch_20261126/chart2_ex2/23B_C2_EX2_FullSitup_HandsOffGround_35mm_CANDIDATE.png` — supporting sit-up body-ground geometry, not identity.

## Invocation

`image_gen__imagegen` with the three listed `referenced_image_paths` in that order and `transparent_background=false`.
