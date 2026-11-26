# V12: independently reviewed A* → B*002 Frames diagnostic, 360p

**Status: conditional source authority only. No video submitted, no credit
reserved, and no exercise-form/video/release acceptance from this contract.**
Historical anatomical left/right remains **UNKNOWN**. The 5BX exercise still
requires two airborne exchanges and a complete loop, neither of which a 3s
A*→B* held-apex segment can prove.

This is a new paid-output profile, not a V10 720p exception. The V11
read-only apex-review gate remains unchanged. The V12 gate separately requires
the corrected V10 exact ten-file replay, exact B*002 generated RGB JPEG,
the independently reviewed B*002 QA bytes, both locally rehashed endpoints,
and **fresh attestation of the real Flow endpoint tiles and live quote**.

| Pin | Exact identity |
| --- | --- |
| V10 A* source PNG | `777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38` |
| V10 corrected manifest | `9271898a33bf54a2c15c722cc32145371431c593aea5ed92d110e81a88c4c100` |
| V10 independent QA JSON | `63f790d95ed46ba3290784a0a4a0a9812c3aaa6f56038aaaf0b7548eb5fa15c7` |
| B*002 original RGB 1344×756 JPEG | `c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886` |
| B*002 independent QA JSON | `98c27fb67e174b3fae2dcf96a4851ce143865e7b51f4d21b9d8f2bb25775a145` |

The independently reviewed B*002 report declares a diagnostic-only candidate:
both shoe bottoms measured 106 px off the A* ground reference, the four
physical color-marker directions reversed at least 40 px, arms were near
shoulder height, and source/body/background/ghost checks passed. These are
reviewer measurements, **not automatic anatomical-form certification**.
Reject B*001, a grounded earlier attempt. Do not substitute the separate
heuristic foreground-matte research outputs.

## Before a credit reservation

1. Reconcile existing immutable **private** project ledger against current
   provider charges; never initialize a new zero-opening ledger in place of it.
2. Independently replay and rehash every V10 source/annotation/canvas/manifest,
   plus both exact B*002 JPEG and QA-report bytes. `verify_sources` reuses
   V11/V10 validators, including exact compositor byte replay.
3. In the existing authenticated private Flow project, select **Video →
   Frames** with A* as start frame and B*002 as end frame. Visually verify the
   two different tiles and their full source identity. Reconfirm selected
   model **Omni 1.2 Flash**, 16:9, 360p, length 3s, x1, live quote **3
   credits**, and project setting **Return silent videos ON**.
4. Save a private screenshot/observation, SHA-256 hash it, and create a
   private `flow_ui_observation` JSON with exact fields below. Record its
   actual UTC observation time; attestation expires in **15 minutes**.
5. Keep an immutable UTF-8 text file containing the actual intended/submitted
   prompt. Reserve **before** clicking Generate, then submit exactly once.
   If any quote or endpoint changes, do not reuse the reservation; record
   the discrepancy and prepare a new distinct attempt only after review.

The module verifies **operator attestation plus file hashes**, not an API-
verified claim that the Flow service really received a given file. A
visually wrong uploaded tile must be marked HOLD even if its attestation
JSON could be made to pass.

### Fresh Flow UI attestation (private file only)

```json
{
  "schema_version": 1,
  "authority": "V12_FLOW_EXACT_ENDPOINTS_LIVE_QUOTE",
  "observed_at_utc": "<ACTUAL_CURRENT_UTC_ISO_8601>",
  "operator": "<NAME_OF_PERSON_OR_AGENT_WHO_OBSERVED_UI>",
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {
    "duration_seconds": 3,
    "aspect_ratio": "16:9",
    "variants": 1,
    "seed": null,
    "generation_mode": "Frames to Video",
    "resolution": "360p",
    "return_silent_videos": true
  },
  "quoted_credits": "3",
  "project_silent_setting_on": true,
  "start_tile": {
    "source_sha256": "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38",
    "pose": "A*",
    "flow_asset_id": "<ACTUAL_FLOW_ASTAR_ASSET_ID>",
    "visually_confirmed": true
  },
  "end_tile": {
    "source_sha256": "c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886",
    "pose": "B*002",
    "flow_asset_id": "<ACTUAL_FLOW_B002_ASSET_ID>",
    "visually_confirmed": true
  },
  "ui_evidence_path": "<PRIVATE_LOCAL_SCREENSHOT_PATH>",
  "ui_evidence_sha256": "<ACTUAL_SHA256_OF_SCREENSHOT>",
  "ledger_reconciled": true
}
```

`visually_confirmed`/`ledger_reconciled` must describe actual observed facts.
The IDs must be distinct. A stale, future, unhashable, altered or absent
observation; unconfirmed endpoints; false/absent quiet setting; changed price,
model or resolution; and missing private source files all **fail closed**.

### Private request contract and commands

Use the existing `photo_motion.experiments` immutable ledger, never a separate
V12 ledger. Save a private JSON request (no private media or prompt content in
Git), with this exact shape; replace every placeholder with an existing
local/private record. The `v10_source_paths` object contains exactly ten
file-path strings, not a wrapper with `assets` metadata.

```json
{
  "schema_version": 1,
  "attempt_key": "chart1-scissor-v12-astar-b002-001",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "<REPO>/photo_motion/segment_specs/chart1-scissor-v12-astar-to-b002.json",
  "submitted_prompt_file": "<PRIVATE_LOCAL_PROMPT_TEXT_FILE>",
  "input_assets": [
    {
      "role": "start-frame",
      "locator": "<PRIVATE_ASTAR_LOCATOR>",
      "sha256": "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38",
      "local_path": "<PRIVATE_ASTAR_PNG_PATH>"
    },
    {
      "role": "end-frame",
      "locator": "<PRIVATE_B002_LOCATOR>",
      "sha256": "c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886",
      "local_path": "<PRIVATE_B002_ORIGINAL_JPEG_PATH>"
    }
  ],
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": null, "generation_mode": "Frames to Video",
    "resolution": "360p", "return_silent_videos": true
  },
  "estimated_credits": "3",
  "source_preflight": {
    "authority": "V12_REVIEWED_APEX_B002_FRAMES_360P",
    "v10_source_paths": {
      "original_a_png": "<PRIVATE_PATH>",
      "original_c_png": "<PRIVATE_PATH>",
      "canvas_jpeg": "<PRIVATE_PATH>",
      "a_annotation": "<PRIVATE_PATH>",
      "c_annotation": "<PRIVATE_PATH>",
      "canvas_annotation": "<PRIVATE_PATH>",
      "shared_manifest": "<PRIVATE_PATH>",
      "derived_a_png": "<PRIVATE_ASTAR_PNG_PATH>",
      "derived_c_png": "<PRIVATE_PATH>",
      "independent_qa_report": "<PRIVATE_PATH>"
    },
    "b_apex_image": "<PRIVATE_B002_ORIGINAL_JPEG_PATH>",
    "independent_b_qa": "<PRIVATE_B002_INDEPENDENT_QA_JSON_PATH>",
    "flow_ui_observation": "<PRIVATE_FRESH_FLOW_UI_OBSERVATION_JSON_PATH>"
  }
}
```

```bash
python3 -m photo_motion.experiments status --store '<EXISTING_PRIVATE_LEDGER>'
python3 -m photo_motion.experiments reserve --store '<EXISTING_PRIVATE_LEDGER>' --request '<PRIVATE_V12_REQUEST_JSON>'
```

After an actual submission, settle the actual provider charge (including a
failed generation's charge, if any) with the unique provider generation ID;
archive the raw result, prompt/settings/source hashes, frame-level QA and
negative observations through existing private provenance procedures. Do not
declare exercise form, video motion, acceptance or release approved.

## Tests and authority boundaries

`python3 -m unittest photo_motion.tests.test_v12_apex_frames` runs synthetic
negative and ledger reservation tests without private images or Flow API.
The source replay additionally passed once against privately restored exact
original/derived files and the independently archived B002 QA JSON (no
provider submission). V10/V11/V7/V8 policies remain unchanged.
