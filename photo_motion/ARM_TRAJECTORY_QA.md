# Actual-video arm-height and extension QA (manual landmarks)

`arm_trajectory_qa.py` is a **read-only, frame-by-frame diagnostic** for a
photographic scissor-jump MP4. It reports whether the two visible wrists stay
approximately at shoulder height and, if elbow landmarks are supplied, whether
each observed elbow stays approximately extended. It was added because a
phase-order check alone can miss a running-style arm pump between valid-looking
end poses. It does **not** track a person, identify physical limbs, infer pose,
validate RCAF form, or authorize publication.

## Workflow

Keep the exact original MP4, its human annotations, and the output report in
the existing **private** media/QA archive, not in Git. `ffmpeg` and `ffprobe`
are required. Start by producing an all-`UNKNOWN` template:

```bash
python3 -m photo_motion.arm_trajectory_qa /private/source.mp4 \
  --template /private/qa/arms-manual-001.json
```

The template binds the SHA-256 of the original MP4, frame count and size, and
SHA-256 of **every decoded RGB24 frame**. Observe the continuous actual video
and the individual frames. Record `review.method = "HUMAN_VISUAL"` and the
actual reviewer's name. For each frame, annotate the **orange** and **teal**
tracked arms' shoulder, wrist, and, where visible, elbow with image pixel
coordinates `[x, y]` (`x` grows right, `y` down). Each landmark has an explicit
`visibility`: `VISIBLE`, `OCCLUDED`, `OUT_OF_FRAME`, or `UNKNOWN`. Use
`point: null` unless visibly measured. **Do not guess occluded joints or
manufacture a human-review attestation from generated pose estimates.**

Color tags are only the reviewer's screen-space observations: this tool cannot
verify that a colored marker stays on the same physical arm, distinguish
anatomical left/right, or recognize marker migration. Review those issues
separately using the existing [scissor phase QA](SCISSOR_PHASE_QA.md) and human
form checklist.

Analyze using a new report path, retaining all evidence:

```bash
python3 -m photo_motion.arm_trajectory_qa /private/source.mp4 \
  --annotations /private/qa/arms-manual-001.json \
  --report /private/qa/arms-report-001.json
```

The CLI refuses to overwrite input media, annotations, or an existing output.
It rechecks the source MP4 bytes, every decoded frame hash, and the annotation
file against the final report; stale or malformed inputs fail verification.

## Diagnostic limits and verdicts

| Metric | Evaluated when | Experimental criterion |
| --- | --- | --- |
| Arm height | Shoulder **and** wrist visible for **both** arms in a frame | `abs(wrist_y − shoulder_y)` no more than `25 × decoded_height / 360` pixels |
| Elbow extension | Shoulder, elbow, and wrist all visible for **both** arms in a frame | Geometric shoulder–elbow–wrist angle at least 150° for each arm |
| Evidence coverage | Entire video decoded and frame hashes checked | At least 90% of decoded frames evaluable **for each metric**; at most 10% unavailable/occluded frame evidence |

The limits are **engineering diagnostics**, not historical RCAF angle or
clearance requirements, medical thresholds, or evidence of safe technique.
Even one observed out-of-tolerance arm fails its metric; missing observations
are not marked good.

- `FAIL_OBSERVED_GEOMETRY`: at least one measured wrist height or elbow angle
  outside that metric's threshold; a failure is retained even when other frames
  are occluded or absent.
- `NOT_EVALUATED`: no observed violation, but insufficient visibility, missing
  frames, absent elbows, or lack of named human review. Wrist-only review can
  assess arm height but **cannot pass extension**.
- `PASS_MANUALLY_ATTESTED_GEOMETRY_ONLY`: named human review with sufficient
  two-arm coverage and no observed threshold violation for **both metrics**.
  This is diagnostic geometry only, never exercise-form or release approval.

The JSON report includes the source and annotation hashes, per-metric frame
counts, individual failure coordinates/angles, missing-evidence reasons,
limits, and the explicit `NOT_EVALUATED` state of anatomical provenance,
physical marker identity, form, and release. Varying true presentation times,
camera motion, loop seams, shoe contacts, identity continuity, and historical
movement correctness belong to the existing independent QA procedures. Record
these observations in the existing exercise QA record—do not create a new
dashboard or release gate.
