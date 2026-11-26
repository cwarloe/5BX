# 5BX photo pilot 09: current-identity knee push-up (2026-11-25)

**Status: photo-card candidate, human review pending. NO new matching Flow video rendered.**

[Contact sheet (mobile Drive)](https://drive.google.com/file/d/1ZyOtuUG4r6bbqmDHTp3nArds1ybp-XD2/view) · [Single up-frame](https://drive.google.com/file/d/1qXL6hpRGY2-RTfpqZCZeb-xDP2cxUUde/view) · [QA/prompt file](https://drive.google.com/file/d/1xQLY5a-D8W4uMDCqYmCY6uInINs114Bq/view)

## Source prompt, QA and handoff

Purpose
Replace the previous olive-tank kneeling push-up video subject with the same 12–14-year-old photographic blue-tank/charcoal-shorts boy used in the straight-leg sit-up test. Keep the entire push-up on one jointly generated card to reduce identity drift. This is a PHOTO-CARD candidate, NOT yet a regenerated Flow video.

Inputs
1. 06_START_FRAME__Straight_Leg_Situp_Supine__2026-11-25.png — exact subject/wardrobe/background anchor.
2. Prior 05 four-frame photographic knee-push-up card — 90-degree side-view exercise mechanics anchor.

IMAGE GENERATION PROMPT (verbatim)
Use case: photorealistic-natural. Create an unlabelled 2×2 photographic exercise-movement contact sheet consisting of four synchronized full-body 35mm photographic stills, identical camera tripod, identical realistic middle-school boy 12–14 and identical setting. IMAGE 1 is the strict character identity and wardrobe anchor, a naturally proportioned young teen Caucasian boy with pale untanned skin, softly undeveloped muscle definition, slightly messy SHORT medium-dark brown hair (less volume and no neat sculpted curls), modest small button nose and unchanged ear size; same light sky-blue athletic tank top, loose charcoal-gray mid-thigh shorts, charcoal socks, gray sneakers with gold/yellow trim, black wristband and outdoor red running track with vivid green field and trees. IMAGE 2 establishes the EXACT correct side-profile body mechanics for a true KNEELING PUSH-UP. Give the boy from IMAGE 1 the poses of IMAGE 2 without changing his identity. Main anatomy priority: the torso stays one straight gently tilted shoulder–hip–knee line, natural buttocks, no arched low back; both kneecaps rooted on the same track marks and both lower legs bent backward and shoes pointing up; BOTH palms rooted and elbows bend naturally together in the same vertical plane with only two arms, no extra hands. Four chronological panels reading left to right then next row: (1) elbows fully straight/up, (2) quarter-way down, (3) low push-up, chest near but not contacting track, elbows near 90°, (4) fully back up exactly same as panel 1. Strict right-facing side-on profile approximately 90 degrees to camera to prevent spider-arm duplication. A normal prepubescent boy's soft arms/shoulders, no prominent biceps/triceps/abs, no body hair, and no change in height, bone length, face, hair or outfits between panels. Natural attainable movement, no extreme flexibility, no floating knees, no toe-supported planks, no extra limbs, no change to background, no labels, white lines dividing four panels only. Realistic film grain and outdoor soft daylight. Faithful high-resolution documentary photography, absolutely NOT cartoon or illustration.

QA — Candidate (not human approved)
- PASS: Blue top, charcoal shorts, grey/yellow footwear, lighter skin, dark short/medium messy hair and natural youth proportions stay consistent across the four panels.
- PASS: Four visible chronological positions, rigid camera, single subject, rightward side profile.
- PASS: Both kneecaps remain on the track and both feet are elevated behind him; no straight-leg/toe-supported push-up.
- PASS: Two hands and two arms are apparent; rear arm mostly occluded but no extra limb artifact.
- REVIEW: Lowest frame's hips sit slightly above an ideal perfectly straight shoulder–hip–knee alignment, and face is angled forward. Natural variation is acceptable if it stays non-exaggerated.
- REVIEW: New card still looks somewhat more developed through shoulders than ideal identity; avoid prompting extra muscle in video.
- MISSING: Google Flow video generated FROM THIS new start frame. Existing Flow 07 is older olive-shirt subject, not this version. Asset transfer from connected Drive/local workspace to cloud Flow file picker must be solved before claim of matching new video.

VIDEO PROMPT READY FOR GOOGLE FLOW (single START frame only, do not attach all four frames)
Generate one continuous 6-second 35mm documentary PHOTO VIDEO from the attached SINGLE image, which is the exact starting frame. Keep the SAME real-looking 13-year-old middle-school boy, his pale skin, messy short dark brown hair, natural soft undeveloped arms and shoulders, blue sleeveless athletic tank, charcoal loose running shorts, dark socks, gray/yellow sneakers and black wristband. Keep the same red school track, green field, tree line, lighting, and fully locked 90-degree right-facing side camera. One strict KNEELING PUSH-UP, not a toe push-up: 0–1 sec hold UP with both elbows extended; 1–3 sec bend BOTH elbows together and lower chest and shoulders naturally until near the track while maintaining a straight shoulder–hip–knee line; 3–6 sec smoothly push back UP, finish with posture identical to opening frame. BOTH kneecaps and BOTH palms remain on the SAME exact track marks for the whole shot. Feet remain bent behind him with shoes elevated, not planted on toes. One continuous exercise without reversing horizontal direction, cutting, cloning arms, growing muscles, changing the boy's age, changing outfits, drifting background, jumping, dissolving between static poses, text, voices or music. Smooth anatomically achievable motion, no unnatural 99th percentile flexibility.

Status: 09 photo-card candidate — READY FOR NEXT FLOW TEST / HUMAN REVIEW.


## In-Flow identity transfer: newly verified procedure (video #10 in progress)

1. Open the successful sit-up video 08 in Flow; seek ~2.10 seconds, when the boy's face and outfit are clearly visible.
2. Select **Save frame** in the video player. Flow creates a native image asset in the same project.
3. Edit this saved still using Nano Banana 2.1 to change **only the posture** to a true kneeling push-up UP position. Preserve the blue tank, charcoal shorts, hair, face, normal youth build, shoes, track and camera. A native edited still was successfully generated (Flow stated 0 credits).
4. In the project chat, **Add ingredient → image**, choose the edited native asset, and verify that the attachment thumbnail visibly shows the boy in the kneeling-UP pose.
5. Ask for one Omni 1.2 Flash 6-second UP→DOWN→UP push-up video. Flow quoted 18 credits; a one-time approval was given. **Video #10 render in progress; movement and identity not yet QA-approved.**

**Critical lesson:** Flow's agent cannot turn a Google Drive URL pasted in chat into an actual attached frame, and the cloud browser's file picker could not access our local/Drive asset. Saving a frame from a video *inside Flow* and transforming that native image bypasses the transfer barrier. Keep the newer four-frame external card separately as pose QA, not as the rendered video's source. 
