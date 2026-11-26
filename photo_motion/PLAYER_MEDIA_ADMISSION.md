# Photographic player-media admission: fail closed

**Status: engineering preflight only. The repository contains no owner-authenticated, admitted photographic exercise clip.** The public player registry stays `{ "schemaVersion": 1, "clips": {} }`; the historical cartoon sprite path is not a photographic approval fallback.

This offline checker verifies private MP4 bytes and metadata against an exact candidate, the active Chart 1 player's timing, the relevant versioned photographic motion contract, and the **existing** `5bx-production` QA note. It does not generate images or video, spend Flow credits, upload media, invent an approval, publish anything, or maintain a separate approval database.

## Offline candidate manifest

Example is **schema only**, not an approved clip. Create this JSON privately for an actual candidate, replacing every illustrative value with measured values. Never commit raw media or its private location to Git.

```json
{
  "schema_version": 1,
  "chart": 1,
  "exercise": 5,
  "action": "scissor",
  "revision": "exact-existing-QA-revision",
  "video": {
    "local_path": "/private/actual-final-silent.mp4",
    "url": "https://example.org/private-review-link",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "media_type": "video/mp4",
    "duration_seconds": 5,
    "width": 1280,
    "height": 720,
    "fps": 24,
    "codec": "h264",
    "audio_stream_count": 0,
    "frame_count": 120
  },
  "playback": {
    "mode": "repeat_full_clip",
    "runtime_slot_seconds": 5
  }
}
```

The schema is deliberately restricted to the Chart 1 actions with independently mapped photographic contracts: `pushup` (exercise 4, 60-second slot), `run` (exercise 5, 40-second run segment), and `scissor` (exercise 5, 5-second jump segment). Expand only alongside a verified player action and a corresponding motion contract. Although run and scissor are both Chart 1 exercise 5, they are **different motions**; the QA contract's `movement_type` must match the requested action. A successful review of one never approves the other.

Run read-only from repository root, with Python 3.11+ and `ffprobe` installed:

```bash
python3 -m photo_motion.player_media_gate /private/candidate-manifest.json --repo-root .
```

Output includes the recalculated content SHA-256, decoded stream properties and frame count, matching canonical QA note path (if valid), technical blockers, `owner_authentication: NOT_EVALUATED`, `admission: HOLD`, and an **empty** `player_manifest`. The command always exits nonzero because it cannot authenticate owner acceptance; a report saying `technical_evidence: PASS` means only that offline pre-authorization checks matched, **never** that the recorded reviewer or human form acceptance was independently verified. Do not wire a build to deploy on `technical_evidence: PASS` alone. Running the command requires no private-video transformation.

For synthetic regression coverage:

```bash
python3 -m unittest photo_motion.tests.test_player_media_gate -v
```

The tests create short `ffmpeg` videos and fabricated QA records in temporary directories. Their claimed `cwarloe / ACCEPT` field is intentionally **fake test data** and proves why the offline gate must stay on HOLD. Test fixtures are never a mechanism for production approval.

## What exact-version matching checks

1. Candidate schema has no arbitrary owner-approval field, action is mapped to a known photographic motion, and declared revision is nonempty.
2. Actual private file is an MP4 **outside Git**, its recalculated SHA-256 equals the manifest, its `ffprobe` width, height, frame rate, duration, codec, audio count, and decoded frame count all match, and H.264 has **zero audio streams**. The failed original Flow videos **#20 and #21** are explicitly denied by loading their existing diagnostic QA notes, without duplicating their private source digests in the new code.
3. The player slot length is read from `game/src/lib/levels.ts`, not from candidate wishes. Only `repeat_full_clip` is implemented: the native clip must fit the player slot by an exact whole number of repeats. No silent trim, five/six-second speed shift, fade, freeze-tail or newly guessed temporal policy is accepted. Today the six-second scissor pilot conflicts with the **five-second** runtime slot and is held until an explicitly reviewed, versioned plan resolves the discrepancy.
4. The existing `sprites/kit/photo_workflow.py` parser must report **no QA validation errors**, and exactly one **`DONE`** record for chart/exercise. The current detailed QA note's revision, video hash, URL, independently reviewed form/motion checks, inspection hash, canonical inventory link and `owner_decision.video_sha256` must align. The associated photographic motion contract must have the correct action's `movement_type` and declared native duration. A `READY_FOR_REVIEW`, `BLOCKED`, missing, duplicate or stale QA marker cannot pass.

This is an **integrity and evidence-consistency** check. A git-controlled note, inventory row, or static `owner_decision` JSON does **not** prove the listed person actually reviewed or accepted the video. Nor does `ffprobe` assess accurate anatomy, correct repetitions, identity, or loop seam. Those remain separately documented human QA responsibilities.

## Future authenticated owner verification (not implemented)

To admit a final clip without making a parallel approval database, add a narrowly scoped trusted **read-through owner-event verification service** at build time:

1. Re-read the *canonical existing QA note*, not a new ledger, to get the exact `DONE` revision, video URL/SHA, reviewer decision link and motion contract. Reject any note that the existing `photo_workflow` validation does not recognize.
2. Resolve the QA note's recorded HTTPS GitHub review comment or PR event via an **authenticated GitHub API**, with the correct owner/repository/issue scope. Confirm that the actual event author is the GitHub account `cwarloe` (from trusted API identity, not JSON text), that the event exists now and records a clear exact-version **ACCEPT** with the full media SHA-256 and revision. Require matching actual account identity, revision and content hash; do not accept producer-authored comments, username-shaped strings, stale edits or links to another take.
3. Compare the retrieved event's immutable identifier/URL and timestamp to the canonical note's evidence link and decision timestamp. Use up-to-date authenticated API data on every admission build; if unavailable, edited, retracted, inconsistent or ambiguous, **fail closed**. If the owner workflow requires a stricter signed/immutable review artifact, use that instead. A SHA-only comment still cannot certify the actual played file unless the byte verification in step 2 above independently succeeds.
4. Only a future production implementation **with that trusted event verification and independent form/release process** may generate the final `ApprovedPhotoClip` export for the photographic player. Its proposed shape is `{schemaVersion:1, clips:{scissor:{url,sha256,mediaType:'video/mp4',revision}}}`; its export should be empty on any failed or unavailable evidence. No fallback to hardcoded URLs, diagnostics, synthetic fixture approval, cartoon sprites, or public sample media.

The trusted verifier is intentionally **absent** today. The owner retains final-declaration authority, and engineering can progress independently on playback, timing, tests, and evidence capture while all real clips remain held.
