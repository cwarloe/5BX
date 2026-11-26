# Engineering diagnostic — photographic kneeling push-up video 10

Date: 2026-11-26 UTC. **Read-only inspection; no new generation, form approval, media replacement or release.** The existing production/review status remains with the numbered photo batch record.

## Exact input observed

- Existing archived video: [10_REVIEW__KneePushup__CurrentBoy_BlueCharcoal_FullCycle__2026-11-25.mp4](https://drive.google.com/file/d/1uNvFvPe2VyyWuaHq7gyOCoCQH9Jv12Kp/view)
- SHA-256 checked against the existing repository's recorded digest: `9c9e3da1421adb506567dec0d1daaf46c47568a40f7e4e0f7ed4288561cf474f` (match)
- Stream: H.264, 1280×720, 24 fps, 144 frames, 6.0 seconds.
- Checked against: `photo_motion/specs/chart1-kneeling-pushup.json` v1 (new *target* contract; do not claim it was the exact Flow input).
- Sampling times: 0.000 s, 1.500 s, 3.000 s and 5.958 s.
- Synthetic-code test and actual-archived-video inspection both succeeded technically; original MP4 unchanged.

## What the sampled frames actually show

1. An upright-on-knees push-up position at the start, a partial descent at 1.5 s, elbows bent and low body at 3.0 s, and return toward the start at 5.958 s. This **supports** a down/up sequence, but sampled stills alone do not prove every intermediate frame moved correctly.
2. At first/last comparison the boy appears to shift relative to the track, particularly around the grounded knee and torso registration. The hand/contact position also needs a closer landmark comparison. **Potential `CONTACT` / `LOOP` defect**, not a certified numerical joint displacement; do not approve a seamless loop on this check.
3. The overall first/last image thumbnail difference is small (screen-space RGB MAE about **4.257/255**), even though planted-contact geometry merits inspection. **Lesson: a low frame-difference score is not a biomechanical or continuity pass.**
4. The archived MP4 has a documented provider/model and prior prompt in `sprites/docs/PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md`, but the inspector was not given a run recipe with a verifiable **exact submitted prompt file and input still hash**. The QA output correctly marked provenance incomplete and form/release approval `NOT_EVALUATED`.

## Next controlled test

Before paying for another Flow take, mark both knee ground-contact points and both hand ground-contact points on the opening frame and a few middle/end frames. Compare those against fixed track landmarks. If planted supports drift, modify **only** the contact-position constraint or the start-frame composition, preserve the previous clip/hash, and rerun the same inspection. Separately watch the entire clip at normal speed for ghosts or stutters. Do not solve contact drift by replacing the boy or changing the identity anchor.

No generated screenshots or raw private video are committed to GitHub. The complete existing review record is [PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md](../../sprites/docs/PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md).
