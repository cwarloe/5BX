"""Read-only first-party *adult* scissor motion-reference intake.

This is a technical evidence gate, not an authenticated consent authority, a
human pose recognizer, a provider-upload permit, or an exercise approval.  All
paths and human-identifying material belong in a private archive outside Git.
"""

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .video_qa import file_sha256, _verify_full_video_decode


REPO_ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{64}\Z")
CAPTURE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{5,79}\Z")
PHASES = ("A0", "B0", "C0", "D0", "A1", "B1", "C1", "D1", "A2")
FLIGHTS = ("B0", "D0", "B1", "D1")
ROOT = {"schema_version", "capture_id", "status", "captured_at_utc", "recorded_local_timezone",
        "source", "setup", "human_motion_evidence", "rights", "release"}
SOURCE = {"locator", "sha256", "bytes", "codec", "width", "height", "fps_reported",
          "fps_measured", "decoded_frames", "duration_seconds", "rotation_degrees",
          "camera_original_reviewed_by", "camera_original_unmodified"}
SETUP = {"camera_model", "camera_side_relative_to_performer", "camera_locked",
         "focus_exposure_white_balance_locked", "full_body_margin_review", "side_on_view_review",
         "static_background_review", "ground_contact_plane_review", "no_bystanders_or_minors_review",
         "no_private_conversations_review"}
MOTION = {"reviewer_full_name", "reviewed_at_utc", "review_evidence_locator",
          "review_evidence_sha256", "nine_checkpoints", "four_distinct_both_shoes_airborne_frame_intervals",
          "all_frames_head_and_shoes_visible", "anatomical_side_continuity",
          "technical_motion_verdict", "form_and_safety_verdict"}
CHECKPOINT = {"id", "frame_number", "timestamp_seconds", "support", "right_leg",
              "left_leg", "right_arm", "left_arm"}
INTERVAL = {"id", "first_frame", "last_frame", "first_timestamp_seconds",
            "last_timestamp_seconds", "both_entire_outsoles_clear_every_frame"}
RIGHTS = {"performer_is_adult_18_plus", "performer_release_locator", "performer_release_sha256",
          "performer_release_signed_and_dated", "consent_reviewer_full_name", "consent_reviewed_at_utc",
          "permitted_filming_and_private_storage", "permitted_editing_and_technical_analysis",
          "permitted_ai_provider_upload", "permitted_derivatives", "permitted_public_educational_commercial_use",
          "permitted_likeness_transfer", "permitted_voice_or_biometric_transfer",
          "permitted_liveness_testing", "permitted_purpose", "withdrawal_terms_recorded",
          "location_permission_status", "location_evidence_locator", "location_evidence_sha256"}


def _exact(value, keys, label, failures):
    if not isinstance(value, dict) or set(value) != keys:
        failures.append(f"{label}: exact schema keys required (no missing/extra fields)")
        return False
    return True


def _date(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0
    except (ValueError, AttributeError):
        return False


def _name(value):
    """Named human, not a placeholder or untraceable role label."""
    if not isinstance(value, str) or len(value.strip()) < 5 or len(value) > 120:
        return False
    words = value.strip().split()
    return (len(words) >= 2 and all(len(word) >= 2 and any(c.isalpha() for c in word) for word in words)
            and not re.search(r"(?i)replace|placeholder|unknown|anonymous|example|test user|not evaluated|tbd", value))


def _private_locator(value):
    return (isinstance(value, str) and len(value) < 240 and
            re.fullmatch(r"private://[a-zA-Z0-9/_-]+", value) is not None)


def _hash(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _int(value):
    return type(value) is int and value >= 0


def _reviewed(value):
    return value == "MANUALLY_VERIFIED"


def _fail(failures, condition, message):
    if not condition:
        failures.append(message)


def _path_bytes(path, expected, label, failures, repo_root):
    """Never dereference symlinks or expose private paths in result/errors."""
    if not isinstance(path, (str, Path)):
        failures.append(f"{label}: local original/evidence file not supplied")
        return None
    path = Path(path)
    try:
        # Reject symlink components before resolve, not only a final link.
        if any(parent.is_symlink() for parent in (path, *path.parents)):
            raise ValueError("symlink")
        absolute = path.resolve(strict=True)
        if not absolute.is_file() or absolute.is_relative_to(Path(repo_root).resolve()):
            raise ValueError("not a private regular file outside repository")
        if not _hash(expected):
            raise ValueError("missing declared digest")
        digest = file_sha256(absolute)
        if digest != expected or digest != file_sha256(absolute):
            raise ValueError("digest mismatch or bytes changed during verification")
        return absolute
    except (OSError, ValueError):
        failures.append(f"{label}: private bytes unavailable, linked, in Git, changed or SHA-256 mismatch")
        return None


def _run_json(command, label):
    try:
        outcome = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise ValueError(f"{label} tool unavailable") from exc
    if outcome.returncode:
        raise ValueError(f"{label} unsuccessful")
    try:
        return json.loads(outcome.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} returned non-JSON") from exc


def _fps(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{1,7}/\d{1,7}", value):
        raise ValueError("FPS must be an exact ffprobe rational n/d")
    numerator, denominator = map(int, value.split("/"))
    if not denominator:
        raise ValueError("FPS denominator zero")
    return numerator / denominator


def inspect_original(path):
    """Independent full-stream decode and per-decoded-frame PTS inspection.

    No intermediate files are written; stderr and filenames never reach the
    report. The exposed timestamp list is internal and omitted from summary.
    """
    path = Path(path)
    metadata = _run_json(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                          "-of", "json", str(path)], "ffprobe stream inspection")
    streams = metadata.get("streams")
    if not isinstance(streams, list):
        raise ValueError("ffprobe streams missing")
    video = [s for s in streams if s.get("codec_type") == "video"]
    if len(video) != 1 or any(s.get("codec_type") not in ("video", "audio") for s in streams):
        raise ValueError("must have exactly one video stream and no auxiliary data streams")
    stream = video[0]
    frames = _run_json(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_frames", "-show_entries", "frame=best_effort_timestamp_time",
                        "-of", "json", str(path)], "ffprobe decoded-frame timing").get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("decoded-frame timing missing")
    try:
        times = [float(frame["best_effort_timestamp_time"]) for frame in frames]
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("decoded PTS missing") from exc
    if not all(math.isfinite(t) for t in times):
        raise ValueError("nonfinite decoded-frame PTS")
    nominal = _fps(stream.get("avg_frame_rate"))
    raw = _fps(stream.get("r_frame_rate"))
    # 59.94 and 60 fps camera modes are normal. Detect VFR from *all* PTS,
    # not merely ffprobe's averaged 60fps claim or container nb_frames.
    if not 59.0 <= nominal <= 60.1 or abs(nominal - raw) > 0.2:
        raise ValueError("60fps native camera timing not verified")
    target_step = 1 / nominal
    if len(times) < 2 or any(delta <= 0 or abs(delta - target_step) > max(0.0008, .05 * target_step)
                             for delta in (b - a for a, b in zip(times, times[1:]))):
        raise ValueError("decoded PTS not strictly monotone near-constant 60fps")
    rotation = []
    tags = stream.get("tags") or {}
    if "rotate" in tags:
        rotation.append(tags["rotate"])
    for side in stream.get("side_data_list") or []:
        if side.get("side_data_type") == "Display Matrix":
            rotation.append(side.get("rotation"))
    try:
        if any(not math.isfinite(float(v)) or abs(float(v)) > 0.01 for v in rotation):
            raise ValueError("nonzero camera display rotation")
    except (ValueError, TypeError) as exc:
        raise ValueError("unreadable/nonzero camera rotation") from exc
    try:
        duration = float(metadata["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("container duration unknown") from exc
    if not math.isfinite(duration) or duration <= 0 or abs(duration - len(times) / nominal) > .1:
        raise ValueError("container duration inconsistent with decoded frames")
    if duration < 10:
        raise ValueError("shorter than preferred 10s continuous two-cycle capture gate")
    width, height = stream.get("width"), stream.get("height")
    if (type(width) is not int or type(height) is not int or width < 1920 or height < 1080 or
            abs(width / height - 16 / 9) > .012):
        raise ValueError("camera native frame smaller than 1080p or not landscape 16:9")
    codec = stream.get("codec_name")
    if not isinstance(codec, str) or not codec or codec == "none":
        raise ValueError("unknown native camera codec")
    _verify_full_video_decode(path)
    return {"sha256": file_sha256(path), "bytes": path.stat().st_size,
            "codec": codec, "width": width, "height": height,
            "fps_measured": stream["avg_frame_rate"], "decoded_frames": len(times),
            "duration_seconds": duration, "rotation_degrees": 0, "times": times}


def _check_checkpoints(motion, times, failures):
    checkpoints = motion.get("nine_checkpoints")
    intervals = motion.get("four_distinct_both_shoes_airborne_frame_intervals")
    if not isinstance(checkpoints, list) or len(checkpoints) != 9:
        failures.append("motion: exactly nine human-reviewed checkpoints required")
        return
    if not isinstance(intervals, list) or len(intervals) != 4:
        failures.append("motion: exactly four independent human-reviewed airborne intervals required")
        return
    indices = {}
    prev = -1
    for phase, item in zip(PHASES, checkpoints):
        if not _exact(item, CHECKPOINT, f"checkpoint {phase}", failures):
            continue
        frame = item["frame_number"]
        _fail(failures, item["id"] == phase, f"checkpoint {phase}: phase ID/order mismatch")
        valid = _int(frame) and frame < len(times)
        _fail(failures, valid and frame > prev, f"checkpoint {phase}: out-of-range or unordered decoded frame")
        if not valid:
            continue
        prev = frame
        indices[phase] = frame
        _fail(failures, _number(item["timestamp_seconds"]) and
              abs(item["timestamp_seconds"] - times[frame]) <= 0.001,
              f"checkpoint {phase}: timestamp disagrees with decoded PTS")
        airborne = phase[0] in "BD"
        _fail(failures, item["support"] == ("BOTH_SHOES_ENTIRELY_AIRBORNE" if airborne else "BOTH_SHOES_GROUNDED"),
              f"checkpoint {phase}: wrong ground/flight support")
        if airborne:
            for limb in ("right_leg", "left_leg", "right_arm", "left_arm"):
                _fail(failures, item[limb] == "EXCHANGING", f"checkpoint {phase}: {limb} not visibly exchanging")
        else:
            forward_right_leg = phase[0] == "A"
            expected = {"right_leg": "FORWARD" if forward_right_leg else "BACK",
                        "left_leg": "BACK" if forward_right_leg else "FORWARD",
                        "right_arm": "BACK" if forward_right_leg else "FORWARD",
                        "left_arm": "FORWARD" if forward_right_leg else "BACK"}
            for limb, position in expected.items():
                _fail(failures, item[limb] == position,
                      f"checkpoint {phase}: physical {limb} not independently reviewed as {position}")
    prev_last = -1
    for phase, interval in zip(FLIGHTS, intervals):
        if not _exact(interval, INTERVAL, f"flight {phase}", failures):
            continue
        start, stop = interval["first_frame"], interval["last_frame"]
        _fail(failures, interval["id"] == phase, f"flight {phase}: ID/order mismatch")
        valid = _int(start) and _int(stop) and start < len(times) and stop < len(times)
        _fail(failures, valid and stop >= start + 1 and start > prev_last,
              f"flight {phase}: needs distinct >=2 contiguous decoded frames")
        if not valid:
            continue
        prev_last = stop
        _fail(failures, interval["both_entire_outsoles_clear_every_frame"] is True,
              f"flight {phase}: entire outsoles not human-verified airborne on EVERY interval frame")
        _fail(failures, _number(interval["first_timestamp_seconds"]) and
              abs(interval["first_timestamp_seconds"] - times[start]) <= .001 and
              _number(interval["last_timestamp_seconds"]) and
              abs(interval["last_timestamp_seconds"] - times[stop]) <= .001,
              f"flight {phase}: interval timestamps disagree with decoded PTS")
        if phase in indices:
            _fail(failures, start <= indices[phase] <= stop,
                  f"flight {phase}: airborne checkpoint not in its flight interval")
        phase_idx = PHASES.index(phase)
        before, after = PHASES[phase_idx - 1], PHASES[phase_idx + 1]
        if before in indices and after in indices:
            _fail(failures, indices[before] < start <= stop < indices[after],
                  f"flight {phase}: interval not between its two grounded endpoints")


def evaluate(receipt, source_path=None, release_path=None, review_path=None,
             location_path=None, repo_root=REPO_ROOT, inspector=inspect_original):
    """Return safe disposition; never include identifying names/private paths.

    `inspector` injection permits synthetic unit fixtures. CLI always uses
    actual ffprobe and ffmpeg. No caller-controlled approval flag is accepted.
    """
    failures = []
    result = {"schema_version": 1, "decision": "NOT_EVALUATED", "blockers": failures,
              "source_bytes_verified": False, "full_decode_and_timing_verified": False,
              "human_review_evidence_bytes_verified": False, "signed_release_bytes_verified": False,
              "location_permission_evidence_bytes_verified": False,
              "provider_upload_authorized": False, "form_correctness_approved": False,
              "public_release_authorized": False}
    if not _exact(receipt, ROOT, "receipt", failures):
        return result
    _fail(failures, type(receipt["schema_version"]) is int and receipt["schema_version"] == 1,
          "unsupported receipt schema version")
    _fail(failures, isinstance(receipt["capture_id"], str) and CAPTURE_ID.fullmatch(receipt["capture_id"]) is not None,
          "capture ID missing/invalid")
    _fail(failures, receipt["status"] == "EXPERIMENTAL_NOT_FORM_APPROVED", "receipt cannot claim form approval")
    _fail(failures, receipt["release"] == "HOLD_FOR_CHARLES_EXACT_VIDEO_REVIEW", "owner review hold required")
    _fail(failures, _date(receipt["captured_at_utc"]), "capture UTC timestamp invalid")
    try:
        ZoneInfo(receipt["recorded_local_timezone"])
    except (TypeError, ZoneInfoNotFoundError, ValueError, KeyError):
        failures.append("recording local IANA timezone invalid")
    source, setup = receipt["source"], receipt["setup"]
    motion, rights = receipt["human_motion_evidence"], receipt["rights"]
    if not all((_exact(source, SOURCE, "source", failures),
                _exact(setup, SETUP, "setup", failures),
                _exact(motion, MOTION, "human_motion_evidence", failures),
                _exact(rights, RIGHTS, "rights", failures))):
        return result
    result["capture_id"] = receipt["capture_id"]
    _fail(failures, _private_locator(source["locator"]), "source: opaque private archive locator required")
    _fail(failures, _hash(source["sha256"]), "source: real lowercase SHA-256 required")
    for field in ("bytes", "width", "height", "decoded_frames"):
        _fail(failures, type(source[field]) is int and source[field] > 0,
              f"source: {field} must be a positive integer")
    _fail(failures, type(source["rotation_degrees"]) is int and source["rotation_degrees"] == 0,
          "source: native landscape camera rotation must be zero")
    _fail(failures, _name(source["camera_original_reviewed_by"]) and
          source["camera_original_unmodified"] is True,
          "camera original must be affirmatively reviewed by a named human")
    _fail(failures, isinstance(source["fps_reported"], str) and
          source["fps_reported"] in ("60/1", "60000/1001"), "nominal native camera fps must be 60 or 59.94")
    _fail(failures, isinstance(setup["camera_model"], str) and len(setup["camera_model"].strip()) >= 3,
          "camera model not recorded")
    _fail(failures, setup["camera_side_relative_to_performer"] in ("PERFORMER_RIGHT", "PERFORMER_LEFT"),
          "physical camera side relative to performer required")
    for field in SETUP - {"camera_model", "camera_side_relative_to_performer"}:
        _fail(failures, _reviewed(setup[field]), f"setup: {field} requires human verification")
    _fail(failures, _name(motion["reviewer_full_name"]) and _date(motion["reviewed_at_utc"]),
          "independent motion review requires named human and UTC timestamp")
    for field in ("all_frames_head_and_shoes_visible", "anatomical_side_continuity"):
        _fail(failures, _reviewed(motion[field]), f"motion: {field} must be human reviewed for ALL frames")
    _fail(failures, motion["technical_motion_verdict"] == "PASS",
          "motion: independent technical verdict must be PASS")
    _fail(failures, motion["form_and_safety_verdict"] == "NOT_EVALUATED",
          "form/safety verdict cannot be inferred or approved by this intake")
    for locator_field, digest_field, label in (("review_evidence_locator", "review_evidence_sha256", "review"),):
        _fail(failures, _private_locator(motion[locator_field]) and _hash(motion[digest_field]),
              f"{label}: private evidence locator and SHA-256 required")
    _fail(failures, _name(rights["consent_reviewer_full_name"]) and _date(rights["consent_reviewed_at_utc"]),
          "rights: named consent reviewer and UTC review time required")
    _fail(failures, _private_locator(rights["performer_release_locator"]) and
          _hash(rights["performer_release_sha256"]), "rights: signed private release evidence hash required")
    _fail(failures, _private_locator(rights["location_evidence_locator"]) and
          _hash(rights["location_evidence_sha256"]), "rights: private location-permission finding hash required")
    required_true = ("performer_is_adult_18_plus", "performer_release_signed_and_dated",
                     "permitted_filming_and_private_storage", "permitted_editing_and_technical_analysis",
                     "permitted_derivatives", "permitted_public_educational_commercial_use", "withdrawal_terms_recorded")
    for key in required_true:
        _fail(failures, rights[key] is True, f"rights: explicit {key} required")
    _fail(failures, rights["permitted_ai_provider_upload"] == ["Google Flow"],
          "rights: explicit named Google Flow motion-only provider-upload consent required")
    for forbidden in ("permitted_likeness_transfer", "permitted_voice_or_biometric_transfer",
                      "permitted_liveness_testing"):
        _fail(failures, rights[forbidden] is False,
              f"rights: {forbidden} MUST be prohibited")
    _fail(failures, rights["permitted_purpose"] == "MOTION_ONLY_NOT_IDENTITY",
          "rights: AI consent restricted to motion mechanics, never identity/likeness")
    _fail(failures, rights["location_permission_status"] in ("PERMISSION_GRANTED", "NONE_REQUIRED_DOCUMENTED"),
          "rights: location permission granted or documented none-required finding")
    # Independent documentary bytes are required before a candidate, though
    # a hash match cannot prove legal sufficiency or authenticate a signature.
    for label, filepath, expected, field in (
        ("human review", review_path, motion["review_evidence_sha256"], "human_review_evidence_bytes_verified"),
        ("adult signed release", release_path, rights["performer_release_sha256"], "signed_release_bytes_verified"),
        ("location permission", location_path, rights["location_evidence_sha256"], "location_permission_evidence_bytes_verified"),
    ):
        result[field] = _path_bytes(filepath, expected, label, failures, repo_root) is not None
    original = _path_bytes(source_path, source["sha256"], "camera original", failures, repo_root)
    if original is not None:
        result["source_bytes_verified"] = True
        try:
            details = inspector(original)
            if details["sha256"] != source["sha256"] or file_sha256(original) != source["sha256"]:
                raise ValueError("original changed or inspector SHA disagrees")
            for field in ("bytes", "codec", "width", "height", "fps_measured", "decoded_frames",
                          "rotation_degrees"):
                _fail(failures, source[field] == details[field], f"source: actual {field} differs from receipt")
            _fail(failures, _number(source["duration_seconds"]) and
                  abs(source["duration_seconds"] - details["duration_seconds"]) <= .001,
                  "source: duration differs from native original")
            times = details["times"]
            _check_checkpoints(motion, times, failures)
            result["full_decode_and_timing_verified"] = True
            result["verified_frame_count"] = len(times)
        except (OSError, ValueError, TypeError, IndexError, KeyError, RuntimeError) as exc:
            # Never reflect an external utility's exception string; it can
            # contain private filenames, filenames of media or other PII.
            failures.append("camera original: full decode/metadata/frame timing inspection failed")
    if not failures:
        result["decision"] = "CAPTURE_REFERENCE_CANDIDATE"
        result["source_sha256"] = source["sha256"]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, help="Private JSON capture receipt, outside Git")
    parser.add_argument("--source", required=True, help="Private exact camera-original MP4/MOV")
    parser.add_argument("--release", required=True, help="Private signed, dated adult release")
    parser.add_argument("--review-evidence", required=True, help="Private signed/named human frame annotations")
    parser.add_argument("--location-evidence", required=True, help="Private location permission or none-required finding")
    args = parser.parse_args(argv)
    # Receipt itself may contain human names and private locators. It is only
    # read, never echoed. Reject local Git-stored receipt and any symlinks.
    guard = []
    try:
        receipt_path = Path(args.receipt)
        # Validate before reading or hashing even if an ancestor, rather than
        # the leaf, is a symlink. Do not print user-supplied filesystem paths.
        if (any(item.is_symlink() for item in (receipt_path, *receipt_path.parents)) or
                not receipt_path.is_file() or receipt_path.resolve().is_relative_to(REPO_ROOT)):
            raise ValueError("receipt not private direct file")
        receipt_digest = file_sha256(receipt_path)
        receipt_path = _path_bytes(receipt_path, receipt_digest, "private receipt", guard, REPO_ROOT)
    except (OSError, ValueError):
        receipt_path = None
        guard.append("private receipt: inaccessible, linked or Git-contained")
    if receipt_path is None:
        print(json.dumps({"schema_version": 1, "decision": "NOT_EVALUATED", "blockers": guard,
                          "provider_upload_authorized": False, "public_release_authorized": False}))
        return 2
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, OSError):
        print(json.dumps({"schema_version": 1, "decision": "NOT_EVALUATED",
                          "blockers": ["private receipt: invalid/unreadable JSON"],
                          "provider_upload_authorized": False, "public_release_authorized": False}))
        return 2
    result = evaluate(receipt, args.source, args.release, args.review_evidence, args.location_evidence)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["decision"] == "CAPTURE_REFERENCE_CANDIDATE" else 2


if __name__ == "__main__":
    sys.exit(main())
