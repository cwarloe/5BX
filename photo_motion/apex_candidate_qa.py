"""Read-only V11 photographic B* apex candidate preflight; never grants credits.

The static marker/clearance measurements are independently supplied human
observations, not automatic pose detection or historical form approval.
"""

import argparse
import hashlib
import io
import json
import math
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .preflight_v10_shared_canvas import verify_segment as verify_v10_pair


class ApexCandidateError(ValueError):
    """Missing source bytes, stale QA, or a non-apex photographic candidate."""


AUTHORITY = "V11_APEX_CANDIDATE_READ_ONLY"
A_STAR_SHA256 = "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38"
C_STAR_SHA256 = "04eb4f9d9fe1d1944da36ba007fb7611329d19c19bddebfe983c8182a583e72b"
V10_MANIFEST_SHA256 = "9271898a33bf54a2c15c722cc32145371431c593aea5ed92d110e81a88c4c100"
V10_QA_SHA256 = "63f790d95ed46ba3290784a0a4a0a9812c3aaa6f56038aaaf0b7548eb5fa15c7"
SIZE = (1344, 756)
MIN_SHOE_CLEARANCE_PX = 25
MIN_MARKER_X_DISPLACEMENT_PX = 40
MAX_WRIST_SHOULDER_DELTA_PX = 45
MAX_A_GROUND_DISCREPANCY_PX = 12
MARKERS = ("orange_ankle", "teal_ankle", "orange_wrist", "teal_wrist")
CHECKS = ("source_integrity", "visible_head_and_shoes", "marker_identity",
          "identity_stability", "background_stability", "no_ghost_or_duplicate",
          "arms_shoulder_high", "both_shoes_airborne")
V10_KEYS = {"original_a_png", "original_c_png", "canvas_jpeg",
            "a_annotation", "c_annotation", "canvas_annotation",
            "shared_manifest", "derived_a_png", "derived_c_png",
            "independent_qa_report"}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _read(path, label):
    item = Path(path).expanduser()
    if item.is_symlink():
        raise ApexCandidateError(f"{label} must not be a symlink")
    item = item.resolve()
    if not item.is_file():
        raise ApexCandidateError(f"{label} is missing")
    return item, item.read_bytes()


def _json(raw, label):
    def distinct(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ApexCandidateError(f"duplicate {label} key")
            obj[key] = value
        return obj
    try:
        value = json.loads(raw, object_pairs_hook=distinct)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ApexCandidateError(f"invalid {label} JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ApexCandidateError(f"{label} must be a JSON object")
    return value


def _px(value, label, maximum):
    if (type(value) not in (int, float) or not math.isfinite(value)
            or not 0 <= value <= maximum):
        raise ApexCandidateError(f"{label} must be an in-bounds finite pixel coordinate")
    return value


def _markers(entry, label):
    if not isinstance(entry, dict) or set(entry) != set(MARKERS):
        raise ApexCandidateError(f"{label} must identify all four physical markers")
    observed = {}
    for name, point in entry.items():
        if not isinstance(point, list) or len(point) != 2:
            raise ApexCandidateError(f"{label}.{name} needs [x,y]")
        observed[name] = (_px(point[0], f"{label}.{name}.x", SIZE[0]),
                          _px(point[1], f"{label}.{name}.y", SIZE[1]))
    return observed


def _measure(report):
    data = report.get("measurements")
    required = {"forward_screen_direction", "reference_a_markers",
                "candidate_b_markers", "reference_a_ground",
                "candidate_b_shoe_bottoms", "candidate_b_shoulders"}
    if not isinstance(data, dict) or set(data) != required:
        raise ApexCandidateError("independent QA measurements require exact marker/ground/shoulder fields")
    if data["forward_screen_direction"] not in ("RIGHT", "LEFT"):
        raise ApexCandidateError("screen-forward direction is unknown")
    forward = 1 if data["forward_screen_direction"] == "RIGHT" else -1
    a = _markers(data["reference_a_markers"], "A* markers")
    b = _markers(data["candidate_b_markers"], "B* markers")
    min_move = MIN_MARKER_X_DISPLACEMENT_PX
    for delta in (
        forward * (a["teal_ankle"][0] - a["orange_ankle"][0]),
        forward * (a["orange_wrist"][0] - a["teal_wrist"][0]),
        forward * (b["orange_ankle"][0] - b["teal_ankle"][0]),
        forward * (b["teal_wrist"][0] - b["orange_wrist"][0]),
    ):
        if delta < min_move:
            raise ApexCandidateError("A*/B* physical arm/leg marker ordering is not reversed")
    for name, sign in (("orange_ankle", 1), ("teal_ankle", -1),
                       ("orange_wrist", -1), ("teal_wrist", 1)):
        if sign * forward * (b[name][0] - a[name][0]) < min_move:
            raise ApexCandidateError(f"B* marker {name} did not reverse at least {min_move}px")

    ground = data["reference_a_ground"]
    shoes = data["candidate_b_shoe_bottoms"]
    shoulders = data["candidate_b_shoulders"]
    if (not isinstance(ground, dict) or set(ground) != {
                "ground_y", "orange_sole_y", "teal_sole_y"}
            or not isinstance(shoes, dict) or set(shoes) != {
                "orange_sole_y", "teal_sole_y"}
            or not isinstance(shoulders, dict) or set(shoulders) != {
                "orange_y", "teal_y"}):
        raise ApexCandidateError("ground/sole/shoulder annotations incomplete")
    baseline = _px(ground["ground_y"], "A* ground", SIZE[1])
    for color in ("orange", "teal"):
        if abs(_px(ground[f"{color}_sole_y"], f"A* {color} sole", SIZE[1]) - baseline) > MAX_A_GROUND_DISCREPANCY_PX:
            raise ApexCandidateError("A* sole does not agree with anchored ground reference")
    clearance = min(baseline - _px(shoes[f"{color}_sole_y"], f"B* {color} sole", SIZE[1])
                    for color in ("orange", "teal"))
    if clearance < MIN_SHOE_CLEARANCE_PX:
        raise ApexCandidateError(f"B* grounded or insufficient two-shoe clearance ({clearance:g}px)")
    for color in ("orange", "teal"):
        shoulder_y = _px(shoulders[f"{color}_y"], f"B* {color} shoulder", SIZE[1])
        if abs(b[f"{color}_wrist"][1] - shoulder_y) > MAX_WRIST_SHOULDER_DELTA_PX:
            raise ApexCandidateError(f"B* {color} arm is not shoulder-high")
    return {"minimum_both_shoe_clearance_px": round(clearance, 3),
            "four_marker_directional_reversals": "MEASUREMENT_CONSISTENT",
            "arms_shoulder_height": "MEASUREMENT_CONSISTENT"}


def check_candidate(v10_paths, b_image, qa_report):
    """Read-only diagnostics; no ledger, generator, owner or release actions."""
    if not isinstance(v10_paths, dict) or set(v10_paths) != V10_KEYS:
        raise ApexCandidateError("exact V10 original/canvas/annotation/derived/QA paths required")
    v10_spec = Path(__file__).parent / "segment_specs/chart1-scissor-v10-astar-to-cstar.json"
    verified = verify_v10_pair(
        v10_spec, v10_paths["original_a_png"], v10_paths["original_c_png"],
        v10_paths["canvas_jpeg"], v10_paths["shared_manifest"],
        v10_paths["derived_a_png"], v10_paths["derived_c_png"],
        a_annotation=v10_paths["a_annotation"], c_annotation=v10_paths["c_annotation"],
        canvas_annotation=v10_paths["canvas_annotation"],
        independent_qa_report=v10_paths["independent_qa_report"], expected_role="A_TO_C")
    if (verified["start_sha256"] != A_STAR_SHA256
            or verified["end_sha256"] != C_STAR_SHA256
            or verified["shared_canvas_manifest_sha256"] != V10_MANIFEST_SHA256
            or verified["independent_source_qa_report_sha256"] != V10_QA_SHA256):
        raise ApexCandidateError("V10 source authority does not match corrected archived A*/C*")
    image_file, image_bytes = _read(b_image, "B* candidate")
    digest = _sha(image_bytes)
    if digest in (A_STAR_SHA256, C_STAR_SHA256):
        raise ApexCandidateError("grounded A*/C* cannot substitute for an apex B*")
    try:
        with Image.open(io.BytesIO(image_bytes)) as frame:
            fmt = frame.format
            if fmt not in ("JPEG", "PNG") or frame.mode != "RGB" or frame.size != SIZE:
                raise ApexCandidateError("B* must be original RGB JPEG/PNG 1344x756 bytes")
            frame.load()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        if isinstance(exc, ApexCandidateError):
            raise
        raise ApexCandidateError(f"B* does not decode completely: {exc}") from exc
    qa_file, qa_bytes = _read(qa_report, "independent B* QA")
    record = _json(qa_bytes, "independent B* QA")
    required = {"schema_version", "authority", "a_star_sha256", "c_star_sha256",
                "v10_manifest_sha256", "v10_qa_sha256", "b_sha256", "b_format",
                "image_size", "producer", "reviewer", "decision", "checks",
                "measurements", "anatomical_left_right_proven", "video_form_release"}
    if (set(record) != required or record["schema_version"] != 1
            or record["authority"] != AUTHORITY
            or record["a_star_sha256"] != A_STAR_SHA256
            or record["c_star_sha256"] != C_STAR_SHA256
            or record["v10_manifest_sha256"] != V10_MANIFEST_SHA256
            or record["v10_qa_sha256"] != V10_QA_SHA256
            or record["b_sha256"] != digest or record["b_format"] != fmt
            or record["image_size"] != list(SIZE)):
        raise ApexCandidateError("B* independent QA is not bound to the exact candidate and V10 lineage")
    if (not isinstance(record["producer"], str) or not record["producer"].strip()
            or not isinstance(record["reviewer"], str) or not record["reviewer"].strip()
            or record["producer"] == record["reviewer"]):
        raise ApexCandidateError("B* QA needs distinct named producer and reviewer")
    if (record["decision"] != "CANDIDATE_FOR_DIAGNOSTIC_ONLY"
            or record["anatomical_left_right_proven"] is not False
            or record["video_form_release"] != "NOT_EVALUATED"):
        raise ApexCandidateError("B* independent QA is on HOLD or claims form/release approval")
    checks = record["checks"]
    if not isinstance(checks, dict) or set(checks) != set(CHECKS):
        raise ApexCandidateError("B* independent QA lacks eight named visual checks")
    for name, check in checks.items():
        if (not isinstance(check, dict) or check.get("verdict") != "PASS"
                or not isinstance(check.get("evidence"), str)
                or len(check["evidence"].strip()) < 20):
            raise ApexCandidateError(f"B* independent QA {name} lacks specific PASS evidence")
    measurements = _measure(record)
    for label, path, prior in (("B*", image_file, digest), ("B* QA", qa_file, _sha(qa_bytes))):
        if _sha(path.read_bytes()) != prior:
            raise ApexCandidateError(f"{label} changed during verification")
    return {"authority": AUTHORITY, "b_sha256": digest, "b_format": fmt,
            "v10_manifest_sha256": V10_MANIFEST_SHA256,
            "independent_b_qa_sha256": _sha(qa_bytes),
            "observed_geometry": measurements,
            "candidate_evidence": "STRUCTURALLY_VERIFIED_NOT_EXERCISE_FORM",
            "paid_video_precredit_authority": "NOT_GRANTED",
            "historical_anatomical_left_right": "UNKNOWN",
            "motion_video_release_approval": "NOT_EVALUATED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("v10_paths_json", help="private V10 source-path map")
    parser.add_argument("b_image", help="original candidate JPEG/PNG")
    parser.add_argument("independent_b_qa", help="private independent still QA report")
    args = parser.parse_args(argv)
    try:
        paths = _json(_read(args.v10_paths_json, "private V10 paths")[1], "private V10 paths")
        print(json.dumps(check_candidate(paths, args.b_image, args.independent_b_qa),
                         indent=2, sort_keys=True))
    except (ApexCandidateError, OSError, ValueError, TypeError) as exc:
        print(f"V11 candidate HOLD: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
