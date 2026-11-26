# V6 photographic scissor diagnostic — deterministic 16:9 input preparation

**Engineering utility only:** [`photo_motion/panel_prep.py`](panel_prep.py). It does not generate photos/videos, spend credits, change the V6 source, approve form, or publish media. No private image bytes belong in Git.

The verified [archived V6 tagged 2×2 diagnostic](https://drive.google.com/file/d/1C9HMa4xwg4CkpDiNo7N8Ue5MqUW_sxWs/view) is a 1536×1024 PNG with SHA-256:

`4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2`

Read-only pixel and visual inspection identifies two clean, half-open source crops (coordinates are `left, top, right, bottom`):

| Panel | Role in proposed two-pose experiment | Half-open crop | Original crop pixels SHA-256 |
| --- | --- | --- | --- |
| **A** (upper-left, CLI default) | Start contact pose | `(4, 4, 764, 508)` | `4b17fbdcab9a052de570e53c52b298b43976374d8a7514028609cc9c493b37c0` |
| **C** (lower-left, `--panel C`) | Opposite contact pose | `(4, 516, 764, 1020)` | `514e96cff2df23253c05646793ffd8102e0280938365c9170a317b1559cf8c2f` |

Each source crop is **760×504**. The V6 card has a white outer border (left x=0–2, top y=0–2, bottom y=1021–1023), vertical divider x=765–770, and horizontal divider y=509–514. Panel C's photo starts at y=515; the 1-pixel inset at y=516 avoids that edge. The boy's complete head, both hands, both shoes, and the diagnostic wrist/ankle tags were visually checked in **both** panels. Neither crop is a native-HD standalone photo, and V6 remains an unapproved *diagnostic* image.

## Deterministic transform, with no subject crop or stretching

1. Verify that the source is an RGB/RGBA PNG. The CLI defaults to the known 1536×1024 dimensions **and exact V6 source SHA-256** so a different card of identical dimensions cannot silently pass as V6. The Python API permits callers to supply optional exact source predicates.
2. Select `--panel A` (default) or `--panel C` and crop its exact clean inset above as an uninterrupted rectangle. Do **not** crop again to force 16:9 or resize the person independently.
3. Require a cropped height divisible by 9 (otherwise exact 16:9 is impossible with horizontal pixel padding alone). Compute width using integer arithmetic: `504 × 16 / 9 = 896`. The deficit is 136 pixels, so add **68 pixels each side**.
4. For each side, reflect 68 pixels of the corresponding outermost panel area. These side strips show background in both inspected V6 panels; no subject limb reaches either strip. This reflection is deterministic and preserves all 760×504 original center pixels exactly. It can create repeated landscape details, so inspect before treating it as a polished photographic master.
5. Leave the native result at **896×504** for the exact-pixel source-preserving version. Optionally resample the **whole 16:9 frame** to **1280×720** with Lanczos for a standard video input; this changes pixels but does not crop the subject or distort the aspect ratio.
6. Write a new PNG and a new `.manifest.json` **exclusively**. Never overwrite an existing output, existing manifest, or symlink. The manifest contains `source_panel: "A"` or `"C"`, whether its bounds match that panel's inspected crop, source SHA before/after, crop geometry and central pixel digest, padding/resampling recipe, tool/Pillow versions, output dimensions and SHA-256. The original single-A pre-credit manifest `version: "1"` remains unchanged for compatibility; the new panel fields are additive.

## Invocation — no derived real V6 output was created or uploaded in this development task

With a permitted, verified local copy of the original archived V6 image and a **new filename** in an existing output directory:

```bash
python3 -m photo_motion.panel_prep /path/to/verified-V6-original.png /path/to/review/V6_A_native_16x9.png \
  --expected-size 1536x1024 \
  --expected-sha256 4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2
```

That gives an **896×504** A PNG and `V6_A_native_16x9.manifest.json`. To independently prepare the opposite contact panel C from the **same exact original image**, use a **different** output path:

```bash
python3 -m photo_motion.panel_prep /path/to/verified-V6-original.png /path/to/review/V6_C_native_16x9.png \
  --panel C --expected-size 1536x1024 \
  --expected-sha256 4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2
```

For explicit 720p candidate inputs, add `--export-size 1280x720` to each command and use **new, unused output filenames**. Both resulting images are 16:9; each has its own manifest, crop digest, and output SHA-256. The software does not overwrite, replace, or delete previous results.

The CLI pins the verified V6 SHA even if `--expected-sha256` is omitted. When preparing a **different controlled source**, pass its own `--expected-sha256` to keep reproducibility anchored to that image. If a hash truly is unavailable, explicitly pass `--allow-unverified-source`; the manifest then records `expected_source_sha256: null`, `source_hash_matches_expected: false`, and subject clearance `NOT_EVALUATED`. The bypass and a supplied expected SHA are mutually exclusive.

## Important limits and follow-up gates

- The four colored tags are diagnostic. In panel A orange **wrist is forward**, orange **ankle back**, teal wrist back and teal ankle forward. In panel C these contact roles visibly reverse: orange **wrist back**, orange **ankle front**, teal wrist forward and teal ankle back. This demonstrates opposite screen-space roles, **not** anatomically proven left/right identities from an original human capture.
- A reflected tree/track border is a geometric preparation method, not authentic new landscape footage. There is no generative fill or claim to restore lost detail. A truly native 1280×720 or larger source should be derived independently from the same immutable chart identity anchor if product-level detail is insufficient.
- Mirrored padding is continuous in the pixel values at each join but reflects/repeats nearby scenery. It removes a harsh seam in color, **not** the risk of visibly mirrored trees or track patterns. The measured subject-preserving center remains unmodified.
- The side strips were visually inspected as subject-free **only** for the exact verified V6 original SHA and exact A/C crops above. For a different source/crop, verify head, hands, shoes, all markers, and both side strips anew; the manifest declares completeness `NOT_EVALUATED` for such inputs.
- A and C supply two static opposite-contact pose candidates, not evidence of the **airborne exchange** between them, a second exchange back, correct form, or a seamless loop. Flow Video #21's failed single-A test hopped without the required scissor exchange, which motivated testing both poses as separate ingredients. **Do not assume image provision forces compliant video motion.**
- The existing [`V6_PRECREDIT.md`](V6_PRECREDIT.md) verification and paid experiment reservation still accept **one A start-frame** only. This tool does **not** authorize two-ingredient spending or silently weaken those guards. A separate versioned dual-ingredient preflight/ledger rule, and owner-authorized provider settings, must be validated before a paid A+C run.
- The manifest records a *deterministic transform* and hashes. It does not claim the result is an accepted new source identity, any AI model will animate it correctly, or a human has approved exercise safety. Store any eventual generated output and exact actual submitted prompt with the canonical photographic QA record, not as a new approval database.

The included tests use synthetic images only and prove separate A/C crop selection, center-pixel preservation, mirrored side geometry, source byte preservation, correct 720p resampling, invalid-panel/bounds handling, source-hash mismatch rejection, existing-file and output-symlink protection, and repeatable hashes/manifests.
