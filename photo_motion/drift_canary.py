"""Read-only A/B canary inspection of *existing* photographic run evidence.

Compare two immutable experiment intents and, optionally, the independently
produced ``photo_motion inspect`` reports. No generation, network, side effects,
new approval ledger, or automatic human-form decisions are made here.

CLI: python3 -m photo_motion.drift_canary compare OLD_INTENT NEW_INTENT --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

from . import experiments


SHA256 = re.compile(r"^[0-9a-f]{64}$")


class CanaryError(ValueError):
    """Malformed or inconsistent evidence is not a successful canary."""


def _intent(data, label):
    if not isinstance(data, dict):
        raise CanaryError(f"{label} must be a JSON object")
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not SHA256.fullmatch(run_id):
        raise CanaryError(f"{label} has no valid run_id SHA-256")
    try:
        experiments._check_intent_record(data, run_id)
    except (experiments.ExperimentError, TypeError, ValueError) as exc:
        raise CanaryError(f"{label} fingerprint/intent validation failed: {exc}") from exc
    request = data["request"]
    for key in ("exercise_id", "spec_sha256", "submitted_prompt_sha256", "provider", "model"):
        if not isinstance(request.get(key), str) or not request[key]:
            raise CanaryError(f"{label} request has no {key}")
    if not isinstance(request.get("settings"), dict) or not isinstance(request.get("input_assets"), list):
        raise CanaryError(f"{label} request lacks settings or input assets")
    if not SHA256.fullmatch(request["spec_sha256"]) or not SHA256.fullmatch(request["submitted_prompt_sha256"]):
        raise CanaryError(f"{label} request has malformed source or prompt SHA-256")
    return request


def _inputs(request, label):
    assets = request["input_assets"]
    if not assets:
        raise CanaryError(f"{label} has no immutable source assets")
    content = []
    source_warnings = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise CanaryError(f"{label} input_assets[{index}] is not an object")
        role, sha = asset.get("role"), asset.get("sha256")
        if not isinstance(role, str) or not role or not isinstance(sha, str) or not SHA256.fullmatch(sha):
            raise CanaryError(f"{label} input_assets[{index}] lacks role or valid SHA-256")
        content.append((role, sha))  # Preserve sequence: image order is semantic.
        if asset.get("verification") != "rehashed_from_local_bytes":
            source_warnings.append(f"{label} input_assets[{index}] ({role}) was not locally rehashed")
    return content, source_warnings


def _inspection(report, request, label):
    if not isinstance(report, dict) or report.get("tool") != "photo_motion.video_qa":
        raise CanaryError(f"{label} must be a photo_motion.video_qa inspection report")
    if report.get("form_and_release_approval") != "NOT_EVALUATED":
        raise CanaryError(f"{label} must explicitly retain form_and_release_approval=NOT_EVALUATED")
    if report.get("spec_sha256") != request["spec_sha256"]:
        raise CanaryError(f"{label} spec_sha256 does not match the immutable run intent")
    if not isinstance(report.get("source_video_sha256"), str) or not SHA256.fullmatch(report["source_video_sha256"]):
        raise CanaryError(f"{label} lacks a valid inspected video SHA-256")
    info = report.get("video")
    if not isinstance(info, dict):
        raise CanaryError(f"{label} lacks video stream information")
    required = ("duration_seconds", "fps", "width", "height", "codec", "pixel_format", "audio_stream_count")
    if any(key not in info for key in required):
        raise CanaryError(f"{label} missing video stream metrics")
    if not isinstance(info["duration_seconds"], (int, float)) or info["duration_seconds"] <= 0:
        raise CanaryError(f"{label} invalid video duration")
    if not isinstance(info["fps"], (int, float)) or info["fps"] <= 0:
        raise CanaryError(f"{label} invalid video frame rate")
    for key in ("width", "height"):
        if not isinstance(info[key], int) or info[key] <= 0:
            raise CanaryError(f"{label} invalid video {key}")
    for key in ("codec", "pixel_format"):
        if not isinstance(info[key], str) or not info[key]:
            raise CanaryError(f"{label} invalid video {key}")
    if not isinstance(info["audio_stream_count"], int) or info["audio_stream_count"] < 0:
        raise CanaryError(f"{label} invalid audio stream count")
    warnings = report.get("technical_warnings")
    if not isinstance(warnings, list) or any(not isinstance(w, str) for w in warnings):
        raise CanaryError(f"{label} lacks valid technical_warnings list")
    provenance = report.get("generation_provenance")
    if not isinstance(provenance, dict):
        warnings = [*warnings, f"{label} inspection lacks generator provenance"]
    else:
        for key in ("provider", "model"):
            if provenance.get(key) != request[key]:
                raise CanaryError(f"{label} inspection {key} does not match the immutable intent")
        if provenance.get("exact_submitted_prompt_sha256") != request["submitted_prompt_sha256"]:
            raise CanaryError(f"{label} inspection exact prompt digest does not match the immutable intent")
        actual_inputs = provenance.get("input_images")
        if (not isinstance(actual_inputs, list) or
                any(not isinstance(asset, dict) for asset in actual_inputs) or
                [(asset.get("role"), asset.get("sha256")) for asset in actual_inputs]
                != _inputs(request, label)[0]):
            raise CanaryError(f"{label} inspection inputs do not match the immutable intent")
        if provenance.get("warnings"):
            warnings = [*warnings, f"{label} generator recipe contains provenance warnings"]
    return info, warnings


def compare(baseline, candidate, *, baseline_inspection=None, candidate_inspection=None):
    """Read-only metadata comparison. Exit 0 is *never* form approval."""
    old = _intent(baseline, "baseline")
    new = _intent(candidate, "candidate")
    if old["exercise_id"] != new["exercise_id"]:
        raise CanaryError("different exercises cannot be compared as one canary")
    old_assets, old_warnings = _inputs(old, "baseline")
    new_assets, new_warnings = _inputs(new, "candidate")
    changes = []

    def changed(field, before, after, reason):
        if before != after:
            changes.append({"field": field, "reason": reason})

    for field in ("spec_sha256", "submitted_prompt_sha256", "provider", "model", "settings", "estimated_credits"):
        changed(field, old.get(field), new.get(field), "Change must be explained and retested; not an automatic improvement")
    changed("input_assets", old_assets, new_assets,
            "Image roles, ordering or content digests changed; requalify physical identity/pose sources")
    # The V6 immutable preflight has an original-card digest AND a derived PNG
    # digest. Hashes of these transformation records belong to the job identity,
    # not just the final reference image; changes require new calibration.
    preflight_fields = ("spec_sha256", "original_v6_card_sha256", "prepared_png_sha256",
                        "preparation_manifest_sha256", "source_marker_start_state",
                        "anatomical_left_right_proven", "preflight_result")
    def preflight_identity(request):
        record = request.get("source_preflight")
        return None if record is None else {key: record.get(key) for key in preflight_fields}
    changed("source_preflight", preflight_identity(old), preflight_identity(new),
            "Prepared-image source/transform authority changed and must be reverified")
    warnings = [*old_warnings, *new_warnings]

    if (baseline_inspection is None) != (candidate_inspection is None):
        raise CanaryError("both inspections must be provided together, or neither")
    video_validation = "NOT_PROVIDED"
    if baseline_inspection is not None:
        old_video, previous_warnings = _inspection(baseline_inspection, old, "baseline")
        new_video, current_warnings = _inspection(candidate_inspection, new, "candidate")
        warnings.extend(previous_warnings)
        warnings.extend(current_warnings)
        for field in ("width", "height", "codec", "pixel_format", "audio_stream_count"):
            changed("video." + field, old_video[field], new_video[field],
                    "Video stream characteristic changed; inspect the new output")
        for field, threshold in (("duration_seconds", 0.25), ("fps", 0.1)):
            if abs(old_video[field] - new_video[field]) > threshold:
                changes.append({"field": "video." + field,
                                "reason": f"Video measurement changed by more than {threshold:g}; inspect the new output"})
        video_validation = ("TECHNICAL_REQUALIFICATION_REQUIRED" if changes or warnings
                            else "TECHNICAL_METADATA_UNCHANGED")

    requalify = bool(changes or warnings)
    return {
        "schema_version": 1,
        "exercise_id": old["exercise_id"],
        "baseline_run_id": baseline["run_id"],
        "candidate_run_id": candidate["run_id"],
        "configuration": "REQUALIFICATION_REQUIRED" if requalify else "UNCHANGED",
        "video_validation": video_validation,
        "changes": changes,
        "source_warnings": warnings,
        "form_verdict": "NOT_ASSESSED",
        "release_verdict": "NO_AUTOMATIC_APPROVAL",
        "interpretation": "Unchanged configuration/technical metadata cannot prove stable AI motion, identity, anatomy, camera, loop or safety. Independent video/form review remains mandatory.",
        "exit_code": 1 if requalify else 0,
    }


def _read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanaryError(f"cannot read valid JSON at {path}: {exc}") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only drift canary comparing existing immutable run evidence")
    commands = parser.add_subparsers(dest="command", required=True)
    compare_cmd = commands.add_parser("compare", help="Compare two runs of the same exercise without media generation")
    compare_cmd.add_argument("baseline", type=Path, help="Existing immutable experiment intent JSON")
    compare_cmd.add_argument("candidate", type=Path, help="Existing immutable experiment intent JSON")
    compare_cmd.add_argument("--baseline-inspection", type=Path)
    compare_cmd.add_argument("--candidate-inspection", type=Path)
    compare_cmd.add_argument("--json", action="store_true", help="Machine-readable result (default also JSON)")
    args = parser.parse_args(argv)
    try:
        result = compare(_read(args.baseline), _read(args.candidate),
                         baseline_inspection=_read(args.baseline_inspection) if args.baseline_inspection else None,
                         candidate_inspection=_read(args.candidate_inspection) if args.candidate_inspection else None)
    except CanaryError as exc:
        print(json.dumps({"error": str(exc), "exit_code": 2,
                          "form_verdict": "NOT_ASSESSED", "release_verdict": "NO_AUTOMATIC_APPROVAL"},
                         indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
