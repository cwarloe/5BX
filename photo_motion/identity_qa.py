"""Reproducible *appearance* diagnostics for real photographic video frames.

This tool only compares explicit human/pose-model-identified patches. It never
locates a face, proves personal identity, certifies exercise form, or approves
an asset. Patches can change location as the person moves: screen coordinates
alone must never be interpreted as persistent physical identity.

Run after `photo_motion inspect` has sampled a genuine MP4; all inputs/outputs
are private/local unless the operator separately archives the result.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def validate_box(box, name):
    if (not isinstance(box, list) or len(box) != 4 or
        any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
            for v in box)):
        raise ValueError(f"{name} must be four finite normalized numeric coordinates")
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise ValueError(f"{name} must follow 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1")
    return box


def _to_pixels(box, width, height, name):
    x0, y0, x1, y1 = validate_box(box, name)
    ix0, iy0 = int(math.floor(x0 * width)), int(math.floor(y0 * height))
    ix1, iy1 = int(math.ceil(x1 * width)), int(math.ceil(y1 * height))
    if ix1 - ix0 < 6 or iy1 - iy0 < 6:
        raise ValueError(f"{name} is under 6 pixels in width or height; choose a larger, visible patch")
    return ix0, iy0, min(width, ix1), min(height, iy1)


def patch_stats(image, box, name):
    """Return robust color/texture proxies, not identification or quality grades."""
    from PIL import ImageChops, ImageStat

    crop = image.crop(_to_pixels(box, *image.size, name)).convert("RGB")
    median_rgb = ImageStat.Stat(crop).median
    # Dimensionless chromaticity separates channel balance from exposure; a
    # brightness jump alone should not be labeled an identity change.
    chroma = [value / max(1.0, float(sum(median_rgb))) for value in median_rgb]
    luma = float(sum(a * b for a, b in zip(median_rgb, [0.2126, 0.7152, 0.0722])))
    gray = crop.convert("L")
    # Adjacent-difference detail proxy: only comparable for *similar camera
    # scale*, sharpness, motion blur, pose/view and lighting.
    dx = float(ImageStat.Stat(ImageChops.difference(
        gray.crop((0, 0, crop.width - 1, crop.height)),
        gray.crop((1, 0, crop.width, crop.height)))).mean[0])
    dy = float(ImageStat.Stat(ImageChops.difference(
        gray.crop((0, 0, crop.width, crop.height - 1)),
        gray.crop((0, 1, crop.width, crop.height)))).mean[0])
    return {
        "rgb_median": [round(float(x), 3) for x in median_rgb],
        "chromaticity": [round(float(x), 6) for x in chroma],
        "luminance_median": round(luma, 3),
        "adjacent_pixel_detail_proxy": round((dx + dy) / 2, 3),
        "patch_size_pixels": [crop.width, crop.height]
    }


def _delta(a, b):
    chroma = math.sqrt(sum((x - y) ** 2 for x, y in zip(a["chromaticity"], b["chromaticity"])))
    rgb = math.sqrt(sum((x - y) ** 2 for x, y in zip(a["rgb_median"], b["rgb_median"]))) / math.sqrt(3)
    lum_ratio = (b["luminance_median"] / a["luminance_median"]
                 if a["luminance_median"] > 1e-6 else None)
    detail_ratio = (b["adjacent_pixel_detail_proxy"] / a["adjacent_pixel_detail_proxy"]
                    if a["adjacent_pixel_detail_proxy"] > 1e-6 else None)
    return {
        "chromaticity_distance": round(chroma, 6),
        "median_rgb_distance_0_to_255": round(rgb, 3),
        "luminance_ratio_to_reference": None if lum_ratio is None else round(lum_ratio, 4),
        "detail_ratio_to_reference": None if detail_ratio is None else round(detail_ratio, 4)
    }


def _box_area(box):
    x0, y0, x1, y1 = box
    return (x1 - x0) * (y1 - y0)


def inspect_manifest(manifest_path):
    """Read a JSON recipe and return a local-only reproducible diagnostic.

    Images use paths relative to the recipe, and each patch bounding box uses
    normalized coordinates [x0,y0,x1,y1]. `reference` is an immutable
    high-resolution photographic master or the chart's approved start frame;
    sampled frames may each have distinct on-screen patch coordinates.
    """
    from PIL import Image

    path = Path(manifest_path).resolve()
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    ref = doc.get("reference")
    if not isinstance(ref, dict) or not ref.get("image") or not isinstance(ref.get("regions"), dict):
        raise ValueError("reference needs image and regions object")
    if not ref["regions"]:
        raise ValueError("reference.regions must name at least one actual garment, face, hair or shoe patch")
    samples = doc.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("samples must be a nonempty list")
    def read_image(filename):
        file = (path.parent / filename).resolve()
        if not file.is_file():
            raise FileNotFoundError(file)
        return file
    ref_path = read_image(ref["image"])
    with Image.open(ref_path) as ref_image:
        reference = {name: patch_stats(ref_image, box, f"reference.{name}")
                     for name, box in ref["regions"].items()}
        ref_dims = ref_image.size
    if "subject_box" in ref:
        validate_box(ref["subject_box"], "reference.subject_box")
    output = []
    for i, sample in enumerate(samples):
        if not isinstance(sample, dict) or not sample.get("image") or not isinstance(sample.get("regions"), dict):
            raise ValueError(f"samples[{i}] needs image and regions object")
        when = sample.get("time_seconds")
        if isinstance(when, bool) or not isinstance(when, (int, float)) or not math.isfinite(when) or when < 0:
            raise ValueError(f"samples[{i}].time_seconds must be a nonnegative finite number")
        file = read_image(sample["image"])
        with Image.open(file) as image:
            detected = {}
            for name in reference:
                if name not in sample["regions"]:
                    detected[name] = {"status": "NOT_EVALUATED", "reason": "Corresponding physical patch not located in sample"}
                    continue
                stats = patch_stats(image, sample["regions"][name], f"samples[{i}].{name}")
                detected[name] = {"status": "COMPARISON_ONLY", "stats": stats, "relative_to_master": _delta(reference[name], stats)}
            if "subject_box" in sample:
                validate_box(sample["subject_box"], f"samples[{i}].subject_box")
            scale = (round(_box_area(sample["subject_box"]) / _box_area(ref["subject_box"]), 4)
                     if "subject_box" in sample and "subject_box" in ref else None)
            output.append({
                "sample_index": i,
                "sample_time_seconds": when,
                "image": str(file), "image_sha256": sha256_file(file),
                "image_size": list(image.size),
                "subject_box_area_ratio_to_master": scale,
                "regions": detected
            })
    return {
        "tool": "photo_motion.identity_qa", "schema_version": 1,
        "input_manifest": str(path), "input_manifest_sha256": sha256_file(path),
        "master_image": str(ref_path), "master_sha256": sha256_file(ref_path),
        "master_image_size": list(ref_dims), "reference_patch_stats": reference,
        "samples": output,
        "identity_verdict": "NOT_EVALUATED",
        "wardrobe_and_appearance_verdict": "HUMAN_REVIEW_REQUIRED",
        "limitations": [
            "Patches must be independently located on the SAME physical shirt, shorts, hair, face or shoes; this code does not track anatomy or detect faces.",
            "Appearance/color/texture similarity cannot establish person identity; matching colors can belong to different people.",
            "Screen-space region size, pose, orientation, shadows, focus and lighting alter chromaticity and detail; do not interpret those deltas as causation.",
            "When subject area or camera framing differ, compare texture/detail only after manual inspection; this does not compensate mathematically.",
            "No exercise-form, motion, loop or release approval is implied by this diagnostic."
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Photographic subject/wardrobe appearance diagnostics from annotated frame regions")
    parser.add_argument("manifest", type=Path, help="JSON with immutable photo reference, sample frames and explicit normalized ROIs")
    parser.add_argument("--out", type=Path, required=True, help="Write JSON report here, not into source images")
    args = parser.parse_args(argv)
    try:
        if args.out.resolve() == args.manifest.resolve():
            raise ValueError("output report must not replace source manifest")
        if args.out.suffix.lower() != ".json":
            raise ValueError("output report must use a .json filename")
        if args.out.exists():
            raise FileExistsError(f"output already exists, refusing to overwrite: {args.out}")
        report = inspect_manifest(args.manifest)
        protected_paths = {report["master_image"], *(row["image"] for row in report["samples"])}
        if str(args.out.resolve()) in protected_paths:
            raise ValueError("output report cannot overwrite a source image")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2) + "\n")
        print(f"Recorded {len(report['samples'])} samples; identity {report['identity_verdict']}; report {args.out}")
        return 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
