"""V12 exact B*002 Frames source and pre-submit Flow observation gate.

Read-only. The V11 candidate gate is necessary but never by itself paid
authority. Provider tile/quote observations are operator assertions tied to
immutable bytes, not independent cryptographic proofs of a Flow upload.
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .apex_candidate_qa import check_candidate


class V12PreflightError(ValueError):
    """B* lineage, independent review or current Flow UI preflight is HOLD."""


AUTHORITY = "V12_REVIEWED_APEX_B002_FRAMES_360P"
FLOW_UI_AUTHORITY = "V12_FLOW_EXACT_ENDPOINTS_LIVE_QUOTE"
SOURCE_B_SHA256 = "c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886"
SOURCE_QA_SHA256 = "98c27fb67e174b3fae2dcf96a4851ce143865e7b51f4d21b9d8f2bb25775a145"
SOURCE_A_SHA256 = "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38"
V10_MANIFEST_SHA256 = "9271898a33bf54a2c15c722cc32145371431c593aea5ed92d110e81a88c4c100"
V10_QA_SHA256 = "63f790d95ed46ba3290784a0a4a0a9812c3aaa6f56038aaaf0b7548eb5fa15c7"
FLOW_MODEL = "Omni 1.2 Flash"
FLOW_QUOTE_CREDITS = "3"
FLOW_SETTINGS = {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": None, "generation_mode": "Frames to Video",
    "resolution": "360p", "return_silent_videos": True,
}
V10_PATHS = {"original_a_png", "original_c_png", "canvas_jpeg",
             "a_annotation", "c_annotation", "canvas_annotation",
             "shared_manifest", "derived_a_png", "derived_c_png",
             "independent_qa_report"}


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _strict_equal(actual, expected):
    """JSON type-stable comparison (bool must not pass for int or vice versa)."""
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def _read(path, label):
    item = Path(path).expanduser()
    if item.is_symlink():
        raise V12PreflightError(f"{label} must not be a symlink")
    item = item.resolve()
    if not item.is_file():
        raise V12PreflightError(f"{label} missing; no paid reservation")
    return item, item.read_bytes()


def _json(raw, label):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise V12PreflightError(f"duplicate {label} field")
            result[key] = value
        return result
    try:
        result = json.loads(raw, object_pairs_hook=unique)
    except (UnicodeDecodeError, ValueError) as exc:
        raise V12PreflightError(f"invalid {label} JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise V12PreflightError(f"{label} must be an object")
    return result


def expected_spec():
    return {
        "schema_version": 1, "authority": AUTHORITY,
        "exercise_id": "chart1-scissor-jump", "segment_role": "A_TO_B002_APEX",
        "start_pose": "A*", "end_pose": "B*002",
        "duration_seconds": 3, "aspect_ratio": "16:9",
        "provider": "Google Flow", "model": FLOW_MODEL,
        "generation_mode": "Frames to Video", "resolution": "360p",
        "variants": 1, "return_silent_videos": True,
        "quoted_credits": FLOW_QUOTE_CREDITS,
        "start_sha256": SOURCE_A_SHA256,
        "end_sha256": SOURCE_B_SHA256,
        "independent_b_qa_sha256": SOURCE_QA_SHA256,
        "reference_v10_manifest_sha256": V10_MANIFEST_SHA256,
        "reference_v10_qa_sha256": V10_QA_SHA256,
        "source_authority": "V10_REPLAYED_ASTAR_AND_V11_INDEPENDENT_B002_CANDIDATE",
        "parent_v6_card_status": "UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED",
        "anatomical_left_right_proven": False,
        "status": "EXPERIMENTAL_DIAGNOSTIC_ONLY_REQUIRES_FRESH_FLOW_UI_AND_LEDGER",
    }


def verify_sources(spec_path, v10_paths, b_apex_image, independent_b_qa):
    """Re-run unchanged V11/V10 byte and independent-still QA gates."""
    spec_file, spec_bytes = _read(spec_path, "V12 Frames specification")
    if not _strict_equal(_json(spec_bytes, "V12 Frames specification"), expected_spec()):
        raise V12PreflightError("V12 Frames spec differs from pinned B002 and 360p authority")
    if not isinstance(v10_paths, dict) or set(v10_paths) != V10_PATHS:
        raise V12PreflightError("V12 requires exact ten locally replayable V10 paths")
    b_file, b_bytes = _read(b_apex_image, "B*002 original image")
    qa_file, qa_bytes = _read(independent_b_qa, "B*002 independent source QA")
    if _sha(b_bytes) != SOURCE_B_SHA256 or _sha(qa_bytes) != SOURCE_QA_SHA256:
        raise V12PreflightError("B002 or its independent QA bytes differ from pinned accepted candidate")
    try:
        result = check_candidate(v10_paths, b_file, qa_file)
    except (OSError, ValueError, TypeError) as exc:
        raise V12PreflightError(f"V11 independent B002 candidate evidence is HOLD: {exc}") from exc
    if (result.get("b_sha256") != SOURCE_B_SHA256
            or result.get("independent_b_qa_sha256") != SOURCE_QA_SHA256
            or result.get("v10_manifest_sha256") != V10_MANIFEST_SHA256
            or result.get("paid_video_precredit_authority") != "NOT_GRANTED"
            or result.get("motion_video_release_approval") != "NOT_EVALUATED"):
        raise V12PreflightError("V11 independent source receipt does not match pinned B002 diagnostic-only evidence")
    for label, file, before in (("B002", b_file, _sha(b_bytes)),
                                ("B002 independent QA", qa_file, _sha(qa_bytes)),
                                ("V12 spec", spec_file, _sha(spec_bytes))):
        if _sha(file.read_bytes()) != before:
            raise V12PreflightError(f"{label} changed during qualification")
    return {
        "authority": AUTHORITY, "segment_role": "A_TO_B002_APEX",
        "spec_sha256": _sha(spec_bytes),
        "start_sha256": SOURCE_A_SHA256, "end_sha256": SOURCE_B_SHA256,
        "v10_manifest_sha256": V10_MANIFEST_SHA256,
        "v10_qa_sha256": V10_QA_SHA256,
        "independent_b_qa_sha256": SOURCE_QA_SHA256,
        "v11_source_review": "INDEPENDENT_CANDIDATE_FOR_DIAGNOSTIC_ONLY",
        "historical_anatomical_left_right": "UNKNOWN",
        "video_motion_form_and_release_approval": "NOT_EVALUATED",
    }


def verify_ui_observation(path, source_receipt):
    """Bind an *actual fresh human-observed* Flow input/price snapshot."""
    file, payload = _read(path, "fresh Flow input/quote observation")
    report = _json(payload, "Flow input/quote observation")
    exact = {"schema_version", "authority", "observed_at_utc", "operator",
             "provider", "model", "settings", "quoted_credits", "project_silent_setting_on",
             "start_tile", "end_tile", "ui_evidence_path", "ui_evidence_sha256",
             "ledger_reconciled"}
    if (set(report) != exact or type(report["schema_version"]) is not int
            or report["schema_version"] != 1 or report["authority"] != FLOW_UI_AUTHORITY):
        raise V12PreflightError("fresh Flow observation requires exact current UI and ledger fields")
    if (report["provider"] != "Google Flow" or report["model"] != FLOW_MODEL
            or not _strict_equal(report["settings"], FLOW_SETTINGS)
            or report["quoted_credits"] != FLOW_QUOTE_CREDITS
            or report["project_silent_setting_on"] is not True
            or report["ledger_reconciled"] is not True):
        raise V12PreflightError("Flow model/price/settings or reconciled ledger differ from live V12 quote")
    if (not isinstance(report["operator"], str) or not report["operator"].strip()
            or not isinstance(report["ui_evidence_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", report["ui_evidence_sha256"])):
        raise V12PreflightError("Flow observed UI evidence/operator identity missing")
    evidence_file, evidence_payload = _read(report["ui_evidence_path"], "fresh Flow UI evidence")
    if not evidence_payload or _sha(evidence_payload) != report["ui_evidence_sha256"]:
        raise V12PreflightError("Flow UI screenshot/observation evidence bytes differ from SHA-256")
    if evidence_file == file:
        raise V12PreflightError("Flow UI evidence must be distinct from its attestation")
    try:
        observed = datetime.fromisoformat(report["observed_at_utc"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise V12PreflightError("fresh Flow quote needs an explicit ISO 8601 UTC time") from exc
    if observed.tzinfo is None or observed.utcoffset().total_seconds() != 0:
        raise V12PreflightError("Flow UI observation timestamp must be UTC")
    elapsed_seconds = (datetime.now(timezone.utc) - observed).total_seconds()
    if not 0 <= elapsed_seconds <= 15 * 60:
        raise V12PreflightError("Flow UI quote/input observation is stale or in the future")
    for name, digest, pose in (("start_tile", SOURCE_A_SHA256, "A*"),
                               ("end_tile", SOURCE_B_SHA256, "B*002")):
        tile = report[name]
        if (not isinstance(tile, dict) or set(tile) != {
                "source_sha256", "pose", "flow_asset_id", "visually_confirmed"}
                or tile["source_sha256"] != digest or tile["pose"] != pose
                or tile["visually_confirmed"] is not True
                or not isinstance(tile["flow_asset_id"], str)
                or not tile["flow_asset_id"].strip()):
            raise V12PreflightError(f"Flow {name} is not an explicitly observed correct endpoint")
    if report["start_tile"]["flow_asset_id"] == report["end_tile"]["flow_asset_id"]:
        raise V12PreflightError("Flow A*/B002 must be two distinct displayed endpoint tiles")
    if _sha(file.read_bytes()) != _sha(payload) or _sha(evidence_file.read_bytes()) != _sha(evidence_payload):
        raise V12PreflightError("Flow UI observation changed during verification")
    return {**source_receipt,
            "provider": "Google Flow", "model": FLOW_MODEL,
            "settings": dict(FLOW_SETTINGS), "quoted_credits": FLOW_QUOTE_CREDITS,
            "flow_ui_observation_sha256": _sha(payload),
            "flow_ui_observed_at_utc": report["observed_at_utc"],
            "precredit_result": "EXACT_SOURCE_AND_FRESH_UI_ATTESTED_DIAGNOSTIC_ONLY",
            "video_motion_form_and_release_approval": "NOT_EVALUATED"}
