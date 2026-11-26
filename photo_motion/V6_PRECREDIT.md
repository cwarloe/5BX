# V6 scissor: source-byte preflight before any Flow credits

This technical check binds the **verified original V6 tagged photographic card**,
its exact panel-A crop, the **actual 16:9 PNG prepared from it**, the preparation
manifest, and the versioned Chart 1 scissor-jump movement specification.
It calls no model, spends no credits, and cannot validate movement from one image.

## 1. Prepare and independently verify the actual uploaded input

First create the PNG with [`panel_prep.py`](panel_prep.py) using the original
card's full SHA-256 as a precondition. Keep the exact prepared bytes and
`.manifest.json` together. For the currently documented V6 source:

```bash
python3 -m photo_motion.panel_prep /private/original-v6-card.png /private/v6-A-1280.png \
  --expected-size 1536x1024 --export-size 1280x720 \
  --expected-sha256 4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2
```

Verify those **actual** three input files against the versioned motion plan:

```bash
python3 -m photo_motion.preflight_v6 \
  photo_motion/specs/chart1-scissor-jump.json \
  /private/original-v6-card.png /private/v6-A-1280.png
```

The verifier checks source SHA and native geometry, original anatomical-marker
claims, all crop/padding/resampling fields, the manifest hash, and an exact
byte-for-byte replay of the prepared PNG. A single-pixel change, a substituted
same-size card, false source-identity claim, edited crop or mismatched spec
fails. Optional `--manifest PATH` selects a non-default manifest;
`--receipt NEW_PATH` writes one **exclusive** JSON record for the existing
private experiment evidence archive, not a new approval database.

Successful output says `VERIFIED_INPUT_BYTES_ONLY`, not `APPROVED`. The prepared
PNG's SHA-256 must **also equal the image already uploaded to Flow**. If Flow
only exposes a thumbnail rather than upload-byte verification, note that
remaining uncertainty in the existing experiment QA record.

## 2. Bind the same files when reserving the one paid attempt

For the current `chart1-scissor-jump` V6 pilot, the existing
`photo_motion.experiments reserve` command now **fails closed** without these
three local files and a single verified `start-frame` asset whose hash matches
the prepared PNG. Add this object to the ordinary private request JSON:

```json
"source_preflight": {
  "original_card": "/private/original-v6-card.png",
  "prepared_png": "/private/v6-A-1280.png",
  "manifest": "/private/v6-A-1280.manifest.json"
}
```

In the same request, use:

- `exercise_id: "chart1-scissor-jump"` and `spec_path` for the same validated
  scissor spec.
- Exactly one `input_assets` entry with `role: "start-frame"`, a stable
  locator, and a `local_path` pointing to the identical prepared PNG. **Do not
  attach the chart identity master as a second image in this controlled V6
  single-frame experiment.** It remains a separate comparison authority.
- `settings.duration_seconds: 6`, `settings.aspect_ratio: "16:9"`, the exact
  provider/model/settings actually used, and a **positive current quoted**
  `estimated_credits` amount. A historical credit rate is not a live quote.

`reserve` reruns the source-byte verifier, records only the verified SHA and
geometry summary in the existing immutable run intent, and blocks mismatched
input roles, images, duration or aspect. A successful **reservation does not
authorize spending**; use only the owner's separately authorized provider cap.
After an actual paid attempt, use the existing charge/artifact receipts and
human video QA. A start frame, even if exact and photographic, cannot establish
two airborne exchanges, correct exercise form, continuity, anatomical
left/right identity, a loop seam, or owner approval.

Changing the original V6 source authority requires a **new versioned source
definition and tests**. Do not silently edit the SHA/crop/physical-marker
claims of this already verified experimental baseline to accommodate a model.
