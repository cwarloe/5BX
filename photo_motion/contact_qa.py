"""Evidence-based contact-point drift screening for *photographic* 5BX videos.

Accepts contact landmark observations from a human annotator or future pose
detector. It measures displacement of *named physical contacts* against their
initial screen locations; it does not infer joints from pixels, approve form,
or assert that a model's landmark identity is correct. The required matching
source video hash prevents accidentally reusing old annotations on new takes.

The module does not import or invoke any cartoon sprite logic.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

DEFAULT_MAX_DRIFT_FRACTION = 0.0125  # 1.25% of native frame width
DEFAULT_MIN_CONFIDENCE = 0.5
DEFAULT_MIN_OBSERVATIONS = 3


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def _validate(doc):
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise ValueError("contact annotations require schema_version 1")
    size = doc.get("frame_size")
    if not isinstance(size, list) or len(size) != 2:
        raise ValueError("frame_size must be [native_video_width, native_video_height]")
    w, h = (_number(v, "frame_size") for v in size)
    if w < 1 or h < 1 or int(w) != w or int(h) != h:
        raise ValueError("frame_size must contain positive integer dimensions")
    points = doc.get("fixed_contacts")
    if not isinstance(points, list) or not points or any(not isinstance(p, str) or not p.strip() for p in points) or len(points) != len(set(points)):
        raise ValueError("fixed_contacts must list unique nonempty landmark names")
    method = doc.get("annotation_method")
    if method not in ("manual", "model"):
        raise ValueError("annotation_method must be manual or model")
    samples = doc.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("samples must be a nonempty list")
    previous_time = -1.0
    for i, sample in enumerate(samples):
        if not isinstance(sample, dict):
            raise ValueError(f"samples[{i}] must be an object")
        t = _number(sample.get("time_seconds"), f"samples[{i}].time_seconds")
        if t < 0 or t <= previous_time:
            raise ValueError("sample times must be nonnegative, unique and strictly increasing")
        previous_time = t
        landmarks = sample.get("landmarks")
        if not isinstance(landmarks, dict):
            raise ValueError(f"samples[{i}].landmarks must be an object")
        if set(landmarks) - set(points):
            raise ValueError(f"samples[{i}] contains undeclared fixed contacts")
        for name, point in landmarks.items():
            if point is None:
                continue  # explicit inability to observe an occluded support
            if not isinstance(point, dict):
                raise ValueError(f"samples[{i}].{name} must be an object or null")
            x = _number(point.get("x"), f"samples[{i}].{name}.x")
            y = _number(point.get("y"), f"samples[{i}].{name}.y")
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(f"samples[{i}].{name} is outside native video dimensions")
            if "confidence" in point:
                confidence = _number(point["confidence"], f"samples[{i}].{name}.confidence")
                if not (0 <= confidence <= 1):
                    raise ValueError(f"samples[{i}].{name}.confidence must be between 0 and 1")
    value = doc.get("source_video_sha256")
    if value is not None and (not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
        raise ValueError("source_video_sha256 must be a lowercase 64-character SHA-256 or null")
    return int(w), int(h)


def evaluate_annotations(doc, *, max_drift_fraction=DEFAULT_MAX_DRIFT_FRACTION,
                         min_confidence=DEFAULT_MIN_CONFIDENCE,
                         min_observations=DEFAULT_MIN_OBSERVATIONS,
                         video_path=None):
    """Return a technical screening result, never a form/release decision.

    A PASS requires at least 3 credible samples for EVERY named planted point,
    and a real MP4 whose native size + SHA-256 match the annotations. An absent
    point, low-confidence model result, missing source pin, or source mismatch
    cannot be silently treated as a PASS.
    """
    w, h = _validate(doc)
    max_drift_fraction = _number(max_drift_fraction, "max_drift_fraction")
    min_confidence = _number(min_confidence, "min_confidence")
    if not (0 < max_drift_fraction < 0.25):
        raise ValueError("max_drift_fraction must be between 0 and 0.25")
    if not (0 <= min_confidence <= 1):
        raise ValueError("min_confidence must be between 0 and 1")
    if not isinstance(min_observations, int) or min_observations < 2:
        raise ValueError("min_observations must be an integer of at least 2")

    warnings = []
    source = None
    pinned = doc.get("source_video_sha256")
    matched = False
    if video_path is not None:
        from .video_qa import probe

        video = Path(video_path).resolve()
        if not video.is_file():
            raise FileNotFoundError(video)
        actual = _sha256(video)
        meta = probe(video)
        if (meta["width"], meta["height"]) != (w, h):
            raise ValueError("contact annotation dimensions do not match native video dimensions")
        if doc["samples"][-1]["time_seconds"] >= meta["duration_seconds"]:
            raise ValueError("contact annotation timestamp is beyond the last video frame")
        if pinned and actual != pinned:
            raise ValueError("source video SHA-256 does not match contact annotations; never reuse annotations across different takes")
        matched = pinned == actual
        if not pinned:
            warnings.append("Source video hash was not pinned in original annotation data; no matching-take PASS")
        source = {"path": str(video), "sha256": actual, "native_width": w,
                  "native_height": h, "duration_seconds": meta["duration_seconds"],
                  "matched_annotation_sha256": matched}
    else:
        warnings.append("No original MP4 supplied: coordinate-only evidence cannot receive a source-verified PASS")

    summaries = []
    status = "PASS"
    margin_px = w * max_drift_fraction
    for name in doc["fixed_contacts"]:
        observations = []
        skipped = []
        for sample in doc["samples"]:
            p = sample["landmarks"].get(name)
            t = sample["time_seconds"]
            if p is None:
                skipped.append({"time_seconds": t, "why": "missing_or_occluded"})
                continue
            if doc["annotation_method"] == "model" and "confidence" not in p:
                skipped.append({"time_seconds": t, "why": "model_confidence_unavailable"})
                continue
            if p.get("confidence", 1.0) < min_confidence:
                skipped.append({"time_seconds": t, "why": "low_confidence"})
                continue
            observations.append({"time_seconds": t, "x": p["x"], "y": p["y"]})

        first_time = doc["samples"][0]["time_seconds"]
        last_time = doc["samples"][-1]["time_seconds"]
        endpoint_missing = (not observations or observations[0]["time_seconds"] != first_time
                            or observations[-1]["time_seconds"] != last_time)
        if len(observations) < min_observations or endpoint_missing:
            reason = ("First and final observations are required for the loop/contact comparison" if endpoint_missing
                      else f"At least {min_observations} valid observations required")
            summaries.append({"landmark": name, "screen_status": "NOT_EVALUATED", "observations": len(observations),
                              "skipped": skipped, "reason": reason})
            status = "NOT_EVALUATED"
            continue
        baseline = observations[0]
        deviations = []
        for obs in observations:
            dx, dy = obs["x"] - baseline["x"], obs["y"] - baseline["y"]
            deviations.append({"time_seconds": obs["time_seconds"], "dx_px": round(dx, 3),
                               "dy_px": round(dy, 3), "distance_px": round(math.hypot(dx, dy), 3),
                               "fraction_of_frame_width": round(math.hypot(dx, dy) / w, 6)})
        max_px = max(d["distance_px"] for d in deviations)
        result = "PASS" if max_px <= margin_px else "WARN"
        summaries.append({"landmark": name, "screen_status": result, "observations": len(observations),
                          "skipped": skipped, "baseline": baseline, "deviations": deviations,
                          "max_drift_px": round(max_px, 3), "max_drift_fraction_width": round(max_px / w, 6),
                          "tolerance_px": round(margin_px, 3)})
        if result == "WARN" and status == "PASS":
            status = "WARN"

    # Incomplete evidence trumps the apparent lack of drift: a hidden hand may
    # be exactly the point that would expose the defect.
    if status != "NOT_EVALUATED" and not matched:
        status = "NOT_EVALUATED"
    return {
        "tool": "photo_motion.contact_qa", "schema_version": 1,
        "technical_contact_screen": status,
        "meaning": "PASS means only that *supplied* named pixel annotations stayed within tolerance; it does not validate exercise form or anatomy.",
        "video": source, "annotation_method": doc["annotation_method"],
        "fixed_contacts": doc["fixed_contacts"], "sample_count": len(doc["samples"]),
        "tolerance_fraction_width": max_drift_fraction,
        "min_confidence": min_confidence, "min_observations": min_observations,
        "per_landmark": summaries, "warnings": warnings,
        "unverified_requirements": [
            "Landmarks correspond to the correct anatomical physical joints and are not swapped or hallucinated",
            "Camera/background remains static rather than moving with the subject",
            "Contact constraints actually match the exercise at all times, including unannotated intermediate frames",
            "Complete continuous motion, exercise form, identity continuity, ghosting, and final human approval"
        ],
        "exercise_form_approval": "NOT_EVALUATED"
    }


def render_overlay(doc, video_path, output_dir, *, max_images=24):
    """Draw raw observed landmark dots and same-point baseline on exact frames.

    Never draws synthetic landmarks when annotations are missing. This is a
    separate visual evidence step; drawing does not change evaluation status.
    """
    from PIL import Image, ImageDraw
    from .video_qa import _extract

    requested = Path(output_dir)
    if requested.is_symlink():
        raise ValueError("overlay output path must not be a symbolic link")
    out = requested.resolve()
    video = Path(video_path).resolve()
    if out == video.parent or out == video or out in video.parents:
        raise ValueError("output directory must be separate from the original video")
    if not out.exists():
        out.mkdir(parents=True, exist_ok=False)
    if not out.is_dir():
        raise ValueError("overlay output must be a directory")
    if any(out.iterdir()):
        raise FileExistsError("overlay output directory is not empty; refusing to replace evidence")
    w, h = _validate(doc)
    palette = ["#ff8c2b", "#19c5bd", "#e95353", "#5aa9ff", "#fff300", "#d66af5"]
    baseline = {}
    for sample in doc["samples"]:
        for name in doc["fixed_contacts"]:
            if name not in baseline and sample["landmarks"].get(name) is not None:
                baseline[name] = sample["landmarks"][name]
    paths = []
    for idx, sample in enumerate(doc["samples"][:max_images]):
        raw_path = out / f"source_frame_{idx + 1:02d}.png"
        path = out / f"annotated_{idx + 1:02d}.png"
        _extract(video, sample["time_seconds"], raw_path)
        with Image.open(raw_path) as opened:
            im = opened.convert("RGB")
        draw = ImageDraw.Draw(im)
        sx, sy = im.width / w, im.height / h
        for c, name in enumerate(doc["fixed_contacts"]):
            color = palette[c % len(palette)]
            p = sample["landmarks"].get(name)
            b = baseline.get(name)
            if b is not None:
                bx, by = b["x"] * sx, b["y"] * sy
                draw.rectangle((bx - 4, by - 4, bx + 4, by + 4), outline=color, width=2)
            if p is not None:
                x, y = p["x"] * sx, p["y"] * sy
                draw.ellipse((x - 4, y - 4, x + 4, y + 4), outline=color, width=3)
                if b is not None:
                    draw.line((bx, by, x, y), fill=color, width=1)
                draw.text((x + 6, y + 5), name, fill=color)
        draw.text((8, 8), f"t = {sample['time_seconds']:.3f}s / annotation overlay (not pose detection)", fill="white", stroke_width=2, stroke_fill="black")
        with path.open("xb") as output:
            im.save(output, format="PNG")
        paths.append(str(path))
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect reproducible video contact-point annotations")
    parser.add_argument("annotations", type=Path, help="JSON with source MP4 SHA-256, native dimensions and named landmarks")
    parser.add_argument("--video", type=Path, help="Original MP4 needed for source-verified PASS and frame overlays")
    parser.add_argument("--out", type=Path, required=True, help="Separate output directory for reports and overlays")
    parser.add_argument("--tolerance", type=float, default=DEFAULT_MAX_DRIFT_FRACTION, help="Maximum Euclidean contact drift as a fraction of native frame width (default 0.0125)")
    parser.add_argument("--min-confidence", type=float, default=DEFAULT_MIN_CONFIDENCE)
    parser.add_argument("--no-overlays", action="store_true", help="Do not render annotated frames from source MP4")
    args = parser.parse_args(argv)
    try:
        original = args.annotations.resolve()
        doc = json.loads(original.read_text(encoding="utf-8"))
        report = evaluate_annotations(doc, max_drift_fraction=args.tolerance,
                                      min_confidence=args.min_confidence, video_path=args.video)
        output = args.out.resolve()
        output.mkdir(parents=True, exist_ok=False)
        report["annotation_sha256"] = _sha256(original)
        if args.video and not args.no_overlays:
            report["overlay_images"] = [str(Path(path).relative_to(output))
                                        for path in render_overlay(doc, args.video, output)]
        with (output / "contact_qa.json").open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"contact_screen": report["technical_contact_screen"],
                          "output": str(output), "source_sha256_checked": bool(report["video"] and report["video"]["matched_annotation_sha256"]),
                          "exercise_form_approval": "NOT_EVALUATED"}, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
