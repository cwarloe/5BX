"""Unpaid replay + independent-QA gate for a V10 generated-canvas Frames pilot.

The A*/C* endpoints are derivative RGB PNGs, never V7 originals. Verify the
entire producer recipe against original A/C and one byte-pinned experimental
A' JPEG in a disposable directory before allowing a *separate* paid request.
No provider calls or exercise-form/release approval occur here.
"""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .source_authority import (
    V7_PARENT_V6_STATUS, V7_PREPARED_A_SHA256, V7_PREPARED_C_SHA256,
)


class SharedCanvasPreflightError(ValueError):
    """Insufficient direct bytes, replay evidence or independent source QA."""


AUTHORITY = "V10_REPLAYED_SHARED_CANVAS_FRAMES"
CANVAS_SHA256 = "10989cf3c87b1b9758599e0ebf3bb015141198fb36a6aec72b7c8491cd4aa550"
SOURCE_SHA256 = {"A": V7_PREPARED_A_SHA256, "C": V7_PREPARED_C_SHA256,
                 "canvas": CANVAS_SHA256}
V10_SETTINGS = {
    "duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
    "seed": None, "generation_mode": "Frames to Video", "resolution": "720p",
}
V10_QUOTE = "9"
TRANSFORM = {
    "scale_numerator": 37, "scale_denominator": 50,
    "rounded_image_size": [947, 533], "offset_xy": [200, 172],
    "window_half_open": [355, 172, 1020, 705],
    "feather_side_top_bottom": [55, 5, 18],
    "interpolation": "Pillow LANCZOS",
    "blend": "linear alpha minimum of horizontal and vertical window ramps",
}
QA_CHECKS = {
    "source_integrity", "annotation_coverage", "background_alignment",
    "composition_replay", "seam_ghosting", "head_shoes_framing",
    "character_identity", "physical_limb_consistency",
}
ROLES = {"A_TO_C": ("A", "C"), "C_TO_A": ("C", "A")}


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _read(path, label):
    file = Path(path).expanduser()
    if file.is_symlink():
        raise SharedCanvasPreflightError(f"{label} must not be a symlink")
    file = file.resolve()
    if not file.is_file():
        raise SharedCanvasPreflightError(f"{label} missing")
    return file, file.read_bytes()


def _json(payload, label):
    def no_duplicates(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise SharedCanvasPreflightError(f"duplicate {label} JSON key")
            obj[key] = value
        return obj

    try:
        result = json.loads(payload, object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, ValueError) as exc:
        raise SharedCanvasPreflightError(f"invalid {label} JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise SharedCanvasPreflightError(f"{label} must be a JSON object")
    return result


def _expected_spec(role):
    start, end = ROLES[role]
    return {
        "schema_version": 1, "authority": AUTHORITY,
        "exercise_id": "chart1-scissor-jump", "segment_role": role,
        "start_pose": f"{start}*", "end_pose": f"{end}*",
        "duration_seconds": 3, "aspect_ratio": "16:9",
        "provider": "Google Flow", "model": "Omni 1.2 Flash",
        "generation_mode": "Frames to Video", "resolution": "720p",
        "variants": 1, "quoted_credits": V10_QUOTE,
        "source_authority": "V7_DIRECT_PREPARED_PAIR_PLUS_ONE_BYTE_PINNED_A_PRIME_CANVAS",
        "original_source_sha256": dict(SOURCE_SHA256),
        "derived_image_size": [1344, 756], "derived_image_format": "RGB PNG",
        "composition_transform": dict(TRANSFORM),
        "parent_v6_card_status": V7_PARENT_V6_STATUS,
        "anatomical_left_right_proven": False,
        "status": "EXPERIMENTAL_INDEPENDENT_SOURCE_QA_REQUIRED_NOT_EXERCISE_APPROVAL",
    }


def _image(payload, label, *, fmt, size):
    import io
    try:
        with Image.open(io.BytesIO(payload)) as frame:
            if frame.format != fmt or frame.mode != "RGB" or frame.size != size:
                raise SharedCanvasPreflightError(f"{label} must be RGB {size[0]}x{size[1]} {fmt}")
            frame.load()
    except (OSError, UnidentifiedImageError, ValueError, SyntaxError) as exc:
        if isinstance(exc, SharedCanvasPreflightError):
            raise
        raise SharedCanvasPreflightError(f"{label} image decode failed: {exc}") from exc


def _qa_report(report, manifest_digest, source_hashes, output_hashes):
    required = {"schema_version", "authority", "manifest_sha256", "source_sha256",
                "output_sha256", "producer", "reviewer", "decision", "checks",
                "anatomical_left_right_proven", "exercise_form", "video_motion_and_release"}
    optional = {"measurements", "date", "limitations", "no_final_approval", "quantitative_methods"}
    if (set(report) - (required | optional) or required - set(report)
            or report["schema_version"] != 1
            or report["authority"] != "V10_SHARED_CANVAS_INDEPENDENT_QA"
            or report["manifest_sha256"] != manifest_digest
            or report["source_sha256"] != source_hashes
            or report["output_sha256"] != output_hashes):
        raise SharedCanvasPreflightError("independent QA report is not bound to the exact shared-canvas source pair")
    if (report.get("no_final_approval", True) is not True
            or ("limitations" in report and
                (not isinstance(report["limitations"], str) or len(report["limitations"].strip()) < 20))
            or ("quantitative_methods" in report and
                (not isinstance(report["quantitative_methods"], dict) or not report["quantitative_methods"]))):
        raise SharedCanvasPreflightError("independent QA optional evidence contradicts the diagnostic-only scope")
    if (not isinstance(report["producer"], str) or not report["producer"].strip()
            or not isinstance(report["reviewer"], str) or not report["reviewer"].strip()
            or report["producer"].strip() == report["reviewer"].strip()):
        raise SharedCanvasPreflightError("independent QA requires distinct named producer and reviewer")
    if (report["decision"] != "CANDIDATE_FOR_DIAGNOSTIC_ONLY"
            or report["anatomical_left_right_proven"] is not False
            or report["exercise_form"] != "NOT_EVALUATED"
            or report["video_motion_and_release"] != "NOT_EVALUATED"):
        raise SharedCanvasPreflightError("independent source QA HOLD or claimed form/release approval")
    checks = report["checks"]
    if not isinstance(checks, dict) or set(checks) != QA_CHECKS:
        raise SharedCanvasPreflightError("independent QA lacks eight required source-pair checks")
    for name, result in checks.items():
        if (not isinstance(result, dict) or result.get("verdict") != "PASS"
                or not isinstance(result.get("evidence"), str)
                or len(result["evidence"].strip()) < 20):
            raise SharedCanvasPreflightError(f"independent QA check {name} lacks a specific PASS and evidence")


def verify_segment(spec_path, original_a_png, original_c_png, canvas_jpeg,
                   shared_manifest, derived_a_png, derived_c_png, *,
                   a_annotation, c_annotation, canvas_annotation,
                   independent_qa_report, expected_role=None):
    """Replay actual artifact bytes; do not trust unauthenticated hashes alone."""
    spec_file, spec_bytes = _read(spec_path, "V10 Frames specification")
    spec = _json(spec_bytes, "V10 Frames specification")
    role = spec.get("segment_role")
    if role not in ROLES or (expected_role is not None and expected_role != role):
        raise SharedCanvasPreflightError("V10 segment_role differs from A_TO_C/C_TO_A contract")
    if spec != _expected_spec(role):
        raise SharedCanvasPreflightError("V10 Frames specification differs from the pinned configuration")
    paths = {
        "A": original_a_png, "C": original_c_png, "canvas": canvas_jpeg,
        "a_annotation": a_annotation, "c_annotation": c_annotation,
        "canvas_annotation": canvas_annotation, "manifest": shared_manifest,
        "A*": derived_a_png, "C*": derived_c_png,
        "qa": independent_qa_report,
    }
    observed = {label: _read(path, label) for label, path in paths.items()}
    if len({item[0] for item in observed.values()}) != len(observed):
        raise SharedCanvasPreflightError("all V10 inputs, outputs, annotations and reports must be distinct")
    for label, expected_sha in SOURCE_SHA256.items():
        if _sha(observed[label][1]) != expected_sha:
            raise SharedCanvasPreflightError(f"V10 {label} original/canvas bytes differ from pinned SHA-256")
    for label, fmt, size in (("A", "PNG", (1280, 720)), ("C", "PNG", (1280, 720)),
                             ("canvas", "JPEG", (1344, 756)),
                             ("A*", "PNG", (1344, 756)), ("C*", "PNG", (1344, 756))):
        _image(observed[label][1], label, fmt=fmt, size=size)
    manifest = _json(observed["manifest"][1], "shared-canvas manifest")
    manifest_sha = _sha(observed["manifest"][1])
    sources = manifest.get("source_images")
    outputs = manifest.get("outputs")
    if (not isinstance(sources, dict) or not isinstance(outputs, dict)
            or any(not isinstance(sources.get(key), dict) for key in SOURCE_SHA256)
            or any(not isinstance(outputs.get(key), dict) for key in ("A", "C"))):
        raise SharedCanvasPreflightError("shared-canvas manifest source/output records are incomplete")
    if (manifest.get("schema_version") != 1 or manifest.get("tool") != "photo_motion.shared_canvas"
            or manifest.get("transform") != TRANSFORM
            or any(sources[key].get("sha256") != SOURCE_SHA256[key] for key in SOURCE_SHA256)):
        raise SharedCanvasPreflightError("shared-canvas manifest lacks pinned source lineage/transform")
    output_hashes = {"A": _sha(observed["A*"][1]), "C": _sha(observed["C*"][1])}
    if (output_hashes["A"] == output_hashes["C"] or
            any(outputs[label].get("sha256") != digest
                for label, digest in output_hashes.items())):
        raise SharedCanvasPreflightError("derived A*/C* bytes differ from independently declared outputs")

    # Full deterministic replay, not just trust in the transform parameters
    # or a manifest's own checksum. The compositor never writes over inputs.
    try:
        from .shared_canvas import compose
    except ImportError as exc:
        raise SharedCanvasPreflightError("shared-canvas compositor unavailable; exact replay cannot run") from exc
    with tempfile.TemporaryDirectory(prefix="v10-replay-") as tmp:
        replay = compose(
            original_a_png, original_c_png, canvas_jpeg, tmp,
            a_sha=SOURCE_SHA256["A"], c_sha=SOURCE_SHA256["C"],
            canvas_sha=SOURCE_SHA256["canvas"],
            a_annotation=a_annotation, c_annotation=c_annotation,
            canvas_annotation=canvas_annotation,
            scale_num=37, scale_den=50, x=200, y=172,
            window=(355, 172, 1020, 705), feather=(55, 5, 18),
        )
        replay_dir = Path(tmp)
        for label, filename in (("A*", "A_shared_canvas.png"),
                                ("C*", "C_shared_canvas.png"),
                                ("manifest", "shared_canvas.manifest.json")):
            if (replay_dir / filename).read_bytes() != observed[label][1]:
                raise SharedCanvasPreflightError(f"V10 {label} differs from exact deterministic replay")
        if replay.get("outputs") != manifest.get("outputs"):
            raise SharedCanvasPreflightError("replayed output manifest differs")

    qa = _json(observed["qa"][1], "independent source QA report")
    _qa_report(qa, manifest_sha, SOURCE_SHA256, output_hashes)
    # Defensive second read: reject paths which changed after first hashing,
    # including a changed QA verdict and substituted local endpoint files.
    for label, (path, payload) in observed.items():
        if _sha(path.read_bytes()) != _sha(payload):
            raise SharedCanvasPreflightError(f"V10 {label} bytes changed during qualification")
    if _sha(spec_file.read_bytes()) != _sha(spec_bytes):
        raise SharedCanvasPreflightError("V10 Frames spec changed during qualification")
    start, end = ROLES[role]
    return {
        "authority": AUTHORITY, "segment_role": role,
        "spec_sha256": _sha(spec_bytes),
        "source_original_sha256": dict(SOURCE_SHA256),
        "shared_canvas_manifest_sha256": manifest_sha,
        "independent_source_qa_report_sha256": _sha(observed["qa"][1]),
        "derived_a_sha256": output_hashes["A"],
        "derived_c_sha256": output_hashes["C"],
        "start_sha256": output_hashes[start], "end_sha256": output_hashes[end],
        "deterministic_replay": "EXACT_BYTE_REPLAY_PASS",
        "independent_source_qa": "CANDIDATE_FOR_DIAGNOSTIC_ONLY",
        "parent_v6_card_status": V7_PARENT_V6_STATUS,
        "anatomical_left_right_proven": False,
        "video_motion_form_and_release_approval": "NOT_EVALUATED",
    }


def _main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for label in ("spec", "original_a_png", "original_c_png", "canvas_jpeg",
                  "shared_manifest", "derived_a_png", "derived_c_png"):
        p.add_argument(label)
    for label in ("a_annotation", "c_annotation", "canvas_annotation", "independent_qa_report"):
        p.add_argument("--" + label.replace("_", "-"), required=True)
    p.add_argument("--segment-role", choices=tuple(ROLES), required=True)
    args = p.parse_args(argv)
    try:
        result = verify_segment(args.spec, args.original_a_png, args.original_c_png,
                                args.canvas_jpeg, args.shared_manifest,
                                args.derived_a_png, args.derived_c_png,
                                a_annotation=args.a_annotation, c_annotation=args.c_annotation,
                                canvas_annotation=args.canvas_annotation,
                                independent_qa_report=args.independent_qa_report,
                                expected_role=args.segment_role)
    except (SharedCanvasPreflightError, OSError, ValueError, TypeError) as exc:
        print(f"V10 preflight HOLD: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
