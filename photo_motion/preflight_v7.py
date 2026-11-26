"""Unpaid V7 *direct prepared-pair* provenance gate for Chart 1 scissor.

This is a distinct, weaker origin claim than V6's fully replayed card crop.
The original 1536x1024 V6 composite is unavailable after an ephemeral-workspace
loss. V7 verifies the exact independently preserved A and C *prepared PNG bytes*
as its new source authority; historical V6 manifests, when supplied, can only
be consistency-checked, not independently replayed.

    python3 -m photo_motion.preflight_v7 SPEC PREPARED_A PREPARED_C \
      [--start-manifest A.json --opposite-manifest C.json]

No API calls, credits, human form approval or production release occur here.
"""

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .contract import validate
from .source_authority import (
    V6_ANATOMICAL_LEFT_RIGHT_PROVEN, V6_PANEL_A_CROP, V6_PANEL_A_START_STATE,
    V6_PANEL_C_CROP, V6_PANEL_C_OPPOSITE_STATE, V6_TAGGED_CARD_SHA256,
    V7_PARENT_V6_STATUS, V7_PREPARED_A_SHA256, V7_PREPARED_C_SHA256,
    V7_PREPARED_PAIR_AUTHORITY, V7_PREPARED_SIZE,
)


class PreflightError(ValueError):
    """Source is not the exact byte-pinned V7 photographic prepared pair."""


def _read(path, label):
    item = Path(path)
    if item.is_symlink():
        raise PreflightError(f"{label} must not be a symlink")
    item = item.resolve()
    if not item.is_file():
        raise PreflightError(f"{label} missing: {item}")
    return item, item.read_bytes()


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _decode_png(payload, expected_sha, label):
    if _hash(payload) != expected_sha:
        raise PreflightError(f"{label} SHA-256 differs from the V7 direct-image authority")
    try:
        with Image.open(io.BytesIO(payload)) as image:
            if image.format != "PNG" or image.mode != "RGB" or image.size != V7_PREPARED_SIZE:
                raise PreflightError(f"{label} must be an RGB 1280x720 PNG")
            image.load()  # Decode all pixels and check PNG chunks, not just headers.
            pixels_sha = _hash(image.tobytes())
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        if isinstance(exc, PreflightError):
            raise
        raise PreflightError(f"{label} is not a complete decodable PNG: {exc}") from exc
    return pixels_sha


def _manifest(path, panel, expected_output):
    label = f"historical {panel} manifest"
    file, payload = _read(path, label)
    try:
        entry = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"{label} must be valid UTF-8 JSON: {exc}") from exc
    if not isinstance(entry, dict):
        raise PreflightError(f"{label} must be an object")
    # Consistency of surviving claims, not independently verified original pixels.
    expected = {
        "tool": "photo_motion.panel_prep",
        "version": "1",
        "output_sha256": expected_output,
        "output_size": list(V7_PREPARED_SIZE),
        "source_image_sha256_before": V6_TAGGED_CARD_SHA256,
        "source_image_sha256_after": V6_TAGGED_CARD_SHA256,
        "source_size": [1536, 1024],
        "crop_bounds_half_open": list(V6_PANEL_A_CROP if panel == "A" else V6_PANEL_C_CROP),
    }
    for key, expected_value in expected.items():
        if entry.get(key) != expected_value:
            raise PreflightError(f"{label} {key} contradicts preserved source claims")
    # V6 A manifest preceded panel labeling; C never had that exception.
    if (panel == "C" or "source_panel" in entry) and entry.get("source_panel") != panel:
        raise PreflightError(f"{label} source_panel contradicts selected image role")
    return file, _hash(payload)


def verify_pair(spec_path, prepared_a, prepared_c, start_manifest=None, opposite_manifest=None):
    """Pin both saved photographic stills. Never claim V6 composite replay."""
    spec_file, spec_bytes = _read(spec_path, "V7 motion specification")
    try:
        spec = json.loads(spec_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"V7 specification is not UTF-8 JSON: {exc}") from exc
    provenance = spec.get("track_provenance") if isinstance(spec, dict) else None
    if (not isinstance(spec, dict) or spec.get("id") != "c1-ex5-scissor-jump-photo-v7-prepared-pair"
            or spec.get("movement_type") != "scissor_jump"
            or not isinstance(provenance, dict)
            or provenance.get("source_authority_version") != V7_PREPARED_PAIR_AUTHORITY):
        raise PreflightError("V7 preflight requires its separately versioned Chart 1 direct-pair motion contract")
    errors = validate(spec)
    if errors:
        raise PreflightError("invalid V7 movement contract: " + "; ".join(errors))

    a_file, a_bytes = _read(prepared_a, "V7 A start PNG")
    c_file, c_bytes = _read(prepared_c, "V7 C opposite PNG")
    if a_file == c_file:
        raise PreflightError("V7 A/C must be separate source files with opposite poses")
    a_pixels = _decode_png(a_bytes, V7_PREPARED_A_SHA256, "V7 A start PNG")
    c_pixels = _decode_png(c_bytes, V7_PREPARED_C_SHA256, "V7 C opposite PNG")

    if (start_manifest is None) != (opposite_manifest is None):
        raise PreflightError("V7 historical manifests must be supplied as a pair or omitted")
    observed = [(spec_file, _hash(spec_bytes), "V7 specification"),
                (a_file, _hash(a_bytes), "V7 A start PNG"),
                (c_file, _hash(c_bytes), "V7 C opposite PNG")]
    historical = None
    if start_manifest is not None:
        a_manifest, a_manifest_sha = _manifest(start_manifest, "A", V7_PREPARED_A_SHA256)
        c_manifest, c_manifest_sha = _manifest(opposite_manifest, "C", V7_PREPARED_C_SHA256)
        observed.extend(((a_manifest, a_manifest_sha, "historical A manifest"),
                         (c_manifest, c_manifest_sha, "historical C manifest")))
        historical = {"start_manifest_sha256": a_manifest_sha,
                      "opposite_manifest_sha256": c_manifest_sha,
                      "status": "CONSISTENCY_CHECKED_ONLY_PARENT_V6_NOT_REPLAYED"}
    for file, digest, label in observed:
        if not file.is_file() or _hash(file.read_bytes()) != digest:
            raise PreflightError(f"{label} changed during verification; discard this result")

    return {
        "tool": "photo_motion.preflight_v7", "schema_version": 1,
        "source_authority_version": V7_PREPARED_PAIR_AUTHORITY,
        "spec_sha256": _hash(spec_bytes), "source_video_type": "STILL_IMAGES_ONLY",
        "prepared_png_sha256": V7_PREPARED_A_SHA256,
        "prepared_png_pixels_sha256": a_pixels,
        "prepared_size": list(V7_PREPARED_SIZE),
        "source_marker_start_state": dict(V6_PANEL_A_START_STATE),
        "opposite_pose_reference": {
            "source_panel": "C", "prepared_png_sha256": V7_PREPARED_C_SHA256,
            "prepared_png_pixels_sha256": c_pixels,
            "prepared_size": list(V7_PREPARED_SIZE),
            "source_marker_opposite_state": dict(V6_PANEL_C_OPPOSITE_STATE),
        },
        "historical_manifests": historical,
        "historical_parent_v6_sha256_claim_only": V6_TAGGED_CARD_SHA256,
        "parent_v6_card_status": V7_PARENT_V6_STATUS,
        "parent_crop_replay_verified": False,
        "anatomical_left_right_proven": V6_ANATOMICAL_LEFT_RIGHT_PROVEN,
        "preflight_result": "VERIFIED_DIRECT_PREPARED_PAIR_BYTES_ONLY",
        "exercise_motion_and_release_approval": "NOT_EVALUATED",
        "warning": "V7 authenticates two prepared photographs directly. The missing V6 card prevents independent verification of historical crop/transform claims, physical airborne motion, anatomical side or human form approval.",
    }


def _main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("prepared_a", type=Path)
    parser.add_argument("prepared_c", type=Path)
    parser.add_argument("--start-manifest", type=Path)
    parser.add_argument("--opposite-manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(verify_pair(args.spec, args.prepared_a, args.prepared_c,
                                     args.start_manifest, args.opposite_manifest), indent=2, sort_keys=True))
    except (PreflightError, OSError, TypeError) as exc:
        print(f"V7 preflight FAIL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main())
