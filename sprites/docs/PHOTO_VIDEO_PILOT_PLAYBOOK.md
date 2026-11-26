# 5BX photographic exercise pilot: repeatable image-to-video workflow

**For handoff to Grok/other agents:** [Prompt transfer log, captured exact wording and failures](PHOTO_VIDEO_PROMPT_TRANSFER_LOG_2026-11-25.md). It distinguishes verbatim executed prompts from reconstructed descriptions, documents the newly observed chart-local identity drift, and supplies unverified cross-model templates.

**Working protocol, 2026-11-25.** This is an experimental production checklist, not a claim that a pose, clip, or animated cycle has been approved for public release. The original cyan-shirt/red-shorts Sprite Boy is a legacy prototype. The target for new work is the [photographic middle-school character](PHOTOREALISTIC_AVATAR_DIRECTION_2026-11-25.md).

**Newest identity-consistency test:** [Pilot 09: blue-shirt kneeling push-up](PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md) uses the boy from the sit-up photographic pilot. The four-phase card and start frame are in Drive. This started as a still-card candidate; an identity-matched Video 10 was subsequently generated. Flow confirmed that pasting a Google Drive URL does **not** attach it as an image ingredient; upload an actual file before requesting video generation.

## 1. Lock the character and reference before generating

Use an owner-accepted photograph as the **identity anchor**, plus the relevant 1959 RCAF 5BX film/booklet pose (or a specifically approved replacement) as the **movement anchor**. These may be different reference images. Do not assume an attractive render is an accurate exercise demonstration.

- Approximately 12–14 years old, recognizably middle school—not elementary school or a mature high-school athlete. Fair/pale, untanned Caucasian skin; smooth face, chest, arms, armpits and legs without visible body/facial hair.
- Ordinary proportional youth: modest waist/chest, slightly soft shoulders, arms, thighs and seat; **no sharply defined muscles, V-line, abs, widened shoulders, or artificially narrow waist**. Do not make the child thicker or thinner merely to remove muscle definition.
- Dark, natural, slightly messy hair with moderate volume, not exaggerated fluffy/spiky hair, precision curls, or a skin-close fade. Keep ear size and soft/button-ish nose consistent. Eyes can be naturally open while looking toward the action.
- 35 mm documentary photograph quality, visible realistic fabric/shoe details, and stable skin tone. A *slightly* posterized variant can be compared, but photographic anatomy is the master. Clothing palettes may vary **between** experiments—lighter shirt/darker shorts and brighter combinations are welcome—but must be unchanged within one movement card/clip.
- Lock the exact face, hair, approximate height, limb lengths, shoes, clothing, background, viewpoint and framing across an exercise. Never grow limbs to force 5BX maximal flexibility or make a child look more mature to reach a position.

## 2. Specify a complete exercise, then generate the **whole card together**

Before image generation, write a compact pose specification with these fields:

| Field | Example: Chart 1 kneeling push-up |
| --- | --- |
| Movement and source | `C1 / Exercise 4`; historical 5BX knee push-up plus approved successful still |
| Ordered phases | `A` top: hands and knees planted, straight shoulder–hip–knee line; `B` lowered: **both elbows bend** together, chin near floor; `C` top again, same contact points |
| Support-point constraints | Both palms and knees fixed on floor; both bent lower legs behind; feet never become a standard toe-plank |
| Camera | Approximately true side view for this hard movement, fixed lens and horizon; do not rotate between frames |
| Character/wardrobe | One identity anchor, one outfit, normal soft middle-school anatomy |
| Allowed limitation | Chin may remain slightly above the floor; correct child proportions matter more than a forced textbook touch |

Generate a **single full-resolution three- or four-pose contact card** with clear panel separation and a constant environment. This improves age, face, clothing, limb-length and camera continuity compared with generating each phase independently. For other movements, a 20°–35° oblique camera often makes near/far limbs legible; toe touches may need near frontal, while kneeling push-ups may need strict side profile to keep the hips and far elbow honest. Choose the camera to show mechanics, not by a universal degree rule.

**Reusable still prompt block:**

> One high-resolution 35 mm documentary contact card, three equal panels of the **same** pale-skinned, ordinary 13–14-year-old American middle-school boy, same recognizable face and modest dark messy haircut, same clothes and running shoes, same fixed camera, track, horizon and body proportions. Real youth anatomy with gently soft, unmuscular arms, shoulders, thighs and waist; no defined biceps, abdominal muscles, V-shaped torso, underarm hair or facial hair. Illustrate the exercise phases **A → B → C** as specified below. Every panel includes the entire head, both complete hands, knees and shoes. Exactly two arms and two legs, with traceable shoulders/elbows/hips/knees and anatomically possible joints. Preserve where his palms, knees and feet touch the ground. Do not swap near/far legs or use mirrored duplicate bodies. No stretched limbs, no gymnast flexibility, no ballet-pointed footwear, no change in age, scale or face. [Insert exact phase geometry and original-reference description here.]

Review all panels together and **discard** a geometrically impossible card rather than trying to prompt a perfect endpoint by elongating arms, torso or legs. Keep the earlier "almost there" V-push-up, for example, rather than the mathematically exact but distorted forehead-to-floor version.

## 3. Review the *stills* with hard gates

1. **Age/identity:** Face, nose, ears, hairline, skin, build and stature remain recognizably the same normal middle-school boy in every panel; no sudden younger child or older muscular athlete.
2. **Body mechanics:** Correct contact points and sequence, realistic flexibility, straight shoulder–hip–knee line in a kneeling push-up, same physical leg traced from shorts hem to shoe on alternating steps. Both elbows must bend if the move requires it; an almost straight far elbow is a failure even when the foreground arm looks fine.
3. **Anatomical count:** Exactly two attached arms, two legs, two hands and two feet; fingers need not be perfect on first experimental pass, but a spider-like extra arm, wrong knee, broken elbow or flipped shoe is a reject.
4. **Registration:** No moving floor, drifting palms/knees/feet when planted, camera swing or body-scale jump. Compare starting and ending support points before attempting a loop.
5. **Visual fidelity:** Fair skin, realistic soft body, ordinary hairstyle, consistent clothing, no ballet toes, duplicated silhouettes, halo edges or inconsistent background. Any transparent PNG needs separate edge and identity QA; do not treat cutout availability as approval.

Use the [54-card experiment index](PHOTO_EXPERIMENT_REVIEW_2026-11-25.md) to avoid known dead ends: knee far-elbow failures, near/far high-knee swaps, stretched V-pikes, missing sit-up recovery, and ghosted video transitions. Text-only instructions and colored limb markers did **not** reliably correct 3D leg ownership—seek a grounded pose photograph or a useful still from the 1959 film, and retain diagnostics separately from cleaned art.

**Same-identity Flow workaround (verified 2026-11-25):** If the desired character already appears in a Flow video but a locally generated new start frame cannot be imported, open that video, seek to a face-visible frame, click **Save frame**, use Flow's native image editor to change *only* the pose into a correct opening position, and attach the resulting **image** (not the video) to the new video prompt. This costs 0 Flow credits for the Nano Banana 2.1 image edit according to Flow, before the video model's quoted per-render charge. Exact repro and [the completed 6-second Video 10](https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/edit/34fcb840-0a51-4a21-af61-ffd32de896ad) are documented in [pilot 09](PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md). Video 10 is a strong sampled-frame REVIEW candidate (not human-approved); its [original MP4 is now directly playable in Drive](https://drive.google.com/file/d/1uNvFvPe2VyyWuaHq7gyOCoCQH9Jv12Kp/view). **Never paste a Drive link as a substitute for image attachment.**

## 4. Video pilot: one anchor is often better than three

The **card is for alignment and QA**, not necessarily three video inputs. Select the single best, complete top/start pose from the accepted card as the **one video start frame**. Earlier three-frame video experiments sometimes reversed image order, cross-faded into duplicate figures, or interpolated odd reversals. A single top kneeling push-up frame produced a more promising up/down/up attempt. Use the video's actual documented start/end-frame options; don't claim it supports a three-frame timeline when it does not.

**Reusable 5–6-second video prompt block:**

> One uninterrupted, locked-off-camera 35 mm documentary view of the same normal, pale-skinned 13–14-year-old boy in the supplied start photograph. Keep his exact face, dark modest messy haircut, softly undeveloped proportions, clothes and shoes. He performs **one** [exercise name] cycle: 0–1 s [start], 1–3 s [down/working phase], 3–5/6 s [controlled return to the identical start]. State the actual real contact points that stay planted and which joints move. End in the original start posture so a short loop will not jump. Keep hands, feet and knees attached to the same places as appropriate, fixed environment and horizon. Exactly one opaque body with two arms and two legs throughout, synchronized elbows, realistic middle-school flexibility and no increased muscle definition. No reversing reference images, mirrored pose, ghost, duplicate head/arms, opacity blending, rapid cuts, background warp, sudden growth/age change, camera movement, text, dialogue or music.

Do not overconstrain unsupported effects: evaluate what the video actually did, not whether the prompt contained a prohibition. For sit-ups, ask explicitly for **supine → rise/reach → return supine**, since two existing clips stopped in a forward reach and cannot loop. A valid partial exercise might be useful as an educational still or non-looping segment but is **not** a complete cycle.

## 5. Inspect, label, publish to the mobile review folder

Review the original-resolution video at normal speed and key frames (opening, midpoint, recovery, ending); verify the clip's complete motion, not just visually plausible isolated frames. A static contact sheet alone cannot prove there's no interpolation ghost.

**Status vocabulary:**

- `REVIEW`: strongest unresolved candidate; owner approval and/or full-speed QA pending.
- `CANDIDATE`: usable source still/card or anchor, with outstanding exercise form or identity checks.
- `PARTIAL`: coherent subset of the move, but incomplete recovery or not a smooth loop.
- `REJECT`: materially wrong anatomy, body mechanics, age, multiple-body ghost, limb swap or broken registration; preserve privately for lessons, never label as production-ready.
- `APPROVED`: use **only after explicit Charles approval** of this exact asset, not automatically from an assistant's `PASS` or a successful render.

For every run record: UTC date; exercise/chart; original pose reference; identity anchor; input frame filename and SHA-256; complete still and video prompts; generator/model/settings; frame layout or time beats; output filenames; assistant QA and precise failure; owner decision; next prompt change (only one targeted change per retry). Retain rejected examples with their reason, so a later agent does not repeat the same dead end.

Deliver **individually playable MP4s** (not ZIPs or GitHub file-tree detours) to the owner's [5BX Video Review Drive folder](https://drive.google.com/drive/folders/1W9dWViCZENv2UvoZ_k0EME8h9xRUWNKY). Use an easy-to-scan mobile filename like `05_REVIEW__Knee_Pushup__Up_Down_Up__2026-11-25.mp4`; reserve leading numbers for review order and update the folder's `00_START_HERE__VIDEO_STATUS_AND_REVIEW_ORDER.txt` with a short summary, status and what feedback is needed. Keep the private footage private until owner release approval. GitHub should carry **source code, prompts, process docs and safe metadata**, not become the phone-first video review interface.

## 6. Prototype integration is a separate gate

Once both form **and** motion are accepted, crop/align backgrounds or cut out the photo subject only if required by the product, inspect alpha edges at display size, normalize frame registration, and register the real cycle in the Mixer. Do not replace the cartoon baseline or claim the Cloudflare-hosted site is updated merely because GitHub documentation or a PR was merged. Verify a live deployment independently.


## 7. Proven back-extension rescue: straight-leg descent, then deterministic reverse

**[Full test report](PHOTO_PILOT_RUN_PRONE_BACK_EXTENSION_2026-11-25.md)** — [Card 11](https://drive.google.com/file/d/1oGTAZeOCDSb5QY7iujNaAH2k91dlU5U3/view), [Video 14 reviewed loop](https://drive.google.com/file/d/1aLi_1ByXmYxxjp8DNROAHyRa1HylKprf/view). User approval is pending.

- Generate a reference card with REST, CHEST, STRAIGHT-LEG, COMBINED phases together. Pelvis always grounded; feet must go **UP**, not **backward**.
- Flow video 12, seeded from REST, raised both feet by **bending the knees** despite repeated explicit no-bend prompts; rejected for incorrect exercise mechanics.
- Flow video 13, seeded from a correct straight-knee PEAK still, produced a plausible ~0–3-second **PEAK-to-REST descent** with knees straight, but knee flexion recurred near second 5 when it tried to lift; only the first segment was valid.
- Rather than paying to keep re-prompting the same strong learned motion prior, trim the valid descent and **reverse it deterministically** to form a PEAK → REST → PEAK loop. This reuses the precise same limbs/frame registration, avoiding a second AI-generated upward path. Reverse playback can still reveal subtle time-direction artifacts, so normal-speed user QA remains mandatory.

A tested 720p H.264 six-second derivative (Video 14) was made with:

```bash
ffmpeg -i source.mp4 -filter_complex '[0:v]trim=start=0:duration=3.0,setpts=PTS-STARTPTS,split=2[down][r];[r]reverse,setpts=PTS-STARTPTS[up];[down][up]concat=n=2:v=1:a=0[v]' -map '[v]' -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart output.mp4
```

**Video export/Drive handoff now verified:** In the signed-in Flow video editor, open **Download media → 720p Original size**. Wait for the browser download event and read its **actual completed path** rather than assuming a filename. In this environment the cloud browser's completed MP4 was visible from the local executor at the returned `/opt/codex/downloads/...` path. Copy it to a task-specific `.mp4` path and upload that actual file with the Google Drive connector to the phone-first review folder. The browser and executor may advertise a shared `/workspace/shared` mount in other sessions; always verify the path actually returned. Original Video 07, Video 08 and Video 10 are now all directly available as Drive MP4s: [07](https://drive.google.com/file/d/1X6nDp2pYoizf7GJ8kGfW8wVM6QcHpKi3/view), [08](https://drive.google.com/file/d/1GL4em3WurZ5pEXEOeF-Wp_5fWBcmP3hg/view), [10](https://drive.google.com/file/d/1uNvFvPe2VyyWuaHq7gyOCoCQH9Jv12Kp/view). This supersedes older notes claiming Flow MP4 export to Drive was blocked.
