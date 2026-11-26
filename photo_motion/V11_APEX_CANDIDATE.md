# V11 photographic B* apex — read-only candidate preflight

**B*002 passed diagnostic still-source review only; no V11 paid authority or
video-form acceptance.** The first image candidate resembled a grounded
opposite stance: independent review measured only 3px and 6px of shoe lift,
failing the declared **25px minimum**. The second, separately hashed B*002
candidate passed an independent eight-check diagnostic-source review (minimum
two-shoe clearance 106px), but historical anatomical left/right and actual
moving video form remain unproven. Never treat a plausible still or its
generation prompt as an approved exercise video.

`python3 -m photo_motion.apex_candidate_qa` is an **experimental, read-only
still-image evidence gate**. It does not integrate with the credit ledger,
reserve credits, call Flow, approve historical anatomy, or release videos.
Prospective paid Frames generation requires the separately versioned
[V12 exact-endpoint 360p gate](V12_APEX_FRAMES_PRECREDIT.md), plus a fresh live
provider quote/settings and actual selected endpoint evidence. A foreground-only animated character on a fixed track
is a parallel research idea and is not qualified by this B* test.

## Inputs and invariants

- The complete corrected V10 lineage must replay exactly: original A/C
  1280×720 PNGs, one generated A′ canvas JPEG, three conservative subject
  annotations, both A*/C* 1344×756 PNGs, the final manifest and the private
  independent source-pair QA. The V10 preflight is called again. The A*
  source hash is `777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38`;
  C* `04eb4f9d9fe1d1944da36ba007fb7611329d19c19bddebfe983c8182a583e72b`;
  manifest `9271898a33bf54a2c15c722cc32145371431c593aea5ed92d110e81a88c4c100`;
  V10 independent QA report
  `63f790d95ed46ba3290784a0a4a0a9812c3aaa6f56038aaaf0b7548eb5fa15c7`.
- The new B* source must be the **original candidate bytes**, a complete
  locally rehashed RGB JPEG or PNG exactly 1344×756, not a disguised grounded
  A*/C*, converted screenshot, sprite, or differently processed image.
- A *different* independent reviewer records a private report bound to the
  exact V10 hashes, B* SHA-256, B* native format and image dimensions, with
  all eight named image checks supported by substantive evidence: source
  integrity, full head/shoes, physical marker identity, character identity,
  background stability, no ghost/duplicate, shoulder-high arms and both
  shoes visibly airborne. `HOLD` or `UNKNOWN` blocks the candidate.
- Named physical orange/teal **ankle and wrist markers** each move in the
  correct signed screen-forward direction by at least **40 pixels**, and
  both ankle and wrist fore/aft orderings reverse with ≥40px separation.
  Forward screen orientation must be observed; screen-side does not prove
  anatomical left/right.
- Ground line is anchored to the planted A* reference soles (within 12px).
  **Both** B* shoe bottoms must be at least **25px above** the same line.
  B* wrists must be within **45px vertically** of their respective shoulder
  centers. These numbers are explicit *diagnostic pixel thresholds*, not RCAF
  safety/form or mandatory prescribed exercise-cadence standards.

This checks the consistency of independent manually supplied landmark
coordinates. It does **not** automatically detect joints or authenticate the
reviewer's observations. Visual identity, historical form, full airborne
motion and loop correctness still require independent assessment on the
actual video. No code path here grants permission to use a B* as a paid
video endpoint.

## Private report and invocation

The private V10 source-path JSON contains exactly these ten keys, with
private filesystem paths as values: `original_a_png`, `original_c_png`,
`canvas_jpeg`, `a_annotation`, `c_annotation`, `canvas_annotation`,
`shared_manifest`, `derived_a_png`, `derived_c_png`, `independent_qa_report`.

The private B* QA JSON requires:

```json
{
  "schema_version": 1,
  "authority": "V11_APEX_CANDIDATE_READ_ONLY",
  "a_star_sha256": "REPLACE_WITH_EXACT_ASTAR_HASH",
  "c_star_sha256": "REPLACE_WITH_EXACT_CSTAR_HASH",
  "v10_manifest_sha256": "REPLACE_WITH_EXACT_V10_MANIFEST_HASH",
  "v10_qa_sha256": "REPLACE_WITH_EXACT_V10_QA_HASH",
  "b_sha256": "REPLACE_WITH_ACTUAL_B_HASH",
  "b_format": "JPEG",
  "image_size": [1344, 756],
  "producer": "ACTUAL_PRODUCING_AGENT",
  "reviewer": "ACTUAL_INDEPENDENT_REVIEWER",
  "decision": "HOLD",
  "checks": {
    "source_integrity": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"},
    "visible_head_and_shoes": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"},
    "marker_identity": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"},
    "identity_stability": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"},
    "background_stability": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"},
    "no_ghost_or_duplicate": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"},
    "arms_shoulder_high": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"},
    "both_shoes_airborne": {"verdict": "HOLD", "evidence": "REQUIRES_INDEPENDENT_REVIEW"}
  },
  "measurements": {
    "forward_screen_direction": "RIGHT",
    "reference_a_markers": {
      "orange_ankle": [450, 550], "teal_ankle": [600, 550],
      "orange_wrist": [650, 240], "teal_wrist": [450, 240]
    },
    "candidate_b_markers": {
      "orange_ankle": [650, 510], "teal_ankle": [450, 510],
      "orange_wrist": [450, 230], "teal_wrist": [650, 230]
    },
    "reference_a_ground": {"ground_y": 700,
                           "orange_sole_y": 700, "teal_sole_y": 698},
    "candidate_b_shoe_bottoms": {"orange_sole_y": 640, "teal_sole_y": 645},
    "candidate_b_shoulders": {"orange_y": 230, "teal_y": 232}
  },
  "anatomical_left_right_proven": false,
  "video_form_release": "NOT_EVALUATED"
}
```

**All example coordinates and HOLD values are synthetic placeholders, not
real B* observations.** They must be replaced by an independent review of
actual hash-identified images. The report, original B* bytes and exact
historical prompts remain private, outside Git.

```bash
python3 -m photo_motion.apex_candidate_qa \
  /private/exact-v10-source-paths.json \
  /private/original-B-apex.jpg \
  /private/independent-B-apex-QA.json
```

The result always carries `paid_video_precredit_authority: NOT_GRANTED` and
`motion_video_release_approval: NOT_EVALUATED`. Once a real B* source passes,
it may support a *new experimental source proposal*, never an automatic
paid run, exercise approval, publication or release.
