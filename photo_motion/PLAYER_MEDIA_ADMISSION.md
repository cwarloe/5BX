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

The schema is deliberately restricted to the Chart 1 actions with independently mapped photographic contracts: `pushup` (exercise 4, 60-second slot), `run` (exercise 5, 40-second run segment), and `scissor` (exercise 5, 5-second jump segment). Expand only alongside a verified player action and a corresponding motion contract. Although run and scissor are both Chart 1 exercise 5, they are **different motions**; the QA contract's `movement_type` must match the requested action. A successful review of one never approves the other. **Known structural gap:** the existing canonical handoff has just **one current QA record per chart/exercise**, so it cannot represent both approved action-specific clips for Chart 1 Exercise 5 simultaneously. Future canonical QA governance must decide how to represent both under its own authority, before either can enter the combined player registry. Do not create a second approval table or silently duplicate the existing `DONE` marker.

Run read-only from repository root, with Python 3.11+ and `ffprobe` installed:

```bash
python3 -m photo_motion.player_media_gate /private/candidate-manifest.json --repo-root .
```

Output includes the recalculated content SHA-256, decoded stream properties and frame count, a `full_stream_decode: PASS` field only after a fatal-on-error full video-stream decode, matching canonical QA note path (if valid), technical blockers, `owner_authentication: NOT_EVALUATED`, `historical_diagnostic_integrity: NOT_EVALUATED`, `delivered_url_byte_integrity: NOT_EVALUATED`, `admission: HOLD`, and an **empty** `player_manifest`. The command always exits nonzero because it cannot authenticate owner acceptance; a report saying `technical_evidence: PASS` means only that offline pre-authorization checks matched, **never** that the recorded reviewer, unaltered historical denylist, delivered URL bytes or human form acceptance were independently verified. Do not wire a build to deploy on `technical_evidence: PASS` alone. Running the command requires no private-video transformation.

For synthetic regression coverage:

```bash
python3 -m unittest photo_motion.tests.test_player_media_gate -v
```

The tests create short `ffmpeg` videos and fabricated QA records in temporary directories. Their claimed `cwarloe / ACCEPT` field is intentionally **fake test data** and proves why the offline gate must stay on HOLD. Test fixtures are never a mechanism for production approval.

## What exact-version matching checks

1. Candidate schema has no arbitrary owner-approval field, action is mapped to a known photographic motion, and declared revision is nonempty.
2. Actual private file is an MP4 **outside Git**, its recalculated SHA-256 equals the manifest, its `ffprobe` width, height, frame rate, duration, codec, audio count, and decoded frame count all match, and H.264 has **zero audio streams**. A full `ffmpeg` video decode with fatal decoder errors rejects corrupt frames that a container probe or phase-frame spot check might miss. Three timings must agree within the browser player's 1 ms tolerance: **declared duration versus native media duration**, **declared frame count/FPS versus declared duration**, and **native decoded frame count/FPS versus native duration**. The broader motion-spec planning tolerance does not override this playback intake rule: a native five-second MP4 mislabeled as 4.99 seconds, or declared with an FPS that skews its frame-count duration, remains a technical HOLD. A second SHA-256 after `ffprobe` detects ordinary source replacement during inspection; for future release, work from a truly immutable local input snapshot as well. The gate compares candidates against the currently recorded failed original Flow **#20 and #21** diagnostic hashes by loading their existing notes, without duplicating full source digests in new code. **Important limitation:** a syntactically valid but falsified edit to those mutable notes can remove a historical failed hash from the filter. This is **not a trustworthy historical denylist** until independently anchored to immutable, authenticated evidence; the regression test demonstrates the weakness while keeping release on HOLD.
3. The player slot length is read from `game/src/lib/levels.ts`, not from candidate wishes. Only `repeat_full_clip` is implemented: the native clip must fit the player slot by an exact whole number of repeats. No silent trim, five/six-second speed shift, fade, freeze-tail or newly guessed temporal policy is accepted. Today the six-second scissor pilot conflicts with the **five-second** runtime slot and is held until an explicitly reviewed, versioned plan resolves the discrepancy.
4. The existing `sprites/kit/photo_workflow.py` parser must report **no QA validation errors**, and exactly one **`DONE`** record for chart/exercise. The current detailed QA note's revision, video hash, URL, independently reviewed form/motion checks, inspection hash, canonical inventory link and `owner_decision.video_sha256` must align. The associated photographic motion contract must have the correct action's `movement_type` and declared native duration. A `READY_FOR_REVIEW`, `BLOCKED`, missing, duplicate or stale QA marker cannot pass.

This is an **integrity and evidence-consistency** check. A git-controlled note, inventory row, or static `owner_decision` JSON does **not** prove the listed person actually reviewed or accepted the video. Nor does `ffprobe` assess accurate anatomy, correct repetitions, identity, or loop seam. Those remain separately documented human QA responsibilities.

## Future authenticated owner verification (not implemented)

To admit a final clip without making a parallel approval database, add a narrowly scoped trusted **read-through owner-event verification service** at build time:

1. Re-read the *canonical existing QA note*, not a new ledger, to get the exact `DONE` revision, video URL/SHA, reviewer decision link and motion contract. Reject any note that the existing `photo_workflow` validation does not recognize.
2. Resolve the QA note's recorded HTTPS GitHub review comment or PR event via an **authenticated GitHub API**, with the correct owner/repository/issue scope. Confirm that the actual event author is the GitHub account `cwarloe` (from trusted API identity, not JSON text), that the event exists now and records a clear exact-version **ACCEPT** with the full media SHA-256 and revision. Require matching actual account identity, revision and content hash; do not accept producer-authored comments, username-shaped strings, stale edits or links to another take.
3. Compare the retrieved event's identifier/URL and timestamp to the canonical note's evidence link and decision timestamp. GitHub comments are editable; an event ID alone is **not** proof of immutable acceptance. Use up-to-date authenticated API data on every admission build; if unavailable, edited, retracted, inconsistent or ambiguous, **fail closed**. If the owner workflow requires a stricter signed/immutable review artifact, use that instead.
4. **Bind the verified bytes to actual delivery, not just a declared URL.** An arbitrary HTTPS review URL string can change or serve different bytes than the locally inspected MP4. With the owner's separate publication authorization, copy the exact verified final bytes into permitted immutable/content-addressed delivery storage, verify the delivered bytes' SHA-256 via a trusted readback, and bind the approved revision/hash to that exact player asset. If a URL cannot provide that guarantee, keep the clip on HOLD. The current offline tool neither fetches nor publishes external media.
5. Only a future production implementation **with that trusted event verification, byte-to-delivery binding, and independent form/release process** may generate the final `ApprovedPhotoClip` export for the photographic player. Its proposed shape is `{schemaVersion:1, clips:{scissor:{url,sha256,mediaType:'video/mp4',revision}}}`; its export should be empty on any failed or unavailable evidence. No fallback to hardcoded URLs, diagnostics, synthetic fixture approval, cartoon sprites, or public sample media.

The trusted verifier is intentionally **absent** today. The owner retains final-declaration authority, and engineering can progress independently on playback, timing, tests, and evidence capture while all real clips remain held.
