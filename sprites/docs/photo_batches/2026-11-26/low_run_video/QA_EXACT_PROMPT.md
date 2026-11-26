# Chart 1 — low stationary run (4-inch lifts): Flow video pilot

Date: 2026-11-26 UTC

Status: **GENERATED; REVIEW, not yet approved.** A real six-second video was produced in Google Flow; its editor opened and playback controls worked. Complete visual motion/frame QA and an archived downloadable MP4 remain pending.

## Direct Flow links

- Video: [20_REVIEW__C1_LowRun_4in__BlueCharcoal__2026-11-26](https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/edit/cfc5982b-03f5-4bc6-a103-afdf05a7558c)
- Initial short-lived title (historical alias): `15_REVIEW__LowRun_4in__BlueCharcoal__2026-11-26`, renumbered to avoid collision with other exercise pilots.
- Standing anchor image edit history: [Saved frame from 08_REVIEW, edited to standing](https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/edit/dfb750af-b6e8-412a-843b-ef40b3fca87f)

## Method and model

1. In authenticated Flow, opened a previously saved still from the 08 straight-sit-up sequence. Used the in-product image editor to change posture to neutral standing, keeping the track, blue tank, charcoal shorts and same person. The image editor identified its model as **Nano Banana 2.1**.
2. Visually inspected the resulting standing full-body single frame in Flow. It has a realistic photographic appearance, right-facing side/very slight oblique track view, legs distinguishable and ample framing. Kept it as a **native Flow asset** and attached through Flow's ingredient picker, so no computer/browser file upload was needed.
3. Submitted a single image-anchored six-second video under Flow's **Omni 1.2 Flash** default model. Flow requested **18 credits** for 1 video; approved only this one generation. Generation completed and video editor opened. Project renamed to the review title above.
4. Video editor reports `Total duration: 00:06:00` (Flow timecode meaning six seconds). Playback was started, its timer advanced, and then paused. `Download media → 720p Original size` displayed the toast **“Your video has been downloaded!”**, but no MP4 appeared in the terminal's `/opt/codex/downloads` directory. Browser guidance pointed to `/workspace/shared/downloads`, which is not mounted in the shell's workspace either. Thus this note cannot attest to local file QA or 720p frame dimensions.

### Exact still-generation prompt

```text
Use case: photorealistic-natural. Generate ONE highly detailed 35mm DOCUMENTARY PHOTOGRAPHIC SINGLE STILL of the EXACT SAME realistic 13-14-year-old boy as this input. Keep his same face, slightly messy brown haircut, age, fair skin, modest softly undeveloped physique, blue tank top, loose charcoal-gray mid-thigh running shorts, charcoal socks, gray/yellow sneakers, black wristband, and the identical red outdoor running track, grass field, trees and even daylight. CHANGE ONLY HIS BODY POSTURE: he is now STANDING UPRIGHT at ease, head to image RIGHT, true right-facing side profile with a subtle 10-15-degree camera oblique angle so the two separate shoes are visible; both feet flat on the track about shoulder width, one foot just 15 cm in front of the other, elbows comfortably bent beside waist preparing to jog gently in place, no running motion yet. Full body is visible, no crop, 10 percent margin on all sides, stable tripod camera with wider full-body framing and ample room above the head and below the shoes for later 4-inch stationary jogging. Maintain source photographic fidelity: crisp fabric texture, realistic youthful face, natural short dark hair, non-muscular arms and thighs, detailed running shoes, natural depth of field. No movement blur, no other people, no bent joints, no extra limbs, no labels, no text, no change of apparent age or scale. It is an entirely new single still pose, not an animation or collage.
```

### Exact submitted video prompt

```text
Generate ONE uninterrupted 6-second high-fidelity 35mm PHOTOGRAPHIC VIDEO using the ATTACHED SINGLE STANDING PHOTO as the exact first frame and identity anchor. This is Chart 1 of the historical 5BX fitness program: an ordinary unmuscular 13-14-year-old middle-school boy performs a LOW STATIONARY RUN IN PLACE, alternating LEFT and RIGHT foot lifts only approximately FOUR INCHES (10 cm) above the red track. The camera is a fully fixed tripod at the same right-facing 10-15 degree profile; same medium-wide full-body framing for the entire shot, no camera movement. 0-0.5 second: relaxed identical standing start. 0.5-5.5 seconds: rhythmic gentle jog in PLACE, five to seven visibly ALTERNATING steps, RIGHT sneaker briefly lifting approximately 4 inches then re-planting, LEFT sneaker lifting about 4 inches then re-planting, repeating with light coordinated opposite arm swing. Each foot returns to approximately the same track mark; hips stay over the same spot, shoulders relaxed, knees never come near waist height, no forward travel, no scissor jump or high hop. 5.5-6 seconds: naturally settle to the same upright stance as the opening frame for a plausible loop. Every foot/shoe stays a physically attached normal-sized limb; no leg swaps or extra legs. Keep the same recognizable boy face, dark slightly messy haircut, age, fair untanned skin, normal soft undeveloped body, same light-blue tank, loose charcoal shorts, dark socks, gray/yellow sneakers, wristband, trees/grass/track, light and natural clothing texture. Continuous real motion with actual airborne and landing intervals, not dissolves or mirrored frames. No camera pan, tilt or zoom; no cuts, ghost copies, duplicate arms, body growth, ballet pointed toes, changing shoes, shifting sky, background warp, text or audio.
```

## QA and provenance caveats

- Chart 1's running instruction is a low stationary run with feet raised approximately 4 inches; no 10-scissor-jump set was attempted within six seconds. This phase separation is intentional.
- The **approved v2 master sheet** was inspected in earlier project work but **was not uploaded as the image ingredient for this video**. The source here was the prior in-Flow `08_REVIEW` straight sit-up saved frame, reposed as a standing still. Exact v2 facial/age/wardrobe adherence should be human-reviewed before promotion. This pilot is useful to assess motion mechanics and static-camera interpretation, not a definitive identity-locked master.
- The browser had a valid authenticated Flow session, native ingredient attachment worked, and a generated video was observed. A local 16:9 high-resolution source upload was **not attempted**; it cannot yet be claimed that local 1672×941 images upload cleanly or yield superior video output.
- In the browser's displayed video frame at around `00:04:16`, the boy appeared full-body on track, blue top/charcoal shorts, one sneaker planted and the other raised, with an ordinary youthful non-muscular physique and no immediately visible extra limbs. The visible raised foot might exceed 4 inches slightly; this should be checked against a proper decode. Flow's timeline timecode could be scrubbed to `00:00:11` and playback advanced, but screenshots continued showing the same cached video frame; therefore **the multiple requested screenshot samples were not independent frame evidence**. Static camera, exact low lift, left/right alternation, body drift, hands/feet count throughout, frame-to-frame identity, and loop closure are **not yet verified** from decoded output frames. Verify by watching the direct Flow clip or downloading it into an accessible environment.
- The original 720p download toast succeeded but local shell QA was blocked by the cloud-browser/shell download boundary. No generated MP4 was copied into this artifact directory; don't mistake the Flow project link for a public unauthenticated URL.
- **Classification: CONDITIONAL IDENTITY, MOTION NEEDS REVIEW.** This is not an approved video for final Chart 1 use until both decoded motion and v2 face/age equivalence pass QA.

## Next test suggestion

If this motion is promising, compare against a directly uploaded native 1672×941 approved-identity single standing photo. Use the **same prompt/model/duration/viewpoint** to isolate whether anchor fidelity changes the face and limb motion. Preserve the local original download and inspect at 0.0, 1.0, 2.0, 3.0, 4.0, 5.0 and 6.0 seconds before marking accepted.
