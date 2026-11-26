"""Fail-closed V13 video-to-video *arm-only* edit precredit authority.

This binds the exact failed V12 raw video, its final independent HOLD report,
the previous native three-credit ledger receipt, the unmodified arm-edit
prompt and a fresh observation of the real Flow edit UI. It never submits an
edit or treats a diagnosis as physical-form approval.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from . import experiments
from .preflight_v12_apex_frames import FLOW_SETTINGS as V12_SETTINGS


class V13PreflightError(ValueError):
    """One required source, native debit or current Flow edit gate is HOLD."""


AUTHORITY = "V13_V12_RAW_ARM_ONLY_V2V_EDIT_360P"
UI_AUTHORITY = "V13_FLOW_LIVE_VIDEO_EDIT_QUOTE"
RAW_V12_SHA256 = "5680aff2e5811ef99d52a533a6c24405ad1d92ef66afa7bf9b37fb7e693d3fba"
V12_QA_SHA256 = "a1477c3d5ca7eae765bbf0d2377a467f4fe29021360805d78e16cea70f128d70"
V12_RUN_ID = "cd098dc731c35283a78b47f500d357ecb0577654068f2f5fe7d95fe00e5ea14a"
PROMPT_SHA256 = "6c46960ec7c400b4d58b296fa2b8f40ef97e2b264c643c2d9a8a9579327ec231"
FLOW_MODEL = "Omni 1.2 Flash"
FLOW_SETTINGS = {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": None, "generation_mode": "Video to Video Edit",
    "resolution": "360p", "return_silent_videos": True,
}
QUOTE_CEILING = Decimal("3")
_SCENE_LINE = re.compile(r"Provider Flow scene ID `([0-9a-f-]{36})`")


def _hash(payload):
    return hashlib.sha256(payload).hexdigest()


def _read_file(path, label):
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise V13PreflightError(f"{label} must not be a symlink")
    candidate = candidate.resolve()
    if not candidate.is_file():
        raise V13PreflightError(f"{label} missing; no paid reservation")
    return candidate, candidate.read_bytes()


def _json_bytes(payload, label):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise V13PreflightError(f"duplicate {label} field")
            result[key] = value
        return result
    try:
        result = json.loads(payload, object_pairs_hook=unique_keys)
    except (ValueError, UnicodeDecodeError) as exc:
        raise V13PreflightError(f"invalid {label}: {exc}") from exc
    if not isinstance(result, dict):
        raise V13PreflightError(f"{label} must be a JSON object")
    return result


def _same(a, b):
    # Type-stable: True may not substitute for 1.
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def expected_spec():
    return {
        "schema_version": 1, "authority": AUTHORITY,
        "exercise_id": "chart1-scissor-jump",
        "experiment": "ARM_MOVEMENT_ONLY_EDIT_RESCUE",
        "source_segment": "V12_ASTAR_TO_B002_APEX_ONLY",
        "source_video_sha256": RAW_V12_SHA256,
        "source_video_format": "H264_640X360_24FPS_72_FRAMES_WITH_AAC",
        "source_independent_qa_sha256": V12_QA_SHA256,
        "source_qa_verdict": "HOLD_WRONG_RUNNING_ARM_AND_CONTACT_MOTION",
        "source_ledger_run_id": V12_RUN_ID,
        "source_native_actual_credits": "3",
        "submitted_prompt_sha256": PROMPT_SHA256,
        "provider": "Google Flow", "model": FLOW_MODEL,
        "settings": dict(FLOW_SETTINGS), "max_quoted_credits": "3",
        "precredit_status": "EXPERIMENTAL_REQUIRES_NATIVE_V12_PROOF_AND_FRESH_FLOW_UI",
        "historical_anatomical_left_right_proven": False,
        "full_scissor_cycle_proven": False,
        "video_form_and_release_approval": "NOT_GRANTED",
    }


def _probe_video(path):
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30, check=True)
        streams = json.loads(probe.stdout)["streams"]
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
            AttributeError, KeyError, TypeError, ValueError) as exc:
        raise V13PreflightError("V12 source MP4 cannot be probed") from exc
    video = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    if (len(video) != 1 or len(audio) != 1
            or video[0].get("codec_name") != "h264"
            or (video[0].get("width"), video[0].get("height")) != (640, 360)
            or video[0].get("avg_frame_rate") != "24/1"
            or video[0].get("nb_frames") != "72"
            or video[0].get("duration") != "3.000000"
            or audio[0].get("codec_name") != "aac"):
        raise V13PreflightError("V12 raw media must be H264 640x360 24fps 72f/3s with original AAC")
    try:
        subprocess.run(
            ["ffmpeg", "-v", "error", "-xerror", "-err_detect", "explode",
             "-i", str(path), "-map", "0:v:0", "-f", "null", "-"],
            capture_output=True, timeout=45, check=True)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise V13PreflightError("V12 MP4 full-video decode failed") from exc


def verify_v12_source(spec_path, raw_video, independent_qa, ledger_store):
    spec, spec_bytes = _read_file(spec_path, "V13 arm-edit spec")
    if not _same(_json_bytes(spec_bytes, "V13 arm-edit spec"), expected_spec()):
        raise V13PreflightError("V13 spec differs from pinned arm-only experiment")
    video, raw_bytes = _read_file(raw_video, "exact original V12 raw MP4")
    qa, qa_bytes = _read_file(independent_qa, "final independent V12 HOLD QA")
    if _hash(raw_bytes) != RAW_V12_SHA256:
        raise V13PreflightError("V12 source video SHA-256 mismatch; no derivative substitution")
    if _hash(qa_bytes) != V12_QA_SHA256:
        raise V13PreflightError("V12 independent HOLD QA bytes differ from final pinned report")
    scene_match = _SCENE_LINE.search(qa_bytes.decode("utf-8"))
    if not scene_match or b"QA HOLD" not in qa_bytes:
        raise V13PreflightError("pinned QA lacks explicit V12 scene identity or HOLD verdict")
    _probe_video(video)
    try:
        audit = experiments.audit_receipts(ledger_store)
        if audit["verdict"] != "PASS_INTERNAL_RECEIPT_CONSISTENCY_ONLY":
            raise V13PreflightError("existing private Flow ledger has inconsistent native receipts")
        with experiments._locked_store(ledger_store) as store:
            policy = experiments._policy(store)
            source_intent = experiments._known_run(store, V12_RUN_ID)
            source_request = source_intent["request"]
            charge_file = store / "charges" / f"{V12_RUN_ID}.json"
            if charge_file.is_symlink():
                raise V13PreflightError("native V12 charge receipt is a symlink")
            charge = experiments._read(charge_file)
            snapshot = experiments._snapshot(store)
            artifact_dir = store / "artifacts" / V12_RUN_ID
            if artifact_dir.is_symlink() or not artifact_dir.is_dir():
                raise V13PreflightError("V12 raw-video immutable artifact receipts absent")
            raw_receipts = [(item, experiments._read(item)) for item in artifact_dir.glob("*.json")
                            if not item.is_symlink() and item.is_file()]
    except experiments.ExperimentError as exc:
        raise V13PreflightError(f"existing private ledger proof unavailable: {exc}") from exc
    assets = source_request.get("input_assets", [])
    if (policy.get("provider") != "Google Flow"
            or source_request.get("exercise_id") != "chart1-scissor-jump"
            or source_request.get("provider") != "Google Flow"
            or source_request.get("model") != FLOW_MODEL
            or not _same(source_request.get("settings"), V12_SETTINGS)
            or source_request.get("estimated_credits") != "3"
            or not isinstance(source_request.get("source_preflight"), dict)
            or source_request["source_preflight"].get("authority")
            != "V12_REVIEWED_APEX_B002_FRAMES_360P"
            or [(a.get("role"), a.get("sha256"), a.get("verification")) for a in assets] != [
                ("start-frame", "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38", "rehashed_from_local_bytes"),
                ("end-frame", "c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886", "rehashed_from_local_bytes"),
            ]):
        raise V13PreflightError("native V12 intent does not bind the pinned photographic Frames run")
    if (charge.get("run_id") != V12_RUN_ID
            or charge.get("release_status") != experiments.HOLD
            or charge.get("actual_credits") != "3"
            or charge.get("outcome") != "COMPLETED"
            or charge.get("provider_generation_id") != scene_match.group(1)):
        raise V13PreflightError("V12 native three-credit charge does not match independent scene identity")
    matching_raw = [(path, r) for path, r in raw_receipts
                    if r.get("proof", {}).get("run_id") == V12_RUN_ID
                    and r["proof"].get("role") == "raw-generated-video"
                    and r["proof"].get("sha256") == RAW_V12_SHA256
                    and r["proof"].get("size_bytes") == len(raw_bytes)
                    and r["proof"].get("verification") == "rehashed_from_local_bytes"]
    if len(matching_raw) != 1:
        raise V13PreflightError("exact original V12 raw MP4 lacks one matching immutable native artifact receipt")
    if any(_hash(file.read_bytes()) != digest for file, digest in
           ((spec, _hash(spec_bytes)), (video, RAW_V12_SHA256), (qa, V12_QA_SHA256))):
        raise V13PreflightError("V13 input source changed during qualification")
    return {
        "authority": AUTHORITY, "spec_sha256": _hash(spec_bytes),
        "source_video_sha256": RAW_V12_SHA256,
        "source_video_size_bytes": len(raw_bytes),
        "source_qa_sha256": V12_QA_SHA256,
        "source_qa_verdict": "HOLD",
        "source_ledger_run_id": V12_RUN_ID,
        "source_native_actual_credits": "3",
        "source_native_charge_receipt_sha256": _hash(charge_file.read_bytes()),
        "source_native_raw_artifact_receipt_sha256": _hash(matching_raw[0][0].read_bytes()),
        "source_scene_id": scene_match.group(1),
        "submitted_prompt_sha256": PROMPT_SHA256,
        "ledger_actual_credits": snapshot["actual_credits"],
        "ledger_pending_reserved_credits": snapshot["pending_reserved_credits"],
        "ledger_available_credits": snapshot["available_credits"],
        "video_motion_form_and_release_approval": "NOT_GRANTED",
    }


def verify_ui_observation(path, source_receipt):
    file, data = _read_file(path, "fresh actual Flow V2V edit observation")
    record = _json_bytes(data, "Flow V13 edit observation")
    exact = {"schema_version", "authority", "observed_at_utc", "operator",
             "provider", "model", "settings", "quoted_credits", "source_scene_id",
             "source_video_visible", "edit_prompt_interface_visible", "source_qa_hold_acknowledged",
             "project_silent_setting_on", "ledger_reconciled", "ledger_actual_credits",
             "ledger_pending_reserved_credits", "ledger_available_credits",
             "ui_evidence_path", "ui_evidence_sha256"}
    if (set(record) != exact or type(record["schema_version"]) is not int
            or record["schema_version"] != 1 or record["authority"] != UI_AUTHORITY):
        raise V13PreflightError("V13 requires exact fresh live video-edit and ledger attestation fields")
    if (record["provider"] != "Google Flow" or record["model"] != FLOW_MODEL
            or not _same(record["settings"], FLOW_SETTINGS)
            or record["source_scene_id"] != source_receipt["source_scene_id"]
            or any(record[field] is not True for field in (
                "source_video_visible", "edit_prompt_interface_visible",
                "source_qa_hold_acknowledged", "project_silent_setting_on", "ledger_reconciled"))):
        raise V13PreflightError("Flow V13 mode/model/source/silence/ledger not expressly confirmed")
    for name in ("actual_credits", "pending_reserved_credits", "available_credits"):
        if record[f"ledger_{name}"] != source_receipt[f"ledger_{name}"]:
            raise V13PreflightError("live-attested ledger differs from current immutable ledger snapshot")
    quote = record["quoted_credits"]
    if (not isinstance(quote, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", quote)
            or not Decimal("0") < Decimal(quote) <= QUOTE_CEILING
            or Decimal(quote) > Decimal(source_receipt["ledger_available_credits"])):
        raise V13PreflightError("fresh quoted edit cost exceeds 3 credits or available budget")
    if not isinstance(record["operator"], str) or not record["operator"].strip():
        raise V13PreflightError("V13 Flow observation lacks a named operator")
    try:
        observed = datetime.fromisoformat(record["observed_at_utc"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise V13PreflightError("V13 Flow observation needs exact UTC time") from exc
    if observed.tzinfo is None or observed.utcoffset().total_seconds() != 0:
        raise V13PreflightError("V13 Flow observation timestamp must be UTC")
    if not 0 <= (datetime.now(timezone.utc) - observed).total_seconds() <= 15 * 60:
        raise V13PreflightError("V13 live Flow edit quote is stale or from the future")
    if (not isinstance(record["ui_evidence_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", record["ui_evidence_sha256"])):
        raise V13PreflightError("V13 Flow UI observation missing screenshot SHA-256")
    evidence, evidence_bytes = _read_file(record["ui_evidence_path"], "fresh private V13 edit screenshot")
    if (evidence == file or not evidence_bytes
            or _hash(evidence_bytes) != record["ui_evidence_sha256"]):
        raise V13PreflightError("V13 Flow edit screenshot bytes missing or changed")
    if _hash(file.read_bytes()) != _hash(data) or _hash(evidence.read_bytes()) != _hash(evidence_bytes):
        raise V13PreflightError("V13 Flow observation altered during verification")
    return {
        **source_receipt, "provider": "Google Flow", "model": FLOW_MODEL,
        "settings": dict(FLOW_SETTINGS), "quoted_credits": quote,
        "flow_ui_observation_sha256": _hash(data),
        "flow_ui_observed_at_utc": record["observed_at_utc"],
        "precredit_result": "V12_NATIVE_VIDEO_AND_LIVE_V2V_EDIT_CONFIRMED_DIAGNOSTIC_ONLY",
        "video_motion_form_and_release_approval": "NOT_GRANTED",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only V13 exact V12 raw/video-edit precredit check")
    parser.add_argument("--request", required=True, help="Private V13 request JSON; never place in Git")
    args = parser.parse_args(argv)
    try:
        _, raw = _read_file(args.request, "private V13 generation request")
        request = _json_bytes(raw, "V13 generation request")
        checked = experiments._validate_request(request)
        if checked["source_preflight"]["authority"] != AUTHORITY:
            raise V13PreflightError("request must use the V13 arm-only Video-to-Video authority")
        # No private paths, scene IDs, prompt text or screenshot locators in output.
        print(json.dumps({
            "verdict": "PREFLIGHT_PASS_DIAGNOSTIC_RESERVATION_STILL_REQUIRED",
            "raw_source_sha256": checked["source_preflight"]["source_video_sha256"],
            "qa_report_sha256": checked["source_preflight"]["source_qa_sha256"],
            "source_qa_verdict": checked["source_preflight"]["source_qa_verdict"],
            "model": checked["model"], "settings": checked["settings"],
            "quoted_credits": checked["estimated_credits"],
            "precredit_result": checked["source_preflight"]["precredit_result"],
            "form_release_approval": "NOT_GRANTED",
        }, indent=2))
        return 0
    except (experiments.ExperimentError, V13PreflightError, OSError, TypeError, ValueError) as exc:
        print(f"V13 precredit HOLD: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
