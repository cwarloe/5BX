# Chart 1 assembly — playable review artifact, not exercise approval

Use `chart1_assembly.py` only after five **actual MP4 motion candidates** exist.
It refuses missing clips, still-image cards, duplicate/misordered media and
overwriting an existing revision. The inputs remain unchanged. It pads without
stretching the boy, strips audio, writes labels into the picture, and records
exact video/manifest hashes in a sidecar evidence JSON. The result remains
**experimental and not instructional** until separate form, motion, identity,
loop and owner reviews are completed in the existing photographic QA records.

From the repository root, create a manifest outside Git (raw media and links may
be private):

```json
{
  "schema_version": 1,
  "chart": 1,
  "clips": [
    {"exercise": 1, "role": "toe_touch", "file": "toe.mp4"},
    {"exercise": 2, "role": "partial_situp", "file": "situp.mp4"},
    {"exercise": 3, "role": "alternate_leg_raise", "file": "legraise.mp4"},
    {"exercise": 4, "role": "kneeling_pushup", "file": "pushup.mp4"},
    {"exercise": 5, "role": "run_and_scissor", "file": "run_scissor.mp4"}
  ]
}
```

Each `file` is relative to the manifest directory (or an absolute file path).
An optional `source_url` and `qa_status` on each entry are copied into the
evidence sidecar, never interpreted as approval. Use a unique output name per
revision:

```bash
python3 -m photo_motion.chart1_assembly private/chart1.json private/chart1_review_r01.mp4
python3 -m unittest photo_motion.tests.test_chart1_assembly -v
```

The resulting `chart1_review_r01.evidence.json` binds the output and source
hashes. Keep the actual MP4 and private source URLs in the existing controlled
review archive, not in GitHub. A successful render is a **technical assembly
pass only**; it cannot turn rejected/incomplete exercise motion into valid 5BX
form, and it must not enter the release player as approved media.

Archived Flow video 08 is a useful full-sit-up *outtake*, **not** a Chart 1
partial sit-up: it raises the torso much too far and swings the arms forward.
Do not insert it under `partial_situp` merely because the video is playable.
