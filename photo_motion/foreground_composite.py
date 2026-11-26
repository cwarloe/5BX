"""Deterministic photographic-foreground / fixed-plate experiment.

Inputs are independently byte-pinned PNGs. This tool only composites supplied
pixels; it cannot extract a person, create a clean plate, or approve exercise
form. Keep private photographic inputs and rendered outputs outside Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image


HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class CompositeError(ValueError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _exact_keys(value: dict, keys: set[str], *, where: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise CompositeError(f"{where} must contain exactly {sorted(keys)}")


def _load_png(asset: dict, *, mode: str, where: str) -> tuple[Path, np.ndarray]:
    _exact_keys(asset, {"path", "sha256"}, where=where)
    path = Path(asset["path"])
    expected = asset["sha256"]
    if not isinstance(expected, str) or not HEX_SHA256.fullmatch(expected):
        raise CompositeError(f"{where}: expected a lowercase SHA-256")
    if not path.is_file() or sha256(path) != expected:
        raise CompositeError(f"{where}: missing or SHA-256-mismatched input")
    with Image.open(path) as img:
        img.load()
        if img.format != "PNG" or img.mode != mode:
            raise CompositeError(f"{where}: exact {mode} PNG required")
        array = np.asarray(img, dtype=np.uint8).copy()
    return path, array


def _load_recipe(path: Path) -> dict:
    recipe = json.loads(path.read_text(encoding="utf-8"))
    _exact_keys(
        recipe,
        {"schema_version", "plate", "frames", "fps", "margin_px", "key_spill"},
        where="recipe",
    )
    if recipe["schema_version"] != 1:
        raise CompositeError("unsupported recipe schema")
    if not isinstance(recipe["frames"], list) or not recipe["frames"]:
        raise CompositeError("frames must be a nonempty ordered list")
    for index, asset in enumerate(recipe["frames"]):
        required = {"path", "sha256"}
        optional = {"required_alpha_points", "required_alpha_regions"}
        if (not isinstance(asset, dict) or
                not required.issubset(asset) or set(asset) - required - optional):
            raise CompositeError(f"frames[{index}]: unexpected asset or landmark fields")
        points = asset.get("required_alpha_points", [])
        if not isinstance(points, list):
            raise CompositeError(f"frames[{index}]: landmarks must be a list")
        labels = []
        for point in points:
            _exact_keys(point, {"label", "x", "y", "min_alpha"}, where="required_alpha_point")
            if not isinstance(point["label"], str) or not point["label"].strip():
                raise CompositeError("required alpha-point label is empty")
            labels.append(point["label"])
            for coordinate in ("x", "y"):
                value = point[coordinate]
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise CompositeError("required alpha-point coordinate must be nonnegative integer")
            value = point["min_alpha"]
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 255:
                raise CompositeError("required alpha-point min_alpha must be 1..255")
        if len(set(labels)) != len(labels):
            raise CompositeError(f"frames[{index}]: landmark labels must be unique")
        regions = asset.get("required_alpha_regions", [])
        if not isinstance(regions, list):
            raise CompositeError(f"frames[{index}]: alpha regions must be a list")
        region_labels = []
        for region in regions:
            _exact_keys(
                region, {"label", "bbox_xyxy", "min_alpha", "max_below_pixels"},
                where="required_alpha_region",
            )
            if not isinstance(region["label"], str) or not region["label"].strip():
                raise CompositeError("required alpha-region label is empty")
            region_labels.append(region["label"])
            bbox = region["bbox_xyxy"]
            if not isinstance(bbox, list) or len(bbox) != 4 or any(
                not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in bbox
            ) or bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                raise CompositeError("required alpha-region bbox must be valid exclusive xyxy")
            value = region["min_alpha"]
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 255:
                raise CompositeError("required alpha-region min_alpha must be 1..255")
            value = region["max_below_pixels"]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise CompositeError("required alpha-region max_below_pixels must be nonnegative")
        if len(set(region_labels)) != len(region_labels):
            raise CompositeError(f"frames[{index}]: alpha-region labels must be unique")
    if not isinstance(recipe["fps"], int) or isinstance(recipe["fps"], bool) or not (1 <= recipe["fps"] <= 120):
        raise CompositeError("fps must be an integer from 1 through 120")
    if not isinstance(recipe["margin_px"], int) or isinstance(recipe["margin_px"], bool) or not (0 <= recipe["margin_px"] <= 100):
        raise CompositeError("margin_px must be an integer from 0 through 100")
    _exact_keys(recipe["plate"], {"asset", "origin", "evidence"}, where="plate")
    if recipe["plate"]["origin"] not in (
        "synthetic_fixture", "camera_plate_claim", "derived_plate_claim"
    ):
        raise CompositeError("unknown plate origin declaration")
    if not isinstance(recipe["plate"]["evidence"], str) or not recipe["plate"]["evidence"].strip():
        raise CompositeError("plate needs a human-readable provenance evidence label")
    if recipe["key_spill"] is not None:
        _exact_keys(recipe["key_spill"], {"rgb", "max_distance", "max_pixels"}, where="key_spill")
        color = recipe["key_spill"]["rgb"]
        if not isinstance(color, list) or len(color) != 3 or any(
            not isinstance(x, int) or isinstance(x, bool) or not 0 <= x <= 255 for x in color
        ):
            raise CompositeError("key_spill.rgb must be three 8-bit integers")
        for field, low, high in (("max_distance", 0, 441), ("max_pixels", 0, 100000000)):
            val = recipe["key_spill"][field]
            if not isinstance(val, int) or isinstance(val, bool) or not low <= val <= high:
                raise CompositeError(f"key_spill.{field} out of range")
    return recipe


def _metrics(
    fg: np.ndarray, margin: int, key: dict | None,
    required_points: list[dict], required_regions: list[dict],
) -> dict:
    alpha = fg[:, :, 3]
    h, w = alpha.shape
    ys, xs = np.nonzero(alpha)
    if xs.size:
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        clipped = bool(bbox[0] < margin or bbox[1] < margin or
                       bbox[2] > w - margin or bbox[3] > h - margin)
    else:
        bbox, clipped = None, True
    hard_edges = int(np.count_nonzero(
        (alpha[:, 1:] == 0) & (alpha[:, :-1] == 255)
    ) + np.count_nonzero(
        (alpha[:, :-1] == 0) & (alpha[:, 1:] == 255)
    ) + np.count_nonzero(
        (alpha[1:, :] == 0) & (alpha[:-1, :] == 255)
    ) + np.count_nonzero(
        (alpha[:-1, :] == 0) & (alpha[1:, :] == 255)
    ))
    key_pixels = None
    if key is not None:
        difference = fg[:, :, :3].astype(np.int16) - np.array(key["rgb"], dtype=np.int16)
        distance_squared = np.sum(difference.astype(np.int32) ** 2, axis=2)
        key_pixels = int(np.count_nonzero(
            (alpha > 0) & (distance_squared <= key["max_distance"] ** 2)
        ))
    absent_points = []
    for point in required_points:
        x, y = point["x"], point["y"]
        if x >= w or y >= h:
            raise CompositeError("required alpha point lies outside source frame")
        if int(alpha[y, x]) < point["min_alpha"]:
            absent_points.append(point["label"])
    failed_regions = []
    for region in required_regions:
        x0, y0, x1, y1 = region["bbox_xyxy"]
        if x1 > w or y1 > h:
            raise CompositeError("required alpha region lies outside source frame")
        deficit = int(np.count_nonzero(
            alpha[y0:y1, x0:x1] < region["min_alpha"]
        ))
        if deficit > region["max_below_pixels"]:
            failed_regions.append({
                "label": region["label"],
                "pixels_below_min_alpha": deficit,
            })
    warnings = []
    if bbox is None:
        warnings.append("EMPTY_FOREGROUND")
    if clipped:
        warnings.append("MASK_NEAR_IMAGE_EDGE")
    if hard_edges:
        warnings.append("HARD_ALPHA_EDGE")
    if key_pixels is None:
        warnings.append("KEY_SPILL_UNASSESSED")
    elif key_pixels > key["max_pixels"]:
        warnings.append("KEY_COLOR_IN_FOREGROUND")
    if absent_points:
        warnings.append("REQUIRED_ALPHA_POINT_MISSING")
    if failed_regions:
        warnings.append("REQUIRED_ALPHA_REGION_HOLE")
    return {
        "alpha_bbox_xyxy_exclusive": bbox,
        "visible_alpha_pixels": int(xs.size),
        "partial_alpha_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
        "hard_alpha_adjacencies": hard_edges,
        "key_color_visible_pixels": key_pixels,
        "required_alpha_points_checked": len(required_points),
        "missing_required_alpha_point_labels": absent_points,
        "required_alpha_regions_checked": len(required_regions),
        "failed_required_alpha_regions": failed_regions,
        "warnings": warnings,
    }


def _render_frame(fg: np.ndarray, plate: np.ndarray) -> np.ndarray:
    # uint16 cannot hold 255*255*2; uint32 guarantees no overflow.
    alpha = fg[:, :, 3:4].astype(np.uint32)
    rgb = fg[:, :, :3].astype(np.uint32)
    background = plate.astype(np.uint32)
    result = ((rgb * alpha + background * (255 - alpha) + 127) // 255).astype(np.uint8)
    if not np.array_equal(result[fg[:, :, 3] == 0], plate[fg[:, :, 3] == 0]):
        raise CompositeError("background pixels changed outside alpha mask")
    return result


def _run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise CompositeError(f"subprocess failed ({command[0]}): {result.stderr[-500:]}")
    return result.stdout


def _encode_mp4(out: Path, fps: int, count: int, width: int, height: int) -> dict:
    command = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-xerror",
        "-framerate", str(fps), "-start_number", "0",
        "-i", str(out / "frame_%06d.png"), "-map", "0:v:0", "-an",
        "-map_metadata", "-1", "-c:v", "libx264", "-preset", "medium",
        "-crf", "16", "-pix_fmt", "yuv420p", "-threads", "1",
        "-movflags", "+faststart", str(out / "composite_preview.mp4"),
    ]
    _run(command)
    video = out / "composite_preview.mp4"
    probe = json.loads(_run([
        "ffprobe", "-v", "error", "-show_streams", "-of", "json", str(video)
    ]))
    streams = probe["streams"]
    if len(streams) != 1 or streams[0]["codec_type"] != "video":
        raise CompositeError("preview has unexpected stream count or audio")
    stream = streams[0]
    if (stream.get("codec_name") != "h264" or stream.get("width") != width or
            stream.get("height") != height or
            stream.get("r_frame_rate") != f"{fps}/1" or
            int(stream.get("nb_frames", -1)) != count):
        raise CompositeError("preview frame geometry, cadence or count changed")
    frame_md5 = _run([
        "ffmpeg", "-v", "error", "-xerror", "-i", str(video),
        "-map", "0:v:0", "-f", "framemd5", "-",
    ])
    frame_lines = [line for line in frame_md5.splitlines() if line and not line.startswith("#")]
    if len(frame_lines) != count:
        raise CompositeError("decoded preview frame count mismatch")
    version = _run(["ffmpeg", "-version"]).splitlines()[0]
    return {
        "file": video.name,
        "sha256": sha256(video),
        "codec": "h264",
        "pixel_format": stream.get("pix_fmt"),
        "audio_streams": 0,
        "frame_count_decoded": len(frame_lines),
        "decoded_framemd5_sha256": hashlib.sha256(frame_md5.encode("utf-8")).hexdigest(),
        "ffmpeg_version": version,
        "encoder_parameters": {"codec": "libx264", "crf": 16, "preset": "medium", "threads": 1, "pix_fmt": "yuv420p"},
        "bit_exact_across_toolchain_versions": False,
        "stream_copy": False,
    }


def composite(recipe_path: Path, out: Path, *, encode_mp4: bool = False) -> dict:
    recipe = _load_recipe(recipe_path)
    if out.exists():
        raise CompositeError("output directory already exists; refusing overwrite")
    plate_path, plate = _load_png(recipe["plate"]["asset"], mode="RGB", where="plate.asset")
    h, w, _ = plate.shape
    if w % 2 or h % 2:
        raise CompositeError("even plate dimensions required for yuv420 preview compatibility")
    paths = [plate_path]
    frame_paths = []
    for i, asset in enumerate(recipe["frames"]):
        path, array = _load_png(
            {"path": asset["path"], "sha256": asset["sha256"]},
            mode="RGBA", where=f"frames[{i}]",
        )
        if array.shape != (h, w, 4):
            raise CompositeError(f"frames[{i}]: foreground/plate dimensions differ")
        for point in asset.get("required_alpha_points", []):
            if point["x"] >= w or point["y"] >= h:
                raise CompositeError(f"frames[{i}]: alpha-point outside image")
        for region in asset.get("required_alpha_regions", []):
            if region["bbox_xyxy"][2] > w or region["bbox_xyxy"][3] > h:
                raise CompositeError(f"frames[{i}]: alpha-region outside image")
        paths.append(path)
        # Validate/decode each source before any write, but retain only its
        # path: large frame sequences must not accumulate in RAM.
        frame_paths.append(path)
    if len(set(path.resolve() for path in paths)) != len(paths):
        raise CompositeError("input assets must be distinct immutable files")
    out.mkdir(parents=True)
    metrics = []
    for index, path in enumerate(frame_paths):
        with Image.open(path) as image:
            fg = np.asarray(image, dtype=np.uint8).copy()
        result = _render_frame(fg, plate)
        target = out / f"frame_{index:06d}.png"
        Image.fromarray(result, "RGB").save(target, format="PNG")
        frame_metrics = _metrics(
            fg, recipe["margin_px"], recipe["key_spill"],
            recipe["frames"][index].get("required_alpha_points", []),
            recipe["frames"][index].get("required_alpha_regions", []),
        )
        frame_metrics.update({
            "index": index,
            "output_png": target.name,
            "output_png_sha256": sha256(target),
            "output_rgb_pixel_sha256": hashlib.sha256(result.tobytes()).hexdigest(),
            "background_outside_alpha_exact": True,
        })
        metrics.append(frame_metrics)
    video = _encode_mp4(out, recipe["fps"], len(frame_paths), w, h) if encode_mp4 else None
    for path, asset in zip(paths, [recipe["plate"]["asset"], *recipe["frames"]]):
        if sha256(path) != asset["sha256"]:
            raise CompositeError("input mutated during processing; reject derived output")
    anomalies = sorted(set(warning for entry in metrics for warning in entry["warnings"]))
    # Source plate provenance is DECLARED by the recipe, never independently
    # authenticated from pixels or promoted to form/production acceptance.
    report = {
        "schema_version": 1,
        "status": "QA_FLAGGED_EXPERIMENTAL_HOLD" if anomalies else "PIXEL_QA_PASS_FORM_HOLD",
        "production_release": "HOLD",
        "exercise_form": "NOT_EVALUATED",
        "plate_origin_claim": recipe["plate"]["origin"],
        "plate_origin_independently_verified": False,
        "plate_evidence_label": recipe["plate"]["evidence"],
        "plate_sha256": recipe["plate"]["asset"]["sha256"],
        "frame_source_sha256": [asset["sha256"] for asset in recipe["frames"]],
        "composition": "integer_alpha_rgb_round_nearest_half_up",
        "dimensions": [w, h],
        "fps": recipe["fps"],
        "margin_px": recipe["margin_px"],
        "key_spill": recipe["key_spill"],
        "static_plate_reused_for_every_frame": True,
        "inputs_rehashed_unchanged": True,
        "frames": metrics,
        "warning_codes": anomalies,
        "video_preview": video,
    }
    (out / "composite_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path, help="JSON with exact SHA-256-pinned PNG inputs")
    parser.add_argument("--out", required=True, type=Path, help="new output directory")
    parser.add_argument("--encode-mp4", action="store_true", help="optional H.264 preview; encoding, not stream-copy")
    args = parser.parse_args(argv)
    try:
        report = composite(args.recipe, args.out, encode_mp4=args.encode_mp4)
    except (CompositeError, OSError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"foreground composite HOLD: {error}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": report["status"],
        "production_release": "HOLD",
        "frames": len(report["frames"]),
        "warnings": report["warning_codes"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
