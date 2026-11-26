"""Human-observed, hash-bound *video* scissor-phase QA; never form approval.

This checker does not discover shoes, wrists, people, anatomy or camera motion.
Every observation is entered by a human for one RGB24-decoded MP4 frame; the
script only checks the proposed A→flight→opposite-C→flight→A sequence against
those observations. A passing result is explicitly a manual technical attestation.
"""

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

from .contract import load_spec, validate
from .framing_qa import _video_snapshot
from .video_qa import file_sha256


LANDMARKS = ("orange_ankle", "teal_ankle", "orange_wrist", "teal_wrist")
CONTACTS = ("orange_shoe", "teal_shoe")
CONTACT_VALUES = {"PLANTED", "AIRBORNE", "UNKNOWN", "OCCLUDED"}
MARKER_VALUES = {"STABLE", "MIGRATED", "UNKNOWN"}
SHA_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
DECODE_METHOD = "ffmpeg-v0-original-frame-size-rgb24-no-fps-filter"
MIN_X_SEPARATION = 0.03
LOOP_POSITION_TOLERANCE = 0.06
MAX_ONE_FRAME_DISPLACEMENT = 0.25  # conservative, not a biomechanics limit
MIN_FLIGHT_FRAMES = 2
WINDOW_HALF_SECONDS = {"B": 0.65, "C": 0.45, "D": 0.65}


def _sha(value, name):
    if not isinstance(value, str) or not SHA_PATTERN.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 64-character SHA-256")
    return value


def _spec_snapshot(path):
    path = Path(path).resolve()
    digest = file_sha256(path)
    spec = load_spec(path)
    errors = validate(spec)
    if errors:
        raise ValueError("invalid movement contract: " + "; ".join(errors))
    if (spec.get("movement_type") != "scissor_jump" or spec.get("chart") != 1 or
            spec.get("exercise") != 5 or
            [p.get("id") for p in spec["phases"]] != ["A", "B", "C", "D", "E"] or
            [p.get("support") for p in spec["phases"]] !=
            ["grounded", "airborne", "grounded", "airborne", "grounded"]):
        raise ValueError("this checker requires the Chart 1 scissor A/B/C/D/E contract")
    if file_sha256(path) != digest:
        raise RuntimeError("motion contract changed during read")
    return path, digest, spec


def make_template(video_path, spec_path, reference_source):
    """Produce an unreviewed template; NO generated observations or implied PASS."""
    video, video_sha, info, hashes = _video_snapshot(video_path)
    spec_file, spec_sha, spec = _spec_snapshot(spec_path)
    if (not math.isfinite(info["fps"]) or info["fps"] <= 0 or
            not math.isfinite(info["duration_seconds"]) or
            abs(info["fps"] - spec["fps"]) > 0.001 or
            abs(info["duration_seconds"] - spec["duration_seconds"]) > 0.10):
        raise ValueError("decoded video rate/duration differs from scissor contract")
    reference = Path(reference_source).resolve()
    source_sha = file_sha256(reference)
    if not hashes or abs(len(hashes) - round(spec["fps"] * spec["duration_seconds"])) > 1:
        raise ValueError("decoded frame count differs from scissor contract")
    result = {
        "schema_version": 1,
        "source_video_sha256": video_sha,
        "contract": {"file": str(spec_file), "sha256": spec_sha},
        "reference_start_image": {"file": str(reference), "sha256": source_sha},
        "frame_size": [info["width"], info["height"]],
        "frame_count": len(hashes), "fps": info["fps"],
        "rgb24_decode_method": DECODE_METHOD,
        "forward_screen_direction": "UNKNOWN",  # human observes front of subject
        "review": {"method": "UNREVIEWED", "reviewer": None},
        "frames": [
            {"index": i, "rgb24_sha256": hash_, "time_seconds": round(i / info["fps"], 6),
             "marker_identity": "UNKNOWN",
             "shoe_contact": {name: "UNKNOWN" for name in CONTACTS},
             "landmarks": {name: {"visibility": "UNKNOWN", "point": None}
                           for name in LANDMARKS}}
            for i, hash_ in enumerate(hashes)
        ]
    }
    if (file_sha256(video) != video_sha or file_sha256(reference) != source_sha or
            file_sha256(spec_file) != spec_sha):
        raise RuntimeError("source changed while creating phase QA template")
    return result


def _point(entry, label, index):
    if not isinstance(entry, dict) or entry.get("visibility") not in ("VISIBLE", "OCCLUDED", "UNKNOWN", "OUT_OF_FRAME"):
        raise ValueError(f"frame {index} {label}: invalid visibility")
    v, point = entry["visibility"], entry.get("point")
    if v != "VISIBLE":
        if point is not None:
            raise ValueError(f"frame {index} {label}: non-visible landmark must have null point")
        return None
    if not isinstance(point, list) or len(point) != 2:
        raise ValueError(f"frame {index} {label}: visible point must be [x,y]")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not 0 <= x <= 1
           for x in point):
        raise ValueError(f"frame {index} {label}: point must be finite normalized coordinates")
    return tuple(point)


def _reviewable(doc):
    info = doc.get("review")
    return (isinstance(info, dict) and info.get("method") == "HUMAN_VISUAL" and
            isinstance(info.get("reviewer"), str) and bool(info["reviewer"].strip()))


def _relative(file_, manifest):
    if not isinstance(file_, str) or not file_:
        raise ValueError("pinned source needs a file path")
    return (manifest.parent / file_).resolve()


def _intervals(indices):
    """Return inclusive consecutive integer runs."""
    if not indices:
        return []
    runs, first, previous = [], indices[0], indices[0]
    for index in indices[1:]:
        if index != previous + 1:
            runs.append((first, previous))
            first = index
        previous = index
    runs.append((first, previous))
    return runs


def _order(points, direction):
    sign = 1 if direction == "RIGHT" else -1
    comparisons = {
        "orange_leg": sign * (points["orange_ankle"][0] - points["teal_ankle"][0]),
        "orange_arm": sign * (points["orange_wrist"][0] - points["teal_wrist"][0]),
    }
    if any(abs(value) < MIN_X_SEPARATION for value in comparisons.values()):
        return None  # insufficient spacing; do not infer fore/aft
    return {"orange_leg": "forward" if comparisons["orange_leg"] > 0 else "back",
            "teal_leg": "back" if comparisons["orange_leg"] > 0 else "forward",
            "orange_arm": "forward" if comparisons["orange_arm"] > 0 else "back",
            "teal_arm": "back" if comparisons["orange_arm"] > 0 else "forward"}


def _expected(spec, phase):
    return next(p["limbs"] for p in spec["phases"] if p["id"] == phase)


def analyze(video_path, annotation_file):
    annotation_file = Path(annotation_file).resolve()
    manifest_sha = file_sha256(annotation_file)
    doc = json.loads(annotation_file.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise ValueError("phase annotation schema_version must be 1")
    video, video_sha, info, hashes = _video_snapshot(video_path)
    if _sha(doc.get("source_video_sha256"), "source_video_sha256") != video_sha:
        raise ValueError("annotated MP4 hash differs from actual video")
    if (doc.get("rgb24_decode_method") != DECODE_METHOD or doc.get("frame_size") !=
            [info["width"], info["height"]] or doc.get("frame_count") != len(hashes) or
            type(doc.get("fps")) not in (float, int) or
            not math.isfinite(doc["fps"]) or not math.isfinite(info["fps"]) or
            abs(doc["fps"] - info["fps"]) > 0.001):
        raise ValueError("decoded frame geometry/count/rate or method mismatch")
    pinned = doc.get("contract")
    if not isinstance(pinned, dict):
        raise ValueError("missing pinned scissor contract")
    spec_file = _relative(pinned.get("file"), annotation_file)
    spec_path, spec_sha, spec = _spec_snapshot(spec_file)
    if _sha(pinned.get("sha256"), "contract.sha256") != spec_sha:
        raise ValueError("pinned scissor contract hash mismatch")
    if (abs(info["fps"] - spec["fps"]) > 0.001 or
            abs(info["duration_seconds"] - spec["duration_seconds"]) > 0.10 or
            abs(len(hashes) - round(spec["fps"] * spec["duration_seconds"])) > 1):
        raise ValueError("video duration/rate/frame count differs from pinned contract")
    anchor = doc.get("reference_start_image")
    if not isinstance(anchor, dict):
        raise ValueError("missing independently pinned photographic start image")
    anchor_path = _relative(anchor.get("file"), annotation_file)
    anchor_sha = file_sha256(anchor_path)
    if _sha(anchor.get("sha256"), "reference_start_image.sha256") != anchor_sha:
        raise ValueError("photographic reference hash mismatch")
    direction = doc.get("forward_screen_direction")
    if direction not in ("RIGHT", "LEFT", "UNKNOWN"):
        raise ValueError("forward_screen_direction must be LEFT, RIGHT or UNKNOWN")
    rows = doc.get("frames")
    if not isinstance(rows, list) or not rows:
        raise ValueError("frames must be a nonempty annotation array")
    observations, failures, missing_evidence = {}, [], []
    for row in rows:
        if not isinstance(row, dict) or type(row.get("index")) is not int:
            raise ValueError("every row must have an integer frame index")
        i = row["index"]
        if not 0 <= i < len(hashes) or i in observations:
            raise ValueError(f"duplicate or out-of-range frame index: {i}")
        if _sha(row.get("rgb24_sha256"), f"frame {i} RGB24 SHA") != hashes[i]:
            raise ValueError(f"frame {i} RGB24 hash changed or annotations migrated")
        if (type(row.get("time_seconds")) not in (float, int) or
                not math.isfinite(row["time_seconds"]) or
                abs(row["time_seconds"] - i / info["fps"]) > 0.00001):
            raise ValueError(f"frame {i} timestamp does not match decoded frame index/rate")
        contact = row.get("shoe_contact")
        if not isinstance(contact, dict) or set(contact) != set(CONTACTS) or any(v not in CONTACT_VALUES for v in contact.values()):
            raise ValueError(f"frame {i} needs explicit orange/teal shoe contacts")
        identity = row.get("marker_identity")
        if identity not in MARKER_VALUES:
            raise ValueError(f"frame {i} needs explicit physical marker-continuity observation")
        if identity == "MIGRATED":
            failures.append({"frame": i, "reason": "PHYSICAL_MARKER_MIGRATION"})
        if identity == "UNKNOWN":
            missing_evidence.append({"frame": i, "reason": "MARKER_IDENTITY_UNASSESSED"})
        if any(v in ("UNKNOWN", "OCCLUDED") for v in contact.values()):
            missing_evidence.append({"frame": i, "reason": "SHOE_CONTACT_UNASSESSED"})
        landmarks = row.get("landmarks")
        if not isinstance(landmarks, dict) or set(landmarks) != set(LANDMARKS):
            raise ValueError(f"frame {i} needs exactly four tracked wrist/ankle landmarks")
        points = {label: _point(landmarks[label], label, i) for label in LANDMARKS}
        if any(point is None for point in points.values()):
            missing_evidence.append({"frame": i, "reason": "TRACKED_LANDMARKS_UNASSESSED"})
        observations[i] = {"points": points, "contact": contact, "identity": identity}
    absent = sorted(set(range(len(hashes))) - set(observations))
    if absent:
        missing_evidence.append({"reason": "MISSING_FRAME_ANNOTATIONS", "count": len(absent), "indices": absent})
    if not _reviewable(doc):
        missing_evidence.append({"reason": "HUMAN_REVIEW_ATTESTATION_MISSING"})
    if direction == "UNKNOWN":
        missing_evidence.append({"reason": "FORWARD_SCREEN_DIRECTION_UNASSESSED"})

    # A/C/E require both shoes PLANTED and all four physical limbs in the
    # expected fore/aft assignment. C may land near the intended 2.5s, not
    # necessarily on the exact nominal frame. E is the last actual frame.
    grounded = {}
    if direction != "UNKNOWN":
        for i, entry in observations.items():
            if all(v == "PLANTED" for v in entry["contact"].values()) and all(v is not None for v in entry["points"].values()):
                grounded[i] = _order(entry["points"], direction)
    n = len(hashes)
    for i, phase in ((0, "A"), (n - 1, "E")):
        sample = observations.get(i)
        if sample is None or any(v in ("UNKNOWN", "OCCLUDED") for v in sample["contact"].values()):
            missing_evidence.append({"frame": i, "reason": f"{phase}_GROUND_CONTACT_UNASSESSED"})
        elif any(v != "PLANTED" for v in sample["contact"].values()):
            failures.append({"frame": i, "reason": f"{phase}_NOT_GROUNDED"})
        if direction != "UNKNOWN" and sample is not None and all(v is not None for v in sample["points"].values()):
            actual = _order(sample["points"], direction)
            if actual is None:
                missing_evidence.append({"frame": i, "reason": f"{phase}_LIMB_ORDER_TOO_AMBIGUOUS"})
            elif actual != _expected(spec, phase):
                failures.append({"frame": i, "reason": f"{phase}_WRONG_PHYSICAL_LIMB_ORDER", "observed": actual})
    first = observations.get(0)
    last = observations.get(n - 1)
    if first and last and all(v is not None for v in first["points"].values()) and all(v is not None for v in last["points"].values()):
        for marker in LANDMARKS:
            displacement = math.dist(first["points"][marker], last["points"][marker])
            if displacement > LOOP_POSITION_TOLERANCE:
                failures.append({"frame": n - 1, "reason": "A_E_MARKER_POSITION_MISMATCH",
                                 "landmark": marker, "normalized_displacement": round(displacement, 5)})
    # A discontinuous colored-dot teleport across adjacent decoded frames is
    # independently evidence against stable physical tracking (conservative
    # threshold; this does not detect all morphing).
    for i in sorted(observations):
        if i == 0 or i - 1 not in observations:
            continue
        previous, current = observations[i - 1]["points"], observations[i]["points"]
        for marker in LANDMARKS:
            if previous[marker] is not None and current[marker] is not None:
                distance = math.dist(previous[marker], current[marker])
                if distance > MAX_ONE_FRAME_DISPLACEMENT:
                    failures.append({"frame": i, "reason": "SUDDEN_MARKER_TELEPORT",
                                     "landmark": marker, "normalized_displacement": round(distance, 5)})

    times = {p["id"]: float(p["time_seconds"]) for p in spec["phases"]}
    def window_indices(phase):
        return [i for i in range(n) if abs(i / info["fps"] - times[phase]) <= WINDOW_HALF_SECONDS[phase]]

    def complete_window(phase, *, require_landmarks=False):
        for i in window_indices(phase):
            sample = observations.get(i)
            if (sample is None or sample["identity"] != "STABLE" or
                    any(value in ("UNKNOWN", "OCCLUDED") for value in sample["contact"].values())):
                return False
            if require_landmarks and any(value is None for value in sample["points"].values()):
                return False
        return True

    c_indices = [i for i in grounded if i in window_indices("C")]
    opposite_candidates = [i for i in c_indices if grounded[i] == _expected(spec, "C")]
    if not opposite_candidates:
        if direction != "UNKNOWN" and complete_window("C", require_landmarks=True):
            failures.append({"reason": "NO_OPPOSITE_GROUNDED_C_WITHIN_WINDOW"})
        else:
            missing_evidence.append({"reason": "C_OPPOSITE_LANDING_NOT_ESTABLISHED"})

    air_indices = sorted(i for i, entry in observations.items()
                         if all(v == "AIRBORNE" for v in entry["contact"].values()))
    all_air_runs = _intervals(air_indices)
    flights = [(a, b) for a, b in all_air_runs if b - a + 1 >= MIN_FLIGHT_FRAMES]
    if all_air_runs and any(b - a + 1 < MIN_FLIGHT_FRAMES for a, b in all_air_runs):
        missing_evidence.append({"reason": "ONE_FRAME_AIRBORNE_OBSERVATION_INSUFFICIENT", "runs": all_air_runs})
    if len(flights) > 2:
        failures.append({"reason": "MORE_THAN_TWO_DISTINCT_AIRBORNE_EVENTS", "runs": flights})
    for phase in ("B", "D"):
        possible = [(a, b) for a, b in flights
                    if abs(((a + b) / 2) / info["fps"] - times[phase]) <= WINDOW_HALF_SECONDS[phase]]
        if not possible:
            if complete_window(phase):
                failures.append({"reason": f"MISSING_{phase}_TWO_FRAME_AIRBORNE_EVENT"})
            else:
                missing_evidence.append({"reason": f"{phase}_FLIGHT_NOT_ESTABLISHED"})
    if len(flights) == 2 and opposite_candidates:
        b_end, d_begin = flights[0][1], flights[1][0]
        if not b_end < min(opposite_candidates) < d_begin:
            failures.append({"reason": "OPPOSITE_C_NOT_BETWEEN_DISTINCT_FLIGHTS"})
    if len(flights) == 2 and (flights[0][0] >= flights[1][0]):
        failures.append({"reason": "FLIGHT_ORDER_INVALID"})

    verdict = "FAIL" if failures else ("NOT_EVALUATED" if missing_evidence else "PASS_MANUALLY_ATTESTED")
    if (file_sha256(video) != video_sha or file_sha256(spec_path) != spec_sha or
            file_sha256(anchor_path) != anchor_sha or file_sha256(annotation_file) != manifest_sha):
        raise RuntimeError("source video, contract, photo reference or annotations changed during inspection")
    return {
        "tool": "photo_motion.scissor_phase_qa", "schema_version": 1,
        "source_video": str(video), "source_video_sha256": video_sha,
        "annotation_manifest": str(annotation_file), "annotation_manifest_sha256": manifest_sha,
        "contract_sha256": spec_sha, "reference_start_image_sha256": anchor_sha,
        "frame_count": n, "annotated_frame_count": len(observations),
        "airborne_runs": [{"first_frame": a, "last_frame": b, "duration_frames": b - a + 1}
                          for a, b in flights],
        "opposite_landing_candidate_frames": opposite_candidates,
        "phase_verdict": verdict, "failures": failures, "not_evaluated": missing_evidence,
        "exercise_form_identity_loop_and_release_approval": "NOT_EVALUATED",
        "limitations": (
            "All positions, planted/airborne contacts and marker continuity are HUMAN observations "
            "of decoded frames, not vision inference. Stable colored markers cannot prove anatomical "
            "left/right, safe form, actual ballistic mechanics, identity, camera stability or loop seamlessness. "
            "A manual phase PASS is never Charles's release approval."
        )
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hash-bound manual photographic scissor phase QA")
    parser.add_argument("video", type=Path, help="actual private MP4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--template", type=Path, help="new unreviewed annotation file")
    mode.add_argument("--annotations", type=Path, help="completed manual annotations")
    parser.add_argument("--spec", type=Path, help="scissor contract; required with --template")
    parser.add_argument("--start-photo", type=Path, help="exact photographic A source; required with --template")
    parser.add_argument("--report", type=Path, help="exclusive report path; required with --annotations")
    args = parser.parse_args(argv)
    try:
        if args.template is not None:
            if args.spec is None or args.start_photo is None or args.report is not None:
                raise ValueError("--template requires --spec and --start-photo, without --report")
            dest = args.template
            result = make_template(args.video, args.spec, args.start_photo)
        else:
            if args.report is None or args.spec is not None or args.start_photo is not None:
                raise ValueError("--annotations requires --report, without spec or photo overrides")
            dest = args.report
            result = analyze(args.video, args.annotations)
        protected = {args.video.resolve()}
        if args.annotations is not None:
            protected.add(args.annotations.resolve())
        for path in (args.spec, args.start_photo):
            if path is not None:
                protected.add(path.resolve())
        if dest.resolve() in protected:
            raise ValueError("output cannot overwrite any input source")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("x", encoding="utf-8") as target:
            json.dump(result, target, indent=2)
            target.write("\n")
        print(json.dumps({"output": str(dest), "phase_verdict": result.get("phase_verdict", "NOT_EVALUATED")}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
