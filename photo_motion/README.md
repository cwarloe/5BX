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

## Exercise contracts

| Contract | Critical invariant | Known unresolved evidence |
| --- | --- | --- |
| `specs/chart1-scissor-jump.json` | **Two** genuine airborne exchanges, opposite physical leg/arm assignments, full recovery to original stance | V7 is a *conditional photographic still*, not verified video. Existing four panels lack a separately proven second flight. Orange/teal marks track generated near/far limbs, **not proven anatomical left/right** from the reference film. |
| `specs/chart1-kneeling-pushup.json` | Both palms and knees planted, elbows bend together, full up/down/up cycle | Existing blue-shirt Flow video 10 remains a review candidate, not final form-approved. |

The remaining Chart 1 photo contracts cover toe touching, **partial** sit-up, alternating physical leg raise, and low stationary running. They use separate exercise-specific checks in `extended_contract.py` and are included by the same wildcard validation command. See [`CHART1_MOTION_CONTRACTS.md`](CHART1_MOTION_CONTRACTS.md) for source-specific assumptions and unresolved still/video evidence. The experimental six-second run timing is not a replacement for the level-dependent prescribed cadence in `data/5bx-charts.json`.

Each spec contains planned phase times, support points, camera/identity instructions, and the source documents to consult. Phase times are **targets** for video generation/inspection, not assertions that the actual video will obey them. A plan that passes `validate` is a coherent *request*, not a valid clip.
For Chart 1 scissor jumps, the movement authority is the **original booklet wording**, not the archival 1959 film (whose documented jump footage depicts other chart exercises). The six-second test duration is an experimental clip target, not a source-mandated scissor-jump cadence.

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

The first actual-video engineering smoke run is documented in [`diagnostics/video10-kneeling-pushup-2026-11-26.md`](diagnostics/video10-kneeling-pushup-2026-11-26.md). It checked the original blue-shirt Flow video 10 and found a contact/loop registration issue worth measuring before any approval. The raw private MP4 and extracted frames are not committed here.

## Additional real-video diagnostics

The following optional diagnostics are independent of the generated pose sheets. They preserve the original MP4 and never issue a form or release verdict.

| Tool | What it measures | Key limitation |
| --- | --- | --- |
| [`contact_qa.py`](CONTACT_QA.md) | Drift of named planted palms/knees/feet, with source MP4 hash, timestamps and overlay frames | Requires real anatomical landmark annotations; it does **not** find or verify joints automatically |
| [`temporal_qa.py`](TEMPORAL_QA.md) | Every decoded frame for sustained stillness, sudden visual changes, irregular frame timing and background motion | Pixel differences cannot prove movement correctness; legitimate holds are normal |
| [`identity_qa.py`](IDENTITY_QA.md) | Color/brightness/texture and framing of explicitly located shirt/shorts/hair/face patches | Requires consistent, independently identified regions; cannot certify a person's identity |

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
