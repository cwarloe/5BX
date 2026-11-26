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
2. At first/last thumbnail comparison the boy appeared to shift relative to the track; that subjective impression needed explicit landmarks. A subsequent **provisional manual near-knee/palm annotation** (below) found the knee returns near its opening coordinate by the *last* frame, but shifts significantly during the middle of the motion. This is a **`CONTACT` defect**, even where the loop endpoints resemble one another.
3. The overall first/last image thumbnail difference is small (screen-space RGB MAE about **4.257/255**), even though planted-contact geometry merits inspection. **Lesson: a low frame-difference score is not a biomechanical or continuity pass.**
4. The archived MP4 has a documented provider/model and prior prompt in `sprites/docs/PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md`, but the inspector was not given a run recipe with a verifiable **exact submitted prompt file and input still hash**. The QA output correctly marked provenance incomplete and form/release approval `NOT_EVALUATED`.
5. Source-authority recheck: the original booklet explicitly requires the **chest to touch the floor** for a completed Chart 1 knee push-up. The 3.0s still shows a bent-arm descent but does *not* independently establish chest contact. The photographic motion contract now requires a gentle chest-floor-touch phase; this archived clip has **not** passed that source requirement.

## Provisional actual-MP4 landmark screen — first measured lesson

A later read-only pass decoded the same SHA-verified 1280×720 source at **0, 1.5, 3.0, 4.5 and 5.958 seconds**. One reviewer visually estimated two visible *physical support contacts* in native pixel coordinates: the near palm and near knee. No automatic pose tracking or far-side occluded landmarks were claimed. The sample positions are approximate (manual inspection, not independent dual-annotation), so this is a **screening measurement**, not certified form evidence.

| Contact | Screen-space position at 0s | Greatest measured deviation | Position at 5.958s | Screening result |
| --- | --- | --- | --- | --- |
| Near palm | (874, 601) | **1.4 px** | (875, 600) | `PASS` for *this annotated point only* |
| Near knee | (495, 579) | **49 px**, about **3.83%** of frame width | (493, 579) | **`WARN`**: exceeds 16px / 1.25% frame-width tolerance |

The original manually estimated samples, preserved here so the check can be reproduced, were:

| MP4 time (s) | Near palm `(x,y)` | Near knee `(x,y)` |
| --- | --- | --- |
| 0.000 | (874,601) | (495,579) |
| 1.500 | (874,601) | (542,579) |
| 3.000 | (875,600) | (544,579) |
| 4.500 | (875,600) | (494,579) |
| 5.958 | (875,600) | (493,579) |

The full source-hash-matched `photo_motion.contact_qa` run returned **`WARN`**, with endpoint coverage confirmed. This does **not** say that all four planted supports passed; only two visible near-side points were annotated, and the intervening 1.5-second gaps remain unverified. The raw MP4, extracted frames, provisional coordinate JSON and overlay PNGs remain in the private working evidence, **not Git**.

**Lesson captured:** a push-up can begin and end with nearly identical foot/knee locations yet violate planted-knee stability *between* endpoints. A screen-space seam score, contact sheet, or pretty completed cycle cannot certify planted supports. Before any production declaration, a second observer should independently identify both knees and palms at more timestamps, distinguish knee skin contact from the shifting body outline, and watch full-speed video for contact slide.

## Next controlled test

Before paying for another Flow knee-pushup take, have a second observer annotate **both** knees and **both** palms (mark occlusion explicitly instead of guessing) against fixed track landmarks at more intermediate frames. Check whether the 49px near-knee swing is a real physical support slide rather than landmark-selection error. If confirmed, change **only** the contact-position constraint or start-frame composition, preserve the current clip/hash, and rerun the same inspection. Separately watch the entire clip at normal speed for ghosts or stutters. Do not solve knee drift by replacing the boy or changing the identity anchor.

No generated screenshots or raw private video are committed to GitHub. The complete existing review record is [PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md](../../sprites/docs/PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md).
