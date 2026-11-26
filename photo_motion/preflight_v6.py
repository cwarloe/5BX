"""Fail-closed, *unpaid* V6 scissor start-frame provenance preflight.

Bind the exact archived diagnostic card, its verified A start crop and optional
C opposite grounded crop, prepared 16:9 PNGs, transform manifests and motion
contract. Pretty still frames never prove exercise motion or form approval.

    python3 -m photo_motion.preflight_v6 SPEC ORIGINAL_CARD PREPARED_FRAME

The verified result can be recorded alongside a private paid-run request; the
experiment ledger re-runs this check before reserving V6 Flow credits.
"""

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image

from .contract import validate
from .panel_prep import _fit_size, _mirror_side_pad
from .source_authority import (
    V6_ANATOMICAL_LEFT_RIGHT_PROVEN, V6_PANEL_A_CROP, V6_PANEL_C_CROP,
    V6_PANEL_A_START_STATE, V6_PANEL_C_OPPOSITE_STATE,
    V6_TAGGED_CARD_SHA256, V6_TAGGED_CARD_SIZE,
)


class PreflightError(ValueError):
    """The submitted reference is not independently reproducible V6 evidence."""


def _bytes(path, label):
    requested = Path(path)
    if requested.is_symlink():
        raise PreflightError(f"{label} cannot be a symlink")
    path = requested.resolve()
    if not path.is_file():
        raise PreflightError(f"{label} missing: {path}")
    return path, path.read_bytes()


def _hash(payload):
    return hashlib.sha256(payload).hexdigest()


def _unchanged(path, initial_hash, label):
    if _hash(path.read_bytes()) != initial_hash:
        raise PreflightError(f"{label} changed during V6 preflight; discard results")


def _manifest_fields(manifest, original, image, source_mode, exported, panel):
    """Validate all identity/geometry fields that could change the artwork."""
    bounds = V6_PANEL_A_CROP if panel == "A" else V6_PANEL_C_CROP
    checks = {
        "tool": "photo_motion.panel_prep", "version": "1",
        "source_image_sha256_before": V6_TAGGED_CARD_SHA256,
        "source_image_sha256_after": V6_TAGGED_CARD_SHA256,
        "source_size": list(V6_TAGGED_CARD_SIZE), "source_mode": source_mode,
        "crop_bounds_half_open": list(bounds),
        "crop_size": [760, 504], "crop_pixels_sha256": _hash(original.crop(bounds).tobytes()),
        "canvas_size_before_resampling": [896, 504],
        "output_sha256": image[0], "output_size": image[1],
    }
    for key, expected in checks.items():
        if manifest.get(key) != expected:
            raise PreflightError(f"preparation manifest {key} does not match verified source/output")
    # Old, verified A-only preparations predate explicit panel labels; keep
    # them accepted without silently granting that legacy exception to C.
    if panel == "C" or "source_panel" in manifest:
        if manifest.get("source_panel") != panel:
            raise PreflightError(f"preparation manifest source_panel must identify V6 panel {panel}")
    if panel == "C" or "crop_matches_verified_panel_bounds" in manifest:
        if manifest.get("crop_matches_verified_panel_bounds") is not True:
            raise PreflightError("preparation manifest must attest verified panel-specific bounds")
    if panel == "C" and (manifest.get("expected_source_sha256") != V6_TAGGED_CARD_SHA256 or
                         manifest.get("source_hash_matches_expected") is not True):
        raise PreflightError("C preparation manifest must pin the original verified V6 source hash")
    padding = manifest.get("padding")
    if not isinstance(padding, dict) or any(padding.get(key) != value for key, value in {
        "left": 68, "right": 68, "top": 0, "bottom": 0,
        "strategy": "reflect_existing_outer_background_strips_horizontal",
    }.items()):
        raise PreflightError("preparation manifest does not describe the verified 68px mirrored side padding")
    resampling = manifest.get("resampling")
    if not isinstance(resampling, dict) or resampling.get("used") is not (exported is not None):
        raise PreflightError("preparation manifest resampling mode is missing or contradictory")
    expected_method = "LANCZOS" if exported is not None else "NONE"
    if resampling.get("method") != expected_method or resampling.get("target_size") != (list(exported) if exported else None):
        raise PreflightError("preparation manifest resampling parameters do not match the output")


def verify(spec_path, original_path, prepared_path, manifest_path=None, *, panel="A"):
    """Independently reproduce prepared bytes; never generate media or spend."""
    if panel not in ("A", "C"):
        raise PreflightError("V6 preflight panel must be A (start) or C (opposite grounded)")
    bounds = V6_PANEL_A_CROP if panel == "A" else V6_PANEL_C_CROP
    spec_file, spec_bytes = _bytes(spec_path, "motion specification")
    try:
        spec = json.loads(spec_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"motion specification is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(spec, dict) or spec.get("movement_type") != "scissor_jump":
        raise PreflightError("V6 preflight requires the Chart 1 scissor-jump motion contract")
    errors = validate(spec)
    if errors:
        raise PreflightError("invalid V6 motion contract: " + "; ".join(errors))

    original_file, original_bytes = _bytes(original_path, "original V6 card")
    original_sha = _hash(original_bytes)
    if original_sha != V6_TAGGED_CARD_SHA256:
        raise PreflightError("original V6 card SHA-256 differs from independently verified source")
    prepared_file, prepared_bytes = _bytes(prepared_path, "prepared PNG")
    if manifest_path is None:
        manifest_path = Path(prepared_path).with_suffix(".manifest.json")
    manifest_file, manifest_bytes = _bytes(manifest_path, "preparation manifest")
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError(f"preparation manifest is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise PreflightError("preparation manifest must be a JSON object")

    with Image.open(io.BytesIO(original_bytes)) as src:
        if src.format != "PNG" or src.mode not in ("RGB", "RGBA") or src.size != V6_TAGGED_CARD_SIZE:
            raise PreflightError("verified original V6 image must be an RGB/RGBA 1536x1024 PNG")
        source_mode = src.mode
        cropped_panel = src.crop(bounds)
        framed = _mirror_side_pad(cropped_panel, 68, 68)
        exported = None
        resampling = manifest.get("resampling")
        if not isinstance(resampling, dict):
            raise PreflightError("preparation manifest needs resampling parameters")
        if resampling.get("used") is True:
            try:
                exported = _fit_size(resampling.get("target_size"))
            except ValueError as exc:
                raise PreflightError(f"invalid prepared output size: {exc}") from exc
            if exported is None:
                raise PreflightError("resampled preparation has no target size")
            framed = framed.resize(exported, Image.Resampling.LANCZOS)
        elif resampling.get("used") is not False:
            raise PreflightError("resampling.used must be true or false")
        rendered = io.BytesIO()
        framed.save(rendered, format="PNG", compress_level=6, optimize=False)
        expected_bytes = rendered.getvalue()
        _manifest_fields(manifest, src, (_hash(prepared_bytes), list(framed.size)), source_mode, exported, panel)

    with Image.open(io.BytesIO(prepared_bytes)) as prepared:
        if (prepared.format != "PNG" or prepared.mode != source_mode
                or prepared.size != framed.size):
            raise PreflightError("prepared input must retain the expected PNG mode and 16:9 dimensions")
    if prepared_bytes != expected_bytes:
        raise PreflightError("prepared PNG bytes differ from replay of verified V6 crop/padding/resampling recipe")
    for path, digest, label in (
        (spec_file, _hash(spec_bytes), "motion specification"),
        (original_file, original_sha, "original V6 card"),
        (prepared_file, _hash(prepared_bytes), "prepared PNG"),
        (manifest_file, _hash(manifest_bytes), "preparation manifest"),
    ):
        _unchanged(path, digest, label)
    receipt = {
        "tool": "photo_motion.preflight_v6", "schema_version": 1,
        "spec_sha256": _hash(spec_bytes), "source_video_type": "STILL_IMAGE_ONLY",
        "original_v6_card_sha256": original_sha,
        "prepared_png_sha256": _hash(prepared_bytes),
        "preparation_manifest_sha256": _hash(manifest_bytes),
        "prepared_size": list(framed.size), "source_crop_half_open": list(bounds),
        "source_marker_start_state": dict(V6_PANEL_A_START_STATE if panel == "A" else V6_PANEL_C_OPPOSITE_STATE),
        "anatomical_left_right_proven": V6_ANATOMICAL_LEFT_RIGHT_PROVEN,
        "preflight_result": "VERIFIED_INPUT_BYTES_ONLY",
        "exercise_motion_and_release_approval": "NOT_EVALUATED",
        "warning": "Only input provenance is checked; a single prepared frame cannot prove video, form, anatomical side or owner approval.",
    }
    if panel == "C":
        receipt["source_panel"] = "C"
        receipt["source_marker_opposite_state"] = receipt.pop("source_marker_start_state")
        receipt["warning"] = "An opposite grounded reference still is not evidence of a filmed airborne transition or human form approval."
    return receipt


def verify_pair(spec_path, original_path, prepared_a_path, manifest_a_path,
                prepared_c_path, manifest_c_path):
    """Verify independent A/C byte replay against ONE canonical V6 card.

    The optional reference is C specifically, never an arbitrary extra image,
    identity master, generated endpoint or unchecked remote photo.
    """
    start = verify(spec_path, original_path, prepared_a_path, manifest_a_path, panel="A")
    opposite = verify(spec_path, original_path, prepared_c_path, manifest_c_path, panel="C")
    if (start["original_v6_card_sha256"] != opposite["original_v6_card_sha256"] or
            start["spec_sha256"] != opposite["spec_sha256"]):
        raise PreflightError("A/C poses must derive from one identical verified V6 source and motion specification")
    if start["prepared_png_sha256"] == opposite["prepared_png_sha256"]:
        raise PreflightError("A and C cannot be byte-identical; the reference must show a real opposite stance")
    # Add explicit A identity only to the NEW dual path: existing single-A
    # receipts/fingerprints remain byte-for-byte compatible with earlier runs.
    return {**start, "source_panel": "A", "opposite_pose_reference": opposite}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify exact V6 source, 16:9 prepared PNG and motion-plan provenance before a paid Flow experiment")
    parser.add_argument("spec", type=Path)
    parser.add_argument("original_card", type=Path)
    parser.add_argument("prepared_png", type=Path)
    parser.add_argument("--panel", choices=("A", "C"), default="A",
                        help="A is the original starting pose; C is the optional opposite grounded reference")
    parser.add_argument("--manifest", type=Path, help="Defaults to PREPARED.manifest.json")
    parser.add_argument("--receipt", type=Path, help="Optional new private JSON preflight receipt; never overwrites")
    args = parser.parse_args(argv)
    try:
        result = verify(args.spec, args.original_card, args.prepared_png, args.manifest, panel=args.panel)
        if args.receipt:
            target = args.receipt
            if target.resolve() in {args.spec.resolve(), args.original_card.resolve(), args.prepared_png.resolve(),
                                    (args.manifest or args.prepared_png.with_suffix(".manifest.json")).resolve()}:
                raise PreflightError("preflight receipt cannot overwrite an input")
            with target.open("x", encoding="utf-8") as receipt:
                json.dump(result, receipt, indent=2)
                receipt.write("\n")
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
