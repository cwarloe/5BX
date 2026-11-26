# V14 — A* to grounded C* single-exchange Frames pilot

**Gate classification: EXPERIMENTAL (originally written before the V14 run).** V14 is
not a continuation of V10's 720p/nine-credit paid authority, nor a workaround
for V12's independently observed wrong motion. It is a separately qualified
360p experiment that asks one narrow question: does replacing V12's airborne
**B*002 end frame** with the opposite **grounded C* end frame** prevent
the grounded runner/lunge steps in the generated A*→landing segment?

The source pose A* remains the same. B*002 remains held out as an airborne
*comparison*, not a third Flow input. A single A*→C* clip could show only one
exchange. It cannot establish a full A→flight→C→flight→A scissor cycle, the
original booklet's anatomical right/left ownership, loop continuity,
historically correct form, identity approval or release. Only Charles can
approve an exact final exercise video.

**Post-run observation (not a change to this gate):** the original V14
grounded-endpoint diagnostic **failed** because grounded gait preceded the
airborne interval. See the [safe V14 result note](diagnostics/v14-astar-cstar-one-flight-hold-2026-11-26.md).
This link does not renew precredit authority or authorize a retake.

## Source/process pins and no-claim boundaries

| Bound input or process | Immutable condition |
| --- | --- |
| Start A* | Exact RGB 1344×756 PNG SHA-256 `777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38` |
| Opposite grounded C* | Exact RGB 1344×756 PNG SHA-256 `04eb4f9d9fe1d1944da36ba007fb7611329d19c19bddebfe983c8182a583e72b` |
| Corrected V10 manifest | Exact SHA-256 `9271898a33bf54a2c15c722cc32145371431c593aea5ed92d110e81a88c4c100` |
| Independent V10 source QA | Exact SHA-256 `63f790d95ed46ba3290784a0a4a0a9812c3aaa6f56038aaaf0b7548eb5fa15c7`, decision diagnostic-source only |
| Third-image *hold-out*, not an input | B*002 SHA-256 `c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886` |
| Verbatim private V14 prompt | SHA-256 `a4f61c6d258987981c4b25426a4d5fdc4580a61b758132aa68e59b5d1e3caaa0`, no trailing LF; keep text/private path outside Git |
| Model and exact settings | Google Flow Omni 1.2 Flash, Frames to Video, 3 seconds, 16:9, 360p, x1, `seed: null`, project Return silent videos ON |
| Fresh actual quoted cost | Positive **current observed quote ≤3 credits**; use its exact value, not the cap as an assumed price |
| Existing private ledger | Same real reconciled Flow ledger with immutable V12 three-credit native debit and raw-artifact receipts; no newly initialized replacement |

### Exact source replay is required

Pass `v10_source_paths` with precisely the ten path keys from the corrected
[V10 source-pair gate](V10_SHARED_CANVAS_FRAMES.md):
`original_a_png`, `original_c_png`, `canvas_jpeg`, `a_annotation`,
`c_annotation`, `canvas_annotation`, `shared_manifest`, `derived_a_png`,
`derived_c_png`, and `independent_qa_report`. Each value is an absolute
private local path. The V14 gate invokes the *unchanged* V10 exact-byte
recompositor using the repository's pinned A_TO_C V10 source-spec file,
then independently checks the corrected manifest and source QA hashes above.
Source labels or copied image hashes without original RGB PNG/JPEG bytes,
annotations and independent QA are insufficient.

The original V7 direct photographic A/C PNGs still prove only their exact
surviving bytes. The original V6 composite remains unrecoverable; **the V6
crop is not byte-replay verified**. The new shared canvas is a derived
diagnostic background, not a changed identity master. Orange/teal markers
track physical limbs but do not themselves establish anatomical right/left.

## Fresh Flow attestation and the real budget

Only after current V13 settlement or explicit reconciliation of any pending
run, open the **existing private Flow project** in authenticated Frames mode.
Visually confirm selected A* in the Start tile and selected C* in the End tile,
no third ingredient, exact model/mode/settings/single output, the actual
3-second 360p live quote, and Return silent videos ON in project settings.
Capture a fresh **private screenshot**, then create a private UTF-8 observation
JSON with **exactly** the following fields:

```json
{
  "schema_version": 1,
  "authority": "V14_FLOW_GROUNDED_ENDPOINTS_LIVE_QUOTE",
  "observed_at_utc": "<ACTUAL_UTC_WITHIN_15_MINUTES_OF_RESERVATION>",
  "operator": "<ACTUAL_NAMED_AGENT_OR_PERSON_WHO_INSPECTED_UI>",
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": null, "generation_mode": "Frames to Video",
    "resolution": "360p", "return_silent_videos": true
  },
  "quoted_credits": "<ACTUAL_POSITIVE_QUOTE_AT_MOST_3>",
  "start_tile": {
    "pose": "A*", "source_sha256": "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38",
    "flow_asset_id": "<ACTUAL_PRIVATE_FLOW_ASSET_ID_A>", "visually_confirmed": true
  },
  "end_tile": {
    "pose": "C*", "source_sha256": "04eb4f9d9fe1d1944da36ba007fb7611329d19c19bddebfe983c8182a583e72b",
    "flow_asset_id": "<ACTUAL_PRIVATE_FLOW_ASSET_ID_C>", "visually_confirmed": true
  },
  "only_two_endpoints_selected": true,
  "project_silent_setting_on": true,
  "ledger_reconciled": true,
  "ledger_actual_credits": "<LIVE_EXISTING_LEDGER_ACTUAL>",
  "ledger_pending_reserved_credits": "<LIVE_EXISTING_LEDGER_PENDING>",
  "ledger_available_credits": "<LIVE_EXISTING_LEDGER_AVAILABLE>",
  "ui_evidence_path": "<ACTUAL_PRIVATE_SCREENSHOT_FILE>",
  "ui_evidence_sha256": "<SCREENSHOT_SHA256>"
}
```

An asserted `flow_asset_id` is observational evidence, not a cryptographic
proof of upload bytes. The operator must compare the displayed image to the
correct source; a stale UI, wrong tile, hidden price, different model/mode,
newly created ledger, unreconciled prior debit or missing screenshot is a
**HOLD**. A quote below three credits is allowed but must be copied exactly
into both the observation and the request. A quote above three is not
authorized by **this** gate; explicitly requalify instead of silently paying.

### Versioned private request

Keep the exact prompt, path inventory, screenshots, output and resulting
receipts **outside Git**. Pass the V14 spec path and the actual two local
derived PNG files, with ordered roles; no B*002 third input:

```json
{
  "schema_version": 1,
  "attempt_key": "chart1-scissor-v14-astar-cstar-grounded-001",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "<REPO>/photo_motion/segment_specs/chart1-scissor-v14-astar-to-cstar-grounded.json",
  "submitted_prompt_file": "<PRIVATE_EXACT_V14_PROMPT_NO_TRAILING_NEWLINE>",
  "input_assets": [
    {"role": "start-frame", "locator": "<PRIVATE_ASTAR_FLOW_REFERENCE>",
     "local_path": "<PRIVATE_EXACT_ASTAR_PNG>",
     "sha256": "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38"},
    {"role": "end-frame", "locator": "<PRIVATE_CSTAR_FLOW_REFERENCE>",
     "local_path": "<PRIVATE_EXACT_CSTAR_PNG>",
     "sha256": "04eb4f9d9fe1d1944da36ba007fb7611329d19c19bddebfe983c8182a583e72b"}
  ],
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": null, "generation_mode": "Frames to Video",
    "resolution": "360p", "return_silent_videos": true
  },
  "estimated_credits": "<SAME_EXACT_LIVE_QUOTE>",
  "source_preflight": {
    "authority": "V14_GROUNDED_ASTAR_CSTAR_FRAMES_360P",
    "v10_source_paths": {
      "original_a_png": "<PRIVATE_ORIGINAL_A>",
      "original_c_png": "<PRIVATE_ORIGINAL_C>",
      "canvas_jpeg": "<PRIVATE_CANVAS>",
      "a_annotation": "<PRIVATE_A_BOUNDS>",
      "c_annotation": "<PRIVATE_CORRECTED_C_BOUNDS>",
      "canvas_annotation": "<PRIVATE_CANVAS_BOUNDS>",
      "shared_manifest": "<PRIVATE_CORRECTED_MANIFEST>",
      "derived_a_png": "<PRIVATE_EXACT_ASTAR_PNG>",
      "derived_c_png": "<PRIVATE_EXACT_CSTAR_PNG>",
      "independent_qa_report": "<PRIVATE_V10_INDEPENDENT_QA>"
    },
    "existing_ledger_store": "<SAME_EXISTING_NATIVE_CHARGE_LEDGER>",
    "flow_ui_observation": "<PRIVATE_FRESH_V14_OBSERVATION>"
  }
}
```

```bash
python3 -m photo_motion.experiments status --store '<EXISTING_PRIVATE_LEDGER>'
python3 -m photo_motion.experiments audit --store '<EXISTING_PRIVATE_LEDGER>'
python3 -m photo_motion.preflight_v14_grounded --request '<PRIVATE_V14_REQUEST>'
# Only after PASS and fresh same-source/same-ledger observations:
python3 -m photo_motion.experiments reserve --store '<SAME_EXISTING_PRIVATE_LEDGER>' --request '<PRIVATE_V14_REQUEST>'
```

The gate is **read-only** until a separately deliberate `reserve` command;
even reserve does **not** submit to Flow. It checks a 15-minute timebound
quote, ledger snapshot and native V12 receipt. Under the store lock, reserve
rejects any new credit debit/reservation that makes that UI ledger attestation
stale. An unchanged synthetic unit test or historical 720p quote is not
current payment authority.

## Pre-register the actual MP4 verdict and stop rule

One 3-second result is diagnostic. Preserve its **original bytes** privately,
actual prompt/settings/source SHA-256, native generation ID and exact charge
receipt even on failure. Compare raw V12 A*→B*002, potential V13 edit and
new V14 A*→C* on the same timeline while separating endpoint differences.
Full-decode the actual MP4 and bind all decoded frame hashes.

* Frame 0 must visibly match grounded A*: both shoes planted and full body in
  frame, correct orange/teal physical marker owners.
* Between A* and C* there must be **at least two consecutive actual frames**
  with **both shoes entirely airborne**, not a running lunge, walking step,
  apparent hover, fade or foot slide. Mark launch, flight and landing frames.
* At the final frame the same boy must be planted in the *opposite grounded*
  C*, with no intervening running/walking contact sequence.
* Compare wrist/shoulder height, elbow shape, physical marker continuity,
  hand direction and natural joints across all evaluable frames. Track
  occlusions as unknown, not interpolated proof.
* Check head/shoe framing throughout, identity, stationary camera/background,
  ghost/duplicate limbs, missing or generated audio and source/endpoint error.

**If V14 fails the grounded one-flight test**, stop same-source endpoint/
prompt-only retakes. Escalate to a consenting adult physical movement
reference under [the first-party protocol](FIRST_PARTY_SCISSOR_MOTION_CAPTURE.md)
and verify the intended provider can actually condition on the reference
before spending more Flow credits. If V14 works, separately qualify a
C*→A* return segment, use the [no-fade joiner](SEGMENT_JOIN.md) and measure
**both** flights and the A→A seam; do not infer these from the first segment.

Synthetic test coverage (`python3 -m unittest photo_motion.tests.test_v14_grounded`)
does not contact Flow and never requires real photographic source files. It
tests exact replay/QA receipt enforcement, source ordering, held-out third
input rejection, prompt and spec integrity, live quote and settings, fresh
source-tile and screenshot attestation, same-store reservation and
concurrent-credit-drift rejection. The operator must still independently
inspect true images and video; no automated form or release verdict exists.
