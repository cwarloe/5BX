# V7 direct A+C photographic source — pre-credit gate

This is a **separately versioned source authority**, not a restoration or
weakening of [V6's original-card replay gate](V6_PRECREDIT.md). The verified
original V6 composite (1536×1024; SHA-256
`4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2`)
was stored in an ephemeral workspace that was lost. The two original prepared
photographic A/C PNGs and their preparation manifests survived in the private
Google Drive photo archive. Attempts to recover the original source card from
Drive, Library and the current workspace failed. **Therefore the historical
V6 crop, mirrored-padding and resampling claims cannot now be independently
replayed or certified.**

V7's narrower, explicit evidence authority is solely the exact **saved A and
C prepared PNG bytes**, rehashed and fully decoded locally before reservation:

| Role | Archived direct authority SHA-256 | Image |
| --- | --- | --- |
| `start-frame` A | `7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f` | RGB PNG, 1280×720 |
| `opposite-pose-reference` C | `c0ede374ee3a65266c19b27fc0f295a44a5a95e9d3aa0c1b41982b64f4a155a0` | RGB PNG, 1280×720 |

The A/C photographic images remain **private and outside Git**. Reference
their verified private file paths only; no cartoon sprite, additional identity
master, third image, substituted image or unverified remote link is permitted
in this particular two-image experiment.

## Verify without spending credits

From the repository root, supply the actual local byte-for-byte recovered
files. The separately versioned V7 **movement** contract retains the original
five-phase A→flight→C→flight→A requirement; it does not assert the generated
video has met it.

```bash
python3 -m photo_motion.preflight_v7 \
  photo_motion/specs/chart1-scissor-jump-v7-prepared-pair.json \
  /private/v6-A-1280.png /private/v6-C-1280.png \
  --start-manifest /private/v6-A-1280.manifest.json \
  --opposite-manifest /private/v6-C-1280.manifest.json
```

Both manifest arguments are optional together. If supplied, their declared
output/image hashes, size, claimed V6 source SHA and cropped-panel coordinates
are checked for consistency against the surviving metadata. They are
**historical claims**, not source-pixel/crop byte-replay proof. The receipt
always states `parent_v6_card_status:
UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED` and
`parent_crop_replay_verified: false`—even when manifests are consistent.

## Paid-run request shape

For an **independently verified current Google Flow price** and an existing
owner-authorized, reconciled budget ledger, use a private request JSON with
these fields (replace private paths, exact submitted prompt and quoted cost):

```json
{
  "schema_version": 1,
  "attempt_key": "C1-EX5-002-V7-Flow-two-image-pose-anchor",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "photo_motion/specs/chart1-scissor-jump-v7-prepared-pair.json",
  "submitted_prompt_file": "/private/exact-flow-submitted-prompt.txt",
  "input_assets": [
    {
      "role": "start-frame",
      "locator": "private://v7/A-start",
      "local_path": "/private/v6-A-1280.png",
      "sha256": "7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f"
    },
    {
      "role": "opposite-pose-reference",
      "locator": "private://v7/C-opposite-grounded",
      "local_path": "/private/v6-C-1280.png",
      "sha256": "c0ede374ee3a65266c19b27fc0f295a44a5a95e9d3aa0c1b41982b64f4a155a0"
    }
  ],
  "provider": "Google Flow",
  "model": "REPLACE_WITH_ACTUAL_DISPLAYED_MODEL",
  "settings": {
    "duration_seconds": 6,
    "aspect_ratio": "16:9",
    "variants": 1,
    "seed": null
  },
  "estimated_credits": "REPLACE_WITH_CURRENT_LIVE_QUOTE",
  "source_preflight": {
    "authority": "V7_DIRECT_PREPARED_PAIR",
    "prepared_png": "/private/v6-A-1280.png",
    "opposite_pose_reference": {
      "prepared_png": "/private/v6-C-1280.png"
    },
    "historical_manifests": {
      "start": "/private/v6-A-1280.manifest.json",
      "opposite": "/private/v6-C-1280.manifest.json"
    }
  }
}
```

The ledger permits exactly those two ordered roles, local independently
rehashable A/C PNGs, a valid V7 contract and six-second 16:9 settings. It
freezes both image hashes, manifest hashes if supplied, the literal prompt,
model/settings, positive quoted estimate and the explicit unrecovered-parent
status in the immutable intent. Unknown image roles or extra inputs fail before
credit reservation. A V7 paid reservation also requires `status` other than
`HOLD` in the motion contract and **exactly one quoted output**:
`settings.variants` must be the integer `1`; only `duration_seconds`,
`aspect_ratio`, `variants` and `seed` are currently recognized. Unknown settings
that may conceal extra outputs or an unquoted provider mode fail closed;
qualify/version a different experiment before changing this controlled recipe.
The previously approved Flow cap does **not** remove the
need to reconcile actual historical charges if an ephemeral ledger is lost.
Do not initialize a fresh empty cap as though earlier charges never occurred.

**The provider UI must still be checked:** A is the intended opening frame,
C is an opposite grounded reference of the *same* boy, and neither a separate
subject nor a second scene. A two-image ingredient interface may not honor
pose timing. The hypothesis is that C anchors the 2.5-second landing, not that
the two stills prove airborne movement. Frame-by-frame video QA must verify
both distinct flight intervals, swapped actual physical limb positions,
complete last-frame recovery, full head/shoe framing and forbidden audio.

This preflight never generates video, spends credits or declares an exercise
ready for production. Experimental runs may proceed under the owner's credit
authorization; **only final exercise-form/production release needs Charles's
approval**.
