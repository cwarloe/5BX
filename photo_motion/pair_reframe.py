"""Byte-traceable paired photographic headroom experiment.

This is an optional follow-on to a controlled A+C motion pilot, not a new
source authority or an exercise-form check. It only shrinks two existing RGB
photographs and fills the exposed frame with *mirrored existing pixels*. A
video model may still crop the subject or fail the prescribed movement.
"""

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path

from PIL import Image, __version__ as PILLOW_VERSION


SCHEMA_VERSION = 1
CANVAS_SIZE = (1280, 720)
OUTPUT_NAMES = ("A_reframed.png", "C_reframed.png", "pair.manifest.json")
RESAMPLING_GUARD_SOURCE_PIXELS = 16


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def _expected_hash(value, name):
    if not isinstance(value, str) or len(value) != 64 or any(
        c not in "0123456789abcdef" for c in value
    ):
        raise ValueError(f"{name} must be a lowercase 64-character SHA-256")


def _load_pinned(path, expected_sha, role):
    path = Path(path)
    _expected_hash(expected_sha, f"expected {role} hash")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{role} input must be an existing non-symlink file")
    sha_before = _sha256(path)
    if sha_before != expected_sha:
        raise ValueError(f"{role} input SHA-256 mismatch; source was substituted")
    with Image.open(path) as source:
        if source.format != "PNG" or source.mode != "RGB" or source.size != CANVAS_SIZE:
            raise ValueError(f"{role} input must be an RGB 1280x720 PNG")
        source.load()
        image = source.copy()
    if _sha256(path) != sha_before:
        raise RuntimeError(f"{role} input bytes changed during decode")
    return image, sha_before


def _subject_annotation(path, *, role, source_sha):
    """Read explicit human-attested subject bounds bound to source bytes.

    A bounding box is a conservative claim about the entire visible person,
    including hair, fingers, clothing, socks and shoes. Pixel code cannot
    establish whether an operator labeled that box truthfully or accurately.
    Uncertain or absent human claims fail closed before any image is written.
    """
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{role} subject annotation must be a non-symlink JSON file")
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f"{role} subject annotation is not valid JSON") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"{role} subject annotation schema must be version 1")
    if data.get("source_image_sha256") != source_sha or data.get("role") != role:
        raise ValueError(f"{role} subject annotation does not bind this source image and role")
    if data.get("image_size") != list(CANVAS_SIZE):
        raise ValueError(f"{role} subject annotation image dimensions mismatch")
    reviewer = data.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError(f"{role} subject annotation requires an identified reviewer")
    if data.get("confidence") != "CERTAIN" or data.get("coverage") != "ALL_VISIBLE_PERSON_PIXELS":
        raise ValueError(f"{role} subject annotation absent or uncertain about full person")
    box = data.get("subject_bounds_half_open")
    if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
        raise ValueError(f"{role} subject bbox must be four integer half-open coordinates")
    l, t, r, b = box
    if not (0 <= l < r <= CANVAS_SIZE[0] and 0 <= t < b <= CANVAS_SIZE[1]):
        raise ValueError(f"{role} subject bbox is outside the source image")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"{role} subject annotation changed during validation")
    return {"role": role, "sha256": digest, "subject_bounds_half_open": box,
            "reviewer": reviewer.strip(), "coverage": data["coverage"],
            "confidence": data["confidence"], "source_image_sha256": source_sha}


def _assert_reflection_safe(annotation, transform):
    """Conservatively exclude the subject from every mirrored edge strip.

    The 16-input-pixel guard exceeds the usual 3-lobe Lanczos support and
    leaves additional breathing room. It does not prove the background is
    aesthetically coherent; visual review remains a separate blocking gate.
    """
    scaled_w, scaled_h = transform["centered_resampled_image_size"]
    pad = transform["padding_pixels"]
    source_w, source_h = CANVAS_SIZE
    safe = [
        math.ceil(pad["left"] * source_w / scaled_w) + RESAMPLING_GUARD_SOURCE_PIXELS,
        math.ceil(pad["top"] * source_h / scaled_h) + RESAMPLING_GUARD_SOURCE_PIXELS,
        source_w - math.ceil(pad["right"] * source_w / scaled_w) - RESAMPLING_GUARD_SOURCE_PIXELS,
        source_h - math.ceil(pad["bottom"] * source_h / scaled_h) - RESAMPLING_GUARD_SOURCE_PIXELS,
    ]
    l, t, r, b = annotation["subject_bounds_half_open"]
    for label, violated in (("left", l < safe[0]), ("top", t < safe[1]),
                            ("right", r > safe[2]), ("bottom", b > safe[3])):
        if violated:
            raise ValueError(
                f"{annotation['role']} mirrored {label} strip overlaps or is too close "
                f"to annotated subject bbox {annotation['subject_bounds_half_open']}; "
                f"safe interior {safe}; refuse duplicated person/body parts"
            )
    return {"safe_subject_interior_half_open": safe,
            "resampling_guard_source_pixels": RESAMPLING_GUARD_SOURCE_PIXELS,
            "result": "NO_ANNOTATED_SUBJECT_IN_REFLECTION_STRIPS"}


def _mirror_background(image, *, scale_percent):
    """Pure central resize plus two-pass edge reflection, no crop or repaint."""
    w, h = image.size
    scaled = (w * scale_percent // 100, h * scale_percent // 100)
    if scaled[0] % 2 or scaled[1] % 2:
        raise ValueError("scale percentage must yield even target dimensions")
    pad_x = (w - scaled[0]) // 2
    pad_y = (h - scaled[1]) // 2
    if pad_x > scaled[0] or pad_y > scaled[1]:
        raise ValueError("source cannot supply enough pixels to reflect")
    subject = image.resize(scaled, Image.Resampling.LANCZOS)
    vertical = Image.new("RGB", (scaled[0], h))
    vertical.paste(subject, (0, pad_y))
    # Mirroring *edge strips* can duplicate track/trees. Keep that visible
    # limitation in the manifest; it is not recovered scene content.
    vertical.paste(
        subject.crop((0, 0, scaled[0], pad_y)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),
        (0, 0),
    )
    vertical.paste(
        subject.crop((0, scaled[1] - pad_y, scaled[0], scaled[1])).transpose(
            Image.Transpose.FLIP_TOP_BOTTOM
        ),
        (0, pad_y + scaled[1]),
    )
    out = Image.new("RGB", (w, h))
    out.paste(vertical, (pad_x, 0))
    out.paste(
        vertical.crop((0, 0, pad_x, h)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),
        (0, 0),
    )
    out.paste(
        vertical.crop((scaled[0] - pad_x, 0, scaled[0], h)).transpose(
            Image.Transpose.FLIP_LEFT_RIGHT
        ),
        (pad_x + scaled[0], 0),
    )
    return out, {
        "scale_percent": scale_percent,
        "interpolation": "Pillow LANCZOS",
        "centered_resampled_image_size": list(scaled),
        "central_region_half_open": [pad_x, pad_y, pad_x + scaled[0], pad_y + scaled[1]],
        "padding_pixels": {"left": pad_x, "right": pad_x, "top": pad_y, "bottom": pad_y},
        "padding_strategy": "reflect_top_bottom_then_left_right_from_resampled_source",
        "subject_scale_claim": (
            "Whole source image scaled uniformly; actual anatomical subject scale "
            "and head/shoe clearance require independent visual review"
        ),
    }


def _png_bytes(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG", compress_level=6, optimize=False)
    return stream.getvalue()


def _write_exclusive(payloads):
    """Reserve all three outputs, then write. Never replace any preexisting file."""
    created = []
    handles = []
    try:
        for path, _ in payloads:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = os.open(path, flags, 0o600)
            handles.append(fd)
            created.append(path)
        for fd, (_, payload) in zip(handles, payloads):
            with os.fdopen(fd, "wb", closefd=False) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
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


def reframe_pair(a_path, c_path, out_dir, *, a_sha256, c_sha256,
                 a_annotation, c_annotation, scale_percent=80):
    """Create A, C and one paired recipe manifest in an existing directory."""
    if type(scale_percent) is not int or not (70 <= scale_percent <= 90):
        raise ValueError("scale_percent must be an integer from 70 through 90")
    if Path(a_path).resolve() == Path(c_path).resolve():
        raise ValueError("A and C source paths must be distinct")
    out_dir = Path(out_dir)
    if not out_dir.is_dir() or out_dir.is_symlink():
        raise ValueError("output directory must exist and must not be a symlink")
    destinations = [out_dir / name for name in OUTPUT_NAMES]
    for dest in destinations:
        if dest.exists() or dest.is_symlink():
            raise FileExistsError(f"refusing to overwrite: {dest}")
        if dest.resolve() in (Path(a_path).resolve(), Path(c_path).resolve()):
            raise ValueError("output cannot replace a source image")
    a, actual_a_sha = _load_pinned(a_path, a_sha256, "A")
    c, actual_c_sha = _load_pinned(c_path, c_sha256, "C")
    if actual_a_sha == actual_c_sha:
        raise ValueError("A and C must be distinct physical poses / images")
    a_bounds = _subject_annotation(a_annotation, role="A", source_sha=actual_a_sha)
    c_bounds = _subject_annotation(c_annotation, role="C", source_sha=actual_c_sha)

    framed_a, transform = _mirror_background(a, scale_percent=scale_percent)
    framed_c, second_transform = _mirror_background(c, scale_percent=scale_percent)
    if transform != second_transform:
        raise AssertionError("A and C must use identical geometric transforms")
    a_clearance = _assert_reflection_safe(a_bounds, transform)
    c_clearance = _assert_reflection_safe(c_bounds, transform)
    a_bytes, c_bytes = _png_bytes(framed_a), _png_bytes(framed_c)
    if _sha256(a_path) != actual_a_sha or _sha256(c_path) != actual_c_sha:
        raise RuntimeError("one or both input files changed during preparation")
    if _sha256(a_annotation) != a_bounds["sha256"] or _sha256(c_annotation) != c_bounds["sha256"]:
        raise RuntimeError("one or both subject annotations changed during preparation")
    manifest = {
        "tool": "photo_motion.pair_reframe",
        "schema_version": SCHEMA_VERSION,
        "pillow_version": PILLOW_VERSION,
        "purpose": "EXPERIMENTAL_FRAMING_ISOLATED_VARIABLE",
        "source_parent_card_provenance": "NOT_VERIFIED_BY_THIS_TOOL",
        "subject_annotation_evidence": {
            "A": {**a_bounds, "reflection_clearance": a_clearance},
            "C": {**c_bounds, "reflection_clearance": c_clearance},
        },
        "source_images": {
            "A": {"filename": Path(a_path).name, "sha256": actual_a_sha, "size": list(CANVAS_SIZE)},
            "C": {"filename": Path(c_path).name, "sha256": actual_c_sha, "size": list(CANVAS_SIZE)},
        },
        "transform": transform,
        "output_images": {
            "A": {"filename": OUTPUT_NAMES[0], "sha256": hashlib.sha256(a_bytes).hexdigest(), "size": list(CANVAS_SIZE)},
            "C": {"filename": OUTPUT_NAMES[1], "sha256": hashlib.sha256(c_bytes).hexdigest(), "size": list(CANVAS_SIZE)},
        },
        "motion_form_identity_and_release": "NOT_EVALUATED",
        "flow_suitability": "NOT_FLOW_SAFE_UNTIL_INDEPENDENT_VISUAL_REVIEW",
        "visual_review_required": (
            "Mirrored top, bottom and side background strips can repeat trees, "
            "track lines or legs near an edge. Review head, shoes, anatomy, "
            "all borders and intended photographic identity before any Flow use."
        ),
        "not_a_generation_authority": (
            "New derived A/C images are NOT automatically authorized as V6 or "
            "V7 pre-credit sources. A future experiment needs its own versioned "
            "source authority, credit reservation, and human video QA."
        ),
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _write_exclusive(list(zip(destinations, (a_bytes, c_bytes, manifest_bytes))))
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description="Reproducible paired photographic A/C headroom experiment; no video or spending")
    parser.add_argument("a", type=Path, help="Existing prepared photographic panel A PNG")
    parser.add_argument("c", type=Path, help="Existing prepared photographic panel C PNG")
    parser.add_argument("out_dir", type=Path, help="Existing output directory; no filenames may already exist")
    parser.add_argument("--a-sha256", required=True, help="Expected complete A PNG SHA-256")
    parser.add_argument("--c-sha256", required=True, help="Expected complete C PNG SHA-256")
    parser.add_argument("--a-annotation", type=Path, required=True,
                        help="A source-bound human subject-bbox JSON; missing/uncertain blocks output")
    parser.add_argument("--c-annotation", type=Path, required=True,
                        help="C source-bound human subject-bbox JSON; missing/uncertain blocks output")
    parser.add_argument("--scale-percent", type=int, default=80, help="Uniform source scale, 70..90; default 80")
    args = parser.parse_args(argv)
    try:
        manifest = reframe_pair(
            args.a, args.c, args.out_dir,
            a_sha256=args.a_sha256, c_sha256=args.c_sha256,
            a_annotation=args.a_annotation, c_annotation=args.c_annotation,
            scale_percent=args.scale_percent,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(manifest, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
