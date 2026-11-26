#!/usr/bin/env python3
"""Non-generative 2×2 card marker audit (diagnostic, not skeletal tracking).

Usage:
  python marker_component_ledger.py tagged_card.png

Requires Pillow, NumPy and SciPy. Reports bright orange/teal connected pixel
components separately for each tile. These are *color blobs*, not proof of
anatomical attachment; human joint-chain tracing remains mandatory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import label


def detect_components(image: Image.Image, min_pixels: int = 8) -> dict:
    hsv = np.asarray(image.convert("HSV"), dtype=np.uint8)
    hue, sat, value = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # Narrow hue+saturation windows reject most skin/track/field/shirt pixels.
    thresholds = {
        "orange": (hue >= 8) & (hue <= 30) & (sat >= 160) & (value >= 75),
        # Upper bound stays below the medium-blue tank's typical hue.
        "teal": (hue >= 112) & (hue <= 139) & (sat >= 85) & (value >= 60),
    }
    output = {}
    for color, mask in thresholds.items():
        labels, count = label(mask)
        comps = []
        for index in range(1, count + 1):
            ys, xs = np.where(labels == index)
            if xs.size < min_pixels:
                continue
            comps.append({
                "pixels": int(xs.size),
                "centroid_xy": [round(float(xs.mean()), 1), round(float(ys.mean()), 1)],
                "bbox_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            })
        output[color] = sorted(comps, key=lambda x: -x["pixels"])[:6]
    return output


def find_track_edge(image: Image.Image) -> int | None:
    """Locate first mostly reddish track row; environmental fiducial only."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    reddish = (r > 85) & (r > 1.20 * g) & (r > 1.27 * b) & (g < 145)
    frac = reddish.mean(axis=1)
    rows = np.where((frac > 0.68) & (np.arange(frac.size) > 0.30 * frac.size))[0]
    return int(rows[0]) if rows.size else None


def audit(path: Path, run_knee_check: bool = False, track_check: bool = False) -> dict:
    with Image.open(path) as original:
        im = original.convert("RGB")
    w, h = im.size
    left = w // 2
    top = h // 2
    rectangles = {
        "A_top_left": (2, 2, left - 2, top - 2),
        "B_top_right": (left + 2, 2, w - 2, top - 2),
        "C_bottom_left": (2, top + 2, left - 2, h - 2),
        "D_bottom_right": (left + 2, top + 2, w - 2, h - 2),
    }
    panels = {}
    for name, rect in rectangles.items():
        tile = im.crop(rect)
        panels[name] = {"tile_size": list(tile.size), **detect_components(tile)}
        if track_check:
            panels[name]["track_edge_y"] = find_track_edge(tile)
    result = {"source": str(path), "image_size": [w, h], "panels": panels,
              "warning": "color-pixel component centers are not anatomical joint tracking"}
    if run_knee_check:
        a, c = panels["A_top_left"], panels["C_bottom_left"]
        try:
            ao = a["orange"][0]
            at = a["teal"][0]
            co = c["orange"][0]
            ct = c["teal"][0]
            a_delta = round(at["centroid_xy"][1] - ao["centroid_xy"][1], 1)
            c_delta = round(co["centroid_xy"][1] - ct["centroid_xy"][1], 1)
            enough_pixels = min(ao["pixels"], at["pixels"], co["pixels"], ct["pixels"]) >= 200
            # Marker centroids are ankle-band *relative heights*, not knees.
            pass_marker_height = enough_pixels and a_delta >= 0.1 * top and c_delta >= 0.1 * top
            result["running_marker_height_check"] = {
                "A_teal_minus_orange_y_pixels": a_delta,
                "C_orange_minus_teal_y_pixels": c_delta,
                "min_required_each_pixels": round(0.1 * top, 1),
                "min_component_area": 200,
                "status": "MARKED HEIGHT EXCHANGE" if pass_marker_height else "NO MARKED HEIGHT PROOF",
                "caution": "Requires manual ankle→knee→hip chain and plantar support inspection",
            }
        except IndexError:
            result["running_marker_height_check"] = {
                "status": "NO MARKED HEIGHT PROOF",
                "reason": "Missing orange or teal components in A or C",
            }
    if track_check:
        ys = [p["track_edge_y"] for p in panels.values()]
        if None in ys:
            result["track_edge_check"] = {"status": "INDETERMINATE", "y_by_panel": ys}
        else:
            spread = max(ys) - min(ys)
            tol = round(0.03 * top, 1)
            result["track_edge_check"] = {
                "y_by_panel": ys, "spread_px": spread, "tolerance_px": tol,
                "status": "TRACK EDGE COHERENT" if spread <= tol else "REVIEW CAMERA REGISTRATION",
                "caution": "Field/track appearance is generated; consistent horizon does not certify camera geometry",
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--run-knee-check", action="store_true",
                        help="For high-knee cards only: require A orange ankle high, C teal ankle high")
    parser.add_argument("--track-check", action="store_true",
                        help="Compare reddish track boundary height across panels")
    args = parser.parse_args()
    print(json.dumps(audit(args.image, args.run_knee_check, args.track_check), indent=2))


if __name__ == "__main__":
    main()
