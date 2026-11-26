# Experimental photographic two-segment stitch (A→C + C→A)

Some video tools support timed start/end photographic frames more reliably
than unordered image ingredients. The proposed scissor-jump fallback is two
**separately generated continuous photographic video clips**:

1. A→C: original grounded A start; first real airborne limb exchange; opposite
   C grounded at the very end.
2. C→A: exact same C grounded start; second real airborne limb exchange;
   original A grounded at the very end.

That is a **new provider-conditioning hypothesis**, not a way to rescue the
earlier failed A-only video or guarantee motion. The provider's actual
supported duration, image endpoints and live credit quote must be observed
before generating. A past 3-credits-per-second price is not authority to
spend. This command calls **no video provider** and spends **zero credits**.

## Strict offline preview assembly

Both separately retained MP4 originals must first be verified:

- Exact SHA-256 known and rehashed; first is explicitly *A→C*, second *C→A*.
- One H.264 yuv420p video stream each, **no audio at all**, no data/subtitles,
  matching dimensions and 16:9 aspect, codec details, declared FPS, frame
  counts, time base and stream properties.
- The last decoded A→C frame and first decoded C→A frame must be below a
  specified **screen-space RGB mean absolute difference** threshold. This
  tests only pixel continuity; a still/frozen fake could pass it.
- No joins with fades, dissolves, speed changes or interpolation. A controlled
  ffmpeg concat remux uses stream copy with `-auto_convert 0` to prevent
  ffmpeg silently inserting H.264 packet conversions.
- Verify the joined output has precisely the two original **ordered
  encoded-packet SHA-256 sequences**, the same **entire decoded RGB24 frame
  sequence** and exact combined frame count, no added audio, and correct
  timing within one frame. No fallback to re-encoding.
- An input change, unknown video stream, unacceptable C seam, incompatible
  clips, unexpected output, or existing output directory stops the operation.
  Neither original is overwritten.

Example for two independently verified 3-second, 24fps, 1280×720 clips
(substitute real unique hashes and source paths):

```bash
python3 -m photo_motion.segment_join \
  /private/a-to-c-original.mp4 /private/c-to-a-original.mp4 \
  --first-sha256 FIRST_ORIGINAL_64_HEX_SHA256 \
  --second-sha256 SECOND_ORIGINAL_64_HEX_SHA256 \
  --expected-fps 24 \
  --expected-frames-per-segment 72 \
  --max-c-seam-mae 8 \
  --out /private/new-technical-preview
```

The command writes `two_segment_preview.mp4` and
`two_segment_manifest.json` into a fresh directory only after all verification
passes. The manifest binds both source hashes, roles, stream properties,
decoded frame counts, joined SHA, C-seam metric/threshold, full decoded RGB
sequence hash, exact ffmpeg command and version, and permanent owner-review
HOLD. If the provider added AAC to either raw clip, **do not hide that raw
audio defect**: retain its receipt and, if appropriate, create a separate
bitstream-verified silent review derivative with `silent_derivative.py` before
trying this join.

The manifest additionally records `outer_loop` screen-space RGB mean absolute
difference between the **last C→A frame** and **first A→C frame**. This is a
diagnostic measurement, not a pass/fail threshold: a low value can occur even
when the character freezes, dissolves, or returns with incorrect limb identity.
The original endpoint frames and continuous final motion still need separate
human assessment before any seamless-loop claim.

## Nonautomatable release gates

Technical packet/frame equivalence does **not** demonstrate the historical 5BX
movement. Independently review every frame for both **distinct airborne
exchanges**, the correct physical orange/teal arm-and-leg reversal, planted C
midpoint, return to A, shoe contacts, safe human anatomy and preserved subject
identity. Also assess the **outer A-end→A-start loop seam** independently of
its reported pixel metric. No frame interpolation is added. The raw originals and
compiled preview remain experimental until Charles explicitly accepts the
actual one-cycle instructional video for final release.

Synthetic-only regression tests:

```bash
python3 -m unittest photo_motion.tests.test_segment_join -v
```
