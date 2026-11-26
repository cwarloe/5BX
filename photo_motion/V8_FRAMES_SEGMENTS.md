# V8 diagnostic Frames-to-Video endpoints (two 3-second attempts)

**Separate from V7.** The 6-second V7 Ingredients/whole-cycle authority and
two-flight scissor contract are unchanged. This V8 fallback separately asks
Google Flow to generate A→airborne→C and C→airborne→A, each with explicit
start/end photographic frames. Neither single segment is an approved exercise
or a complete five-phase scissor cycle.

The existing direct-source A/C PNGs remain the only authorized inputs. The
dedicated V8 preflight reuses V7's strict full-PNG byte/decode verification;
it does **not** reconstruct the lost V6 composite or certify historical crop
replay. No new media is placed in Git.

## Versioned input contracts

- `segment_specs/chart1-scissor-v8-a-to-c.json`: start A, end C, one genuine
  airborne limb exchange; intended first half of a later loop
- `segment_specs/chart1-scissor-v8-c-to-a.json`: start C, end A, second genuine
  airborne exchange; intended second half

Each is 3 seconds, 24fps target, 16:9, 720p, one output, no invented seed.
Observed Flow settings on 2026-11-26: Frames to Video, Omni 1.2 Flash, 3s,
720p, x1; the then-live quote was **9 credits per segment**. This is
historical observation, not a permanent provider price. Verify again at each
reservation; do not make either paid call if the quote/model/mode changes
without explicit requalification. Two attempts would cost 18 credits **only
if both live quotes remain 9**; reserve each separately under the same
reconciled private Flow ledger.

Prepare one private request per segment, with distinct `attempt_key`, exact
submitted prompt file and real A/C local paths. An A→C example (substitute
the actual private paths and current quote):

```json
{
  "schema_version": 1,
  "attempt_key": "C1-EX5-003-V8-A_TO_C",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "photo_motion/segment_specs/chart1-scissor-v8-a-to-c.json",
  "submitted_prompt_file": "/private/submitted-a-to-c.txt",
  "input_assets": [
    {"role": "start-frame", "locator": "example-archive-A", "local_path": "/private/a.png", "sha256": "7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f"},
    {"role": "end-frame", "locator": "example-archive-C", "local_path": "/private/c.png", "sha256": "c0ede374ee3a65266c19b27fc0f295a44a5a95e9d3aa0c1b41982b64f4a155a0"}
  ],
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {"duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1, "seed": null, "generation_mode": "Frames to Video", "resolution": "720p"},
  "estimated_credits": "9",
  "source_preflight": {"authority": "V8_FRAMES_DIRECT_A_C_SEGMENTS", "a_png": "/private/a.png", "c_png": "/private/c.png", "segment_role": "A_TO_C"}
}
```

For C→A, use its distinct spec/attempt key and swap the two `input_assets`
while retaining the A/C private paths and changing `segment_role` to
`C_TO_A`. The ledger validates both endpoint roles against the pinned bytes
before reservation; a declared SHA without locally rehashed bytes fails.
Use the existing `python3 -m photo_motion.experiments reserve`, `settle`,
`artifact` and `status` commands; do not initialize a duplicate ledger.

After retaining raw outputs and separate charge receipts, run full per-MP4
inspection and independent form/motion QA. Only then try the offline
`segment_join` utility with both original hashes and the declared 72 frames
per segment. Its C midpoint and outer A loop metrics are technical evidence,
not proof of airborne exchange or correct anatomy. Hold all final form,
release and publication for Charles's explicit video-specific decision.

### Independent postflight endpoint measurement

After a segment actually exists, the read-only postflight inspector compares
its first and final **decoded frames** against the exactly pinned start and
end photographs. It verifies source SHA-256 values against the ordered V8
contract, fully decodes the video, measures original-resolution RGB mean
absolute pixel error, records frame count/duration and **decoded audio level**,
and emits a JSON report with no form or release approval:

```bash
python3 -m photo_motion.v8_postflight \
  photo_motion/segment_specs/chart1-scissor-v8-a-to-c.json \
  /private/verified-A.png /private/verified-C.png \
  /private/raw-v8-a-to-c.mp4 --report /private/new-v8-postflight.json
```

For `C_TO_A`, reverse the positional photograph arguments. The report path
must not already exist; originals are left untouched. Endpoint MAE is an
**observation**, deliberately not an arbitrary pass threshold: a photorealistic
clip can match both endpoints perfectly while stepping, crossfading, clipping
its head, changing the subject or otherwise failing the actual 5BX exercise.
Any audio stream is reported as a technical violation even if its decoded
samples happen to be silent. Independent visual inspection and the existing
frame-by-frame physical-marker/contact review remain mandatory.
