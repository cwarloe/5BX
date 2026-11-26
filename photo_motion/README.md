# Photographic exercise motion — current development path

This is the active engineering path for **real 35 mm-style photographic 5BX exercise videos**. It is independent of the historical cartoon sprite pipeline under `video/` and `sprites/kit/`. Nothing in this package imports, converts, recolors or renders cartoon artwork.

The tool takes a stricter approach to reproducibility:

1. Define **what physical movement must occur** in a versioned JSON contract, before generating a video.
2. Check the planned frame/phase order, tracked limb identity, planted contacts and complete recovery automatically.
3. Generate an **actual video** using the separate photo identity reference and movement reference. The contract can produce a repeatable *draft prompt*, but it does not call a paid image/video model.
4. For the actual generator run, save the **verbatim prompt**, provider/model/settings and source-image identity. Keep outputs and source media in the existing private 5BX video archive and put safe source metadata in the existing experiment record.
5. Inspect the output MP4 frame by frame at planned phase timestamps. Save its content hash, frame samples, phase contact sheet, basic codec information and a start/end screen-space comparison.
6. Have a real person verify form, anatomical limb continuity, camera stability and normal-speed motion. **Never promote an automatic technical PASS into exercise-form approval.**

The JSON contracts and CLI are development controls, **not a second Kanban board, traveler or approval database**. The process advisor's existing review records remain the status authority.

**Pre-publication privacy preflight:** before a photographic engineering PR,
stage only intended source changes and run
`python3 -m photo_motion.privacy_preflight --cached --check`. It inspects
**newly added diff lines**, not historical unchanged QA evidence or deleted
lines. It holds explicit Google Drive/Flow locators, labeled Drive file IDs,
private-storage URIs and uninspectable binary changes; output prints a rule
and diff position **without displaying the matched identifier**. An exact
SHA-256 alone is allowed because content hashes are needed for reproducibility.
The lightweight PR CI check repeats this scan against the event's exact base
commit, with full Git history to handle GitHub's synthetic merge checkout.
Missing base data is a **HOLD**, never an empty-diff PASS. Use only synthetic
fixtures in tests; keep private source links and media in the controlled
review archive. This narrowly scoped pattern guard cannot detect every
possible secret, obfuscated URL, identity leak or private photographic image;
it is **not** a privacy certification or publication permission.

**Photographic player-media admission:** the read-only
[`player_media_gate.py`](PLAYER_MEDIA_ADMISSION.md) cross-checks a proposed
private MP4's exact bytes, metadata, active-player slot timing and canonical
QA `DONE` evidence. It **never** authenticates an owner from static JSON,
emits a nonempty playback registry or authorizes release. The six-second
scissor pilot cannot silently fit a five-second runtime slot.

**Agent work/owner handoff is now executable:** read the repository's
[`AGENTS.md`](../AGENTS.md), maintain a `5bx-production` comment inside the
**existing detailed photographic QA note**, and run
`python3 sprites/kit/photo_workflow.py --repo-root . --check` before a PR.
The command enforces source evidence and a two-active-exercise limit on
**registered** jobs. A fully inspected video becomes `READY_FOR_REVIEW` and
frees a producer slot while Charles decides whether to use it; `DONE` is
reserved for Charles's exact-version acceptance. No existing clip is promoted
merely because a prompt, plan or automated inspect command succeeded. See
the [handoff contract](../sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md#executable-handoff-and-owner-queue).

## Quick start

From repository root, with Python 3.11+, ffmpeg/ffprobe, and Pillow installed:

```bash
python3 -m photo_motion validate photo_motion/specs/*.json
python3 -m unittest discover -s photo_motion/tests -v
python3 -m photo_motion prompt photo_motion/specs/chart1-scissor-jump.json
python3 -m photo_motion inspect photo_motion/specs/chart1-scissor-jump.json /path/to/real-scissor.mp4 --out /path/to/qa-scissor
```

The `inspect` command leaves the source video untouched and writes `inspection.json`, a `phase_contact_sheet.png` and individual frame PNGs into the explicitly provided output directory. A real 6-second clip is needed; a four-panel contact-card still **is not video**.
Use a **new output directory for every inspection**. Reusing an existing directory is rejected to prevent accidental overwrites of earlier frame evidence.

For the V6 photographic scissor pilot, **before reserving or spending Flow
credits**, run the exact original-card/prepared-PNG/transform-manifest binding
check in [`V6_PRECREDIT.md`](V6_PRECREDIT.md). The experiment reservation now
requires that verified binding and the identical uploaded start-frame bytes;
the check does not approve the resulting exercise video.

If the original V6 composite is unavailable, do **not** relax that gate.
For the separately authorized archival-source experiment, use the
[`V7 direct A+C prepared-pair authority`](V7_DIRECT_PAIR_PRECREDIT.md): it
pins both surviving private photographic PNGs directly while explicitly
declining to certify historical V6 parent crop/transform claims. Its movement
spec is `specs/chart1-scissor-jump-v7-prepared-pair.json`.

## Exercise contracts

| Contract | Critical invariant | Known unresolved evidence |
| --- | --- | --- |
| `specs/chart1-scissor-jump.json` | **Two** genuine airborne exchanges, opposite physical leg/arm assignments, full recovery to original stance | V7 is a *conditional photographic still*, not verified video. Existing four panels lack a separately proven second flight. Orange/teal marks track generated near/far limbs, **not proven anatomical left/right** from the reference film. |
| `specs/chart1-kneeling-pushup.json` | Both palms and knees planted, elbows bend together, **gentle chest-floor touch** at low point per booklet, full up/down/up cycle | Existing blue-shirt Flow video 10 remains a review candidate, not final form-approved; provisional near-knee contact drift requires independent confirmation. |

The remaining Chart 1 photo contracts cover toe touching, **partial** sit-up, alternating physical leg raise, and low stationary running. They use separate exercise-specific checks in `extended_contract.py` and are included by the same wildcard validation command. See [`CHART1_MOTION_CONTRACTS.md`](CHART1_MOTION_CONTRACTS.md) for source-specific assumptions and unresolved still/video evidence. The experimental six-second run timing is not a replacement for the level-dependent prescribed cadence in `data/5bx-charts.json`.

Each spec contains planned phase times, support points, camera/identity instructions, and the source documents to consult. Phase times are **targets** for video generation/inspection, not assertions that the actual video will obey them. A plan that passes `validate` is a coherent *request*, not a valid clip.
For Chart 1 scissor jumps, the movement authority is the **original booklet wording**, not the archival 1959 film (whose documented jump footage depicts other chart exercises). The six-second test duration is an experimental clip target, not a source-mandated scissor-jump cadence.

If a future generator experiment truly needs *live-action motion conditioning*,
use the [first-party adult movement-reference field protocol](FIRST_PARTY_SCISSOR_MOTION_CAPTURE.md).
It requires a consented adult demonstration of two whole A→airborne→C→airborne→A
cycles, fixed side-on full-body framing, explicit rights for private AI input,
and byte-verified raw-source evidence. It is a **capture protocol only**, not
new footage, permission to reuse a stranger's video or approval to transfer a
real demonstrator's face/biometrics to the target character.

## Pin the real generator inputs

The prompt command prints a **proposed** tool-neutral prompt. If you use it in Google Flow or another tool, preserve the text **actually submitted**, including any manual edits. Do not mislabel an automatically generated draft as the submitted text.

When an MP4 comes back, the optional `--recipe /path/to/run.json` argument attaches the run's provenance to its inspection record. A recipe file beside `submitted.txt` can look like:

```json
{
  "schema_version": 1,
  "provider": "Google Flow",
  "model": "replace with exact model shown on run",
  "generation_id": "replace with actual run/editor ID",
  "submitted_prompt_file": "submitted.txt",
  "input_images": [
    {"role": "start-frame", "locator": "replace with real immutable reference location", "sha256": null}
  ],
  "settings": {"duration_seconds": 6, "seed": null}
}
```

Use the real model/asset IDs and values. Unknown seed/settings remain `null`; never invent them. If the file exists locally, inspection calculates and verifies its SHA-256. If it exists only in Flow/Drive and no hash is available, inspection reports incomplete provenance. An unavailable image cannot be claimed recoverable just because a URI was recorded.

```bash
python3 -m photo_motion inspect photo_motion/specs/chart1-scissor-jump.json /path/to/actual.mp4 --recipe /path/to/run.json --out /path/to/qa-scissor
```

Each inspection records the exact MP4 SHA-256, contract SHA-256, exact submitted prompt SHA-256 (if supplied), provider/model/known settings, original frame references, codec, FPS, phase sampling times, and any technical warnings. This makes deterministic **downstream inspection** repeatable and preserves the experimental recipe. AI video synthesis itself may be nondeterministic even when all known inputs match.

Before extracting the sparse phase samples, inspection decodes the entire
video stream with fatal decoder-error handling. This catches damaged frames
between target timestamps that a successful container probe or contact sheet
would miss. It is a read-only technical intake check and still cannot certify
motion, anatomy, camera stability or exercise form.

### Provider/model/prompt drift canary

The offline [`drift_canary.py`](DRIFT_CANARY.md) compares two existing immutable
experiment intents and optionally the corresponding real-video inspection
reports. It flags changes in model, input identities, source transforms,
prompt, contract, settings, cost estimates, and technical media format. It
never calls a paid generator or approves form. For example:

```bash
python3 -m photo_motion.drift_canary compare /path/to/old-intent.json /path/to/new-intent.json --json
```

Exit `0` means only *configuration* is unchanged, not that AI output is stable;
nonzero means requalification or bad evidence. A genuinely useful drift test
still needs a newly generated canary MP4 with independently inspected motion
and identity; see [the limitations and comparison rules](DRIFT_CANARY.md).

### Audio as an explicit delivery constraint

Add `"audio_policy": "forbid"` to a motion spec when its video must contain **no audio stream**, not even a silent one. The field is optional; omitted contracts use `"unspecified"` and do not fail just for containing audio. Inspection records stream count/codecs and read-only decoded mean/peak dBFS metadata. If a forbidden stream exists, it adds a technical warning even for digitally silent AAC. A finite decoded peak indicates nonzero PCM samples, **not necessarily audibility**. If the decoder cannot measure a track, the file still fails the forbidden-stream condition. The original source MP4 is never altered, and the inspector never marks form or release approved. Remove audio only from a separate, documented derived delivery asset if the owner chooses to use the clip.

For a motion-valid candidate whose generator added unwanted audio, use the
independent, [bitstream-verifying silent derivative command](SILENT_DERIVATIVE.md).
It makes a silent review copy and immutable source/output manifest, without
rewriting the raw generator's failed audio-policy result or approving exercise
form. It never spends generation credits.

If a later provider experiment supplies separate photographic A→C and C→A
**actual video** segments, the experimental
[`segment_join.py`](SEGMENT_JOIN.md) command can create a strictly verified
no-fade stream-copy preview. It rejects changed encoded packets, altered
decoded frames, unsafe C joins, incompatible stream properties and unexpected
audio. It cannot certify the scissor exercise or the outer loop seam, and
it does not call a generator or spend credits.

The separately versioned [V8 Frames-to-Video endpoint pilot](V8_FRAMES_SEGMENTS.md)
binds two 3-second segment requests to the same V7-authenticated exact A/C
source bytes without weakening the six-second, two-flight V7 cycle contract.

The distinct [V9 zero-credit image-outpaint pilot](V9_OUTPAINT_SOURCE.md)
authenticates only an **original A or C photographic PNG** before a single
experimental Flow image edit. Its generated stills are unreviewed derived
images, not verified V7/V8 motion sources or approved exercise videos.

The first actual-video engineering smoke run is documented in [`diagnostics/video10-kneeling-pushup-2026-11-26.md`](diagnostics/video10-kneeling-pushup-2026-11-26.md). It checked the original blue-shirt Flow video 10 and found a contact/loop registration issue worth measuring before any approval. The raw private MP4 and extracted frames are not committed here.

## Additional real-video diagnostics

The following optional diagnostics are independent of the generated pose sheets. They preserve the original MP4 and never issue a form or release verdict.

| Tool | What it measures | Key limitation |
| --- | --- | --- |
| [`contact_qa.py`](CONTACT_QA.md) | Drift of named planted palms/knees/feet, with source MP4 hash, timestamps and overlay frames | Requires real anatomical landmark annotations; it does **not** find or verify joints automatically |
| [`temporal_qa.py`](TEMPORAL_QA.md) | Every decoded frame for sustained stillness, sudden visual changes, irregular frame timing and background motion | Pixel differences cannot prove movement correctness; legitimate holds are normal |
| [`identity_qa.py`](IDENTITY_QA.md) | Color/brightness/texture and framing of explicitly located shirt/shorts/hair/face patches | Requires consistent, independently identified regions; cannot certify a person's identity |
| [`framing_qa.py`](FRAMING_QA.md) | Full-frame manual head/shoe boundary annotations bound to exact MP4, decoded frame and identity-master hashes | **No automatic person detector**; a `PASS_MANUALLY_ATTESTED` requires all decoded frames, while observed clipping fails early and missing evidence remains `NOT_EVALUATED` |
| [`scissor_phase_qa.py`](SCISSOR_PHASE_QA.md) | Manual every-frame orange/teal physical-marker positions, shoe contact and two distinct flights around the opposite grounded pose | Frame hashes/observations do not prove anatomy or safety; `PASS_MANUALLY_ATTESTED` certifies only the stipulated phase evidence |

For example, after saving the true input MP4 and a contact-annotation file, run `python3 -m photo_motion.contact_qa /path/to/contacts.json --video /path/to/input.mp4 --out /path/to/new-contact-qa-dir`. For temporal analysis use `python3 -m photo_motion.temporal_qa /path/to/input.mp4 --report /path/to/new-report.json`. Appearance comparison accepts a manifest of reference and frame image regions, documented in `IDENTITY_QA.md`. Always choose a **new** destination for each run: existing output files are deliberately never replaced.

## What automated QA can and cannot prove

- **Can check:** valid planned phase ordering, complete scissor flight/landing topology, opposite track ownership in the plan, fixed push-up contact points in the plan, exact input/output hashes, MP4 decoding, FPS/duration and reproducibly sampled frames.
- **Cannot yet check:** whether a generated *video* actually follows those limb constraints frame by frame, whether a camera subtly moves, real anatomical left/right provenance, exercise-form safety, or identity drift without human review. A low first/last pixel error is not proof of a good loop; a test pattern can score well while demonstrating no exercise at all.
- **Release:** remain EXPERIMENTAL/REVIEW/HOLD until Charles explicitly approves the exact candidate. Current contracts intentionally cannot set `APPROVED` from code.

## Change protocol for engineering

1. When a defect appears, add a failing test of the *requirement* before changing the motion contract or validation logic.
2. Change one declared movement assumption or implementation behavior; retain source and output hashes and keep the failed example as diagnostic evidence in the existing archive.
3. Run the whole contract suite plus `inspect` on a representative **actual photographic MP4**, then visually review all intermediate movement and the final loop seam.
4. Record what changed and its observed result in the existing numbered photo batch notes. Do not replace the original approved identity anchor with a frame descended from a previous exercise's generated video; this accumulated identity drift in earlier experiments.
5. Only after a specific video passes human form/motion review should it be considered for Mixer integration. There is no automatic publication step in this tool.

The existing photographic standard work is in [`sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md`](../sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md) and the grounded scissor-marker experiments are in [`sprites/docs/photo_batches/2026-11-26/COLOR_MARKER_POSE_CONTROL_PLAYBOOK.md`](../sprites/docs/photo_batches/2026-11-26/COLOR_MARKER_POSE_CONTROL_PLAYBOOK.md). Their verdicts supersede any earlier generic animation advice.

For a *later*, explicitly requalified framing-only experiment, the
[`pair_reframe.py`](PAIR_REFRAME.md) utility can resize a pair of byte-pinned
photographic A/C references together, preserving both originals and recording
every central-resize and reflected-border pixel operation. Its derived images
are not substitutes for any V6/V7 verified-source authority, and no extra Flow
credits or video generation are triggered by preparation.
