# Optional photographic appearance-continuity check

This engineering check compares **explicitly located patches in real video frames** against a frozen chart identity image. It is not face recognition, a pose estimator, or a substitute for human image/motion review.

It targets a documented problem in the 2026-11-25 Flow pilots: a blue shirt appeared progressively paler, shorts became gray-blue, hair/face shifted, and subject framing became smaller when each exercise was derived from a previous generated video. The evidence does **not** isolate a single cause; changed lighting, pose, scale, loss of native resolution and regenerated pixels can all contribute. See [`PHOTO_VIDEO_PROMPT_TRANSFER_LOG_2026-11-25.md`](../sprites/docs/PHOTO_VIDEO_PROMPT_TRANSFER_LOG_2026-11-25.md).

## Inputs and execution

1. Select the immutable approved identity reference for the specific **chart**. Changing it requires explicit owner decision; do not use a screenshot generated from a previous exercise as the next chart master.
2. Obtain actual MP4 phase frames with `python3 -m photo_motion inspect ...`. These are output PNGs, not artwork replacements.
3. Mark **specific, small, solid-color garment or hair patches** corresponding to the same physical region in the master and each video frame. A human or an independently validated landmark detector can supply these boxes. The code never automatically guesses where the body is.
4. Save an annotation manifest beside the PNGs with normalized image coordinates. For example:

```json
{
  "schema_version": 1,
  "reference": {
    "image": "chart1-immutable-master.png",
    "subject_box": [0.20, 0.10, 0.80, 0.95],
    "regions": {
      "shirt": [0.42, 0.33, 0.55, 0.45],
      "shorts": [0.43, 0.47, 0.57, 0.57]
    }
  },
  "samples": [
    {
      "image": "frame_01_A.png", "time_seconds": 0.0,
      "subject_box": [0.20, 0.12, 0.78, 0.92],
      "regions": {
        "shirt": [0.44, 0.34, 0.57, 0.45],
        "shorts": [0.45, 0.51, 0.58, 0.60]
      }
    }
  ]
}
```

**The example boxes are illustrative only.** They must be freshly chosen from the actual images; applying these coordinates to an arbitrary video would compare the wrong pixels and manufacture a misleading result. If a face or garment patch cannot be reliably located, omit it from that sample and the tool reports `NOT_EVALUATED` for that region.

Run the standalone tool (Pillow only, already used by video QA):

```bash
python3 -m photo_motion.identity_qa /path/to/annotations.json --out /path/to/new-identity-report.json
```

The program refuses to overwrite existing reports, input manifests or source images. It preserves SHA-256 hashes of the annotation file, reference still and every sampled frame. Store the report with the **existing** video QA evidence and numbered batch notes, not in a new tracking database. Private frames/master images do not belong in the repository.

## What its metrics mean

| Measurement | Useful question | What it cannot prove |
| --- | --- | --- |
| Median RGB distance | How different are the actual sampled garment colors? | Whether the boy is the same person |
| Chromaticity distance | Does the color *balance* change even after factoring out pure brightness scaling? | Consistent color under changes of shadow, white balance, saturation or illumination |
| Median luminance ratio | Might an observed color shift simply be exposure/lighting? | What caused the change |
| Adjacent-pixel detail ratio | Did the selected patch lose fine texture? | Quality differences when camera distance, pose, blur or patch size differ |
| Relative subject-box area | Did the apparent size/framing change? | Whether the camera zoomed or the character stretched |

Do not auto-score facial identity from RGB similarity. Never mark an exercise `APPROVED` from this output. All identity metrics are `COMPARISON_ONLY`; the top-level identity verdict is permanently `NOT_EVALUATED` and the appearance verdict is `HUMAN_REVIEW_REQUIRED`.

### Actual-video smoke test (Video 10, provisional)

The tool was exercised against real extracted frames from the [archived six-second kneeling-push-up video 10](https://drive.google.com/file/d/1uNvFvPe2VyyWuaHq7gyOCoCQH9Jv12Kp/view) (source SHA-256 `9c9e3da1421adb506567dec0d1daaf46c47568a40f7e4e0f7ed4288561cf474f`). The **first video frame** was used as an *internal clip baseline*, **not** a substitute for the Chart 1 identity master. Approximate shirt/shorts boxes were manually placed at 0, 1.5, 3.0 and 5.958 s; the exact provisional annotation recipe is [`diagnostics/video10-identity-patches-provisional.json`](diagnostics/video10-identity-patches-provisional.json). Copy that JSON beside the four phase-frame PNGs to rerun; do not commit the frames.

- Shirt chromaticity distance from first frame at 1.5/3.0/5.958 s: about **0.0133 / 0.0107 / 0.0029**.
- Shorts chromaticity distance: about **0.0045 / 0.0120 / 0.0050**.
- These small patch-color changes are compatible with pose/shading differences, but do **not** verify facial identity, historical form or chart-level wardrobe consistency. No frame-level face test was attempted. A different placement of the approximate ROI can change the numbers.

**Lesson:** repeated within-clip palette similarity is useful evidence for visual-review triage, not proof that the same boy survived cross-exercise generations. The chart master must be independently supplied and sampled under comparable pose, framing and lighting conditions before stronger claims can be considered.

## Repeatability and change control

- Keep the actual submitted prompt/model and source-image hashes in the existing generator run recipe. The region annotations are separate **measurement evidence**, not replacements for original frames.
- Choose the same garment patch area where possible, but allow coordinates to change when the person moves. Do not track a shirt by a fixed screen rectangle or mistake foreground/background occlusion for a color change.
- Compare like-for-like resolution and subject size. Inspect the scale ratio before interpreting detail variation; the metric does not numerically normalize for camera perspective.
- Change only one generation variable per controlled experiment. Re-run against the same master and annotation method, then record **what worked and what failed** in the existing batch QA note.
