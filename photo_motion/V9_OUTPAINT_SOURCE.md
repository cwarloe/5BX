# V9 zero-credit photographic outpaint — source and ledger gate

**Status: experimental still-image research, not an approved video source.**
The original direct-source photographic A/C PNGs each have tight head/shoe
margins. A Flow image edit may make a more useful full-body frame, but new
pixels are **model-generated**. Do not call the result a verified V7 prepared
PNG, historical V6 replay, approved identity master, motion segment or final
exercise video. V6, V7 and V8 authorities are unchanged.

This gate allows **one observational outpaint of one directly archived A or C
input** under the specific free image-editor configuration observed in Flow.
It does not itself call Flow, spend credits or approve the result.

## Evidence and exact request

1. Reconcile the **existing** private Flow credit ledger and check the live
   provider quote before each image edit. A zero estimate is allowed for V9
   **only** when the quote actually displays `0 credits`; do not infer free
   usage from a previous run. Do not create a fresh zero-spend ledger.
2. Rehash the actual local original RGB 1280×720 PNG. Role `A` must match
   `7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f`;
   role `C` must match
   `c0ede374ee3a65266c19b27fc0f295a44a5a95e9d3aa0c1b41982b64f4a155a0`.
   Neither a generated outpaint, remote-only SHA, sprite, nor substitute
   photograph is accepted as the V9 input.
3. Use the exact Flow editor recipe: model `Nano Banana 2.1`, image editor,
   aspect `Original`, thinking `High`, and **one requested image output**.
   The `requested_outputs: 1` field is an operator-controlled run constraint;
   it was **not** observed as a provider-visible selector. Similarly, `1K
   Original size` was offered **after generation** as a download option, not
   a known pre-submit size control. Do not invent a seed, resolution, duration,
   alternate model or second-image input. Unknown settings require a new
   qualification. Independently check the **actual** output count.
4. Keep the exact sent prompt, private source path, generator output, observed
   charge and literal settings **outside Git**. Preserve the original source
   and derivative separately. A source provenance PASS proves only the exact
   input bytes; visual identity, anatomy, framing, contact, exercise form and
   downstream video suitability all remain unreviewed.

Offline source check (without provider or credits):

```bash
python3 -m photo_motion.preflight_v9_outpaint \
  photo_motion/image_specs/chart1-scissor-v9-outpaint.json \
  /private/original-A.png --source-pose A
```

Private ledger request shape (replace paths/locators/prompt/attempt key with
actual private evidence; change both role and path from A to C for C):

```json
{
  "schema_version": 1,
  "attempt_key": "C1-EX5-V9-outpaint-A-001",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "photo_motion/image_specs/chart1-scissor-v9-outpaint.json",
  "submitted_prompt_file": "/private/exact-sent-image-edit-prompt.txt",
  "input_assets": [
    {
      "role": "source-photo",
      "locator": "REPLACE_WITH_PRIVATE_ARCHIVE_LOCATOR",
      "local_path": "/private/original-A.png",
      "sha256": "7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f"
    }
  ],
  "provider": "Google Flow",
  "model": "Nano Banana 2.1",
  "settings": {
    "generation_mode": "Image editor",
    "aspect_ratio": "Original",
    "thinking_level": "High",
    "requested_outputs": 1
  },
  "estimated_credits": "0",
  "source_preflight": {
    "authority": "V9_DIRECT_A_OR_C_OUTPAINT_IMAGE_EDIT",
    "source_png": "/private/original-A.png",
    "source_pose": "A"
  }
}
```

Run `python3 -m photo_motion.experiments reserve --store /private/existing-ledger
--request /private/v9-request.json` **before** submitting the matching
observational image edit. The immutable intent retains the actual prompt
bytes, original source digest, source-pixel digest, original-pose role, model,
quote, exact declared settings, and explicit non-approval state.

When the provider result is known, `experiments settle` records the **actual
observed** charge, including verified `0`; do not invent zero for an unknown
charge. `experiments artifact --role raw-generated-still` records the raw
download's exact digest and length. Privately record its native format,
dimensions, identity/framing inspection, number of outputs, editor run ID,
and any defects. A JPEG output is not the original PNG. Retain any rejected
outpaint and its original prompt as a learning artifact; never crop or
overwrite the original input to make its hash appear to match.

**Stop condition for later paid video:** V9's still-image request schema
*cannot* authorize a paid video or silently enter a V7/V8 input slot. A pair
of V9-derived A/C outputs needs independent exact-output hashes, original
source-role lineage, checked registration, visual identity/limb/form/framing
QA and a **new versioned paid-video precredit authority** before any video
reservation using them. The original V6 parent card remains
`UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED` throughout. Only Charles can approve a
final exercise video for production/release.
