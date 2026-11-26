# Optional photographic-video support-point QA

`photo_motion/contact_qa.py` screens whether **annotated** fixed support points move unexpectedly during an actual video. It is intended for knee push-ups and other exercises where palms, knees or feet genuinely remain planted. Do **not** use this test to insist that feet stay planted during scissor jumps or running. The camera must be fixed for pixel displacement to have meaning.

This is a *development diagnostic* and remains separate from the process manager's status/travelers. It does not track joints from pixels automatically, infer anatomical left/right, or approve form. A human/pose-estimation model must first provide contact positions; missing/occluded/low-confidence points cannot quietly be counted as stable.

## Data contract

Save a JSON file with the **actual video SHA-256** (not a generated still, card or derived re-export). Coordinates are in the **native MP4 pixel space**, not the 640px preview displayed by `photo_motion.video_qa`. `annotation_method` must say `manual` or `model`. Model annotations require a confidence value between 0 and 1 for each point.

```json
{
  "schema_version": 1,
  "source_video_sha256": "replace-with-real-64-character-sha256-of-mp4",
  "frame_size": [1280, 720],
  "annotation_method": "manual",
  "fixed_contacts": ["near_palm", "far_palm", "near_knee", "far_knee"],
  "samples": [
    {
      "time_seconds": 0.0,
      "landmarks": {
        "near_palm": {"x": 920, "y": 590},
        "far_palm": {"x": 905, "y": 588},
        "near_knee": {"x": 520, "y": 591},
        "far_knee": {"x": 510, "y": 589}
      }
    },
    {
      "time_seconds": 2.0,
      "landmarks": {
        "near_palm": {"x": 918, "y": 592},
        "far_palm": {"x": 906, "y": 588},
        "near_knee": {"x": 523, "y": 592},
        "far_knee": {"x": 513, "y": 589}
      }
    },
    {
      "time_seconds": 5.9,
      "landmarks": {
        "near_palm": {"x": 919, "y": 590},
        "far_palm": {"x": 908, "y": 589},
        "near_knee": {"x": 522, "y": 591},
        "far_knee": {"x": 512, "y": 590}
      }
    }
  ]
}
```

The pixel numbers above are **illustrative synthetic values**, **not observations from the 5BX videos**. To annotate the actual kneeling push-up, inspect the raw opening, low and final MP4 frames; trace the same planted points relative to the track paint and ground landmarks. Do not annotate the shoulder or head as a fixed support because it deliberately moves during a push-up.

## Execution

From the repository root:

```bash
python3 -m photo_motion.contact_qa /path/to/actual-video-10-contacts.json \
  --video /path/to/actual-video-10.mp4 \
  --out /path/to/contact-qa-10
```

Outputs are a JSON result (`contact_qa.json`) and separate timestamped annotated PNGs with baseline squares, observed circles and displacement lines. No original media or artwork is modified. Omit `--video` only when doing a dry run; the screen will then be `NOT_EVALUATED` even if coordinate values look stable.

The default threshold is **1.25% of native video width** (16 pixels at 1280px), Euclidean point movement from its first trusted observation. The threshold is a **screening tolerance**, not a clinical or biomechanical safety limit. Override with `--tolerance 0.01` for a stricter experiment, record which value was used, and compare the same source. At least three valid observations per named point are required, **including valid first and final samples**; check additional intermediate frames whenever possible.

- `PASS` means only supplied, source-hash-matched annotations stayed within tolerance. It does **not** certify anatomy, form, actual stationary camera, or all unannotated intermediate frames.
- `WARN` means at least one supported landmark moved beyond the tolerance. Inspect actual video and annotation accuracy before blaming the generator.
- `NOT_EVALUATED` means missing/low-confidence support data, missing matched source MP4/hash, or otherwise insufficient evidence. This is intentionally *not a pass*.

It records which observations were skipped and why. A strong metric is a reproducible **diagnostic**, never a substitute for exercise-form approval from Charles.

The first observed possible contact/loop registration drift is documented without a fabricated pixel measurement in [the existing video 10 engineering diagnostic](diagnostics/video10-kneeling-pushup-2026-11-26.md). The next controlled step is to produce annotated **actual** contact positions, not to assume the example coordinates above represent that video.
