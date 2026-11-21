"""Read-only technical inspection of a pose sheet using the kit's own keyer/segmenter.

This is not movement/form approval. All thresholds are screening guidance;
WARN/FAIL means inspect the image, not silently replace a selected asset.
Pillow and NumPy are needed only when this optional inspection runs.
"""

from pathlib import Path

PASS, WARN, FAIL, NOT_RUN = "PASS", "WARN", "FAIL", "NOT_RUN"


def _row(name, status, detail):
    return {"name": name, "status": status, "detail": detail}


def _finish(rows):
    # Optional floor/lift checks may be unconfigured without hiding a useful
    # overall result. No runnable checks at all must never read as PASS.
    status = next((s for s in (FAIL, WARN, PASS) if any(r["status"] == s for r in rows)), NOT_RUN)
    return {"status": status, "checks": rows}


def _dilate(mask, np):
    """One eight-neighbour expansion on the kit's 4px segmentation grid."""
    padded = np.pad(mask, 1, mode="constant")
    h, w = mask.shape
    out = mask.copy()
    for dy in range(3):
        for dx in range(3):
            out |= padded[dy:dy + h, dx:dx + w]
    return out


def _clearance(lab, left, right, width, ds, np):
    """Conservative, grid-resolution gap: enough precision for a warning gate."""
    a, b = lab == left, lab == right
    steps = max(1, int(0.03 * width / ds) + 1)
    for step in range(steps + 1):
        if np.any(a & b):
            return max(0, step - 1) * ds / width
        a = _dilate(a, np)
    return 0.03  # definitely exceeds the warning threshold


def inspect_sheet(path, poses, *, rows=1, row=0, qc=None, palette=None):
    """Return PASS/WARN/FAIL/NOT_RUN checks; never write to the art or ledger.

    `qc` may contain zero-based `grounded` pose indices, `floor_check`, and
    `airborne` index -> required fraction of sheet height. If not configured,
    those exercise-specific checks are explicitly NOT_RUN.
    """
    source = Path(path)
    if not source.is_file():
        return _finish([_row("availability", NOT_RUN, "Source image not local; technical inspection not performed")])
    try:
        import numpy as np
        from PIL import Image
        from . import build, keyer
    except ImportError as error:
        return _finish([_row("dependencies", NOT_RUN, f"Image inspection needs Pillow and NumPy: {error}")])

    checks = []
    try:
        with Image.open(source) as original:
            fmt = original.format
            rgb = np.asarray(original.convert("RGB"))
            transparent = keyer.has_real_transparency(original)
            rgba = keyer.key(original)
    except (OSError, ValueError) as error:
        return _finish([_row("readable image", FAIL, str(error))])

    h, w = rgb.shape[:2]
    checks.append(_row("format", PASS if fmt == "PNG" else WARN, f"{fmt or 'unknown'} {w}×{h}"))
    if transparent:
        checks.append(_row("background", PASS, "Actual alpha transparency present"))
    else:
        border = np.concatenate([rgb[:6].reshape(-1, 3), rgb[-6:].reshape(-1, 3),
                                 rgb[:, :6].reshape(-1, 3), rgb[:, -6:].reshape(-1, 3)]).astype(float)
        median = np.median(border, axis=0)
        delta = float(np.linalg.norm(median - np.array((255, 0, 255))))
        spread = float(np.percentile(np.linalg.norm(border - median, axis=1), 99))
        # The production keyer deliberately accepts the pink drift common in
        # generated sheets. The old qc-line 30/60 rule flagged most known-good
        # sheets; 60/95 screens drift while avoiding those repeated false alarms.
        state = PASS if delta <= 60 else (WARN if delta <= 95 else FAIL)
        checks.append(_row("background", state,
                           f"Border RGB {tuple(map(int, median))}, distance {delta:.0f} from magenta; noise p99 {spread:.0f}"))

    if rows > 1:
        try:
            bounds = build.row_bounds(rgba, rows, str(source))
            if not 0 <= row < len(bounds):
                raise ValueError(f"row index {row} outside 0–{len(bounds) - 1}")
            y0, y1 = bounds[row]
            rgba = rgba.crop((0, y0, w, y1))
        except (SystemExit, ValueError) as error:
            checks.append(_row("row selection", FAIL, str(error)))
            return _finish(checks)

    a = np.asarray(rgba)
    mask = a[:, :, 3] > 128
    lab, ds = build.components(mask)
    areas = np.bincount(lab.ravel())[1:]
    identifiers = [i + 1 for i, n in enumerate(areas) if n > 400]
    identifiers.sort(key=lambda i: float(np.argwhere(lab == i)[:, 1].mean()))
    actual = len(identifiers)
    checks.append(_row("figure count", PASS if actual == poses else FAIL,
                       f"Detected {actual}; expected {poses}. A mismatch can mean touching figures, fragments or wrong pose count"))
    if actual != poses:
        return _finish(checks)

    bounds = []
    for i in identifiers:
        yy, xx = np.where(lab == i)
        bounds.append((int(xx.min() * ds), int(yy.min() * ds),
                       int((xx.max() + 1) * ds), int((yy.max() + 1) * ds)))
    close_edges = sum(x0 < 0.008 * w or x1 > 0.992 * w or
                      y0 < 0.008 * a.shape[0] or y1 > 0.992 * a.shape[0]
                      for x0, y0, x1, y1 in bounds)
    checks.append(_row("edge margin", WARN if close_edges else PASS,
                       f"{close_edges} of {actual} figures within 0.8% of the image edge" if close_edges
                       else "All figures clear of image edges"))

    gaps = [_clearance(lab, identifiers[i], identifiers[i + 1], w, ds, np)
            for i in range(len(identifiers) - 1)]
    if gaps:
        gap = min(gaps)
        state = PASS if gap >= 0.03 else (WARN if gap >= 0.005 else FAIL)
        checks.append(_row("figure clearance", state,
                           f"Conservative grid estimate: {gap:.1%} of width; WARN below 3%, FAIL below 0.5%"))

    profile = qc or {}
    grounded = [int(i) for i in profile.get("grounded", [])]
    if profile.get("floor_check") and len(grounded) >= 2:
        if any(i not in range(actual) for i in grounded):
            checks.append(_row("floor alignment", FAIL, "Grounded-pose indices exceed figure count"))
        else:
            bottoms = [bounds[i][3] / a.shape[0] for i in grounded]
            spread = max(bottoms) - min(bottoms)
            checks.append(_row("floor alignment", PASS if spread <= .03 else (WARN if spread <= .06 else FAIL),
                               f"Grounded-pose bottom spread {spread:.1%} of image height"))
    else:
        checks.append(_row("floor alignment", NOT_RUN, "No grounded-pose specification for this strip"))

    airborne = profile.get("airborne") or {}
    if airborne and grounded:
        floor_y = float(np.median([bounds[i][3] for i in grounded if i < actual]))
        for ix, required in airborne.items():
            i = int(ix)
            if i >= actual:
                checks.append(_row("airborne lift", FAIL, f"Pose {i + 1} not present"))
            else:
                lift = (floor_y - bounds[i][3]) / a.shape[0]
                checks.append(_row("airborne lift", PASS if lift >= required else FAIL,
                                   f"Pose {i + 1}: {lift:.1%} above floor; minimum {required:.1%}"))
    else:
        checks.append(_row("airborne lift", NOT_RUN, "No airborne-pose specification for this strip"))

    if palette:
        thin, absent = [], []
        for j, ident in enumerate(identifiers):
            up = np.kron(lab == ident, np.ones((ds, ds), bool))
            full = np.zeros(a.shape[:2], bool)
            full[:up.shape[0], :up.shape[1]] = up
            pixels = a[:, :, :3][full & (a[:, :, 3] > 128)]
            if not len(pixels):
                continue
            px = pixels.astype(float)
            for color in palette:
                hexc = color["hex"].lstrip("#")
                target = np.array([int(hexc[k:k+2], 16) for k in (0, 2, 4)], float)
                frac = float((np.linalg.norm(px - target, axis=1) <= color["tol"]).mean())
                tag = f"{color['name']} pose {j + 1}"
                if frac < color["min_frac"] / 10:
                    absent.append(tag)
                elif frac < color["min_frac"]:
                    thin.append(tag)
        state = FAIL if absent else (WARN if thin else PASS)
        detail = ("Missing colour: " + ", ".join(absent[:6])) if absent else (
            "Thin colour: " + ", ".join(thin[:6]) if thin else "Configured character colours present")
        checks.append(_row("character palette", state, detail))
    else:
        checks.append(_row("character palette", NOT_RUN, "No palette configured for this avatar"))
    return _finish(checks)
