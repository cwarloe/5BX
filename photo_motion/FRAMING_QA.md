# Fail-closed photographic framing QA (manual, per-frame)

`photo_motion.framing_qa` is a **read-only-on-input** guard for cropped heads
and shoes in actual photographic MP4s. It deliberately **does not detect a
person, infer landmarks from background motion, or certify an identity**.
Human annotations specify the head and the *physical* left and right shoes.
Every annotation is bound to the original MP4 SHA-256, the exact decoded
frame's RGB24 SHA-256, and—if available—a locally reverified photographic
identity master. A stale/mutated source is rejected.

The principle is **observed defect → `FAIL`; missing or uncertain evidence →
`NOT_EVALUATED`; only exhaustive, human-attested evidence →
`PASS_MANUALLY_ATTESTED`**. Even that last verdict is **framing only**, not
exercise-form, personal-identity, loop, release, or owner approval.

## 1. Create a private annotation template

```bash
python3 -m photo_motion.framing_qa /private/video.mp4 \
  --identity-source /private/verified-photo-master.png \
  --template /private/video-framing-unreviewed.json
```

This decodes **all frames**, records each zero-based index and RGB24 frame
digest, and leaves all three landmarks `UNKNOWN`. It neither makes paid
generation calls nor copies private images into the repository. A missing
identity source is allowed for diagnostic triage (omit `--identity-source`),
but prevents a `PASS_MANUALLY_ATTESTED` result.

Review the actual MP4 one frame at a time, preserving its exact frame order.
For viewing-only extraction, for example, use a **new private directory**:

```bash
mkdir /private/video-review-frames
ffmpeg -nostdin -v error -i /private/video.mp4 -map 0:v:0 -vsync 0 \
  /private/video-review-frames/frame_%06d.png
```

With this `ffmpeg` image-sequence command, PNG `frame_000001.png` corresponds
to zero-based annotation index `0`. The PNG file bytes are *not* the decoded
RGB24 hash in the template; the latter binds the video frame contents.
The output of a different decoder/build may change raw frame RGB, which fails
closed on verification instead of silently reusing annotations.

## 2. Annotate each head and shoe, or mark the uncertainty

For each frame, replace the three `UNKNOWN` entries with a manual observation:

```json
{
  "index": 0,
  "rgb24_sha256": "the digest already generated in your template",
  "landmarks": {
    "head": {"visibility": "VISIBLE", "box": [0.39, 0.05, 0.51, 0.20]},
    "left_shoe": {"visibility": "VISIBLE", "box": [0.25, 0.84, 0.36, 0.96]},
    "right_shoe": {"visibility": "VISIBLE", "box": [0.61, 0.84, 0.73, 0.96]}
  }
}
```

Coordinates are `[left, top, right, bottom]`, divided by actual video width
and height, not by a thumbnail's dimensions. A complete head or shoe includes
all of its visible outer bounds; don't just mark the nose or ankle. For
overlapping legs, **physical left/right** must be established by an independent
reference; screen-left/screen-right and orange/teal diagnostic tags are not
proof of anatomical identity. If uncertain which shoe is which, use `UNKNOWN`.

Use these visibility values:

| Value | Meaning | Consequence |
| --- | --- | --- |
| `VISIBLE` | Entire named part can be confidently bounded with a normalized box | Check horizontal margin, head top, and shoe bottom |
| `PARTIAL` | Named part is cut by the picture boundary | `FAIL` |
| `OUT_OF_FRAME` | Named part is completely outside the picture | `FAIL` |
| `OCCLUDED` | Other anatomy/object obscures whether part is in frame | `NOT_EVALUATED` |
| `UNKNOWN` | No reliable manual observation, including unreviewed frames | `NOT_EVALUATED` |

Non-visible observations must use `"box": null` (a `PARTIAL` box may document
the visible fragment). After human review, set:

```json
"review": {"method": "HUMAN_VISUAL", "reviewer": "internal-reviewer-id"}
```

These fields are human assertions, not machine-verifiable proof of good
judgment. A self-declared review does not establish an actual person is the
photographic master. Template metadata (SHA, frame indices, RGB hashes) should
never be manually modified. Annotate a copy of the template and keep it next
to the existing private experiment QA evidence, not in Git.

## 3. Evaluate without overwriting any evidence

```bash
python3 -m photo_motion.framing_qa /private/video.mp4 \
  --annotations /private/video-framing-annotated.json \
  --report /private/video-framing-report-v1.json
```

- Default edge clearances are 2% of height above the head, 2% below either
  shoe, and 1% of width on both sides of each region. Explicit normalized
  thresholds live in the annotation manifest and are included in the report.
  Thresholds may be tightened; never weaken them to make a failing video pass.
- Any observed `PARTIAL`, `OUT_OF_FRAME`, or clearance breach means `FAIL`, even
  if most frames are not annotated. This is useful for inexpensive early
  rejection of known clipping (as with scissor video #21).
- Passing requires valid observations for all three landmarks in **every
  decoded frame**, the exact source hash and per-frame digest, a verified local
  identity-source hash, and explicit human review attestation. There are no
  interpolation, sample-rate, or background-motion shortcuts to `PASS`.
- Missing frames, occlusion, unknown labels, no local master, or absent review
  attestation produce `NOT_EVALUATED` unless an observed failure already exists.
- Any invalid annotation, duplicated index, altered video/master/manifest, or
  stale decoded frame hash is rejected with an error, not quietly downgraded.

## 4. Production interpretation

This tool cannot know whether a human's `VISIBLE` box is honestly placed. A
person still needs to review the exact imagery. It does not evaluate jump
height, skeletal continuity, camera motion, background reflection seams,
wardrobe consistency, photographic person identity, or looping. Pair it with
`temporal_qa`, `identity_qa`, motion contracts, and owner review as separate
evidence. Keep all private MP4s, frame PNGs and image masters outside Git.
