# V15 — neutral procedural motion + photographic A* Ingredients feasibility

**Status: EXPERIMENTAL precredit gate only; no uploaded motion guide, no paid V15
generation, no human-form or release authority.** V12 and V14 both inserted
grounded running/lunge steps; V13's arm-only edit did not correct V12. The V14
stop rule forbids same-source prompt/endpoint-only retakes. This different
zero-credit **synthetic motion-guided method** asks one limited question:

> Can Google Flow's actual Video **Ingredients** mode use a new, independently
> re-rendered motion video to induce *two* real scissor flights in the existing
> photographic boy, while preserving the boy's identity and static track?

It is **not** the repo's preferred consenting adult motion-reference capture,
not evidence that a gray mannequin depicts sound 5BX technique, not an approved
human motion source, and not a substitute for the original historical exercise
authority. A failed result stops this synthetic-guide method. Preserve it as a
diagnostic instead of paraphrasing the same prompt or paying for repetitions.

## Exact inputs and method identity

| Item | Pinned exact SHA-256 / constraints |
| --- | --- |
| A* photographic boy ingredient | `777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38`, 1344×756 RGB PNG; strict replay from V10 original A/C/canvas/annotations/QA ten-file chain |
| Synthetic motion-only ingredient | `1a8fb1c47ef5de21cfe0b519815f81b8cd97771ff12b8ceda02124cf86c06b5d`, three seconds, 640×360, H.264 High yuv420p, 24fps, 72 frames, one video stream and **no audio** |
| Independent replay of motion video | Second separately rendered and encoded MP4 must have the **same exact SHA** and a different file path |
| Physical joint/contact sidecar | `7fc18c45223aaca4b9e72c502aae2d78d410e78a8dd1a71dfef1f4bbac229cab`, identical from each independent render; both-shoes-airborne frames 12–21 and 40–48, endpoints grounded |
| Blender generator source | `c9d30d5af5553150f599eca4f1e33111b04b1068c7ecde5ad8644d5f3706a090`; original self-authored geometry, **no old sprite artwork, images, stock footage or copied likeness** |
| Actual preregistered private prompt | `e481d4d1015cb01799869b003b9df23995e1bacef1756b089a441782cc017208` (the UTF-8 file has a final LF); exact text stays private |
| Actual provider profile | Google Flow, **Omni 1.2 Flash**, Video mode → **Ingredients**, 16:9, 360p, 3 Sec, x1, unknown seed (`null`), Return silent videos ON |
| Current quote requirement | Fresh **post-asset** visible actual positive price **at most 3 Flow credits**; pre-asset three-credit display is informational, not sufficient |
| Credit authority | The same immutable existing privately reconciled Google Flow ledger; V12 and V14 native three-credit receipts and all prior actual charges remain intact, with fresh balance attestation |

The source-side geometry/contact JSON reports two airborne windows. These are
hash-bound generator assertions, **not independently tracked shoe silhouettes
in the decoded video**. The procedural guide has a known *interpretation risk*: its straight horizontal
arms swing through the 3D depth axis, becoming very short in the strict side
projection mid-exchange. The physical upper arms do not shrink, but Flow may
copy the apparent nubs or blend subject identities. Do not call the source
human movement. An initial prototype with **real telescoping arms** was
preserved privately and is explicitly **not** this authorized input. The
ordinary CRF18 H.264 test also had a non-exact decoded outer seam; this
version pins the separately keyframed H.264 variant whose 72-frame full decode
has an exact first/last RGB picture. These checks test *input quality*, not
whether the generated human video will follow its timing.

## First verify all private local source bytes without spending

All actual source paths, both MP4s, mechanical QA, prompt, screenshot, the
private request and ledger stay **outside Git**. The V15 gate replays V10's
original photographic A/C derivative through the unchanged V14 source verifier;
validates both distinct exact motion-guide encodes and both contact sidecars;
rechecks the Blender code digest, source-side QA, 72 decoded RGB frames,
format, zero audio and exact loop seam; and rechecks all file hashes after
verification. It then inspects the *same actual* native-charge ledger.

Create a private request matching the following shape (replace every example
path and source locator; never commit this request):

```json
{
  "schema_version": 1,
  "attempt_key": "chart1-scissor-v15-procedural-video-ingredients-001",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "<REPO>/photo_motion/segment_specs/chart1-scissor-v15-neutral-motion-ingredients.json",
  "submitted_prompt_file": "<PRIVATE_PINNED_EXACT_V15_PROMPT_FILE>",
  "input_assets": [
    {"role": "identity-image", "locator": "<PRIVATE_ACTUAL_ASTAR_FLOW_ASSET>",
     "local_path": "<PRIVATE_EXACT_ASTAR_PNG>",
     "sha256": "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38"},
    {"role": "motion-reference-video", "locator": "<PRIVATE_ACTUAL_GUIDE_FLOW_ASSET>",
     "local_path": "<PRIVATE_EXACT_KEYFRAMED_MOTION_MP4>",
     "sha256": "1a8fb1c47ef5de21cfe0b519815f81b8cd97771ff12b8ceda02124cf86c06b5d"}
  ],
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {"duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
               "seed": null, "generation_mode": "Ingredients",
               "resolution": "360p", "return_silent_videos": true},
  "estimated_credits": "<ACTUAL_FRESH_POST_ASSET_PRICE_NOT_ASSUMED>",
  "source_preflight": {
    "authority": "V15_SYNTHETIC_MOTION_GUIDE_INGREDIENTS_360P_EXPERIMENTAL",
    "source_paths": {
      "v10_source_paths": {
        "original_a_png": "<PRIVATE>", "original_c_png": "<PRIVATE>",
        "canvas_jpeg": "<PRIVATE>", "a_annotation": "<PRIVATE>",
        "c_annotation": "<PRIVATE>", "canvas_annotation": "<PRIVATE>",
        "shared_manifest": "<PRIVATE>", "derived_a_png": "<PRIVATE>",
        "derived_c_png": "<PRIVATE>", "independent_qa_report": "<PRIVATE>"
      },
      "motion_guide_mp4": "<PRIVATE_RUN_02_PREFERRED_MP4>",
      "motion_guide_replay_mp4": "<PRIVATE_RUN_03_IDENTICAL_PREFERRED_MP4>",
      "motion_sidecar": "<PRIVATE_RUN_02_JOINTS_CONTACTS_JSON>",
      "motion_replay_sidecar": "<PRIVATE_RUN_03_JOINTS_CONTACTS_JSON>",
      "motion_qa_report": "<PRIVATE_RUN_02_MECHANICAL_QA_JSON>",
      "motion_generator_script": "<PRIVATE_EXACT_BLENDER_SOURCE_PY>"
    },
    "existing_ledger_store": "<SAME_EXISTING_PRIVATE_NATIVE_CHARGE_LEDGER>",
    "flow_ui_observation": "<PRIVATE_FRESH_UI_JSON>"
  }
}
```

### Fresh, post-selection Flow UI observation (private only)

Upload/select only the preferred **new video guide** and already authenticated
A* photographic image as two **Ingredients** in the existing private project.
Keep both on screen with their correct source role, distinct actual native Flow
asset IDs and full image/video thumbnail confirmation. Flow thumbnails and IDs
are **visual attestation**, not provider-side byte rehash. Verify model, mode,
3 Sec, 360p, 16:9, x1, project silent setting and **live price after both
ingredients are selected and exact prompt entered**. Take a private screenshot
and a time-stamped JSON observation **within 15 minutes** of reserve:

```json
{
  "schema_version": 1,
  "authority": "V15_FLOW_TWO_INGREDIENTS_LIVE_QUOTE",
  "observed_at_utc": "<ACTUAL_FRESH_UTC>",
  "operator": "<ACTUAL_PERSON_OR_AGENT>",
  "provider": "Google Flow", "model": "Omni 1.2 Flash",
  "settings": {"duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
               "seed": null, "generation_mode": "Ingredients",
               "resolution": "360p", "return_silent_videos": true},
  "quoted_credits": "<ACTUAL_POST_ASSET_PRICE_AT_MOST_3>",
  "identity_tile": {"asset_kind": "image",
    "source_sha256": "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38",
    "flow_asset_id": "<REAL_PRIVATE_FLOW_IMAGE_ASSET_ID>", "visually_confirmed": true},
  "motion_video_tile": {"asset_kind": "video",
    "source_sha256": "1a8fb1c47ef5de21cfe0b519815f81b8cd97771ff12b8ceda02124cf86c06b5d",
    "flow_asset_id": "<REAL_PRIVATE_FLOW_VIDEO_ASSET_ID>", "visually_confirmed": true},
  "only_two_ingredients_selected": true,
  "no_frames_endpoints": true, "post_asset_quote_confirmed": true,
  "project_silent_setting_on": true, "ledger_reconciled": true,
  "ledger_actual_credits": "<EXACT_LIVE_LEDGER>",
  "ledger_pending_reserved_credits": "<EXACT_LIVE_LEDGER>",
  "ledger_available_credits": "<EXACT_LIVE_LEDGER>",
  "ui_evidence_path": "<PRIVATE_FRESH_SCREENSHOT_FILE>",
  "ui_evidence_sha256": "<ACTUAL_SCREENSHOT_SHA256>"
}
```

```bash
python3 -m photo_motion.experiments status --store '<SAME_PRIVATE_LEDGER>'
python3 -m photo_motion.experiments audit --store '<SAME_PRIVATE_LEDGER>'
python3 -m photo_motion.preflight_v15_synthetic --request '<PRIVATE_V15_REQUEST>'
# Only when all inputs and observations really PASS, separately reserve:
python3 -m photo_motion.experiments reserve --store '<SAME_PRIVATE_LEDGER>' --request '<PRIVATE_V15_REQUEST>'
```

The preflight above is **read-only**, no media upload, no generation, and no
approval. The existing immutable ledger's reserve is a separate deliberate
operation; the user's current credit authorization covers controlled
diagnostics, not purchase of other services or publication. A stale quote,
wrong mode, missing asset, ambiguous model, changed prompt, changed ledger,
wrong render, new ledger, extra selected asset, or missing screenshot is a
hard **HOLD**. A pre-asset quote or guessed price cannot pass.

## Preregistered output verdict and stop rule

Preserve exact original generated MP4, native provider scene/output ID and
debit, prompt hash, actual settings, screenshot, actual frame hashes, full
decode, contacts, arms, identity and background privately **even on failure**.

The output is a **method test**. Success at the narrow hypothesis would require
two distinct intervals of at least two consecutive *actual* dual-shoe airborne
frames around A→C and C→A, opposite physical arm/leg assignments, no grounded
running/lunge/walking interludes, no dissolves/ghosting, no detached or
backwards hands, stable boy identity, entire head and shoes visible throughout,
fixed photographic track and a seamless grounded A→A outer loop. Compare to
V12, V13, V14. Generated audio can be stripped in a separate verified
derivative, but the raw file's presence of audio must still be recorded.

The two guide windows, exact guide seam, static background and limb lengths
are *input* measurements. They do not prove generated output quality. The
relevant original 5BX booklet, independent human form QA and Charles's
exact-video approval remain separate **unpassed** gates. If the guide's gray
appearance leaks into the boy, arms foreshorten/duplicate, two flights fail,
or the provider does not honor video motion conditioning, stop this source
method. The next preferred production reference is an explicitly consenting
adult physical recording under
[`FIRST_PARTY_SCISSOR_MOTION_CAPTURE.md`](FIRST_PARTY_SCISSOR_MOTION_CAPTURE.md),
not prompt-only source recycling.
