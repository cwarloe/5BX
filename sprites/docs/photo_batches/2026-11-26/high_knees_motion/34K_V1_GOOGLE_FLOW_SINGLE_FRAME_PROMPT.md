# 34K-V1 — Google Flow high-knee test: single-frame animation

## Input

- **Start frame only:** `34K_V1_START_FarKneeUp_2x.png`, extracted losslessly as to pose/content from lower-left quadrant of human-preferred `34K_HigherFarElbow_Review.png`, then Lanczos 2× resized without adding AI details.
- **Alternate start if needed (new job, one variable):** `34K_V1_ALT_START_NearKneeUp_2x.png`, upper-left quadrant, for an independent comparison.
- [Primary start-frame image (Google Drive)](https://drive.google.com/file/d/1XM0whA2kq1ILwFD0KbZp-uimWmjF7Wpx/view) | [alternate start-frame image](https://drive.google.com/file/d/1PxLP4lA_VE3m4QG8rybB5mMiVRJSbVAy/view) | [full four-panel master](https://drive.google.com/file/d/106bH7oPR8fB6trXiOXppJ95DtG-WcP0Z/view)
- [Named **34K-V1 high-knee scene** in the existing Google Flow 5BX project](https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/scene/d21f6ab8-4f51-484b-a426-9e92f5dfa69f). Scene is an empty prepared workspace, not a completed clip.
- Do **not** upload the entire four-panel contact sheet as the video start image. It is a reference and process record, not a four-character scene.
- Do **not** supply end or middle keyframes on V1. Prior Flow tests glitched when interpolating between poses and behaved better with a single up-pose input.

## Exact video prompt — single start image

> Six-second continuous documentary 35 mm sports photograph brought naturally to life. The supplied opening frame is the exact identity, costume, environment, camera, and first pose: the SAME ordinary 13–14-year-old boy, pale Caucasian skin, natural short slightly messy dark brown hair, softly developed age-appropriate arms and thighs (not muscular), gentle middle-school facial features, bright blue sleeveless athletic tank top, charcoal-gray running shorts, dark socks, gray trainers with yellow details. He is centered in full-body view on the same red running track with green grass and forest in soft focus.
>
> ACTION: He performs moderate-tempo **stationary high-knee running in place**, one continuous forward-in-time sequence. From the pictured knee-up position, lower that foot naturally beneath his hip with a visible weight transfer, then raise the **opposite knee** to approximately waist height; lower it and repeat alternating knees. His arms pump naturally **opposite the corresponding legs**, elbows softly bent, alternating forward and backward throughout. Each hand belongs to the correct left or right arm; don't swap sides. The far/background arm may disappear behind the torso as perspective requires. Its upper arm must remain shorter in apparent length, and if its elbow is visible it sits **higher than the foreground elbow**, without the far forearm or fist protruding unnaturally around the body. Shoes remain athletic and neutral, never ballerina-pointed.
>
> CAMERA: One locked-off, eye-to-waist-height camera, same slightly oblique side view and full-body framing as the still, tripod-stable, no pan, no zoom, no tilt, no rotation or perspective shift. Natural outdoor daylight; grass, tree line, and red lanes remain fixed. Clothing and face match the opening image throughout, with ordinary subtle fabric motion; no sudden muscle definition, apparent age change, enlarged shoulders, extra limbs, or stretched arms.
>
> TIME: Consistent forward chronology at human pace. Never run any frames or body movement backward, never reverse the video or ping-pong the animation to return to the starting pose. End while naturally progressing through another running step, without cut, crossfade, frozen hold, rewind, teleportation, or body morph. Ambient outdoor sound only; no music, speech, on-screen text, or logos.

## Video acceptance traveler

| Gate | Observable pass | Failure to reject |
| --- | --- | --- |
| 01 Identity | Same middle-school face, hair, age, normal soft body from opening to closing frame | Older/more muscular face/body, outfit or shade drift |
| 02 Leg alternation | Raised knee clearly switches from **near leg** to **far leg** on successive steps | Same leg lifts repeatedly; two feet float; mirrored-leg cheat |
| 03 Coupled arms | Foreground wristband-side arm swings backward then forward as the opposite knee lifts | Frozen arm (34C error), two right arms (34E–G error), detached hand |
| 04 Occlusion | Far elbow high and plausible; far forearm/hand may remain hidden behind ribs/torso | Shoulder-to-elbow longer than front, low fist behind hip, extra appendage |
| 05 Camera continuity | Feet/track lines stay fixed in frame, entire person visible | Sliding across scene, dynamic pan, clipping a foot |
| 06 Temporal continuity | Alternating steps progress forward and contacts look human | Midclip reverse/ping-pong, sudden jump cut, pose morph |
| 07 Usable loop | Last step can transition to first after a natural stride phase, if possible | Hard reset or time reversal (looping is secondary to clean mechanics) |

## Status / experiment rationale

- This is a **ready-to-run prompt**. No Flow render is claimed here.
- Generation status: the connected browser extension failed, but the authenticated Google Flow project was accessible in the cloud browser. A new named 34K-V1 scene was created. **No image was uploaded to Flow and no video render was started yet**; the prompt and start frame are both ready in Drive. Magnific was also checked as an alternative, but its connected plan is Free and video generation is paid-only.
- Crop originals retained for P1–P4; full four-panel 34K remains the appearance master.
- Start with ONE image because a previous Flow run using multiple positional images produced temporal reversal/glitches, whereas a single up frame worked. The best next test changes only the *far elbow* in the master, keeping model/camera, age, body and wardrobe stable.
- If V1 fails on a frozen arm, make **V2 only change the action paragraph**: explicitly demand visible opposite-direction alternating arm swing every footfall, leaving all identity and camera text unchanged.
