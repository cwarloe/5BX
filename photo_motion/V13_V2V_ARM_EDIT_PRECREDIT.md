# V13: video-to-video arm-only rescue of failed V12 — precredit gate

**Gate classification: EXPERIMENTAL (originally written before the V13 run).**
This is a narrowly scoped precredit authority, independent of the prior V12 Frames-to-Video
gate. A valid preflight or a successfully edited clip would **not** establish
Chart 1 Exercise 5 historical form, the grounded opposite landing, a second
airborne exchange, loop continuity, identity approval or release.

**Post-run observation (not a change to this gate):** the original V13
arm-edit diagnostic **failed** independent comparison; see the
[safe V13 result note](diagnostics/v13-v2v-arm-edit-hold-2026-11-26.md).
Its stop rule remains binding; this retrospective link does not renew
precredit authority or authorize another generation.

## One falsifiable experiment

**Source failure:** the real 3-second V12 A*→B*002 clip preserved its visual
endpoints, but independently reviewed frames 18–36 became runner-like, with
lowered/pumping arms and intermittent grounded steps. It first shows clear
two-shoe flight at approximately frame 42. The raw MP4 also has non-silent
AAC. The separate immutable V12 ledger records exactly **3 credits spent**.
See [the safe V12 diagnostic](diagnostics/v12-astar-b002-motion-hold-2026-11-26.md)
and the actual independent report held in the existing **private** archive.

**Hypothesis:** Google Flow's Omni 1.2 Flash edit of the **exact original V12
raw MP4** can replace its running-style **arm trajectory only** with
approximately shoulder-level extended reciprocal arms, without disrupting
person identity, the existing photographic track, physical marker ownership,
leg motion, camera, or either endpoint.

The **single requested correction is arm movement**, not legs or ground
contacts. Model workflow changes from V12 new Frames generation to the
separately qualified Video-to-Video edit operation; compare the same temporal
samples before and after. No changed source photo, alternate model, longer
duration, batch output, background extraction, motion-control video, face
replacement or second target is authorized by this particular gate. A
successful arm-only edit is diagnostic, **not a playable 5BX exercise**.

| Immutable pin | Exact value |
| --- | --- |
| Source | *Original* V12 provider MP4 `5680aff2e5811ef99d52a533a6c24405ad1d92ef66afa7bf9b37fb7e693d3fba` |
| Original video format | H.264 640×360, 24 fps, exactly 72 frames/3s, original AAC preserved |
| Final independent V12 QA | `a1477c3d5ca7eae765bbf0d2377a467f4fe29021360805d78e16cea70f128d70`, verdict **HOLD** |
| Existing settled V12 attempt | `cd098dc731c35283a78b47f500d357ecb0577654068f2f5fe7d95fe00e5ea14a`, native actual charge **3** |
| Exact V13 prompt SHA-256 | `6c46960ec7c400b4d58b296fa2b8f40ef97e2b264c643c2d9a8a9579327ec231`, **no trailing newline/space** |
| Model/mode | Google Flow, **Omni 1.2 Flash**, **Video to Video Edit** in existing V12 scene |
| Profile | 3 s, 16:9, 360p, x1, seed unknown (`null`), silent-video project setting ON |
| Price ceiling | **Positive actual current quote ≤3 credits**, estimate must equal that quote exactly |

The archived source input and final independent QA must be rehashed locally;
the previous raw-video immutable artifact receipt, native three-credit
provider-charge receipt, scene ID and original V12 Frames intent must match
the **same existing private reconciled ledger**. Source gate full-decodes the
raw H.264 before trusting it. It rejects silent derivatives, rescaled copies,
missing independent QA, unsettled/mismatched native debit, altered intent,
stale UI evidence and ledger replacement. Audit/receipt checks cannot prove
the actual Flow service's state: a named operator must still visually check
the authenticated edit page, current quote and real provider balance.

## Fresh UI observation — private only

In the existing Flow V12 scene's **Edit video** view, confirm the source clip
is loaded and the edit-prompt field is available, inspect the actual model,
3-second timeline, resolution, single-output intent and price. Open the
model/credit menu: a hidden or merely assumed quote is a **HOLD**. Capture
private screenshot evidence after all fields are visible. Verify that
`source_scene_id` matches the **native settled V12 charge ID**; never put the
private scene URL/ID, screenshot or user-account information in Git.

Make a private JSON file with **exactly** these fields; its `observed_at_utc`
must be real UTC and no more than **15 minutes** old at reservation:

```json
{
  "schema_version": 1,
  "authority": "V13_FLOW_LIVE_VIDEO_EDIT_QUOTE",
  "observed_at_utc": "<CURRENT_ACTUAL_UTC>",
  "operator": "<PERSON_OR_AGENT_WHO_LOOKED_AT_REAL_EDIT_UI>",
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {
    "duration_seconds": 3,
    "aspect_ratio": "16:9",
    "variants": 1,
    "seed": null,
    "generation_mode": "Video to Video Edit",
    "resolution": "360p",
    "return_silent_videos": true
  },
  "quoted_credits": "3",
  "source_scene_id": "<ACTUAL_PRIVATE_V12_SCENE_ID>",
  "source_video_visible": true,
  "edit_prompt_interface_visible": true,
  "source_qa_hold_acknowledged": true,
  "project_silent_setting_on": true,
  "ledger_reconciled": true,
  "ledger_actual_credits": "<EXACT_IMMUTABLE_LEDGER_SNAPSHOT>",
  "ledger_pending_reserved_credits": "<EXACT_IMMUTABLE_LEDGER_SNAPSHOT>",
  "ledger_available_credits": "<EXACT_IMMUTABLE_LEDGER_SNAPSHOT>",
  "ui_evidence_path": "<PRIVATE_SCREENSHOT_FILE>",
  "ui_evidence_sha256": "<ACTUAL_SCREENSHOT_SHA256>"
}
```

The quote can be lower than 3 if that is what Flow actually displays, but
must remain positive and ≤3. The example's price is **not a substitute for a
fresh quote**. Any changed model, mode, pricing, count, video, required
setting or insufficient reconciled balance invalidates the attestation.

## Exact private request and no-spend validation

Keep the actual UTF-8 submitted prompt **outside the repository**. Its
complete bytes must match the pinned SHA above; Flow's editable field may
normalize a trailing newline to whitespace, so the controlled prompt has
**no final newline or extra trailing whitespace**. Visually/DOM-verify
the exact resulting edit text before reservation. Do not commit the private
request, QA report, source MP4, prompt, ledger or UI screenshot.

```json
{
  "schema_version": 1,
  "attempt_key": "chart1-scissor-v13-v12-v2v-arm-rescue-001",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "<REPO>/photo_motion/segment_specs/chart1-scissor-v13-v12-arm-edit.json",
  "submitted_prompt_file": "<PRIVATE_EXACT_ARM_ONLY_PROMPT_TXT>",
  "input_assets": [
    {
      "role": "source-video",
      "locator": "<PRIVATE_ORIGINAL_V12_VIDEO_REFERENCE>",
      "local_path": "<PRIVATE_EXACT_V12_RAW_MP4>",
      "sha256": "5680aff2e5811ef99d52a533a6c24405ad1d92ef66afa7bf9b37fb7e693d3fba"
    }
  ],
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {
    "duration_seconds": 3,
    "aspect_ratio": "16:9",
    "variants": 1,
    "seed": null,
    "generation_mode": "Video to Video Edit",
    "resolution": "360p",
    "return_silent_videos": true
  },
  "estimated_credits": "3",
  "source_preflight": {
    "authority": "V13_V12_RAW_ARM_ONLY_V2V_EDIT_360P",
    "raw_v12_video": "<PRIVATE_EXACT_V12_RAW_MP4>",
    "independent_v12_qa": "<PRIVATE_FINAL_V12_QA_REPORT>",
    "existing_ledger_store": "<SAME_EXISTING_RECONCILED_PRIVATE_LEDGER>",
    "flow_ui_observation": "<PRIVATE_FRESH_V13_UI_JSON>"
  }
}
```

The single source-video role is intentional; an extra ingredient or still
would change the experiment. No new ledger may be initialized. Reconcile the
provider's *live actual* charges against the historical immutable ledger;
the previous V12 native three-credit debit must remain present. Use the
live quoted amount in both `estimated_credits` and observation.

```bash
python3 -m photo_motion.experiments status --store '<EXISTING_PRIVATE_LEDGER>'
python3 -m photo_motion.experiments audit --store '<EXISTING_PRIVATE_LEDGER>'
python3 -m photo_motion.preflight_v13_v2v --request '<PRIVATE_V13_REQUEST_JSON>'
# Only after no-spend preflight PASS, fresh UI evidence, and actual reconciliation:
python3 -m photo_motion.experiments reserve --store '<SAME_EXISTING_PRIVATE_LEDGER>' --request '<PRIVATE_V13_REQUEST_JSON>'
```

`preflight_v13_v2v` is **read-only** and prints no private media/scene
locators or prompt text on success. `reserve` creates an immutable 3-credit
reservation against the existing ledger; it still **does not** call Flow or
grant final production authority. After a verified reservation, submit
**one** edit with the identical prompt in the same scene, not another
Frames-to-Video generation. If UI/quote/prompt changes, stop; refresh
attestation and make a **new versioned** plan. Record the actual provider
debit, unique generation/scene ID, unmodified V13 raw MP4 and all results in
the existing private archive/ledger; never treat cancellation or failed
generation as zero-cost without provider evidence.

## Pre-registered comparison and stop rule

Review actual V12 and V13 source frames **0, 18, 36, 54, 71**, then all 72
V13 decoded frames and corresponding V12 frames. Use the newly merged
[full-video arm trajectory QA](ARM_TRAJECTORY_QA.md) with real named-human
shoulder/wrist/elbow landmarks; generate its frame-hash-bound annotation
template and analyze the exact raw MP4. Its stricter current criteria are
**engineering proxies**, not historical 5BX form tolerances:

1. Both visible wrists stay within **±25 pixels** vertically of their
   respective shoulder levels at 640×360. At least **90% of all decoded
   frames** must be evaluable for height; **any** observed violation fails
   that metric. Missing/occluded frames are reported, not imputed.
2. Visible elbow angles stay **≥150°** in both arms with at least 90%
   full-coverage frames; any observed bent-arm violation fails the extension
   metric. Independently assess plausible hand orientation, especially the
   rear hand. Computer-generated keypoints cannot impersonate human review.
3. Physical orange/teal marker assignments remain continuous. No dropped,
   duplicated, mirrored or reversed-in-time hands/arms, ghosting or new
   anatomical impossibility appears.
4. Exact original/end pose likeness, identity, frame visibility, stationary
   background and existing leg movement show no material regression. Save
   reviewer regions and numeric ROI deltas before choosing verdicts. A
   seemingly more perfect arm frame that changes legs fails this experiment.
5. Run technical full-video decode, media/hash/codec audit, audio-stream
   detection, independent motion/contact and human anatomy review. Non-silent
   AAC may still be present; record it as raw defect and optionally derive a
   bitstream-verified mute copy **without replacing the raw**.

**Success:** both arm metrics achieve
`PASS_MANUALLY_ATTESTED_GEOMETRY_ONLY` with no collateral changes;
classify only `ARM_EDIT_METHOD_DIAGNOSTIC_PASS`, while entire V13 video
remains **FORM/CONTACT/FLIGHT HOLD** until a separate exercise-correct
leg/flight trial. **Failure:** arm proxy misses threshold or significant
collateral motion/identity defects arise. Preserve the exact paid output,
mark `ARM_EDIT_METHOD_DIAGNOSTIC_FAIL`, **stop edit/prompt paraphrase retries**
for the same defect and prioritize a separately authorized motion reference
from a consenting adult or validated phase-controlled editing workflow.
No edit result constitutes A→C→A loop proof or Charles's video acceptance.

## Synthetic engineering coverage

`python3 -m unittest photo_motion.tests.test_v13_v2v` uses **only generated
synthetic test video, synthetic QA, mocked hashes and an isolated test ledger**.
It checks raw MP4 identity and codec, exact prompt, V12 HOLD report, previous
native debit/artifact proof, current Flow edit mode/quote, 15-minute attestation,
singular output, request/ledger equality, and privacy-sensitive restrictions.
It makes no Flow calls, stores no private media in Git, and cannot certify
exercise form, provider honesty, or release.
