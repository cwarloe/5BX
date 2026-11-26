"""Read-only V15 synthetic-motion Ingredients feasibility gate.

This gates one experimental *method* test, not new 5BX production/form
authority. No Flow calls, credits, uploads, ledger writes, or consent claims.
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
from . import preflight_v14_grounded as v14


class V15PreflightError(ValueError):
    """Experimental V15 source/provider provenance HOLD."""


AUTHORITY = "V15_SYNTHETIC_MOTION_GUIDE_INGREDIENTS_360P_EXPERIMENTAL"
UI_AUTHORITY = "V15_FLOW_TWO_INGREDIENTS_LIVE_QUOTE"
MODEL = "Omni 1.2 Flash"
SETTINGS = {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": None, "generation_mode": "Ingredients",
    "resolution": "360p", "return_silent_videos": True,
}
MAX_CREDITS = Decimal("3")  # Ceiling, never a substituted live price.
IMAGE_SHA256 = v14.A_SHA256
GUIDE_SHA256 = "1a8fb1c47ef5de21cfe0b519815f81b8cd97771ff12b8ceda02124cf86c06b5d"
GUIDE_SIDECAR_SHA256 = "7fc18c45223aaca4b9e72c502aae2d78d410e78a8dd1a71dfef1f4bbac229cab"
GUIDE_SCRIPT_SHA256 = "c9d30d5af5553150f599eca4f1e33111b04b1068c7ecde5ad8644d5f3706a090"
PROMPT_SHA256 = "e481d4d1015cb01799869b003b9df23995e1bacef1756b089a441782cc017208"
V14_RUN_ID = "4c769f1031440c470eee93013e743c739f20fdc2f58a8a6adf7419b3654476db"
GUIDE_WINDOWS = ((12, 21), (40, 48))  # One-based inclusive; assertions, not human form evidence.


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _read(path, label):
    item = Path(path).expanduser()
    if item.is_symlink() or not item.is_file():
        raise V15PreflightError(f"{label} missing or symlink; HOLD")
    item = item.resolve()
    payload = item.read_bytes()
    if not payload:
        raise V15PreflightError(f"{label} is empty")
    return item, payload


def _json(raw, label):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise V15PreflightError(f"duplicate {label} field")
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=unique)
    except (ValueError, UnicodeError) as exc:
        raise V15PreflightError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise V15PreflightError(f"{label} must be a JSON object")
    return value


def _same(first, second):
    return json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def expected_spec():
    return {
        "schema_version": 1, "authority": AUTHORITY,
        "exercise_id": "chart1-scissor-jump",
        "method": "VIDEO_INGREDIENTS_PHOTOGRAPHIC_IDENTITY_PLUS_NEUTRAL_3D_MOTION",
        "source_defect": "V12_V14_GROUNDED_RUNNING_INSTEAD_OF_TWO_SCISSOR_FLIGHTS",
        "hypothesis": "CAN_MODEL_TRANSFER_TWO_JUMPS_FROM_NEUTRAL_GUIDE_TO_FIXED_PHOTO_IDENTITY",
        "provider": "Google Flow", "model": MODEL,
        "settings": dict(SETTINGS), "max_quoted_credits": str(MAX_CREDITS),
        "identity_image_sha256": IMAGE_SHA256,
        "guide_video_sha256": GUIDE_SHA256,
        "guide_manifest_sha256": GUIDE_SIDECAR_SHA256,
        "guide_generator_script_sha256": GUIDE_SCRIPT_SHA256,
        "guide_airborne_windows_1_based": [list(w) for w in GUIDE_WINDOWS],
        "submitted_prompt_sha256": PROMPT_SHA256,
        "identity_source": "REPLAYED_V10_ASTAR_EXPERIMENTAL_DERIVATIVE",
        "guide_source": "ORIGINAL_DETERMINISTIC_NONHUMAN_BLENDER_MANNEQUIN",
        "human_motion_capture": False, "human_form_verified": False,
        "parent_v6_crop_byte_replay_verified": False,
        "photographic_video_release_approval": "NOT_GRANTED",
        "status": "EXPERIMENTAL_METHOD_TEST_REQUIRES_FRESH_FLOW_AND_LEDGER",
    }


def _run_json(args, label):
    try:
        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 check=False, timeout=45)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise V15PreflightError(f"{label} unavailable or timed out") from exc
    if process.returncode != 0:
        raise V15PreflightError(f"{label} failed; no credit authority")
    return _json(process.stdout, label)


def verify_guide_video(path, *, expected_sha=GUIDE_SHA256):
    """Full-decode one H.264 test reference; no synthetic form certification."""
    movie, original = _read(path, "original procedural motion-reference MP4")
    if _digest(original) != expected_sha:
        raise V15PreflightError("motion-reference MP4 SHA mismatch")
    probe = _run_json([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,codec_name,profile,pix_fmt,width,height,r_frame_rate,nb_frames",
        "-of", "json", str(movie)], "motion-reference ffprobe")
    streams = probe.get("streams", [])
    if (not isinstance(streams, list) or len(streams) != 1
            or streams[0] != {
                "codec_name": "h264", "profile": "High", "codec_type": "video",
                "width": 640, "height": 360, "pix_fmt": "yuv420p",
                "r_frame_rate": "24/1", "nb_frames": "72",
            } or probe.get("format", {}).get("duration") != "3.000000"):
        raise V15PreflightError("motion-reference video format/duration/audio deviates")
    try:
        decoded = subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(movie),
            "-map", "0:v:0", "-an", "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise V15PreflightError("full motion-reference MP4 decode unavailable") from exc
    frame_bytes = 640 * 360 * 3
    if decoded.returncode != 0 or len(decoded.stdout) != 72 * frame_bytes:
        raise V15PreflightError("motion-reference full video decode/frame count HOLD")
    if decoded.stdout[:frame_bytes] != decoded.stdout[-frame_bytes:]:
        raise V15PreflightError("motion-reference first/last decoded frame seam differs")
    if _digest(movie.read_bytes()) != _digest(original):
        raise V15PreflightError("motion-reference MP4 mutated during preflight")
    return {"motion_video_sha256": expected_sha, "duration_seconds": 3,
            "frame_count": 72, "decoded_rgb_loop_seam": "EXACT", "no_audio_stream": True}


def _verify_guide_sidecar(path, qa_path, code_path):
    manifest_path, raw = _read(path, "procedural joints/contact sidecar")
    qa_file, qa_raw = _read(qa_path, "procedural mechanical QA")
    script, script_raw = _read(code_path, "procedural Blender source")
    if (_digest(raw) != GUIDE_SIDECAR_SHA256
            or _digest(script_raw) != GUIDE_SCRIPT_SHA256):
        raise V15PreflightError("procedural sidecar or generator source SHA mismatch")
    data = _json(raw, "procedural contact sidecar")
    qa = _json(qa_raw, "procedural mechanical QA")
    if (data.get("frame_count") != 72 or data.get("fps") != 24
            or data.get("duration_seconds") != 3.0
            or not data.get("camera", {}).get("locked")
            or not isinstance(data.get("frames"), list) or len(data["frames"]) != 72
            or qa.get("status") != "PASS_TECHNICAL_ONLY"
            or qa.get("errors") != []
            or qa.get("metrics", {}).get("keyframed_h264_high_yuv420p_sha256") != GUIDE_SHA256
            or qa.get("metrics", {}).get("keyframed_h264_high_yuv420p_exact_decoded_loop") is not True):
        raise V15PreflightError("procedural 72-frame contact/camera/QA evidence HOLD")
    both_airborne = []
    for index, frame in enumerate(data["frames"], 1):
        if frame.get("frame_1_based") != index:
            raise V15PreflightError("nonsequential procedural frame evidence")
        grounded = frame.get("grounded", {})
        clearance = frame.get("sole_clearance_m", {})
        if set(grounded) != {"left", "right"} or set(clearance) != {"left", "right"}:
            raise V15PreflightError("incomplete physical left/right contact evidence")
        if (not grounded["left"] and not grounded["right"]
                and clearance["left"] > 0 and clearance["right"] > 0):
            both_airborne.append(index)
    expected = [i for low, high in GUIDE_WINDOWS for i in range(low, high + 1)]
    if both_airborne != expected:
        raise V15PreflightError("procedural two-flight physical contact windows differ")
    if any(not data["frames"][frame]["grounded"][leg]
           for frame in (0, 71) for leg in ("left", "right")):
        raise V15PreflightError("motion guide endpoints are not both grounded")
    for index, phase, shoe_sign, arm_sign in (
            (0, "A_grounded", 1, -1), (26, "C_grounded", -1, 1),
            (71, "A_recovered", 1, -1)):
        frame = data["frames"][index]
        joints = frame.get("joints_world_m")
        if not isinstance(joints, dict) or frame.get("phase") != phase or frame.get("right_left_anatomy_is_explicit") is not True:
            raise V15PreflightError("synthetic physical A/C/A phase or side ownership missing")
        try:
            shoe_delta = joints["right_shoe"][0] - joints["left_shoe"][0]
            arm_delta = joints["right_wrist"][0] - joints["left_wrist"][0]
        except (KeyError, TypeError, IndexError) as exc:
            raise V15PreflightError("synthetic physical limb ownership coordinates incomplete") from exc
        if shoe_delta * shoe_sign <= 0 or arm_delta * arm_sign <= 0:
            raise V15PreflightError("synthetic A/C/A physical limb ownership did not reverse")
    metrics = qa["metrics"]
    if (metrics.get("both_shoes_airborne_frame_windows_1_based_inclusive")
            != [list(w) for w in GUIDE_WINDOWS]
            or metrics.get("maximum_horizontal_grounded_shoe_slip_m") != 0
            or metrics.get("min_elbow_interior_angle_deg", 0) < 175):
        raise V15PreflightError("procedural mechanical QA claims contradicted")
    for file, payload in ((manifest_path, raw), (qa_file, qa_raw), (script, script_raw)):
        if _digest(file.read_bytes()) != _digest(payload):
            raise V15PreflightError("procedural evidence mutated during preflight")
    return {"motion_manifest_sha256": _digest(raw), "generator_script_sha256": _digest(script_raw),
            "mechanical_qa_sha256": _digest(qa_raw), "both_shoes_airborne_windows": [list(w) for w in GUIDE_WINDOWS]}


def verify_sources(spec_path, paths):
    """Replay photographic A* and two independent deterministic guide encodes."""
    spec_file, spec_raw = _read(spec_path, "V15 specification")
    if not _same(_json(spec_raw, "V15 specification"), expected_spec()):
        raise V15PreflightError("V15 specification/prompt/source pins differ")
    exact = {"v10_source_paths", "motion_guide_mp4", "motion_guide_replay_mp4",
             "motion_sidecar", "motion_replay_sidecar", "motion_qa_report",
             "motion_generator_script"}
    if not isinstance(paths, dict) or set(paths) != exact:
        raise V15PreflightError("seven exact independent guide/photographic source-chain fields required")
    try:
        v14_spec = Path(__file__).resolve().parent / "segment_specs" / "chart1-scissor-v14-astar-to-cstar-grounded.json"
        photo = v14.verify_sources(v14_spec, paths["v10_source_paths"])
    except (v14.V14PreflightError, OSError, TypeError, ValueError) as exc:
        raise V15PreflightError(f"V10 photographic identity source replay HOLD: {exc}") from exc
    if photo["start_sha256"] != IMAGE_SHA256:
        raise V15PreflightError("photographic A* identity source differs")
    guide = verify_guide_video(paths["motion_guide_mp4"])
    replay_file, replay_bytes = _read(paths["motion_guide_replay_mp4"], "independent procedural render")
    movie_file, _ = _read(paths["motion_guide_mp4"], "preferred procedural render")
    if (replay_file == movie_file or _digest(replay_bytes) != GUIDE_SHA256):
        raise V15PreflightError("second independent procedural render absent or differs")
    sidecar_file, sidecar_bytes = _read(paths["motion_replay_sidecar"], "independent procedural contact sidecar")
    original_sidecar_file, _ = _read(paths["motion_sidecar"], "procedural contact sidecar")
    if (sidecar_file == original_sidecar_file or _digest(sidecar_bytes) != GUIDE_SIDECAR_SHA256):
        raise V15PreflightError("second independent procedural contact evidence differs")
    guide.update(_verify_guide_sidecar(paths["motion_sidecar"], paths["motion_qa_report"],
                                        paths["motion_generator_script"]))
    if (_digest(replay_file.read_bytes()) != GUIDE_SHA256
            or _digest(sidecar_file.read_bytes()) != GUIDE_SIDECAR_SHA256
            or _digest(spec_file.read_bytes()) != _digest(spec_raw)):
        raise V15PreflightError("procedural replay or spec changed during preflight")
    return {
        "authority": AUTHORITY, "spec_sha256": _digest(spec_raw),
        "identity_image_sha256": IMAGE_SHA256, **guide,
        "photographic_identity_source_replay": "EXACT_BYTE_REPLAY_PASS",
        "motion_guide_replay": "TWO_INDEPENDENT_BYTE_IDENTICAL_RENDERS",
        "nonhuman_source_only": True, "human_motion_form_approval": "NOT_EVALUATED",
        "video_motion_form_and_release_approval": "NOT_GRANTED",
    }


def verify_existing_ledger(path):
    """Inspect the existing native-charge ledger; never initialize a new one."""
    try:
        snapshot = v14.verify_existing_ledger(path)
        with experiments._locked_store(path) as store:
            previous = experiments._known_run(store, V14_RUN_ID)
            charge = experiments._read(store / "charges" / f"{V14_RUN_ID}.json")
        if (previous.get("release_status") != experiments.HOLD
                or charge.get("run_id") != V14_RUN_ID or charge.get("actual_credits") != "3"
                or charge.get("outcome") != "COMPLETED"
                or charge.get("release_status") != experiments.HOLD):
            raise V15PreflightError("V14 native charge/held method failure not preserved")
    except (experiments.ExperimentError, v14.V14PreflightError, KeyError, OSError, TypeError) as exc:
        raise V15PreflightError(f"reconciled existing Flow ledger HOLD: {exc}") from exc
    return snapshot


def verify_ui_observation(path, source_receipt):
    """Only a *fresh post-asset* actual quote counts; never infer Flow price."""
    file, raw = _read(path, "fresh post-asset Flow Ingredients observation")
    report = _json(raw, "fresh Flow Ingredients observation")
    exact = {"schema_version", "authority", "observed_at_utc", "operator",
             "provider", "model", "settings", "quoted_credits", "identity_tile",
             "motion_video_tile", "only_two_ingredients_selected", "no_frames_endpoints",
             "project_silent_setting_on", "ledger_reconciled", "ledger_actual_credits",
             "ledger_pending_reserved_credits", "ledger_available_credits",
             "ui_evidence_path", "ui_evidence_sha256", "post_asset_quote_confirmed"}
    if set(report) != exact or type(report.get("schema_version")) is not int or report.get("schema_version") != 1 or report.get("authority") != UI_AUTHORITY:
        raise V15PreflightError("V15 requires exact fresh two-ingredient UI fields")
    if (report["provider"] != "Google Flow" or report["model"] != MODEL
            or not _same(report["settings"], SETTINGS)
            or any(report[k] is not True for k in (
                "only_two_ingredients_selected", "no_frames_endpoints", "post_asset_quote_confirmed",
                "project_silent_setting_on", "ledger_reconciled"))):
        raise V15PreflightError("Flow Ingredients model/mode/settings/selection/silence HOLD")
    quote = report["quoted_credits"]
    if (not isinstance(quote, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", quote)
            or not Decimal(0) < Decimal(quote) <= MAX_CREDITS
            or Decimal(quote) > Decimal(source_receipt["ledger_available_credits"])):
        raise V15PreflightError("positive fresh post-asset Ingredients quote <=3 required")
    if not isinstance(report["operator"], str) or not report["operator"].strip():
        raise V15PreflightError("Flow operator missing")
    try:
        when = datetime.fromisoformat(report["observed_at_utc"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise V15PreflightError("Flow UTC observation invalid") from exc
    if when.tzinfo is None or when.utcoffset().total_seconds() != 0 or not 0 <= (datetime.now(timezone.utc) - when).total_seconds() <= 900:
        raise V15PreflightError("Flow post-asset Ingredients UI observation stale/future/non-UTC")
    for name, typ, digest in (("identity_tile", "image", IMAGE_SHA256),
                              ("motion_video_tile", "video", GUIDE_SHA256)):
        tile = report[name]
        if (not isinstance(tile, dict) or set(tile) != {"asset_kind", "source_sha256", "flow_asset_id", "visually_confirmed"}
                or tile["asset_kind"] != typ or tile["source_sha256"] != digest
                or tile["visually_confirmed"] is not True
                or not isinstance(tile["flow_asset_id"], str) or not tile["flow_asset_id"].strip()):
            raise V15PreflightError(f"Flow {name} does not match selected exact visual source")
    if report["identity_tile"]["flow_asset_id"] == report["motion_video_tile"]["flow_asset_id"]:
        raise V15PreflightError("two Ingredients must use distinct actual Flow assets")
    for key in ("actual_credits", "pending_reserved_credits", "available_credits"):
        if report[f"ledger_{key}"] != source_receipt[f"ledger_{key}"]:
            raise V15PreflightError("Flow quote ledger snapshot drifted")
    screenshot, screenshot_bytes = _read(report["ui_evidence_path"], "private post-asset Flow screenshot")
    if (screenshot == file or not isinstance(report["ui_evidence_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", report["ui_evidence_sha256"])
            or _digest(screenshot_bytes) != report["ui_evidence_sha256"]):
        raise V15PreflightError("private Flow screenshot SHA mismatch")
    if _digest(file.read_bytes()) != _digest(raw) or _digest(screenshot.read_bytes()) != _digest(screenshot_bytes):
        raise V15PreflightError("Flow UI evidence changed during preflight")
    return {
        **source_receipt, "provider": "Google Flow", "model": MODEL,
        "settings": dict(SETTINGS), "quoted_credits": quote,
        "flow_ui_observation_sha256": _digest(raw),
        "flow_ui_observed_at_utc": report["observed_at_utc"],
        "precredit_result": "TWO_INGREDIENT_SYNTHETIC_MOTION_METHOD_FEASIBILITY_ONLY",
        "video_motion_form_and_release_approval": "NOT_GRANTED",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only V15 synthetic motion/photographic Flow Ingredients preflight")
    parser.add_argument("--request", required=True, help="private experiment request outside Git")
    args = parser.parse_args(argv)
    try:
        _, raw = _read(args.request, "private V15 request")
        request = _json(raw, "private V15 request")
        checked = experiments._validate_request(request)
        if checked["source_preflight"]["authority"] != AUTHORITY:
            raise V15PreflightError("V15 authority missing")
        print(json.dumps({
            "verdict": "EXPERIMENTAL_METHOD_PREFLIGHT_PASS_RESERVATION_STILL_REQUIRED",
            "identity_sha256": checked["source_preflight"]["identity_image_sha256"],
            "motion_guide_sha256": checked["source_preflight"]["motion_video_sha256"],
            "model": checked["model"], "settings": checked["settings"],
            "quoted_credits": checked["estimated_credits"],
            "human_motion_reference": "NO", "form_release_approval": "NOT_GRANTED",
        }, indent=2))
        return 0
    except (experiments.ExperimentError, V15PreflightError, OSError, TypeError, ValueError, KeyError) as exc:
        print(f"V15 exploratory precredit HOLD: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
