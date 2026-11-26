# Temporal MP4 QA — screen-space diagnostics, not form approval

`photo_motion.temporal_qa` screens **actual photographic video**, frame by frame. It does not use the cartoon/sprite renderer, generate paid media, alter the original file, publish output, or certify exercise safety.

It complements the existing phase contact-sheet inspector in `video_qa.py`:

| Test | What it measures | What it does **not** establish |
| --- | --- | --- |
| Near-identical frames | Consecutive decoded frames with very small grayscale pixel change | The same anatomical pose or a correct hold |
| Sustained stillness | A continuous run of low screen-space change lasting at least 0.5 seconds | That the video froze: the planned workout may hold a pose |
| Potential abrupt cuts | Exceptional jumps in pixel difference relative to the clip baseline | An actual editor cut rather than rapid movement, occlusion or a flash |
| Frame pacing anomalies | Duplicate/long decoded presentation timestamp intervals | Smoothness, hand/foot tracking or pose continuity |
| Background/border change | Average change in pixels outside the central frame region | Camera motion: foliage, lighting and generative background drift also cause change |

## Usage

Install Python 3.11+, ffmpeg and ffprobe, plus `numpy` (`pip install -r photo_motion/requirements-temporal.txt`). The utility is streaming: it does not retain all full-resolution video frames in memory.

```bash
python3 -m photo_motion.temporal_qa /path/to/actual-video.mp4 --report /path/to/qa/temporal.json

# If the *approved* motion plan deliberately includes a static hold from 0 to 1s:
python3 -m photo_motion.temporal_qa /path/to/actual-video.mp4 --hold 0:1 --report /path/to/qa/temporal.json

python3 -m unittest discover -s photo_motion/tests -p test_temporal_qa.py -v
```

Use actual hold windows from a grounded exercise plan. A declared hold suppresses the *unexpected-stillness* warning for that span only; an entirely static video still prompts review. Do not invent hold windows merely to make warnings disappear.

The JSON report includes the source video SHA-256, decoded frame count, frame rate and codec, aggregate and border pixel-change metrics, stillness intervals, possible cuts, timestamp irregularities and human-review caveats. `exercise_form_and_release_approval` remains `NOT_EVALUATED` even if no warnings occur.

## Known limitations

- At 160×90 grayscale diagnostic resolution, a hand or foot can move while the whole-frame average changes very little. Conversely, background wind, clothing detail or image grain can create pixel change with a **frozen person**.
- A stillness span is an **inspection pointer**. For a six-second rep, a hold at start/end may be intentional. You must inspect normal-speed playback and joints/support contacts before deciding.
- Sudden cuts are detected conservatively: an intra-body jump might be too small to trigger the whole-frame gate. A positive cut flag can be a false alarm.
- A 24-fps CFR video can have smooth presentation timestamps while animated anatomy is physically incorrect. This test cannot validate left/right limb identity, true airborne exchanges, camera lock, exercise form, identity or loop seam.
- Source video is never modified. Reports may include absolute local file paths; keep raw media and detailed QA output within the existing private 5BX archive, not a public pull request.

## Engineering lesson / next control

The first archived photographic knee-push-up test is documented at [`diagnostics/video10-temporal-motion-2026-11-26.md`](diagnostics/video10-temporal-motion-2026-11-26.md). It shows a real completed clip can pass duration/codec checks while exhibiting repeated low-motion frames requiring inspection. A future pose-estimator/landmark system should attach **physical joint tracks** to these timing intervals; don't call screen-space change 'motion QA passed'.
