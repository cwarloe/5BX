# Experimental foreground-on-static-plate compositor

The [foreground_composite.py](foreground_composite.py) utility tests the
photographic layered-video architecture **without extracting a person or
inventing a clean background**. A byte-pinned RGBA foreground frame sequence
is composited over one byte-pinned, fixed RGB PNG plate. Inputs and outputs
must remain in private storage outside this repository. The repository's
tests generate only synthetic rectangles, gradient plates, and masks.

This is a **diagnostic video-assembly tool**, not an AI generator, a person
segmenter, a background inpainting tool, a historical 5BX form validator, or
an approval mechanism. Even a perfectly clean pixel/codec run remains
production_release: HOLD until separate form, identity, anatomy, motion,
loop, and owner gates are satisfied.

## Input contract

Save a private recipe JSON:

~~~json
{
  "schema_version": 1,
  "plate": {
    "asset": {"path": "/private/empty-plate.png", "sha256": "REPLACE_WITH_64_LOWERCASE_HEX"},
    "origin": "camera_plate_claim",
    "evidence": "Private reference to independent empty-plate camera inspection"
  },
  "frames": [
    {"path": "/private/foreground000.png", "sha256": "REPLACE_WITH_64_LOWERCASE_HEX"},
    {"path": "/private/foreground001.png", "sha256": "REPLACE_WITH_64_LOWERCASE_HEX"}
  ],
  "fps": 24,
  "margin_px": 8,
  "key_spill": {"rgb": [0, 255, 0], "max_distance": 32, "max_pixels": 0}
}
~~~

Each foreground frame must be an exact-mode RGBA PNG, and the static plate an
exact-mode RGB PNG, all with equal even dimensions. Paths are local input
files; references are checked against SHA-256 **before and after** rendering.
The output destination must not exist. The order of frames is playback
order. There is no automatic positional tracking or moving-background layer.

An optional annotation field on each frame can check alpha coverage at
independently chosen limb landmarks, for example:

~~~json
{"path": "/private/foreground002.png",
 "sha256": "REPLACE_WITH_64_LOWERCASE_HEX",
 "required_alpha_points": [
   {"label": "rear_wrist", "x": 615, "y": 315, "min_alpha": 192},
   {"label": "rear_shoe", "x": 520, "y": 615, "min_alpha": 192}
 ]}
~~~

If a required pixel is absent from the matte, the tool flags
REQUIRED_ALPHA_POINT_MISSING. The annotation must come from independent
source inspection. A matched alpha pixel **cannot** establish that a real
hand is attached to the correct wrist, has the right orientation or number
of fingers, or has no duplicate behind it; those demand full-body and
occlusion review.

For a source region independently confirmed to be solid anatomy (for
example a visible thigh), use a required alpha region on that frame:

~~~json
{"label": "solid_thigh", "bbox_xyxy": [620, 380, 660, 400],
 "min_alpha": 224, "max_below_pixels": 0}
~~~

Place this object in that frame's optional required_alpha_regions list.
The xyxy bounding box uses exclusive right/bottom coordinates. A count
above max_below_pixels triggers REQUIRED_ALPHA_REGION_HOLE; the report
retains the defect count without editing source pixels. Choose a region
known to be opaque from the **original** photograph/video. An ordinary gap
between body parts, a legitimate occlusion, or a transparent shadow is not
proof of a defect. This check never auto-fills missing skin or accepts form.

Allowed plate.origin declarations are synthetic_fixture,
camera_plate_claim, and derived_plate_claim. They preserve provenance
categories but **cannot prove** that a scene was empty, that an inpainted
region is authentic, or that private images are safe to publish. The report
always sets plate_origin_independently_verified: false. Inspect actual
camera/source evidence separately and retain it in the existing private
photographic QA record; this JSON must not become a second approval ledger.

To run:

~~~bash
python3 -m photo_motion.foreground_composite /private/recipe.json \
  --out /private/new-composite-run --encode-mp4
~~~

Omit --encode-mp4 to generate only lossless RGB PNG frames and a JSON
report. The optional preview is H.264/yuv420p at CRF 16, one encoding thread,
no audio. Repeated runs with the *same* local FFmpeg build and exact inputs
are expected to produce the same MP4 bytes, tested with synthetic media.
Cross-FFmpeg-version or cross-platform bit identity is **not guaranteed**.
The report pins preview bytes, encoder/version parameters, decoded per-frame
framemd5 stream, codec, geometry, FPS, frame count, and absence of audio.
No unmodified compressed packets can be stream-copied from the foreground
video after compositing changes pixels; this step necessarily **re-encodes**.
Preserve any actual raw generator video separately.

The pixel computation is deliberately specified:

~~~
outRGB = floor((foregroundRGB * alpha +
                plateRGB * (255 - alpha) + 127) / 255)
~~~

All intermediates use 32-bit integer arrays. Alpha-zero output pixels must
remain exactly identical to the pinned static plate on **every** frame. RGB
PNG hashes and decoded-pixel hashes are included for replay comparisons.

## Automated warnings and stop conditions

| Warning | Measured evidence | Interpretation |
| --- | --- | --- |
| EMPTY_FOREGROUND | No pixel has alpha > 0 | Missing subject; hold |
| MASK_NEAR_IMAGE_EDGE | Any nonzero alpha within margin_px of frame boundaries | Potential clipping; anatomy not independently determined |
| HARD_ALPHA_EDGE | Direct 0↔255 neighbor pair without intermediate alpha | Matte may look cut out or aliased |
| REQUIRED_ALPHA_POINT_MISSING | A manually annotated expected wrist/hand/shoe point is absent from the cutout | Cutout loses an anticipated limb region; point presence does not prove anatomy |
| REQUIRED_ALPHA_REGION_HOLE | More source-annotated solid-body ROI pixels fall below a minimum alpha than allowed | Likely missing thigh/hand/etc interior matte; legitimate gaps must not be designated solid ROIs |
| KEY_COLOR_IN_FOREGROUND | Visible-alpha pixels whose RGB lies within configured Euclidean distance of chroma key, above allowed count | Possible background spill; teal clothing or legitimate green can cause false positives |
| KEY_SPILL_UNASSESSED | key_spill: null | No chromakey-specific assurance |

Presence of warnings yields QA_FLAGGED_EXPERIMENTAL_HOLD.
Their absence yields **only** PIXEL_QA_PASS_FORM_HOLD, never human-form or
release acceptance. A solid key color or automatic green suppression can
destroy legitimate shirt/wristband pixels; the thresholds must be inspected
on actual photographic boundaries, including dark hair, light shoes, and
occluded limbs. The tool cannot certify halos from unknown backgrounds,
mask topology, ground shadows, identity, camera motion within the generated
foreground, or historical exercise correctness.

## Repeatable test

~~~bash
python3 -m unittest photo_motion.tests.test_foreground_composite -v
~~~

The fixtures check exact alpha math and static-pixel invariance,
deterministic PNG/JSON/MP4 replay, source mutation rejection, edge/spill/limb-point/opaque-ROI
holds, non-RGBA rejection, no output overwrite, full preview decode,
and no unexpected audio. No private media enters these tests or GitHub.
