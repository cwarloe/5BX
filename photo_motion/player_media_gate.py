"""Read-only, fail-closed admission preflight for *photographic* player clips.

This does not authorize a release. In particular, a Git-controlled QA note
claiming ``cwarloe / ACCEPT`` is not proof of an authenticated owner action.
The only public-player registry produced here is deliberately empty. See
PLAYER_MEDIA_ADMISSION.md for a future authenticated integration boundary.
"""

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

from .video_qa import _verify_full_video_decode, file_sha256, probe


REPO_ROOT = Path(__file__).resolve().parents[1]
# Source-of-truth failed media digests are already in these diagnostic QA
# notes. Read them in place, never copy sensitive full hashes into new code.
FAILED_DIAGNOSTIC_NOTES = (
    "photo_motion/diagnostics/video20-low-stationary-run-2026-11-26.md",
    "photo_motion/diagnostics/video21-scissor-v6-2026-11-26.md",
)
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
ACTION_MOVEMENT_TYPES = {
    (1, 4, "pushup"): "kneeling_pushup",
    (1, 5, "scissor"): "scissor_jump",
    (1, 5, "run"): "stationary_run_low",
}
MEDIA_KEYS = {"local_path", "url", "sha256", "media_type", "duration_seconds", "width",
              "height", "fps", "codec", "audio_stream_count", "frame_count"}
ROOT_KEYS = {"schema_version", "chart", "exercise", "action", "revision", "video", "playback"}
PLAYBACK_KEYS = {"mode", "runtime_slot_seconds"}
EPS_SECONDS = 0.02
EPS_FPS = 0.01
PLAYER_TIMING_EPS_SECONDS = 0.001  # Must not exceed game/src/lib/photo-video.ts tolerance.


def _source_runtime(repo_root, action):
    """Re-read the shipped player timing rather than trusting candidate timing.

    It intentionally rejects unexpected source layout instead of continuing
    with stale duplicated timing constants after a player refactor.
    """
    source = (Path(repo_root) / "game/src/lib/levels.ts").read_text(encoding="utf-8")
    if action in ("scissor", "run"):
        symbol = "SCISSOR_SECONDS" if action == "scissor" else "JOG_SECONDS"
        matches = re.findall(rf"export const {symbol}\s*=\s*(\d+(?:\.\d+)?)\s*;", source)
        if len(matches) != 1:
            raise ValueError(f"cannot determine trusted {symbol} in active player")
        return float(matches[0])
    if action == "pushup":
        # The Chart 1 exercise list declares its seconds before its action.
        matches = re.findall(r'\{\s*name:\s*"KNEE PUSH-UPS",\s*seconds:\s*(\d+(?:\.\d+)?),'
                             r'\s*goal:\s*goals\[3\],\s*unit:\s*"REPS",\s*action:\s*"pushup"\s*\}', source)
        if len(matches) != 1:
            raise ValueError("cannot determine trusted Chart 1 pushup duration")
        return float(matches[0])
    raise ValueError("action is not an explicitly supported photographic player slot")


def _decoded_frame_count(video_path):
    outcome = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_frames", "-of", "json", str(video_path)],
        capture_output=True, text=True, check=False)
    if outcome.returncode:
        raise ValueError("ffprobe could not decode/count video frames")
    streams = json.loads(outcome.stdout).get("streams")
    if not isinstance(streams, list) or len(streams) != 1:
        raise ValueError("ffprobe returned no unique video-frame count")
    frames = streams[0].get("nb_read_frames")
    if not isinstance(frames, str) or not frames.isdecimal() or int(frames) <= 0:
        raise ValueError("ffprobe decoded-frame count missing")
    return int(frames)


def _failed_diagnostic_hashes(repo_root):
    """Fail closed if existing #20/#21 QA diagnoses cannot be read faithfully."""
    digests = set()
    for relative in FAILED_DIAGNOSTIC_NOTES:
        raw = (Path(repo_root) / relative).read_text(encoding="utf-8")
        matches = re.findall(r"\| Original SHA-256 \|\s*`([0-9a-f]{64})`", raw)
        if len(matches) != 1:
            raise ValueError("required original FAILED diagnostic hash missing/ambiguous in " + relative)
        digests.add(matches[0])
    if len(digests) != len(FAILED_DIAGNOSTIC_NOTES):
        raise ValueError("failed original diagnostic digests must be distinct")
    return frozenset(digests)


def _canonical_record(repo_root, chart, exercise):
    """Read the *existing* QA source; do not establish an approval ledger."""
    # Existing workflow enforces all five checks, independent reviewers,
    # inventory, owner-decision structure, and one current QA per chart/exercise.
    from sprites.kit import photo_workflow

    snapshot = photo_workflow.collect(repo_root)
    if snapshot["errors"]:
        raise ValueError("canonical QA workflow has validation errors: " + "; ".join(snapshot["errors"]))
    matches = [item for item in snapshot["done"]
               if item["chart"] == chart and item["exercise"] == exercise]
    if len(matches) != 1:
        raise ValueError("exact chart/exercise lacks one valid canonical QA DONE record")
    record = matches[0]
    path = Path(repo_root) / record["source"]
    markers = list(photo_workflow.MARKER.finditer(path.read_text(encoding="utf-8")))
    if len(markers) != 1:
        raise ValueError("canonical QA source must have exactly one current production marker")
    return record, json.loads(markers[0].group(1))


def evaluate(candidate, repo_root=REPO_ROOT):
    """Check candidate bytes, current UI timing and QA source; never admit.

    Return a machine-readable technical report, *not* an approval or video
    registry. No caller-supplied ``owner_approved`` flag is accepted.
    """
    root = Path(repo_root).resolve()
    blockers = []
    verified = {}
    result = {
        "schema_version": 1,
        "admission": "HOLD",
        "form_and_release_approval": "NOT_EVALUATED",
        "owner_authentication": "NOT_EVALUATED",
        "historical_diagnostic_integrity": "NOT_EVALUATED",
        "delivered_url_byte_integrity": "NOT_EVALUATED",
        "technical_evidence": "HOLD",
        "public_release_authorized": False,
        "player_manifest": {"schemaVersion": 1, "clips": {}},
        "verified_video": verified,
        "canonical_qa_source": None,
        "blockers": blockers,
    }
    if not isinstance(candidate, dict):
        result["blockers"].append("candidate manifest must be an object")
        return result
    if set(candidate) != ROOT_KEYS or candidate.get("schema_version") != 1:
        blockers.append("candidate schema/version mismatch or untrusted extra fields")
        return result
    chart, exercise, action = candidate.get("chart"), candidate.get("exercise"), candidate.get("action")
    if (type(chart) is not int or type(exercise) is not int or
            not isinstance(action, str) or
            (chart, exercise, action) not in ACTION_MOVEMENT_TYPES):
        blockers.append("unsupported chart/exercise/action mapping")
        return result
    result.update({"chart": chart, "exercise": exercise, "action": action})
    if not isinstance(candidate.get("revision"), str) or not candidate["revision"].strip():
        blockers.append("candidate revision is absent")
    video, playback = candidate.get("video"), candidate.get("playback")
    if not isinstance(video, dict) or set(video) != MEDIA_KEYS:
        blockers.append("video metadata must contain exactly the declared verification fields")
        return result
    if not isinstance(playback, dict) or set(playback) != PLAYBACK_KEYS:
        blockers.append("playback policy is missing or contains extra fields")
        return result
    if (video.get("media_type") != "video/mp4" or
            not isinstance(video.get("url"), str) or not video["url"].startswith("https://") or
            not isinstance(video.get("sha256"), str) or not SHA256.fullmatch(video["sha256"])):
        blockers.append("video must have an exact lowercase SHA-256, HTTPS URL, and MP4 media type")
    try:
        if isinstance(video.get("sha256"), str) and video["sha256"] in _failed_diagnostic_hashes(root):
            blockers.append("known failed diagnostic #20/#21 original is not an admissible clip")
    except (OSError, ValueError) as exc:
        blockers.append("cannot verify failed diagnostic exclusions: " + str(exc))
    numeric = ("duration_seconds", "width", "height", "fps", "audio_stream_count", "frame_count")
    if (any(type(video.get(k)) not in (int, float) or
            not math.isfinite(video[k]) or video[k] < 0 for k in numeric) or
            any(type(video.get(k)) is not int for k in
                ("width", "height", "audio_stream_count", "frame_count")) or
            not isinstance(video.get("codec"), str) or
            video.get("duration_seconds", 0) <= 0 or video.get("fps", 0) <= 0 or
            video.get("width", 0) <= 0 or video.get("height", 0) <= 0 or
            video.get("frame_count", 0) <= 0):
        blockers.append("video metadata has invalid values")
    if (playback.get("mode") != "repeat_full_clip" or
            type(playback.get("runtime_slot_seconds")) not in (int, float) or
            (isinstance(playback.get("runtime_slot_seconds"), (int, float)) and
             (not math.isfinite(playback["runtime_slot_seconds"]) or
              playback["runtime_slot_seconds"] <= 0))):
        blockers.append("only full-native-duration replay is allowed; no trim/fade/speed alteration")
    if blockers:
        # Malformed input is already a HOLD. Never coerce hostile types when
        # comparing decoded media numbers to the asserted manifest.
        return result
    try:
        trusted_slot = _source_runtime(root, action)
    except (OSError, ValueError) as exc:
        blockers.append(str(exc))
        trusted_slot = None
    if trusted_slot is not None:
        result["trusted_player_slot_seconds"] = trusted_slot
        if abs(playback["runtime_slot_seconds"] - trusted_slot) > EPS_SECONDS:
            blockers.append("declared playback slot differs from active player source")
    declared_duration = video.get("duration_seconds")
    if (trusted_slot is not None and isinstance(declared_duration, (int, float)) and
            declared_duration > 0):
        multiples = trusted_slot / declared_duration
        if abs(multiples - round(multiples)) > EPS_SECONDS / declared_duration or multiples < 1:
            blockers.append("native clip duration cannot fill player slot by complete repeats; no implicit 6s→5s trim/speed")
    # Never trust only the declared hash/metadata; verify actual private bytes.
    raw_path = video.get("local_path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        blockers.append("locally readable original MP4 bytes are required")
    else:
        path = Path(raw_path).resolve()
        try:
            if (not path.is_file() or path.suffix.lower() != ".mp4" or
                    path.is_relative_to(root)):
                blockers.append("video must be an existing private MP4 outside the Git repository")
            else:
                digest = file_sha256(path)
                verified["sha256"] = digest
                if digest != video["sha256"]:
                    blockers.append("local media SHA-256 mismatch")
                details = probe(path)
                # Container metadata and frame count alone can overlook
                # recoverable bitstream errors between sampled frames.
                _verify_full_video_decode(path)
                verified["full_stream_decode"] = "PASS"
                details["frame_count"] = _decoded_frame_count(path)
                verified.update(details)
                if not math.isfinite(details["fps"]) or details["fps"] <= 0:
                    blockers.append("verified native frame rate is invalid for browser playback")
                else:
                    decoded_duration = details["frame_count"] / details["fps"]
                    if abs(decoded_duration - details["duration_seconds"]) > PLAYER_TIMING_EPS_SECONDS:
                        blockers.append("decoded frame count/FPS differs from native duration required by browser player")
                # The browser compares its actual native duration with the
                # trusted registry to 1ms. The broader motion-spec planning
                # tolerance must not admit a manifest duration that the
                # browser would later reject as a different clip.
                if abs(details["duration_seconds"] - video["duration_seconds"]) > PLAYER_TIMING_EPS_SECONDS:
                    blockers.append("native duration differs from declared video duration beyond browser 1ms tolerance")
                if abs(details["fps"] - video["fps"]) > EPS_FPS:
                    blockers.append("ffprobe fps mismatch")
                for key in ("width", "height", "codec", "audio_stream_count", "frame_count"):
                    if details[key] != video[key]:
                        blockers.append(f"ffprobe {key} mismatch")
                if details["audio_stream_count"] != 0:
                    blockers.append("player asset contains audio; require a separately hashed silent derivative")
                if details["codec"] != "h264":
                    blockers.append("player asset must use H.264 for the current player")
                if trusted_slot is not None:
                    multiples = trusted_slot / details["duration_seconds"]
                    if abs(multiples - round(multiples)) > EPS_SECONDS / details["duration_seconds"] or multiples < 1:
                        blockers.append("verified native clip cannot fill exact active slot without implicit trim/speed")
                # A concurrent file replacement between first SHA, probe and
                # frame count must never yield a seemingly stable report.
                if file_sha256(path) != digest:
                    blockers.append("media bytes changed during hash/probe verification; discard this inspection")
        except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
            blockers.append("local video verification failed: " + str(exc))
    try:
        record, qa = _canonical_record(root, chart, exercise)
        result["canonical_qa_source"] = record["source"]
        if record["revision"] != candidate["revision"]:
            blockers.append("candidate revision differs from canonical QA DONE revision")
        if record["video_sha256"] != video["sha256"] or record["video_url"] != video["url"]:
            blockers.append("candidate video hash/URL differs from canonical QA exact version")
        contract = (root / qa["contract"]).resolve()
        if not contract.is_relative_to(root / "photo_motion/specs"):
            blockers.append("canonical QA contract is not a photographic motion specification")
        else:
            spec = json.loads(contract.read_text(encoding="utf-8"))
            if spec.get("movement_type") != ACTION_MOVEMENT_TYPES[(chart, exercise, action)]:
                blockers.append("canonical QA motion contract is for a different player action")
            if spec.get("status") == "HOLD":
                blockers.append("canonical QA motion contract remains on HOLD")
            if (type(spec.get("duration_seconds")) not in (int, float) or
                    abs(spec["duration_seconds"] - video["duration_seconds"]) > EPS_SECONDS):
                blockers.append("candidate native duration differs from approved-version motion contract")
        decision = qa.get("owner_decision")
        if not isinstance(decision, dict) or decision.get("video_sha256") != video["sha256"]:
            blockers.append("canonical QA lacks structurally matching exact-version owner ACCEPT")
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        blockers.append("canonical QA is not eligible: " + str(exc))
    if not blockers:
        result["technical_evidence"] = "PASS"
    # The QA note's owner_decision is *not* an authenticated owner event.
    # Even a technically matched claimed DONE must remain held offline.
    blockers.append("owner acceptance identity and exact-version event NOT_EVALUATED (authentication required)")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="Private candidate manifest (JSON, read only)")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    try:
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
        result = evaluate(candidate, args.repo_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"admission": "HOLD", "form_and_release_approval": "NOT_EVALUATED",
                  "owner_authentication": "NOT_EVALUATED", "public_release_authorized": False,
                  "historical_diagnostic_integrity": "NOT_EVALUATED",
                  "delivered_url_byte_integrity": "NOT_EVALUATED",
                  "player_manifest": {"schemaVersion": 1, "clips": {}},
                  "blockers": ["invalid candidate: " + str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1  # Deliberate: no CLI case produces an approval/deployable registry.


if __name__ == "__main__":
    sys.exit(main())
