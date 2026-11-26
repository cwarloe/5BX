"""Read-only shoulder-height/extension diagnostics for photographed arm motion.

The landmarks are supplied by a human reviewer; this module detects no pose,
tracks no colored marker and cannot approve exercise form or release. It binds
each observation to the actual decoded RGB24 video frame.
"""

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

from .framing_qa import _video_snapshot
from .video_qa import file_sha256


ARM_COLORS = ("orange", "teal")
JOINTS = ("shoulder", "elbow", "wrist")
VISIBILITY = {"VISIBLE", "OCCLUDED", "UNKNOWN", "OUT_OF_FRAME"}
MIN_FRAME_FRACTION = 0.90
MAX_WRIST_SHOULDER_DELTA_AT_360P = 25.0
MIN_ELBOW_ANGLE_DEGREES = 150.0
FRAME_HASH_METHOD = "ffmpeg-v0-original-frame-size-rgb24-no-fps-filter"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def make_template(video_path):
    """Return an all-frame, all-UNKNOWN manual annotation manifest."""
    video, digest, info, hashes = _video_snapshot(video_path)
    if file_sha256(video) != digest:
        raise RuntimeError("source video changed while preparing arm annotations")
    return {
        "schema_version": 1,
        "source_video_sha256": digest,
        "frame_size": [info["width"], info["height"]],
        "frame_count": len(hashes),
        "rgb24_decode_method": FRAME_HASH_METHOD,
        "review": {"method": "UNREVIEWED", "reviewer": None},
        "frames": [
            {"index": index, "rgb24_sha256": frame_hash,
             "arms": {color: {joint: {"visibility": "UNKNOWN", "point": None}
                              for joint in JOINTS} for color in ARM_COLORS}}
            for index, frame_hash in enumerate(hashes)
        ],
    }


def _point(record, name, width, height):
    if not isinstance(record, dict) or set(record) != {"visibility", "point"}:
        raise ValueError(f"{name} must declare visibility and point")
    visibility, coordinates = record["visibility"], record["point"]
    if visibility not in VISIBILITY:
        raise ValueError(f"{name} has invalid visibility")
    if visibility != "VISIBLE":
        if coordinates is not None:
            raise ValueError(f"{name} non-visible point must be null")
        return None
    if not isinstance(coordinates, list) or len(coordinates) != 2:
        raise ValueError(f"{name} visible point must be [x,y] pixels")
    x, y = coordinates
    if (any(isinstance(v, bool) or not isinstance(v, (float, int))
            or not math.isfinite(v) for v in coordinates)
            or not 0 <= x < width or not 0 <= y < height):
        raise ValueError(f"{name} pixel point outside decoded frame")
    return float(x), float(y)


def _elbow_angle(shoulder, elbow, wrist):
    first = shoulder[0] - elbow[0], shoulder[1] - elbow[1]
    second = wrist[0] - elbow[0], wrist[1] - elbow[1]
    length = math.hypot(*first) * math.hypot(*second)
    if length < 1e-6:
        raise ValueError("shoulder, elbow and wrist must not share a zero-length segment")
    cosine = max(-1.0, min(1.0, (first[0] * second[0] + first[1] * second[1]) / length))
    return math.degrees(math.acos(cosine))


def _metric_verdict(frame_count, evaluable, bad, attested):
    """Any observed violation fails; limited unknowns cannot mask failures."""
    if bad:
        return "FAIL_OBSERVED_GEOMETRY"
    if evaluable / frame_count + 1e-9 < MIN_FRAME_FRACTION or not attested:
        return "NOT_EVALUATED"
    return "PASS_MANUALLY_ATTESTED_GEOMETRY_ONLY"


def analyze(video_path, manifest_path):
    """Verify exact video/frame hashes and score only observed arm geometry."""
    manifest = Path(manifest_path).resolve()
    payload = manifest.read_bytes()
    manifest_sha = hashlib.sha256(payload).hexdigest()
    data = json.loads(payload)
    if not isinstance(data, dict) or set(data) != {
            "schema_version", "source_video_sha256", "frame_size", "frame_count",
            "rgb24_decode_method", "review", "frames"} or type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("arm annotation must have the exact schema_version 1 fields")
    video, source_sha, info, frame_hashes = _video_snapshot(video_path)
    if (not isinstance(data["source_video_sha256"], str)
            or not SHA256.fullmatch(data["source_video_sha256"])
            or data["source_video_sha256"] != source_sha):
        raise ValueError("arm annotation source video SHA mismatch")
    width, height = info["width"], info["height"]
    if (data["frame_size"] != [width, height]
            or data["frame_count"] != len(frame_hashes)
            or data["rgb24_decode_method"] != FRAME_HASH_METHOD):
        raise ValueError("arm annotation frame count/size/decode method mismatch")
    rows = data["frames"]
    if not isinstance(rows, list):
        raise ValueError("arm annotations must contain a frames list")
    threshold = MAX_WRIST_SHOULDER_DELTA_AT_360P * height / 360.0
    frame_count = len(frame_hashes)
    reviewed = data["review"]
    attested = (isinstance(reviewed, dict) and set(reviewed) == {"method", "reviewer"}
                and reviewed["method"] == "HUMAN_VISUAL"
                and isinstance(reviewed["reviewer"], str) and reviewed["reviewer"].strip())
    seen = set()
    height_evaluable = elbow_evaluable = 0
    height_bad = elbow_bad = 0
    height_failures, elbow_failures = [], []
    unknown = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"index", "rgb24_sha256", "arms"} or type(row["index"]) is not int:
            raise ValueError("every arm row requires an integer index, RGB hash and two arms")
        index = row["index"]
        if index < 0 or index >= frame_count or index in seen:
            raise ValueError(f"arm frame index out of range or duplicated: {index}")
        seen.add(index)
        if row["rgb24_sha256"] != frame_hashes[index]:
            raise ValueError(f"arm frame {index} RGB24 hash mismatch")
        arms = row["arms"]
        if not isinstance(arms, dict) or set(arms) != set(ARM_COLORS):
            raise ValueError(f"arm frame {index} must have orange and teal physical tags")
        have_height, have_elbow = True, True
        this_height_bad, this_elbow_bad = False, False
        for color in ARM_COLORS:
            joints = arms[color]
            if not isinstance(joints, dict) or set(joints) != set(JOINTS):
                raise ValueError(f"arm frame {index} {color} needs shoulder, elbow, wrist")
            points = {joint: _point(joints[joint], f"frame {index} {color} {joint}", width, height)
                      for joint in JOINTS}
            if points["wrist"] is None or points["shoulder"] is None:
                have_height = False
                unknown.append({"frame": index, "arm": color, "metric": "height", "reason": "MISSING_SHOULDER_OR_WRIST"})
            else:
                difference = abs(points["wrist"][1] - points["shoulder"][1])
                if difference > threshold:
                    this_height_bad = True
                    height_failures.append({"frame": index, "arm": color,
                                            "reason": "WRIST_NOT_SHOULDER_HIGH", "delta_y_px": round(difference, 3)})
            if any(points[joint] is None for joint in JOINTS):
                have_elbow = False
                unknown.append({"frame": index, "arm": color, "metric": "extension", "reason": "MISSING_JOINT"})
            else:
                angle = _elbow_angle(points["shoulder"], points["elbow"], points["wrist"])
                if angle < MIN_ELBOW_ANGLE_DEGREES:
                    this_elbow_bad = True
                    elbow_failures.append({"frame": index, "arm": color,
                                           "reason": "ELBOW_BENT", "angle_degrees": round(angle, 3)})
        height_evaluable += int(have_height)
        elbow_evaluable += int(have_elbow)
        height_bad += int(this_height_bad)
        elbow_bad += int(this_elbow_bad)
    missing_indices = sorted(set(range(frame_count)) - seen)
    if missing_indices:
        unknown.append({"reason": "MISSING_FRAME_ANNOTATIONS", "frame_indices": missing_indices})
    if not attested:
        unknown.append({"reason": "HUMAN_REVIEW_ATTESTATION_MISSING"})
    height_verdict = _metric_verdict(frame_count, height_evaluable, height_bad, attested)
    elbow_verdict = _metric_verdict(frame_count, elbow_evaluable, elbow_bad, attested)
    if "FAIL_OBSERVED_GEOMETRY" in (height_verdict, elbow_verdict):
        overall = "FAIL_OBSERVED_GEOMETRY"
    elif height_verdict.startswith("PASS") and elbow_verdict.startswith("PASS"):
        overall = "PASS_MANUALLY_ATTESTED_GEOMETRY_ONLY"
    else:
        overall = "NOT_EVALUATED"
    if file_sha256(video) != source_sha or file_sha256(manifest) != manifest_sha:
        raise RuntimeError("video or arm annotation changed during QA")
    return {
        "tool": "photo_motion.arm_trajectory_qa", "schema_version": 1,
        "source_video_sha256": source_sha, "annotation_sha256": manifest_sha,
        "frame_size": [width, height], "frame_count": frame_count,
        "annotated_frame_count": len(seen), "human_review_attested": bool(attested),
        "limits": {"wrist_shoulder_delta_px": threshold,
                   "minimum_elbow_angle_degrees": MIN_ELBOW_ANGLE_DEGREES,
                   "minimum_evaluable_and_passing_frame_fraction": MIN_FRAME_FRACTION},
        "arm_height": {"verdict": height_verdict, "evaluable_frames": height_evaluable,
                       "observed_bad_frames": height_bad, "failures": height_failures},
        "elbow_extension": {"verdict": elbow_verdict, "evaluable_frames": elbow_evaluable,
                            "observed_bad_frames": elbow_bad, "failures": elbow_failures},
        "not_evaluated": unknown,
        "trajectory_verdict": overall,
        "anatomical_left_right_physical_marker_identity_exercise_form_and_release": "NOT_EVALUATED",
        "limitations": (
            "Human-supplied joint positions can be mistaken; frame hashes pin bytes but do not prove annotations. "
            "Orange/teal labels are screen-observed markers, not independently authenticated anatomical sides. "
            "Even a complete geometry PASS is not scissor-jump form, safe anatomy, full-cycle motion, or owner approval."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only manual photographic arm-trajectory QA")
    parser.add_argument("video", type=Path, help="actual private source MP4")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--template", type=Path, help="exclusive unreviewed annotation template")
    action.add_argument("--annotations", type=Path, help="reviewer-supplied all-frame observations")
    parser.add_argument("--report", type=Path, help="exclusive result file with --annotations")
    args = parser.parse_args(argv)
    try:
        if args.template is not None:
            if args.report is not None:
                raise ValueError("--report requires --annotations")
            result, output = make_template(args.video), args.template
        else:
            if args.report is None:
                raise ValueError("--annotations requires --report")
            result, output = analyze(args.video, args.annotations), args.report
        protected = {args.video.resolve()}
        if args.annotations is not None:
            protected.add(args.annotations.resolve())
        if output.resolve() in protected:
            raise ValueError("output cannot overwrite the MP4 or annotation file")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"output": str(output), "trajectory_verdict": result.get("trajectory_verdict", "NOT_EVALUATED")}, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
