#!/usr/bin/env python3
"""Objective visual continuity checks for a four-panel 5BX photographic card.

This is a production-line *screen*, not exercise-form or age certification.
It measures camera/track registration and a conservative subset of saturated
blue tank-top pixels. Anatomical joint ownership and safe form require a
separate human review, ideally with tagged diagnostics.

Usage:
    python photo_card_consistency.py 34K_HigherFarElbow_Review.png
    python photo_card_consistency.py 34J.png --compare 34K.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import label


PANEL_KEYS = ("A_top_left", "B_top_right", "C_bottom_left", "D_bottom_right")


def split_four(image: Image.Image) -> dict[str, Image.Image]:
    """Keep a 4-px border away from the center grid so white isn't sampled."""
    w, h = image.size
    mid_x, mid_y = w // 2, h // 2
    rects = (
        (3, 3, mid_x - 3, mid_y - 3),
        (mid_x + 3, 3, w - 3, mid_y - 3),
        (3, mid_y + 3, mid_x - 3, h - 3),
        (mid_x + 3, mid_y + 3, w - 3, h - 3),
    )
    return {name: image.crop(box).convert("RGB")
            for name, box in zip(PANEL_KEYS, rects)}


def dominant_blue_shirt(panel: Image.Image) -> dict | None:
    """Median RGB of the largest plausible saturated-blue garment blob."""
    hsv = np.asarray(panel.convert("HSV"), dtype=np.uint8)
    rgb = np.asarray(panel.convert("RGB"), dtype=np.uint8)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    # PIL HSV scale: blue fabric (roughly 190–235°) => H=135–167.
    shirt = (h >= 132) & (h <= 176) & (s >= 85) & (v >= 65)
    labels, n = label(shirt)
    if not n:
        return None
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    idx = int(np.argmax(sizes))
    if sizes[idx] < 1000:
        return None
    ys, xs = np.where(labels == idx)
    colors = rgb[labels == idx]
    med = np.median(colors, axis=0)
    return {
        "pixels": int(sizes[idx]),
        "median_rgb": [int(round(x)) for x in med],
        "bbox_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "center_xy": [round(float(xs.mean()), 1), round(float(ys.mean()), 1)],
    }


def track_boundary(panel: Image.Image) -> int | None:
    """First majority-red row in the bottom part of an individual panel."""
    rgb = np.asarray(panel.convert("RGB"), dtype=np.float32)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    red = (r > 85) & (r > 1.20 * g) & (r > 1.27 * b) & (g < 145)
    fraction = red.mean(axis=1)
    y = np.arange(len(fraction))
    hits = np.flatnonzero((fraction >= 0.68) & (y >= len(y) * 0.30))
    return int(hits[0]) if len(hits) else None


def audit(path: Path) -> dict:
    with Image.open(path) as source:
        image = source.convert("RGB")
    panels = split_four(image)
    rows = {}
    for name, part in panels.items():
        rows[name] = {
            "track_boundary_y": track_boundary(part),
            "blue_shirt": dominant_blue_shirt(part),
        }
    track = [rows[k]["track_boundary_y"] for k in PANEL_KEYS]
    track_spread = None if any(v is None for v in track) else max(track) - min(track)
    track_tol = round(image.height / 2 * .03, 1)

    garments = [rows[k]["blue_shirt"] for k in PANEL_KEYS]
    if any(g is None for g in garments):
        shirt_max_channel_range = None
    else:
        medians = np.array([g["median_rgb"] for g in garments], dtype=int)
        shirt_max_channel_range = int(np.max(np.ptp(medians, axis=0)))

    return {
        "file": str(path),
        "image_dimensions": list(image.size),
        "panels": rows,
        "checks": {
            "track": {
                "spread_px": track_spread,
                "tolerance_px": track_tol,
                "status": "PASS" if track_spread is not None and track_spread <= track_tol else "REVIEW",
            },
            "blue_shirt": {
                "max_channel_median_range": shirt_max_channel_range,
                "tolerance_rgb_8bit": 18,
                "status": "PASS" if shirt_max_channel_range is not None
                                    and shirt_max_channel_range <= 18 else "REVIEW",
            },
            "anatomy_and_age": {
                "status": "HUMAN REVIEW REQUIRED",
                "why": "Clothing pixels and track lines cannot validate joint ownership, age, or safe form.",
            },
        },
    }


def compare(base: dict, candidate: dict) -> dict:
    drift = {}
    for name in PANEL_KEYS:
        b = base["panels"][name]
        c = candidate["panels"][name]
        bshirt, cshirt = b["blue_shirt"], c["blue_shirt"]
        color_shift = None if bshirt is None or cshirt is None else max(
            abs(x - y) for x, y in zip(bshirt["median_rgb"], cshirt["median_rgb"])
        )
        bt, ct = b["track_boundary_y"], c["track_boundary_y"]
        drift[name] = {
            "shirt_median_channel_max_absolute_delta": color_shift,
            "track_boundary_delta_px": None if bt is None or ct is None else ct - bt,
        }
    return {
        "baseline": base["file"],
        "candidate": candidate["file"],
        "panels": drift,
        "interpretation": "Optical continuity only. Use full-res side-by-side human anatomy QA.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--compare", type=Path, help="Second card to compare by panel")
    p.add_argument("--out", type=Path, help="Write JSON report in addition to stdout")
    args = p.parse_args()
    a = audit(args.image)
    payload = {"baseline": a}
    if args.compare:
        b = audit(args.compare)
        payload["candidate"] = b
        payload["comparison"] = compare(a, b)
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
