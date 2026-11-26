# V6 photographic scissor diagnostic — deterministic 16:9 input preparation

**Engineering utility only:** [`photo_motion/panel_prep.py`](panel_prep.py). It does not generate photos/videos, spend credits, change the V6 source, approve form, or publish media. No private image bytes belong in Git.

The verified [archived V6 tagged 2×2 diagnostic](https://drive.google.com/file/d/1C9HMa4xwg4CkpDiNo7N8Ue5MqUW_sxWs/view) is a 1536×1024 PNG with SHA-256:

`4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2`

The top-left A panel's clean inset is half-open `(left=4, top=4, right=764, bottom=508)` yielding **760×504** original pixels. This avoids the outer white border and the 2×2 white separators (vertical x=765–770, horizontal y=509–514). The photographed boy's complete head, both hands, both shoes, and all four diagnostic wrist/ankle tags were visually checked in the source panel. The selected upper-left image is **not** a full native-HD standalone photo, and V6 remains an unapproved *diagnostic* marker image.

## Deterministic transform, with no subject crop or stretching

1. Verify that the source is an RGB/RGBA PNG, optionally matching the expected 1536×1024 dimensions and the **exact** source SHA-256.
2. Crop exactly `(4,4,764,508)` as an uninterrupted rectangle. Do **not** crop again to force 16:9 or resize the person independently.
3. Require a cropped height divisible by 9 (otherwise exact 16:9 is impossible with horizontal pixel padding alone). Compute width using integer arithmetic: `504 × 16 / 9 = 896`. The deficit is 136 pixels, so add **68 pixels each side**.
4. For each side, reflect 68 pixels of the corresponding outermost panel area. These side strips show the background in the inspected V6 panel; no subject limb reaches the strip. This reflection is deterministic and preserves all 760×504 original center pixels exactly. It can create repeated landscape details, so inspect before treating it as a polished photographic master.
5. Leave the native result at **896×504** for the exact-pixel source-preserving version. Optionally resample the **whole 16:9 frame** to **1280×720** with Lanczos for a standard video input; this changes pixels but does not crop the subject or distort the aspect ratio.
6. Write a new PNG and a new `.manifest.json` **exclusively**. Never overwrite an existing output, existing manifest, or symlink. The manifest contains the source SHA before/after, crop geometry and central pixel digest, padding/resampling recipe, tool/Pillow versions, output dimensions and SHA-256.

## Invocation — no real image was processed by this development task

With a permitted, verified local copy of the original archived V6 image and a **new filename** in an existing output directory:

```bash
python3 -m photo_motion.panel_prep /path/to/verified-V6-original.png /path/to/review/V6_A_native_16x9.png \
  --expected-size 1536x1024 \
  --expected-sha256 4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2
```

That gives a **896×504** PNG and `V6_A_native_16x9.manifest.json`. For explicit 720p delivery, add `--export-size 1280x720` and use a *different, unused output filename*. The software does not overwrite, replace, or delete previous results.

## Important limits and follow-up gates

- The four colored tags are diagnostic. In panel A the orange **wrist is forward** and orange **ankle is back**, while teal wrist is back and teal ankle is forward. This demonstrates visible track roles, not anatomically proven left/right identities from an original human capture.
- A reflected tree/track border is a geometric preparation method, not authentic new landscape footage. There is no generative fill or claim to restore lost detail. A truly native 1280×720 or larger source should be derived independently from the same immutable chart identity anchor if product-level detail is insufficient.
- The side strips were visually inspected as subject-free **only** for the exact verified V6 original SHA and A crop. For a different source/crop, verify head, hands, shoes, all markers, and both side strips anew; the manifest declares completeness `NOT_EVALUATED` for such inputs.
- A single A pose cannot establish either airborne exchange, full scissor form or a seamless video loop. It is suitable only as **one candidate start-frame input** to an independently verified motion test.
- The manifest records a *deterministic transform* and hashes. It does not claim the result is an accepted new source identity, any AI model will animate it correctly, or a human has approved exercise safety. Store any eventual generated output and exact actual submitted prompt with the canonical photographic QA record, not as a new approval database.

The included tests use synthetic images only and prove center-pixel preservation, correct mirrored side geometry, source byte preservation, correct 720p resampling, invalid-bounds handling, source-hash mismatch rejection, existing-file and output-symlink protection, and repeatable hashes/manifests.
