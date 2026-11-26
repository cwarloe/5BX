# V10 shared-canvas A*/C* Frames — paid-video precredit gate

**Experimental diagnostic authority only. No final form, video or release
approval.** This is a new, derivative-source branch, not a modification of
the V6/V7/V8 direct prepared-photo authorities. The original V6 source card
remains unavailable and its crop has **not** been independently replayed.

V9's individually generated A′ and C′ JPEGs had substantial background and
framing differences. V10 instead uses one exact generated **A′ canvas JPEG**
to place both original V7 A and C photographic poses on the **same canvas**
through a deterministic central resize, location and feather window. The
archived A/C originals remain the person/pose authority; the model-generated
canvas is exterior background and must not silently become an identity master.
The derived outputs `A*` and `C*` are new RGB 1344×756 PNGs, not substitutes
for the original 1280×720 A/C PNGs.

## Requirements before reserving nine credits

1. **Exact, locally rehashed source chain:** original A/C PNGs must match
   their V7 SHA-256s and RGB 1280×720 format. The *single* generated canvas
   is an RGB 1344×756 JPEG SHA-256
   `10989cf3c87b1b9758599e0ebf3bb015141198fb36a6aec72b7c8491cd4aa550`.
   Separately archive all three source files, conservative subject-bound
   annotation files, both A*/C* outputs and the composition manifest. No
   sprite, historical V6 crop assertion or other generated source is allowed.
2. **Replay the complete composition:** `photo_motion.shared_canvas` must
   deterministically regenerate **exact bytes** for both output PNGs **and
   the manifest**, using shrink 37/50, rounded size 947×533, offset (200,172),
   window [355,172,1020,705), side/top/bottom feathers 55/5/18, Pillow
   LANCZOS and linear-alpha blending. The full manifest includes source,
   annotation, transform, library version and output digests. Merely knowing
   a hash or copying output filenames never passes this check.
3. **Independent source-pair QA:** the actual report file must rehash to its
   immutable recorded digest and bind the *corrected* manifest, three source
   SHA-256s and both output PNG SHA-256s. Producer and reviewer must be named
   and distinct. All eight checks—source integrity, annotation coverage,
   background alignment, composition replay, seam/ghosting, head/shoes framing,
   character identity and physical limb consistency—must explicitly PASS with
   substantive evidence. Decision
   must be exactly `CANDIDATE_FOR_DIAGNOSTIC_ONLY`; `HOLD` blocks reservation.
   The report explicitly retains unknown historical anatomical side, and
   `NOT_EVALUATED` exercise form and video/release. This structural check
   cannot cryptographically authenticate the human reviewer's identity or
   replace independent visual judgment.
4. **One quoted Flow video:** a 2026-11-26 live UI observation in the existing
   Flow project showed Video → Frames, model **Omni 1.2 Flash**, aspect
   **16:9**, resolution **720p**, length **3 Sec**, **x1** output and **9
   credits**. The request schema pins exactly those values, with unknown
   seed `null`; no added settings, output multiplier, alternate model or
   implicit paid retry. Check the quote and reconciled existing project
   ledger **again** at the actual reservation/submission time. If UI settings
   or quote drift, HOLD and version/requalify this gate.
5. **Two separate segments:** reserve A*→C* and C*→A* independently (nine
   credits each if still quoted), only after source QA passes. Distinct
   attempt keys, prompts and immutable run IDs are mandatory. No generation
   happens in the preflight. The V8 no-fade segment joiner remains a separate
   technical comparison; neither a correct midpoint nor a good endpoint
   pixel score proves two airborne exchanges, real anatomical physical side,
   stable identity, audio policy or a seamless complete exercise cycle.

### Offline source verification

```bash
python3 -m photo_motion.preflight_v10_shared_canvas \
  photo_motion/segment_specs/chart1-scissor-v10-astar-to-cstar.json \
  /private/original-A.png /private/original-C.png \
  /private/generated-A-prime-canvas.jpg \
  /private/shared_canvas.manifest.json \
  /private/A_shared_canvas.png /private/C_shared_canvas.png \
  --a-annotation /private/A-subject-bounds.json \
  --c-annotation /private/C-subject-bounds.json \
  --canvas-annotation /private/canvas-subject-bounds.json \
  --independent-qa-report /private/V10-independent-source-qa.json \
  --segment-role A_TO_C
```

The source preflight recomposes into a temporary directory, never replaces
private media, never calls Flow and never touches the credit ledger. Verify
the corrected manifest, not the rejected earlier C-bounds version. In
particular, conservative C subject annotation must include the forward
forearm/hand; a visually plausible render is insufficient if its coverage
proof is false.

### Private immutable experiment request

Create a **private, untracked** request and exact UTF-8 submitted prompt.
Change the spec/segment role and reverse `input_assets` for `C_TO_A`. The
local paths/locators below are placeholders, not public or replayable URLs.

```json
{
  "schema_version": 1,
  "attempt_key": "C1-EX5-V10-astar-to-cstar-001",
  "exercise_id": "chart1-scissor-jump",
  "spec_path": "photo_motion/segment_specs/chart1-scissor-v10-astar-to-cstar.json",
  "submitted_prompt_file": "/private/exact-submitted-a-to-c-prompt.txt",
  "input_assets": [
    {"role": "start-frame", "locator": "REPLACE_WITH_PRIVATE_ASTAR_LOCATOR", "local_path": "/private/A_shared_canvas.png"},
    {"role": "end-frame", "locator": "REPLACE_WITH_PRIVATE_CSTAR_LOCATOR", "local_path": "/private/C_shared_canvas.png"}
  ],
  "provider": "Google Flow",
  "model": "Omni 1.2 Flash",
  "settings": {
    "duration_seconds": 3,
    "aspect_ratio": "16:9",
    "variants": 1,
    "seed": null,
    "generation_mode": "Frames to Video",
    "resolution": "720p"
  },
  "estimated_credits": "9",
  "source_preflight": {
    "authority": "V10_REPLAYED_SHARED_CANVAS_FRAMES",
    "original_a_png": "/private/original-A.png",
    "original_c_png": "/private/original-C.png",
    "canvas_jpeg": "/private/generated-A-prime-canvas.jpg",
    "a_annotation": "/private/A-subject-bounds.json",
    "c_annotation": "/private/C-subject-bounds.json",
    "canvas_annotation": "/private/canvas-subject-bounds.json",
    "shared_manifest": "/private/shared_canvas.manifest.json",
    "derived_a_png": "/private/A_shared_canvas.png",
    "derived_c_png": "/private/C_shared_canvas.png",
    "independent_qa_report": "/private/V10-independent-source-qa.json",
    "segment_role": "A_TO_C"
  }
}
```

The ledger `reserve` freezes exact submitted prompt bytes, two ordered
locally rehashed derived endpoints, original source digests, versioned spec,
fully replayed manifest digest and independent QA report digest. A missing,
unreviewed or changed source chain is a HOLD before credits. For a real
submitted run, reconcile the existing **200-credit 5BX workstream limit**
and settle the **actual** provider debit (including failed results). Do not
equate the provider's separately displayed account balance or daily credits
with the workstream's authorized ledger allowance. Preserve raw MP4, prompt,
all settings, source SHA links and frame-level defects privately. Do not
record a pre-submit reservation retrospectively as though it preceded Flow.

**Important limits:** One qualifying three-second segment is not a complete
5BX scissor cycle. The original exercise requires physical right leg/left
arm forward in the start stance; color markers alone do not prove that
anatomical side assignment. No result may be declared historically correct,
production-ready, published or released without the owner's exact-video
form decision.
