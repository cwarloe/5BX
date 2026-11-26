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
| Optional first/last seam | Grayscale MAE between the **actual first and last decoded frames** at the analysis grid; warn only with `--expect-loop` | A seamless **physical** transition, limb identity or acceptable exercise cycle |
| Optional declared static-background ROIs | All frame-to-frame changes and first/last drift inside reviewer-chosen person-free regions | Automatic matte detection or the cause of the changes: body intrusion, codec noise, lighting and a moving camera are possible |

## Usage

Install Python 3.11+, ffmpeg and ffprobe, plus `numpy` (`pip install -r photo_motion/requirements-temporal.txt`). The utility is streaming: it does not retain all full-resolution video frames in memory.

```bash
python3 -m photo_motion.temporal_qa /path/to/actual-video.mp4 --report /path/to/qa/temporal.json

# If the *approved* motion plan deliberately includes a static hold from 0 to 1s:
python3 -m photo_motion.temporal_qa /path/to/actual-video.mp4 --hold 0:1 --report /path/to/qa/temporal.json

# Only when the MP4 is expected to close a loop, inspect its outer seam:
python3 -m photo_motion.temporal_qa /path/to/whole-cycle.mp4 --expect-loop --report /path/to/qa/loop-temporal.json

# Sample one or more independently confirmed, person-free background rectangles
# in normalized x0:y0:x1:y1 coordinates (each span must cover >=2 analysis pixels):
python3 -m photo_motion.temporal_qa /path/to/actual-video.mp4 \
  --background-roi 0.02:0.20:0.18:0.45 \
  --background-roi 0.84:0.60:0.98:0.80 \
  --report /path/to/qa/background-temporal.json

python3 -m unittest discover -s photo_motion/tests -p test_temporal_qa.py -v
```

Use actual hold windows from a grounded exercise plan. A declared hold suppresses the *unexpected-stillness* warning for that span only; an entirely static video still prompts review. Do not invent hold windows merely to make warnings disappear.

The JSON report includes the source video SHA-256, decoded frame count, frame rate and codec, aggregate and border pixel-change metrics, a first/last screen-space seam measurement, stillness intervals, possible cuts, timestamp irregularities and human-review caveats. Optional ROIs add median/max change, first/last change, and frame-index/time-stamped large-change events. A static ROI is **declared by the reviewer**; do not choose a person-covered area and then call its expected motion a background defect. Raw MP4 bytes are preserved, the full decoded stream is scanned with fatal decoder-error handling, and `exercise_form_and_release_approval` remains `NOT_EVALUATED` even if no warnings occur.

## Known limitations

- At 160×90 grayscale diagnostic resolution, a hand or foot can move while the whole-frame average changes very little. Conversely, background wind, clothing detail or image grain can create pixel change with a **frozen person**.
- A stillness span is an **inspection pointer**. For a six-second rep, a hold at start/end may be intentional. You must inspect normal-speed playback and joints/support contacts before deciding.
- Sudden cuts are detected conservatively: an intra-body jump might be too small to trigger the whole-frame gate. A positive cut flag can be a false alarm.
- A 24-fps CFR video can have smooth presentation timestamps while animated anatomy is physically incorrect. This test cannot validate left/right limb identity, true airborne exchanges, camera lock, exercise form, or identity. A low outer seam MAE is **not** certification of a natural animation loop: a static video also has an excellent seam score but no exercise.
- Do **not** set `--expect-loop` for a deliberately one-way A→C segment. Its different endpoints are expected, and a discontinuity warning would be misleading. Use it only on a complete cycle or an explicitly repeatable clip.
- ROIs run at 160×90 grayscale resolution. An unchanged person-free ROI can miss matte halos near the body; a changed ROI can reflect camera, background, body intrusion or codec behavior. Inspect full-resolution samples and all relevant contacts. ROI warnings are diagnostic, not `FAIL` form verdicts.
- Source video is never modified. Reports may include absolute local file paths; keep raw media and detailed QA output within the existing private 5BX archive, not a public pull request.

## Engineering lesson / next control

The first archived photographic knee-push-up test is documented at [`diagnostics/video10-temporal-motion-2026-11-26.md`](diagnostics/video10-temporal-motion-2026-11-26.md). It shows a real completed clip can pass duration/codec checks while exhibiting repeated low-motion frames requiring inspection. A future pose-estimator/landmark system should attach **physical joint tracks** to these timing intervals; don't call screen-space change 'motion QA passed'.
