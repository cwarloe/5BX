# Photographic drift canary — read-only A/B change control

Use the canary whenever a provider, model, prompt, movement contract, reference
image, prepared-frame transform, or delivery setting may have changed. It is a
**metadata-and-technical-evidence control**, not an image/video generator, not
a 5BX exercise-form judge, and not a new approval ledger.

## What gets compared

The command consumes two **existing, immutable**
[`photo_motion.experiments`](EXPERIMENTS.md) intent JSON receipts for the same
exercise. It verifies each record's cryptographic fingerprint before reporting
on the following sources of *possible* shift/drift:

- Exact movement-contract SHA-256 and submitted-prompt SHA-256.
- Provider and model label, provider settings and estimated credits.
- **Ordered** image roles and actual source SHA-256 digests; different role order
  can change which image becomes the generator's identity authority.
- V6 scissor original-card, prepared-frame, and transform-manifest digests,
  plus important physical marker/provenance declarations.
- Whether each source image was locally rehashed at reservation time. A
  declared remote digest is **not** independently verified input bytes.

Optionally provide the matching original
`python3 -m photo_motion inspect` `inspection.json` for **both** runs. These
are cross-checked against each intent's actual model, submitted prompt, inputs,
and contract. The comparison flags changes to resolution, video/audio format,
frame rate, duration, and existing technical warnings. Changing video bytes
between runs is expected and is not, by itself, evidence of model degradation.
No image quality, contact, gait, or visual identity rating is inferred from
matching codec statistics or a low loop-seam pixel difference.

## Usage

```bash
# No model calls or new credits. Paths are to records that already exist.
python3 -m photo_motion.drift_canary compare \
  /path/to/private-ledger/intents/BASELINE_SHA.json \
  /path/to/private-ledger/intents/NEW_SHA.json --json

# Compare already-produced MP4 inspection evidence too:
python3 -m photo_motion.drift_canary compare \
  /path/to/baseline-intent.json /path/to/new-intent.json \
  --baseline-inspection /path/to/baseline/inspection.json \
  --candidate-inspection /path/to/new/inspection.json --json
```

Outputs are machine-readable JSON. Shell status:

- `0`: Configuration and optionally technical metadata are unchanged. **Not**
  a release, video-quality, or form PASS. If inspections are omitted,
  `video_validation` is explicitly `NOT_PROVIDED`.
- `1`: Any relevant field changed, or an input/inspection has a provenance
  warning. Quarantine for an appropriate *new* canary review before applying
  the altered method to a batch; this may be an intentional upgrade.
- `2`: Invalid, mismatched, or tampered evidence; fail closed and investigate.

Every normal result includes `form_verdict: NOT_ASSESSED` and
`release_verdict: NO_AUTOMATIC_APPROVAL`. This is intentionally stronger than
just saying an output "looks good." Never map `exit_code: 0` to
`READY_FOR_REVIEW` or `DONE`; those remain governed by the existing versioned
QA record and photographic handoff validator.

## Suggested first-article / canary routine

1. Select **one existing, attributable reference run** for the same exercise,
   carefully noting whether its own QA is still experimental. A baseline run
   is **not automatically owner-approved**.
2. Before sending a new paid batch, compare its immutable reserved intent with
   the reference. If the model, prompt or source has changed, treat this as a
   new calibration experiment rather than a routine production rerun.
3. After generating the candidate, inspect the playable MP4 under the existing
   motion contract. Repeat the read-only A/B comparison with both inspection
   reports, then independently assess the actual full-motion/loop/form/identity
   evidence and record any defect in the **same existing QA note**.
4. If the control detects a critical or unexplained change, stop **only the
   affected model/exercise lane** and continue unrelated ready work. Apply the
   existing two-attempt same-defect escalation rule. Keep the original failed
   example as a regression case; don't silently overwrite it.

### What this cannot detect

The same named model, prompt and settings can yield a different video (sampling
nondeterminism or silent provider changes). Therefore, identical metadata
**does not rule out model drift**. Technical similarity cannot prove facial
identity, hip/ankle lineage, a genuine second scissor flight, safe movement,
stable camera, smooth loop, or human acceptance. The real detection of those
failures requires a known-motion canary clip with independent form/identity
review and comparison to the original photographic master.

This module never calls Grok, Google Flow, a paid API, or the user's cloud
accounts. It stores no private videos or new approval state.
