"""V14 A*->C* grounded-endpoint 360p Frames-to-Video precredit gate.

No Flow calls or ledger writes. Replays both V10 photographic source images,
checks their independent QA and the existing reconciled V12 charge ledger,
then requires a fresh operator observation of Flow's actual two Frames tiles.
Neither source QA nor an experiment reservation is exercise-form approval.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from . import experiments
from .preflight_v10_shared_canvas import (
    SharedCanvasPreflightError, verify_segment as verify_v10_segment,
)
from .preflight_v13_v2v import V12_RUN_ID


class V14PreflightError(ValueError):
    """Required photographic source, real Flow quote or existing ledger HOLD."""


AUTHORITY = "V14_GROUNDED_ASTAR_CSTAR_FRAMES_360P"
UI_AUTHORITY = "V14_FLOW_GROUNDED_ENDPOINTS_LIVE_QUOTE"
A_SHA256 = "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38"
C_SHA256 = "04eb4f9d9fe1d1944da36ba007fb7611329d19c19bddebfe983c8182a583e72b"
V10_MANIFEST_SHA256 = "9271898a33bf54a2c15c722cc32145371431c593aea5ed92d110e81a88c4c100"
V10_QA_SHA256 = "63f790d95ed46ba3290784a0a4a0a9812c3aaa6f56038aaaf0b7548eb5fa15c7"
HELD_OUT_APEX_SHA256 = "c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886"
PROMPT_SHA256 = "a4f61c6d258987981c4b25426a4d5fdc4580a61b758132aa68e59b5d1e3caaa0"
V12_NATIVE_CHARGE_SHA256 = "bc9ebb8cb46c61901d03bd1073ff456ca95427695e2d88841e6e6bb6159ef644"
V12_RAW_ARTIFACT_RECEIPT_SHA256 = "643d13d10a98822b8e0db8aca1abec9296303ae5e6d9dc6e4f0708bb789a4533"
FLOW_MODEL = "Omni 1.2 Flash"
FLOW_SETTINGS = {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": None, "generation_mode": "Frames to Video",
    "resolution": "360p", "return_silent_videos": True,
}
MAX_QUOTE_CREDITS = Decimal("3")  # Ceiling, not a claim about the live price.
V10_PATHS = {
    "original_a_png", "original_c_png", "canvas_jpeg", "a_annotation",
    "c_annotation", "canvas_annotation", "shared_manifest",
    "derived_a_png", "derived_c_png", "independent_qa_report",
}


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _same(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _read(path, label):
    item = Path(path).expanduser()
    if item.is_symlink():
        raise V14PreflightError(f"{label} must not be a symlink")
    item = item.resolve()
    if not item.is_file():
        raise V14PreflightError(f"{label} missing; no paid reservation")
    return item, item.read_bytes()


def _json(payload, label):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise V14PreflightError(f"duplicate {label} field")
            value[key] = item
        return value
    try:
        result = json.loads(payload, object_pairs_hook=unique)
    except (UnicodeDecodeError, ValueError) as exc:
        raise V14PreflightError(f"invalid {label}: {exc}") from exc
    if not isinstance(result, dict):
        raise V14PreflightError(f"{label} must be an object")
    return result


def expected_spec():
    return {
        "schema_version": 1, "authority": AUTHORITY,
        "exercise_id": "chart1-scissor-jump", "segment_role": "A_TO_C_GROUNDED",
        "start_pose": "A* grounded", "end_pose": "C* opposite grounded",
        "phase_hypothesis": "ONE_PUSH_OFF_ONE_AIRBORNE_EXCHANGE_OPPOSITE_GROUNDED_LANDING",
        "source_defect": "V12_INSERTED_GROUNDED_RUNNING_STEPS_BEFORE_LATE_APEX",
        "duration_seconds": 3, "aspect_ratio": "16:9",
        "provider": "Google Flow", "model": FLOW_MODEL,
        "settings": dict(FLOW_SETTINGS), "max_quoted_credits": str(MAX_QUOTE_CREDITS),
        "start_sha256": A_SHA256, "end_sha256": C_SHA256,
        "reference_v10_manifest_sha256": V10_MANIFEST_SHA256,
        "reference_v10_independent_qa_sha256": V10_QA_SHA256,
        "held_out_apex_sha256_not_generation_input": HELD_OUT_APEX_SHA256,
        "submitted_prompt_sha256": PROMPT_SHA256,
        "source_authority": "EXACT_REPLAYED_V10_ASTAR_CSTAR_DERIVED_PHOTOGRAPHIC_ENDPOINTS",
        "parent_v6_card_status": "UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED",
        "anatomical_left_right_proven": False,
        "full_scissor_cycle_proven": False,
        "video_form_and_release_approval": "NOT_GRANTED",
        "status": "EXPERIMENTAL_FRESH_FLOW_UI_AND_SAME_NATIVE_LEDGER_REQUIRED",
    }


def verify_sources(spec_path, v10_paths):
    """Replay V10 A*/C* from actual input bytes; not hash labels alone."""
    spec_file, spec_bytes = _read(spec_path, "V14 specification")
    if not _same(_json(spec_bytes, "V14 specification"), expected_spec()):
        raise V14PreflightError("V14 specification differs from the pinned grounded-endpoint test")
    if not isinstance(v10_paths, dict) or set(v10_paths) != V10_PATHS:
        raise V14PreflightError("V14 requires all ten exact replayable V10 source/QA paths")
    v10_spec = Path(__file__).resolve().parent / "segment_specs" / "chart1-scissor-v10-astar-to-cstar.json"
    try:
        checked = verify_v10_segment(
            v10_spec, v10_paths["original_a_png"], v10_paths["original_c_png"],
            v10_paths["canvas_jpeg"], v10_paths["shared_manifest"],
            v10_paths["derived_a_png"], v10_paths["derived_c_png"],
            a_annotation=v10_paths["a_annotation"],
            c_annotation=v10_paths["c_annotation"],
            canvas_annotation=v10_paths["canvas_annotation"],
            independent_qa_report=v10_paths["independent_qa_report"],
            expected_role="A_TO_C")
    except (SharedCanvasPreflightError, OSError, ValueError, TypeError) as exc:
        raise V14PreflightError(f"V10 exact photographic source replay HOLD: {exc}") from exc
    pinned = (("derived_a_png", A_SHA256), ("derived_c_png", C_SHA256),
              ("shared_manifest", V10_MANIFEST_SHA256),
              ("independent_qa_report", V10_QA_SHA256))
    observed = {name: _read(v10_paths[name], name) for name, _ in pinned}
    if (any(_sha(observed[name][1]) != digest for name, digest in pinned)
            or checked.get("start_sha256") != A_SHA256
            or checked.get("end_sha256") != C_SHA256
            or checked.get("shared_canvas_manifest_sha256") != V10_MANIFEST_SHA256
            or checked.get("independent_source_qa_report_sha256") != V10_QA_SHA256
            or checked.get("deterministic_replay") != "EXACT_BYTE_REPLAY_PASS"
            or checked.get("independent_source_qa") != "CANDIDATE_FOR_DIAGNOSTIC_ONLY"
            or checked.get("parent_v6_card_status") != "UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED"
            or checked.get("anatomical_left_right_proven") is not False
            or checked.get("video_motion_form_and_release_approval") != "NOT_EVALUATED"):
        raise V14PreflightError("V10 corrected manifest/output/independent QA does not match pinned A*/C* source")
    for name, (file, payload) in observed.items():
        if _sha(file.read_bytes()) != _sha(payload):
            raise V14PreflightError(f"{name} changed during qualification")
    if _sha(spec_file.read_bytes()) != _sha(spec_bytes):
        raise V14PreflightError("V14 specification changed during qualification")
    return {
        "authority": AUTHORITY, "spec_sha256": _sha(spec_bytes),
        "segment_role": "A_TO_C_GROUNDED",
        "start_sha256": A_SHA256, "end_sha256": C_SHA256,
        "v10_manifest_sha256": V10_MANIFEST_SHA256,
        "v10_independent_qa_sha256": V10_QA_SHA256,
        "deterministic_source_replay": "EXACT_BYTE_REPLAY_PASS",
        "source_qa": "CANDIDATE_FOR_DIAGNOSTIC_ONLY",
        "held_out_apex_sha256": HELD_OUT_APEX_SHA256,
        "historical_anatomical_left_right": "UNKNOWN",
        "video_motion_form_and_release_approval": "NOT_GRANTED",
    }


def verify_existing_ledger(path):
    """Require the *actual* prior native V12 debit and artifact, not a new cap."""
    try:
        audit = experiments.audit_receipts(path)
        if audit["verdict"] != "PASS_INTERNAL_RECEIPT_CONSISTENCY_ONLY":
            raise V14PreflightError("existing Flow ledger receipt audit HOLD")
        with experiments._locked_store(path) as store:
            policy = experiments._policy(store)
            previous = experiments._known_run(store, V12_RUN_ID)
            charge_file = store / "charges" / f"{V12_RUN_ID}.json"
            if charge_file.is_symlink():
                raise V14PreflightError("native V12 charge receipt is a symlink")
            charge = experiments._read(charge_file)
            artifacts = store / "artifacts" / V12_RUN_ID
            if artifacts.is_symlink() or not artifacts.is_dir():
                raise V14PreflightError("native V12 raw-video receipt folder missing")
            artifact_receipts = [file for file in artifacts.glob("*.json")
                                 if file.is_file() and not file.is_symlink()]
            snapshot = experiments._snapshot(store)
        if (policy.get("provider") != "Google Flow"
                or previous.get("release_status") != experiments.HOLD
                or previous.get("request", {}).get("exercise_id") != "chart1-scissor-jump"
                or previous["request"].get("source_preflight", {}).get("authority")
                != "V12_REVIEWED_APEX_B002_FRAMES_360P"
                or charge.get("run_id") != V12_RUN_ID
                or charge.get("actual_credits") != "3"
                or charge.get("release_status") != experiments.HOLD
                or charge.get("outcome") != "COMPLETED"
                or _sha(charge_file.read_bytes()) != V12_NATIVE_CHARGE_SHA256
                or sum(_sha(file.read_bytes()) == V12_RAW_ARTIFACT_RECEIPT_SHA256
                       for file in artifact_receipts) != 1):
            raise V14PreflightError("V12 native three-credit/immutable-artifact provenance absent from this ledger")
    except (experiments.ExperimentError, KeyError, OSError, TypeError, ValueError) as exc:
        if isinstance(exc, V14PreflightError):
            raise
        raise V14PreflightError(f"same existing native Flow debit ledger unavailable: {exc}") from exc
    return {f"ledger_{key}": snapshot[key] for key in
            ("actual_credits", "pending_reserved_credits", "available_credits")}


def verify_ui_observation(path, source_receipt):
    """Do not turn an inferred model price or tile name into paid authority."""
    file, payload = _read(path, "fresh Flow V14 quote observation")
    report = _json(payload, "Flow V14 quote observation")
    exact = {"schema_version", "authority", "observed_at_utc", "operator",
             "provider", "model", "settings", "quoted_credits", "start_tile",
             "end_tile", "only_two_endpoints_selected", "project_silent_setting_on",
             "ledger_reconciled", "ledger_actual_credits", "ledger_pending_reserved_credits",
             "ledger_available_credits", "ui_evidence_path", "ui_evidence_sha256"}
    if (set(report) != exact or type(report["schema_version"]) is not int
            or report["schema_version"] != 1 or report["authority"] != UI_AUTHORITY):
        raise V14PreflightError("V14 needs exact fresh real Flow endpoint/ledger evidence fields")
    if (report["provider"] != "Google Flow" or report["model"] != FLOW_MODEL
            or not _same(report["settings"], FLOW_SETTINGS)
            or any(report[key] is not True for key in (
                "only_two_endpoints_selected", "project_silent_setting_on", "ledger_reconciled"))):
        raise V14PreflightError("Flow V14 model/settings/selected endpoints/silence/ledger attestation differ")
    quote = report["quoted_credits"]
    if (not isinstance(quote, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", quote)
            or not Decimal("0") < Decimal(quote) <= MAX_QUOTE_CREDITS
            or Decimal(quote) > Decimal(source_receipt["ledger_available_credits"])):
        raise V14PreflightError("V14 needs a current positive quote ≤3 within existing available credits")
    if not isinstance(report["operator"], str) or not report["operator"].strip():
        raise V14PreflightError("V14 observed Flow operator missing")
    try:
        observed = datetime.fromisoformat(report["observed_at_utc"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise V14PreflightError("V14 Flow observation needs a valid UTC time") from exc
    if (observed.tzinfo is None or observed.utcoffset().total_seconds() != 0
            or not 0 <= (datetime.now(timezone.utc) - observed).total_seconds() <= 15 * 60):
        raise V14PreflightError("V14 Flow observation missing UTC or is stale/future")
    for name, pose, digest in (("start_tile", "A*", A_SHA256),
                               ("end_tile", "C*", C_SHA256)):
        tile = report[name]
        if (not isinstance(tile, dict) or set(tile) != {
                "pose", "source_sha256", "flow_asset_id", "visually_confirmed"}
                or tile["pose"] != pose or tile["source_sha256"] != digest
                or tile["visually_confirmed"] is not True
                or not isinstance(tile["flow_asset_id"], str) or not tile["flow_asset_id"].strip()):
            raise V14PreflightError(f"Flow {name} not verified as the correct exact selected photo")
    if report["start_tile"]["flow_asset_id"] == report["end_tile"]["flow_asset_id"]:
        raise V14PreflightError("Flow A*/C* selected endpoints must have distinct asset IDs")
    for name in ("actual_credits", "pending_reserved_credits", "available_credits"):
        if report[f"ledger_{name}"] != source_receipt[f"ledger_{name}"]:
            raise V14PreflightError("live V14 ledger attestation differs from native receipts")
    screenshot, screenshot_bytes = _read(report["ui_evidence_path"], "V14 private Flow screenshot")
    if (screenshot == file or not screenshot_bytes
            or not isinstance(report["ui_evidence_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", report["ui_evidence_sha256"])
            or _sha(screenshot_bytes) != report["ui_evidence_sha256"]):
        raise V14PreflightError("V14 Flow screenshot differs from its exact private SHA-256")
    if _sha(file.read_bytes()) != _sha(payload) or _sha(screenshot.read_bytes()) != _sha(screenshot_bytes):
        raise V14PreflightError("V14 UI attestation changed during qualification")
    return {**source_receipt, "provider": "Google Flow", "model": FLOW_MODEL,
            "settings": dict(FLOW_SETTINGS), "quoted_credits": quote,
            "flow_ui_observation_sha256": _sha(payload),
            "flow_ui_observed_at_utc": report["observed_at_utc"],
            "precredit_result": "EXACT_ASTAR_CSTAR_AND_FRESH_GROUNDED_ENDPOINT_UI_DIAGNOSTIC_ONLY",
            "video_motion_form_and_release_approval": "NOT_GRANTED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only V14 A* to grounded C* source/Flow precredit gate")
    parser.add_argument("--request", required=True, help="private exact V14 request; do not commit")
    args = parser.parse_args(argv)
    try:
        _, raw = _read(args.request, "private V14 request")
        request = _json(raw, "private V14 request")
        checked = experiments._validate_request(request)
        if checked["source_preflight"]["authority"] != AUTHORITY:
            raise V14PreflightError("request does not use V14 grounded-endpoint authority")
        print(json.dumps({
            "verdict": "PREFLIGHT_PASS_DIAGNOSTIC_RESERVATION_STILL_REQUIRED",
            "source_replay": checked["source_preflight"]["deterministic_source_replay"],
            "start_sha256": checked["source_preflight"]["start_sha256"],
            "end_sha256": checked["source_preflight"]["end_sha256"],
            "model": checked["model"], "settings": checked["settings"],
            "quoted_credits": checked["estimated_credits"],
            "form_release_approval": "NOT_GRANTED",
        }, indent=2))
        return 0
    except (experiments.ExperimentError, V14PreflightError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"V14 precredit HOLD: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
