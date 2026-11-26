# Chart 1 Ex1 toe-touch start frame — wider-camera headroom edit

Status: **STRONG PROVISIONAL STILL / not video- or human-approved**. Built-in imagegen image edit of the original high-resolution single still, using the approved master as the second reference. No Flow test yet.

## Inputs

1. EDIT TARGET: `02_CANDIDATE__Chart1_ToeTouch_ArmsUpStart_Full16x9_35mm.png`, 1672×941. Already excellent body/form/detail, but fingertips were within ~2–3% of top edge.
2. IDENTITY REFERENCE: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`. Identity, skin, hair, outfit, soft normal physique.

## Output

`03_CANDIDATE__Chart1_ToeTouch_ArmsUpStart_Headroom35mm.png` (1672×941, full-res PNG)

## Exact prompt supplied to imagegen

```text
Use case: identity-preserve, precise image edit
Asset: high-quality 35mm-style photographic start frame for a 5BX exercise animation.
Image 1 is the EXACT photo to edit (full-body 13–14-year-old boy with both arms raised on red running track). Image 2 is the immutable approved identity reference. Change one thing: reframe Image 1 to give the fingertips at least 12–15% of picture-height empty background above them, using a wider camera field of view / moving a virtual camera backwards. This must visually SHRINK the boy as a whole slightly within the same 16:9 horizontal landscape frame. Keep the entire body fully visible, with 5–8% floor clearance below both shoes. Place him center, frontal near-zero-degree with both feet evenly planted slightly apart, both arms extended straight UP naturally above shoulders; hands fully open and anatomically normal.
IMAGE IDENTITY LOCK: The exact same middle-school boy from Image 2, age 13–14, pale Caucasian skin not tanned, compact slightly messy dark-brown hair, natural small button nose, exact ear sizes, brown eyes, innocent neutral unsmiling expression. Typical undeveloped teen body, gentle soft arm contours, NO pronounced muscle, not thicker or thinner; same blue sleeveless tank top, charcoal gray athletic shorts, dark ankle socks and light gray shoes with yellow accents, black fitness wristband. Preserve outfit and colors.
BACKGROUND LOCK: Match the same outdoor track, red rubberized lanes, green field and green treeline and level midday soft photographic lighting, real natural depth and texture as Image 1.
DO NOT lengthen arms, stretch torso, change stance, bend arms, make hands larger, add movement, change face, hair, skin, shoes, clothing, perspective or camera height. No cropped extremities, no added people, captions or labels, no logos. Preserve near-photographic quality, subtle 35mm film grain, realistic teenage anatomy. Only composition/framing changes.
Very important final geometric check: visible sky/treeline space from highest fingertip to top edge equals at least 12% of image height, the arms/hands have normal original length, and both feet are visible with floor margin. Single image, not a contact sheet.
```

## Visual QA

| Gate | Observation | Verdict |
|---|---|---|
| Top margin | Highest fingertips around y=152 in 941px high frame (~16% margin), comfortably exceeds 12% target. | PASS |
| Bottom margin | Both complete shoes around y=867/941, ~7.8% clearance. | PASS |
| Body/pose | One boy centered; balanced shoulder-width astride stance, knees straight, both feet flat, both hands raised with natural open palms, no lengthening, hands remain separated. | PASS |
| Identity | Blue/charcoal/gray-yellow outfit and soft body match master. Face retains broad resemblance. Hair slightly more textured/curly than 02, body may be a little narrower due camera distance. | MINOR WATCH |
| Scene | Same red rubber track, green field, treeline; natural daylight and detailed filmic texture. Background has a bit more pale sky than 02, as expected from reframe. | PASS |
| Motion/Flow | This is a still. No animation and no verified motion. | NOT TESTED |

**Verdict:** the targeted correction succeeded. Prefer **03** over **02** as the safe start frame for a first toe-touch image-to-video experiment. Track the small hair/face differences if other pose start frames are matched together; maintain the v2 identity master as authority. A static camera can use this framing without cutting off fingers in the upward/backward stretch. This does **not** certify generated motion or age consistency across a future video.

## Next experiment

Try an image-to-video segment anchored on this ONE high-res still with a static camera; insist on both feet grounded, normal arm length, hands descend to floor approximately between feet rather than physically impossible 6-inch outside-foot reach. Do not force perfect flexibility; body proportions immutable. Review real exported frames before approved status.
