"""Fail-closed photographic *framing* QA from human-annotated MP4 frames.

No face/body detector, tracking inference, background subtraction, or exercise
approval is performed. Every decoded RGB24 frame is pinned by SHA-256 so that
annotations cannot silently migrate to a different edit of the same clip.
"""

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .video_qa import file_sha256, probe


LANDMARKS = ("head", "left_shoe", "right_shoe")
KNOWN_VISIBILITY = {"VISIBLE", "PARTIAL", "OUT_OF_FRAME", "OCCLUDED", "UNKNOWN"}
DEFAULT_LIMITS = {"head_top": 0.02, "shoe_bottom": 0.02, "horizontal": 0.01}
HEX_SHA = re.compile(r"[0-9a-f]{64}\Z")


def _require_sha(value, name):
    if not isinstance(value, str) or not HEX_SHA.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 64-character SHA-256 digest")
    return value


def _stream_frame_hashes(video, width, height):
    """Decode ALL RGB24 frames without writing extracted private images."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required for decoded RGB24 frame binding")
    command = ["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-i", str(video),
               "-map", "0:v:0", "-an", "-sn", "-dn", "-vsync", "0", "-pix_fmt", "rgb24",
               "-f", "rawvideo", "pipe:1"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    frame_bytes = width * height * 3
    hashes = []
    try:
        while True:
            blob = process.stdout.read(frame_bytes)
            if not blob:
                break
            if len(blob) != frame_bytes:
                raise RuntimeError(f"truncated decoded video frame {len(hashes)}")
            hashes.append(hashlib.sha256(blob).hexdigest())
        errors = process.stderr.read().decode("utf-8", errors="replace")
        if process.wait() != 0:
            raise RuntimeError(f"ffmpeg decode failed: {errors[-600:]}")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        process.stderr.close()
    if not hashes:
        raise ValueError("video has no decoded frames")
    return hashes


def _video_snapshot(video):
    video = Path(video).resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    source_sha = file_sha256(video)
    metadata = probe(video)
    width, height = metadata["width"], metadata["height"]
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        raise ValueError("video must expose positive frame dimensions")
    hashes = _stream_frame_hashes(video, width, height)
    if file_sha256(video) != source_sha:
        raise RuntimeError("source MP4 changed during decoding; discard all frame hashes")
    return video, source_sha, metadata, hashes


def make_template(video_path, *, identity_source=None):
    """Prepare a versioned recipe. UNKNOWN fields require *manual* annotation."""
    video, source_sha, metadata, hashes = _video_snapshot(video_path)
    identity = None
    if identity_source is not None:
        image = Path(identity_source).resolve()
        identity = {"file": str(image), "sha256": file_sha256(image)}
        if file_sha256(image) != identity["sha256"]:
            raise RuntimeError("identity source changed while building annotation template")
    if file_sha256(video) != source_sha:
        raise RuntimeError("source MP4 changed while building annotation template")
    return {
        "schema_version": 1,
        "source_video_sha256": source_sha,
        "identity_source": identity,
        "frame_size": [metadata["width"], metadata["height"]],
        "frame_count": len(hashes),
        "rgb24_decode_method": "ffmpeg-v0-original-frame-size-rgb24-no-fps-filter",
        "minimum_clearance": DEFAULT_LIMITS.copy(),
        "review": {"method": "UNREVIEWED", "reviewer": None},
        "frames": [{"index": i, "rgb24_sha256": digest,
                    "landmarks": {name: {"visibility": "UNKNOWN", "box": None} for name in LANDMARKS}}
                   for i, digest in enumerate(hashes)]
    }


def _box(value, name, width, height):
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError(f"{name} needs a normalized [x0,y0,x1,y1] box")
    if any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) for x in value):
        raise ValueError(f"{name} box coordinates must be finite numbers")
    x0, y0, x1, y1 = value
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise ValueError(f"{name} box must be within [0,1] with positive size")
    if (x1 - x0) * width < 2 or (y1 - y0) * height < 2:
        raise ValueError(f"{name} box must span at least two pixels on each axis")
    return value


def _limits(doc):
    raw = doc.get("minimum_clearance")
    if not isinstance(raw, dict) or set(raw) != set(DEFAULT_LIMITS):
        raise ValueError("minimum_clearance must have head_top, shoe_bottom and horizontal")
    for label, value in raw.items():
        if (isinstance(value, bool) or not isinstance(value, (float, int)) or
            not math.isfinite(value) or value < DEFAULT_LIMITS[label] or value > 0.20):
            raise ValueError(f"minimum_clearance.{label} must be within [{DEFAULT_LIMITS[label]}, 0.20]; do not weaken the baseline")
    return raw


def analyze(video_path, manifest_path):
    """Require complete frame observations for PASS; observed failures always fail."""
    manifest = Path(manifest_path).resolve()
    blob = manifest.read_bytes()
    manifest_sha = hashlib.sha256(blob).hexdigest()
    doc = json.loads(blob.decode("utf-8"))
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise ValueError("framing annotation schema_version must be 1")
    video, video_sha, info, hashes = _video_snapshot(video_path)
    if _require_sha(doc.get("source_video_sha256"), "source_video_sha256") != video_sha:
        raise ValueError("annotated video SHA does not match actual MP4")
    if doc.get("rgb24_decode_method") != "ffmpeg-v0-original-frame-size-rgb24-no-fps-filter":
        raise ValueError("unsupported RGB24 decode method")
    if doc.get("frame_size") != [info["width"], info["height"]] or doc.get("frame_count") != len(hashes):
        raise ValueError("annotated frame size/count does not match decoded video")
    limits = _limits(doc)
    identity = doc.get("identity_source")
    identity_hash = None
    identity_path = None
    if identity is not None:
        if not isinstance(identity, dict) or not isinstance(identity.get("file"), str):
            raise ValueError("identity_source must contain file and sha256")
        _require_sha(identity.get("sha256"), "identity_source.sha256")
        identity_path = (manifest.parent / identity["file"]).resolve()
        identity_hash = file_sha256(identity_path)
        if identity_hash != identity["sha256"]:
            raise ValueError("identity-source master SHA does not match annotation")
    rows = doc.get("frames")
    if not isinstance(rows, list) or not rows:
        raise ValueError("frames must be a nonempty annotation list")
    observed, complete, failures, unassessed = set(), set(), [], []
    for row in rows:
        if not isinstance(row, dict) or type(row.get("index")) is not int:
            raise ValueError("each frame needs an integer index")
        index = row["index"]
        if not 0 <= index < len(hashes) or index in observed:
            raise ValueError(f"frame index out of range or duplicated: {index}")
        observed.add(index)
        if _require_sha(row.get("rgb24_sha256"), f"frame {index} RGB24 SHA") != hashes[index]:
            raise ValueError(f"frame {index} decoded RGB24 hash mismatch; annotations are stale")
        landmarks = row.get("landmarks")
        if not isinstance(landmarks, dict):
            raise ValueError(f"frame {index} needs landmarks object")
        all_visible = True
        for label in LANDMARKS:
            part = landmarks.get(label)
            if not isinstance(part, dict) or part.get("visibility") not in KNOWN_VISIBILITY:
                raise ValueError(f"frame {index} {label} needs a declared visibility status")
            visibility, coords = part["visibility"], part.get("box")
            if visibility == "VISIBLE":
                x0, y0, x1, y1 = _box(coords, f"frame {index} {label}", info["width"], info["height"])
                if x0 < limits["horizontal"] or x1 > 1 - limits["horizontal"]:
                    failures.append({"frame": index, "landmark": label, "reason": "HORIZONTAL_EDGE_CLEARANCE"})
                if label == "head" and y0 < limits["head_top"]:
                    failures.append({"frame": index, "landmark": label, "reason": "HEAD_TOP_CLEARANCE"})
                if label != "head" and y1 > 1 - limits["shoe_bottom"]:
                    failures.append({"frame": index, "landmark": label, "reason": "SHOE_BOTTOM_CLEARANCE"})
            elif visibility in ("PARTIAL", "OUT_OF_FRAME"):
                if coords is not None:
                    _box(coords, f"frame {index} {label}", info["width"], info["height"])
                failures.append({"frame": index, "landmark": label, "reason": visibility})
                all_visible = False
            else:
                if coords is not None:
                    raise ValueError(f"frame {index} {label} {visibility} must have null box")
                unassessed.append({"frame": index, "landmark": label, "reason": visibility})
                all_visible = False
        if all_visible:
            complete.add(index)
    missing = sorted(set(range(len(hashes))) - observed)
    if missing:
        unassessed.append({"reason": "MISSING_FRAME_ANNOTATIONS", "frame_indices": missing})
    review = doc.get("review")
    review_valid = (isinstance(review, dict) and review.get("method") == "HUMAN_VISUAL" and
                    isinstance(review.get("reviewer"), str) and bool(review["reviewer"].strip()))
    if not review_valid:
        unassessed.append({"reason": "HUMAN_REVIEW_ATTESTATION_MISSING"})
    if identity_hash is None:
        unassessed.append({"reason": "IDENTITY_SOURCE_UNVERIFIED"})
    verdict = "FAIL" if failures else ("NOT_EVALUATED" if unassessed else "PASS_MANUALLY_ATTESTED")
    if identity_path is not None and file_sha256(identity_path) != identity_hash:
        raise RuntimeError("identity source changed during inspection")
    if file_sha256(video) != video_sha:
        raise RuntimeError("video changed during framing inspection")
    if file_sha256(manifest) != manifest_sha:
        raise RuntimeError("annotation manifest changed during inspection")
    return {
        "tool": "photo_motion.framing_qa", "schema_version": 1,
        "source_video": str(video), "source_video_sha256": video_sha,
        "annotation_manifest": str(manifest), "annotation_manifest_sha256": manifest_sha,
        "identity_source": str(identity_path) if identity_path is not None else None,
        "identity_source_sha256_verified": identity_hash,
        "frame_count": len(hashes), "annotated_frame_count": len(observed),
        "fully_visible_frame_count": len(complete), "minimum_clearance": limits,
        "framing_verdict": verdict, "failures": failures,
        "not_evaluated": unassessed,
        "exercise_form_person_identity_and_release_approval": "NOT_EVALUATED",
        "limitations": (
            "Boxes and physical left/right shoe labels must be independently HUMAN-annotated "
            "from the EXACT decoded MP4. A matching background, color, or RGB hash does not locate a person, "
            "prove anatomy, or certify photographic identity. Even a manually attested framing PASS "
            "is not exercise-form, identity, loop, or owner approval."
        )
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manual, fail-closed photographic head/shoe framing QA")
    parser.add_argument("video", type=Path, help="actual private photographic MP4")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--template", type=Path, help="create unreviewed all-frame annotation template")
    selection.add_argument("--annotations", type=Path, help="previously annotated template JSON")
    parser.add_argument("--identity-source", type=Path, help="local immutable photo master for template hash binding")
    parser.add_argument("--report", type=Path, help="exclusive JSON report path with --annotations")
    args = parser.parse_args(argv)
    try:
        if args.template is not None:
            if args.report is not None:
                raise ValueError("--report is only used with --annotations")
            output = args.template
            result = make_template(args.video, identity_source=args.identity_source)
        else:
            if args.report is None or args.identity_source is not None:
                raise ValueError("--annotations requires --report and cannot override pinned identity source")
            output = args.report
            result = analyze(args.video, args.annotations)
        protected = {args.video.resolve()}
        if args.annotations is not None:
            protected.add(args.annotations.resolve())
        if args.identity_source is not None:
            protected.add(args.identity_source.resolve())
        if args.annotations is not None and result["identity_source"] is not None:
            protected.add(Path(result["identity_source"]).resolve())
        if output.resolve() in protected:
            raise ValueError("output must not overwrite video, master or annotation manifest")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"output": str(output), "framing_verdict": result.get("framing_verdict", "NOT_EVALUATED")}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
