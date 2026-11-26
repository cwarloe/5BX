# Chart 1 low stationary run — original Flow video #20 diagnostic

**Date:** 2026-11-26 UTC. **Decision: HOLD / HUMAN REVIEW, not form-approved and not a loop-ready deliverable.** No new generation, credits, media upload, media replacement, publication, or release-status change was performed for this analysis.

## Immutable media and generation provenance

| Field | Observed/reported value | Verification boundary |
| --- | --- | --- |
| Flow title | `20_REVIEW__C1_LowRun_4in__BlueCharcoal__2026-11-26` | [Original in-Flow pilot record](../../sprites/docs/photo_batches/2026-11-26/low_run_video/QA_EXACT_PROMPT.md) (path from repository root: `sprites/docs/photo_batches/2026-11-26/low_run_video/QA_EXACT_PROMPT.md`) |
| Native Flow editor | `https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/edit/cfc5982b-03f5-4bc6-a103-afdf05a7558c` | Authenticated provider asset; not a public export URL |
| Video model | Omni 1.2 Flash, one six-second video, 18 credits | Recorded at generation time in the pilot note; not verified from an embedded MP4 model tag |
| Standing still | Native Flow edit of an archived #08 image, edited with Nano Banana 2.1 | **Not** the immutable v2 master image; source still bytes/hash unavailable |
| Retrieved original video | 3,520,954 bytes; `video/mp4`; H.264 1280×720, 24 fps, 144 frames, six seconds | Independently probed from original unmodified download |
| Original SHA-256 | `687f07a766725e23f550d1cae1c6e27cddd06022c38bc581b30eee189e4e4b84` | Independently recalculated, private original retained outside Git |
| Prompt capture | `sprites/docs/photo_batches/2026-11-26/low_run_video/QA_EXACT_PROMPT.md`, heading **Exact submitted video prompt** | SHA-256 of the recorded fenced prompt text, excluding trailing newline: `06ae11eb2e022f35994453f2987f480ea7aeeca94ebf42565130a20db160a72a`; does not verify provider-side submission bytes |
| Generator seed/settings | Unknown beyond recorded model, input still, duration and price | Do not invent values or claim deterministic AI regeneration |

The raw MP4, decoded frame grids, and audio samples are **private review media outside the repository**. This note is a pointer to an immutable content hash, not a redistribution of the video.

**Archive gap:** At this review, the recovered source was readable in local private scratch but **no verified durable Drive copy existed**. A proposed upload to the existing private review folder was blocked by an explicit external-disclosure policy decision. It was **not** retried or bypassed. Long-term preservation requires explicit owner authorization and verified destination metadata; the SHA-256 alone cannot recover missing media bytes.

## Two distinct test protocols: do not silently conflate them

| | 17-phase pedagogical movement contract | Actual six-second Flow #20 pilot protocol |
| --- | --- | --- |
| Authority | `photo_motion/specs/chart1-stationary-low-run.json` | Verbatim recorded submitted prompt linked above |
| Version/intent | `c1-ex5-stationary-low-run-photo-v1`, illustrative alternate contact state sequence | Historical one-shot exploratory video, **neutral start → gentle run → neutral settle** |
| At time 0 | R00 calls for one orange-tracked foot planted, teal foot lifted ~10 cm | 0–0.5 s both feet on track, relaxed neutral standing, elbows bent |
| During run | Seventeen contact states spaced 0.375 s; rule requests continuous steps for six seconds | 0.5–5.5 s five to seven alternating low (~10 cm) foot lifts, no forward advance |
| At time 6 | R16 visually matches R00 with one low raised foot; supports a phase loop | 5.5–6 s return to the **same neutral pose as first frame**, intended neutral loop |
| Anatomical left/right | Orange/teal are camera-near/far tracks, not proof of anatomical left/right | Prompt says literal left/right, but source orientation and overlap make independent side identification uncertain |
| Exercise cadence | **Not** level-dependent 5BX repetitions; no authoritative count derived from 17 frames | Five–seven is an experimental generation request, **not** an update to `data/5bx-charts.json` |

The current `photo_motion inspect` contact sheet is useful for codec, duration, frame sampling, frame deltas, and photo evidence. **Its R00–R16 `target_pose` labels are not valid acceptance labels for the neutral-start Flow #20 pilot.** Do not weaken or rewrite the canonical 17-phase contract to fit this video. A future neutral-start pilot should be a separately versioned contract or explicit protocol variant, with its own start/end sample targets and immutable submitted-prompt receipt.

## Read-only decoded video findings

1. **Real temporal video:** 144 individually decodable video frames at 24 fps, six-second duration. The two-dimensional frame grids show continuous in-place stepping, reciprocal small arm movements, a visually fixed camera, and consistent clothing/track background. No obvious extra limbs or severe jump cuts at the reviewed scales. This is not a sprite carousel or still dissolve.
2. **Start and main motion:** Opening posture has bent elbows, slight staggered feet. The first roughly half-second is mostly standing; low step motion becomes visible thereafter. Small, apparently alternating foot lifts continue through the middle, then the subject relaxes toward a neutral stance around the final second. Physical left/right identity and a precisely counted **five–seven** alternating footfalls are **not proven** from overlapping side-profile shoes.
3. **Low lift is plausible, not calibrated:** Cropped frames show feet traveling relatively small distances above track; no waist-high knee drive. A measured **10 cm** shoe-ground clearance cannot be asserted from a single uncalibrated oblique camera and shoe perspective. Joint continuity and occasional very close shoe overlap still require a full-resolution human review.
4. **Loop seam fails visible pose equivalence:** At t=0 the elbows are bent, forearms raised near waist and the shoes staggered; at t=5.958 s the arms hang down and the feet rest more evenly. Compared on the inspector's 640×360 samples, first-to-last mean absolute RGB difference is **5.20/255** overall, **13.03/255** in approximate subject ROI x=230–409/y=15–354, versus **2.24/255** in static background ROI x=0–184/y=15–354. These pixel metrics are evidence of a visible endpoint difference, **not** a joint-level loop proof.
5. **Audio prompt violation:** The recorded submitted video prompt requested **no audio**. Original MP4 contains one AAC audio stream: decoded RMS-style mean level **−51.2 dBFS**, peak **−23.7 dBFS**, with nonzero PCM samples. Volume alone cannot prove perceptual audibility; the **presence of a stream** already violates the explicitly forbidden policy. `photo_motion inspect` now flags this automatically when the relevant spec contains `"audio_policy": "forbid"` (PR #53).
6. **No machine-discovered frame discontinuity:** Streaming `photo_motion.temporal_qa` found **13 near-identical frame-to-frame transitions out of 143**, no sustained freezes, no abrupt-cut candidates, and no PTS/frame pacing anomalies. Intentional holds 0–0.5 and 5.5–6.0 s were declared. These screen-space checks do not verify physical form, anatomical side, or exercise timing.

**Inspection limitation:** All 144 frames were reviewed in three indexed 48-frame contact grids, plus 17 larger phase samples and targeted shoe crops. This catches obvious sequence and pose issues, but can miss small one-frame anatomical distortions. No independent full-speed owner signoff, v2 identity comparison, calibrated sole-to-ground measurement, or peer-certified exact count has occurred.

## Repeatable no-credit measurement protocol

Use a locally recovered, **private** MP4 whose hash matches the original above. The commands read the original and place new evidence in a separate private directory; they do not invoke Flow, generate media, upload files, or approve form. Replace `/private/video20-original.mp4` and `/private/video20-qa-*` with real non-repository paths. Do not commit any generated media or reports containing private paths.

```bash
sha256sum /private/video20-original.mp4
ffprobe -v error -show_format -show_streams -of json /private/video20-original.mp4
python3 -m photo_motion inspect photo_motion/specs/chart1-stationary-low-run.json /private/video20-original.mp4 --out /private/video20-qa-phase
python3 -m photo_motion.temporal_qa /private/video20-original.mp4 --hold 0:0.5 --hold 5.5:6 --report /private/video20-qa-temporal.json
ffmpeg -nostdin -hide_banner -i /private/video20-original.mp4 -map 0:a:0 -af volumedetect -f null -
ffmpeg -nostdin -hide_banner -loglevel error -i /private/video20-original.mp4 -map 0:v:0 -vf 'scale=160:90,tile=8x6:padding=2:margin=2' -fps_mode vfr -frames:v 3 /private/video20-qa-grid_%02d.png
```

Inspect three grids (48 source frames each), then verify specific foot contacts and both terminal poses at full resolution. Record physical near/far shoe tracking and counted ground contacts separately; don't use pixel differences as substitutes for anatomical observation. Recompute hash after inspection. For future experimental comparisons change **one** generation input or prompt constraint at a time, retain the failed source hash and actual paid run receipt, and get owner authorization before another paid attempt.

## Current decision and next controlled experiment

- **Preserve:** Genuine continuous low-stationary movement and fixed camera are promising technical results; do not discard the original or erase this experiment's lessons.
- **Hold:** Not loopable as supplied; output includes forbidden audio; input anchor lacks independently hashed v2 identity; exact prescribed-side steps and ~10 cm clearance remain uncertain. `form_and_release_approval` stays `NOT_EVALUATED`.
- **Next versioned hypothesis:** With **the same exact identity anchor, camera, model, duration and approved budget**, explicitly constrain both neutral endpoints to the same **elbows-bent, staggered-shoe** pose and no audio track; then compare the new original to this SHA-pinned take. Do not treat text-only `no audio` as a reliable encoder setting; apply a deterministic stream-free delivery transformation only to a clearly derived asset if approved. An approved v2 source anchor would be a **separate** variable/experiment, not combined with loop-correction in the same causal test.

