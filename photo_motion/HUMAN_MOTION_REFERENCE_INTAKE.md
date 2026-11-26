# Read-only intake for future first-party adult scissor-motion references

**Experimental standard work — no adult footage has been supplied or approved.**
This supplements, and does not replace, [the first-party capture field protocol](FIRST_PARTY_SCISSOR_MOTION_CAPTURE.md), the original Chart 1 movement authority, the current V7 A/C still authorities, or the existing photographic QA/release records. No new Kanban, traveler, or approval ledger is created.

The validator `photo_motion.human_motion_reference_intake` is **local and read-only**. It does not contact Flow or another provider, write derivatives, submit footage, authenticate a signature, recognize anatomy from pixels, or approve historically correct 5BX form. `CAPTURE_REFERENCE_CANDIDATE` means only that byte-level technical checks and explicitly named human evidence claims are complete enough to **propose** a separately reviewed motion-conditioning experiment. The output always sets `provider_upload_authorized`, `form_correctness_approved`, and `public_release_authorized` to `false`.

## Capture and private evidence

Follow the first-party protocol: consenting adult (18+), unmodified camera-original MP4/MOV, fixed true side-on 16:9 at native 1080p60 or better, full person/hands/shoes/ground visible, and two uncut complete physical A→B→C→D→A cycles. Prefer 10–15 seconds; this conservative intake gate requires **at least 10 continuous seconds**. A is physical **right leg + left arm forward**; C is physical **left leg + right arm forward**. Each of B0/D0/B1/D1 must belong to a distinct contiguous interval with at least **two decoded frames** where *both entire outsoles* are clear. Never infer physical right/left from the V7 stills' orange/teal tags or from a 1959 archival film.

Archive **outside Git** all five items separately, owner-only:

1. The exact camera-original file; never edit, strip its audio, rotate or change its FPS.
2. One JSON capture receipt containing metadata, human annotations, named consent summaries and **opaque private-scheme archive locators**, with no private filesystem paths.
3. A named, dated private human frame-review evidence artifact (e.g., annotated frame report); record its SHA-256 in the receipt.
4. A signed, dated adult-performer release explicitly covering filming, analysis, AI motion-conditioning upload to the named provider, derivatives, intended educational/commercial public use, withdrawals and no identity transfer; record its SHA-256.
5. A private location/property permission or recorded none-required finding and SHA-256. No bystanders/minors/private conversations.

The receipt must use **exact keys and types** defined in `human_motion_reference_intake.py` (`ROOT`, `SOURCE`, `SETUP`, `MOTION`, `CHECKPOINT`, `INTERVAL`, `RIGHTS`). The synthetic, fake-by-design test fixture in `tests/test_human_motion_reference_intake.py` demonstrates the full structure; it is **not a reusable consent assertion**. Required fields include:

| Receipt section | Required evidence/control |
| --- | --- |
| Root | schema version 1, opaque capture ID, UTC capture time, IANA recording time zone, `EXPERIMENTAL_NOT_FORM_APPROVED`, `HOLD_FOR_CHARLES_EXACT_VIDEO_REVIEW` |
| `source` | private locator; 64-digit lowercase original SHA-256; byte count, codec, coded geometry, reported and measured FPS rationals, decoded frame count, original duration/rotation; named camera-original reviewer and affirmative unmodified-original attestation |
| `setup` | camera model and named physical camera side; explicitly `MANUALLY_VERIFIED` locked camera, focus/exposure/white balance, head/shoe/hand margins, side angle, static background, contact plane, no bystanders/minors/conversations |
| `human_motion_evidence` | named reviewer and UTC review time, separately rehashed private review artifact, nine **ordered** named frame/PTS/support/physical-limb records A0/B0/C0/D0/A1/B1/C1/D1/A2, four individually named first/last frame and PTS intervals, all-frames visibility/anatomy verification, technical `PASS`, form/safety `NOT_EVALUATED` |
| `rights` | adult and dated signature assertions, named consent reviewer/time, separate release and location evidence hashes, explicit filming/analysis/derivative/public-use permission, provider list exactly `["Google Flow"]` for this version, consent withdrawal terms, motion-only purpose, **false** for likeness/voice/biometric transfer and liveness testing |

The listed manual attestations **cannot be proven by a JSON claim**. A named reviewer, the actual independently hashed review document and signed release are mandatory, and the owner must still check their authenticity, legal scope and the actual content before any provider upload. The tool verifies their **bytes**, not the truth or legal sufficiency of what a human wrote. Missing, unknown, unsigned, ambiguous or unavailable evidence fails closed.

## Private offline command

```bash
python3 -m photo_motion.human_motion_reference_intake \
  --receipt /private/.../capture-receipt.json \
  --source /private/.../camera-original.mov \
  --review-evidence /private/.../named-frame-review.pdf \
  --release /private/.../signed-adult-performer-release.pdf \
  --location-evidence /private/.../location-permission-finding.pdf
```

The CLI prints a **redacted machine-readable decision**, with neither private paths nor names, and exits `0` only for `CAPTURE_REFERENCE_CANDIDATE`, otherwise `2`. It refuses symlink-based or Git-contained inputs. It independently rehashes all four evidence files, probes native codec/geometry/FPS, decodes the **entire camera-original video** with ffmpeg error escalation, inspects **every** frame's PTS for near-constant 59.94/60fps timing, verifies receipt/frame count/duration agreement, exact phase order and timing, distinct ≥2-frame flight windows and physical limb assignments. A claimed visual annotation is still a **human claim**, not algorithmic pose detection.

Do not save console captures containing private shell paths, raw footage, releases or actual names to Git. Keep failure receipts, frame evidence and corrective actions in the **existing private photographic QA/production record**. A fail-closed result is `NOT_EVALUATED` (including confirmed defects); the field capture protocol can separately classify a proven defective take as `RETAKE_REQUIRED`. Never equate this tool's disposition to final instructional acceptance, provider authorization or public release.

Run synthetic regressions with `python3 -m unittest photo_motion.tests.test_human_motion_reference_intake`. Only the test harness injects a synthetic inspector and fabricated review/rights bytes; the CLI always performs **real** ffprobe/ffmpeg checks. There is currently **no genuine adult reference input** to test or propose for generation.
