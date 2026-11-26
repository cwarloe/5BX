"""Deterministic, no-subject-crop 16:9 photo-panel preparation.

Default half-open crop (4, 4, 764, 508) is the verified clean upper-left
panel A of the archived V6 tagged photographic scissor-jump *diagnostic card*.
The original image is never edited, uploaded, or written to by this tool.

Pure geometry: take a contiguous crop with no cut through the known subject,
then fill ONLY the missing left/right canvas using reflected border pixels.
Optional resampling is explicitly recorded and is not pixel-lossless.
"""

import argparse
import hashlib
import io
import json
import os
import sys
from pathlib import Path

from PIL import Image, __version__ as PILLOW_VERSION


PIPELINE_VERSION = "1"
DEFAULT_V6_A_BOUNDS = (4, 4, 764, 508)  # left, top, right, bottom; half-open
EXPECTED_V6_CARD_SIZE = (1536, 1024)
VERIFIED_V6_SOURCE_SHA256 = "4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_available_output(path):
    """Check both existence and dangling symlinks; exclusive create follows."""
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing file or symlink: {path}")
    if not path.parent.is_dir():
        raise FileNotFoundError(f"output directory does not exist: {path.parent}")


def _reserve_exclusive(path):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(path, flags, 0o644)


def _write_pair_exclusive(image_path, image_bytes, manifest_path, manifest_bytes):
    """Create both new files; on failure remove only placeholders we created.

    No existing file can be silently replaced. We reserve both destinations
    before writing, preventing partial delivery caused by a preexisting manifest.
    """
    created = []
    handles = []
    try:
        for path in (image_path, manifest_path):
            fd = _reserve_exclusive(path)
            created.append(path)
            handles.append(fd)
        for fd, payload in zip(handles, (image_bytes, manifest_bytes)):
            with os.fdopen(fd, "wb", closefd=False) as output:
                output.write(payload)
                output.flush()
                os.fsync(output.fileno())
    except BaseException:
        for path in created:
            try:
                path.unlink()
            except OSError:
                pass
        raise
    finally:
        for fd in handles:
            try:
                os.close(fd)
            except OSError:
                pass


def _bounds(image_size, crop):
    if not isinstance(crop, (list, tuple)) or len(crop) != 4:
        raise ValueError("crop must be four half-open pixel coordinates: left,top,right,bottom")
    if any(type(v) is not int for v in crop):
        raise ValueError("crop coordinates must be integers")
    l, t, r, b = crop
    w, h = image_size
    if not (0 <= l < r <= w and 0 <= t < b <= h):
        raise ValueError(f"crop {tuple(crop)} is outside source {w}x{h} or has zero area")
    return l, t, r, b


def _fit_size(size):
    if size is None:
        return None
    if not isinstance(size, (tuple, list)) or len(size) != 2 or any(type(v) is not int or v <= 0 for v in size):
        raise ValueError("export_size must be [positive_integer_width, positive_integer_height]")
    if size[0] * 9 != size[1] * 16:
        raise ValueError("export_size must be exact 16:9; stretching is prohibited")
    return tuple(size)


def _mirror_side_pad(crop, left, right):
    """Reflect only the source's outer strips into added background pixels.

    This does not assume mirror padding can repair a moving limb that touches
    the crop boundary. V6 A was visually checked to have subject-free sides.
    """
    w, h = crop.size
    if left > w or right > w:
        raise ValueError("mirror padding cannot exceed original cropped width")
    final = Image.new(crop.mode, (left + w + right, h))
    final.paste(crop, (left, 0))
    if left:
        final.paste(crop.crop((0, 0, left, h)).transpose(Image.Transpose.FLIP_LEFT_RIGHT), (0, 0))
    if right:
        final.paste(crop.crop((w - right, 0, w, h)).transpose(Image.Transpose.FLIP_LEFT_RIGHT), (left + w, 0))
    return final


def prepare(source_path, output_path, *, crop=DEFAULT_V6_A_BOUNDS,
            expected_source_sha256=None, expected_source_size=None,
            export_size=None):
    """Prepare an existing photo into a new image+manifest; never overwrite.

    Returns the deterministic transform manifest as a dict. It does not claim
    to identify anatomy or exercise-form approval. No video-generation API is
    invoked.
    """
    src = Path(source_path)
    out = Path(output_path)
    if src.is_symlink():
        raise ValueError("source must be an explicit non-symlink image for stable provenance")
    if not src.is_file():
        raise FileNotFoundError(src)
    if out.suffix.lower() != ".png":
        raise ValueError("output must have .png extension")
    manifest_path = out.with_suffix(".manifest.json")
    if out.absolute() == src.absolute() or manifest_path.absolute() == src.absolute():
        raise ValueError("output cannot be the source image")
    _require_available_output(out)
    _require_available_output(manifest_path)

    if expected_source_sha256 is not None:
        if not isinstance(expected_source_sha256, str) or len(expected_source_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_source_sha256):
            raise ValueError("expected_source_sha256 must be a 64-character lowercase SHA-256")
    source_sha_before = sha256_file(src)
    if expected_source_sha256 and source_sha_before != expected_source_sha256:
        raise ValueError("source SHA-256 differs from the expected image; refusing to crop")

    with Image.open(src) as opened:
        if opened.format != "PNG":
            raise ValueError("source must be a PNG for the verified photographic panel recipe")
        if opened.mode not in ("RGB", "RGBA"):
            raise ValueError("source must be RGB/RGBA to preserve original pixel colors and alpha")
        image_size = opened.size
        if expected_source_size and tuple(expected_source_size) != image_size:
            raise ValueError(f"source dimensions {image_size} do not match expected {tuple(expected_source_size)}")
        box = _bounds(image_size, crop)
        panel = opened.crop(box)
        panel.load()

    panel_w, panel_h = panel.size
    if panel_h % 9:
        raise ValueError("crop height must be divisible by 9 for exact pixel-grid 16:9 side padding")
    full_w = panel_h * 16 // 9
    if full_w < panel_w:
        raise ValueError("selected panel is wider than 16:9; side padding cannot fix it without distortion")
    padding = full_w - panel_w
    pad_left, pad_right = padding // 2, padding - padding // 2
    framed = _mirror_side_pad(panel, pad_left, pad_right)
    target = _fit_size(export_size)
    if target:
        framed = framed.resize(target, Image.Resampling.LANCZOS)

    stream = io.BytesIO()
    framed.save(stream, format="PNG", compress_level=6, optimize=False)
    png = stream.getvalue()
    img_sha = hashlib.sha256(png).hexdigest()
    source_sha_after = sha256_file(src)
    if source_sha_after != source_sha_before:
        raise RuntimeError("source image changed during preparation; no output written")

    manifest = {
        "tool": "photo_motion.panel_prep", "version": PIPELINE_VERSION,
        "pillow_version": PILLOW_VERSION,
        "source_filename": src.name, "source_image_sha256_before": source_sha_before,
        "source_image_sha256_after": source_sha_after,
        "expected_source_sha256": expected_source_sha256,
        "source_hash_matches_expected": bool(expected_source_sha256 and source_sha_before == expected_source_sha256),
        "source_size": list(image_size), "source_mode": panel.mode,
        "crop_bounds_half_open": list(box), "crop_size": [panel_w, panel_h],
        "crop_pixels_sha256": hashlib.sha256(panel.tobytes()).hexdigest(),
        "canvas_size_before_resampling": [full_w, panel_h],
        "padding": {"left": pad_left, "right": pad_right, "top": 0, "bottom": 0,
                    "strategy": "reflect_existing_outer_background_strips_horizontal"},
        "resampling": {"used": target is not None,
                       "method": "LANCZOS" if target else "NONE",
                       "target_size": list(target) if target else None,
                       "note": "Resampling changes pixels; no subject cropping or aspect distortion" if target else "Central cropped panel pixels copied unchanged"},
        "output_filename": out.name, "output_size": list(framed.size),
        "output_sha256": img_sha,
        "video_motion_and_form": "NOT_EVALUATED",
        "visual_subject_completeness": (
            "PREVIOUSLY_VISUALLY_INSPECTED_V6_A_NOT_RETYPED_OR_APPROVED"
            if source_sha_before == VERIFIED_V6_SOURCE_SHA256 and box == DEFAULT_V6_A_BOUNDS
            else "NOT_EVALUATED_FOR_THIS_SOURCE_AND_CROP"
        ),
        "mirrored_side_extension_risk": "Reflected trees/track/background can repeat visual features and look artificial. Source subject-clearance is only visually documented for verified V6 panel A; other sources require an independent review.",
        "warning": "Tagged V6 still is diagnostic only; this geometric preparation does not establish anatomical identity or a completed video cycle."
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _write_pair_exclusive(out, png, manifest_path, manifest_bytes)
    return manifest


def _parse_pair(text):
    parts = text.lower().split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("expected WIDTHxHEIGHT")
    try:
        return int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected numeric WIDTHxHEIGHT") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create a 16:9 diagnostic photo frame from source V6 A without subject cropping")
    parser.add_argument("source", type=Path, help="Existing original 2x2 PNG; never modified")
    parser.add_argument("output", type=Path, help="New PNG path. Directory must exist, no overwrite or symlink")
    parser.add_argument("--crop", type=int, nargs=4, default=DEFAULT_V6_A_BOUNDS,
                        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="Half-open bounds; default verified V6 A safe inset: 4 4 764 508")
    parser.add_argument("--expected-sha256", help="Exact source hash precondition; defaults to the verified V6 source SHA")
    parser.add_argument("--allow-unverified-source", action="store_true",
                        help="Explicitly bypass the default V6 SHA pin for a different controlled source; visual clearance then NOT_EVALUATED")
    parser.add_argument("--expected-size", type=_parse_pair, default=EXPECTED_V6_CARD_SIZE,
                        help="Original source dimensions, default 1536x1024; pass another explicit size for other controlled tests")
    parser.add_argument("--export-size", type=_parse_pair, help="Optional true 16:9 export, e.g. 1280x720")
    args = parser.parse_args(argv)
    if args.allow_unverified_source and args.expected_sha256 is not None:
        parser.error("--allow-unverified-source and --expected-sha256 are mutually exclusive")
    expected_sha256 = (None if args.allow_unverified_source
                       else args.expected_sha256 or VERIFIED_V6_SOURCE_SHA256)
    try:
        result = prepare(args.source, args.output, crop=args.crop,
                         expected_source_sha256=expected_sha256,
                         expected_source_size=args.expected_size,
                         export_size=args.export_size)
    except (ValueError, FileExistsError, FileNotFoundError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"source_sha256": result["source_image_sha256_before"],
                      "expected_source_sha256": result["expected_source_sha256"],
                      "source_hash_matches_expected": result["source_hash_matches_expected"],
                      "output_sha256": result["output_sha256"],
                      "output_size": result["output_size"],
                      "crop_bounds_half_open": result["crop_bounds_half_open"],
                      "padding": result["padding"],
                      "visual_subject_completeness": result["visual_subject_completeness"],
                      "manifest": str(Path(args.output).with_suffix(".manifest.json"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
