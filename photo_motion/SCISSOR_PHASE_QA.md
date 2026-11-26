# Scissor-jump actual-video phase QA (human annotations, no automatic form pass)

`scissor_phase_qa.py` verifies a *manually observed* six-second photographic
Chart 1 scissor sequence against its versioned A/B/C/D/E motion contract. It
is useful for separating two run-like hops from **two genuine opposing limb
exchanges**. It never reads cartoon sprites, estimates body pose automatically,
edits a video, calls a generator, or approves instructional form/release.

## Run on the exact private MP4

Create a complete, blank annotation manifest with pinned byte hashes of the
MP4, its **every** decoded RGB24 frame, the current scissor JSON contract and
the original photographic A image actually used for the generation:

```bash
python3 -m photo_motion.scissor_phase_qa /private/exact-source.mp4 \
  --template /private/qa/phase-annotations-001.json \
  --spec photo_motion/specs/chart1-scissor-jump.json \
  --start-photo /private/verified-start-A.png
```

This initial manifest has **all observations `UNKNOWN`**. A human reviewer
must watch the actual continuous MP4 and each decoded frame, then record:

- `review.method = "HUMAN_VISUAL"` and a named `review.reviewer`;
- `forward_screen_direction = "RIGHT"` or `"LEFT"` based on where this fixed
  side-on subject faces (not the anatomical side of a colored marker);
- for each frame: `marker_identity` (`STABLE`, `MIGRATED`, `UNKNOWN`) for
  physical continuity of each original colored wrist/ankle marking;
- `shoe_contact.orange_shoe` and `.teal_shoe` as `PLANTED`, `AIRBORNE`,
  `OCCLUDED`, or `UNKNOWN` based on *both entire shoes* and the ground;
- exact normalized `[x,y]` image coordinates for the centers of the original
  orange/teal ankle and wrist markers, with `visibility = "VISIBLE"`.
  An occluded/unknown/offscreen landmark has a `null` point.

The JSON `time_seconds` field is the nominal `frame_index / fps`, **not** a
substitute for inspecting original presentation timestamps if the provider
emits variable-frame-rate video. Use `temporal_qa` separately for temporal
integrity. Human identity/continuity observations need genuine inspection;
inserting `STABLE` because a screenshot contains similar colors is not valid.

Analyze without editing the original MP4 or annotations:

```bash
python3 -m photo_motion.scissor_phase_qa /private/exact-source.mp4 \
  --annotations /private/qa/phase-annotations-001.json \
  --report /private/qa/phase-report-001.json
```

The CLI refuses to replace existing outputs, source video, annotations and
input sources; use a **new report path** for each QA run. The exact input
hashes are rechecked during inspection. A changed MP4, reference image,
contract, annotation JSON, or decoded frame causes a hard verification error.

## What the checker tests

| Expected evidence | Fixed experimental limit |
| --- | --- |
| A at first frame | Both shoes planted; orange ankle behind teal, orange wrist ahead of teal; minimum x separation 3% frame width |
| First flight B | At least two consecutive frames with **both** shoes airborne, centered within 0.65 s of B = 1.4 s |
| Opposite grounded C | Both shoes planted; physical orange ankle **ahead**, teal behind, orange wrist **behind**, teal ahead, at least one sample within ±0.45 s of C = 2.5 s |
| Second flight D | A **different** two-frame-or-longer all-shoes-airborne interval, centered within 0.65 s of D = 3.8 s |
| E at final actual frame | Return to grounded A limb ordering; all four original markers within 6% normalized Euclidean distance of their first-frame centers |
| Whole-take continuity | Same physically tracked marker attachments attested at every frame; no more than two separated airborne intervals; marker center cannot jump over 0.25 normalized-coordinate units between consecutive frames |

All parameters are explicit constants in the tool and regression tested.
They are diagnostic tolerances for the **specific six-second experimental
recipe**, not new RCAF instructions or safety/biomechanics thresholds. The
contract nominal E at 6.0s is represented by the last decoded actual frame,
not an invented non-existent frame at timestamp 6.0.

Three verdicts:

- **`FAIL`:** an observed contradiction such as no opposite C, a missing
  first or second flight in a completely annotated window, colored marker
  migration, wrong endpoint, third airborne interval, or large marker jump.
- **`NOT_EVALUATED`:** any missing/uncertain frame, incomplete human review,
  unknown shoe/marker visibility, missing forward orientation, or insufficient
  evidence in a required phase window, with no separately established fail.
- **`PASS_MANUALLY_ATTESTED`:** every decoded frame has complete, explicit
  human observations; two distinct flights bracket the opposite grounded
  stance and return to A within declared tolerances.

Even a phase `PASS_MANUALLY_ATTESTED` **does not establish** actual anatomy,
historically correct form, safe range of motion, same-person facial identity,
camera stability, lack of audio, pixel-perfect loop seam, or Charles's
production approval. Complement with framing, contact, identity, temporal,
video-technical, and independent form review.

## Known #21 failure this would capture

In the existing #21 diagnostic, visual inspection found two hop-like events
but **orange ankle remained behind and teal ahead**, including around C.
When independently annotated frame-by-frame, that observed lack of opposite
grounded stance must produce `NO_OPPOSITE_GROUNDED_C_WITHIN_WINDOW` rather than
passing just because two airborne intervals occur. The raw #21 MP4 is not
bundled in Git; this new tool has not claimed to run against it. Synthetic
regressions include precisely that failure pattern.
