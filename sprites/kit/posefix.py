"""Small helpers for fixing a pose by compositing instead of regenerating it.

Taken from the Chart 1 scissor jump (v3, v4) and knee push-up (v1) fixes, November 2026.
See sprites/docs/POSE_FIX_LESSONS.md for when to use each one.

- key_unmix: cut a figure out of a generated *video* frame whose background is a textured
  pink-magenta (about 221,5,196) rather than flat magenta. Measures the background from the
  corners and unmixes the edge pixels so no pink fringe is left. For flat-magenta image sheets
  use keyer.key instead.
- darken: make far-side limbs slightly darker (default 18 percent, factor 0.82). Same hue,
  never brown-black. Never call it on a near-side limb.
- rotate_about: rotate (and optionally scale) an RGBA layer about a fixed joint, for example
  about planted hands or a knee, so that joint does not move.
- loop_seam: compare the last-to-first frame difference with a normal frame-to-frame step,
  so you can tell whether a clip loops without a visible jump.
"""
import numpy as np
from PIL import Image

FAR_LIMB = 0.82


def measure_background(rgb, corner=100):
    """Median colour of the top-left and bottom-right corners (assumed to be background)."""
    a = np.asarray(rgb)[..., :3]
    c = np.concatenate([a[:corner, :corner].reshape(-1, 3), a[-corner:, -corner:].reshape(-1, 3)])
    return np.median(c, 0)


def key_unmix(im, bg=None, lo=25, hi=110):
    """Background -> transparency with edge unmixing: fg = (pixel - (1 - alpha) * bg) / alpha.
    alpha ramps from 0 at colour distance `lo` from the background to 1 at `hi` (sum of |dR|+|dG|+|dB|)."""
    a = np.asarray(im.convert("RGB")).astype(float)
    bg = measure_background(a) if bg is None else np.asarray(bg, float)
    dist = np.abs(a - bg).sum(2)
    al = np.clip((dist - lo) / (hi - lo), 0, 1)
    fg = (a - (1 - al)[..., None] * bg) / np.maximum(al, 1e-3)[..., None]
    out = np.dstack([np.clip(fg, 0, 255), al * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def darken(rgba, mask, k=FAR_LIMB):
    """Multiply RGB by k inside mask. Keeps hue, so a far limb reads as the same skin in shade."""
    a = np.array(rgba, copy=True)
    a[mask, :3] = (a[mask, :3].astype(float) * k).clip(0, 255).astype(np.uint8)
    return a


def rotate_about(im, pivot, degrees, sx=1.0):
    """Rotate an RGBA image counter-clockwise by `degrees` about `pivot` (x, y), with optional
    horizontal scale sx about the same point. The pivot stays exactly where it was. Coordinates are
    PIL's continuous ones, so the centre of pixel (i, j) is (i + 0.5, j + 0.5).
    Uses premultiplied alpha so edges do not pick up a dark or coloured halo."""
    t = np.radians(degrees); c, s = np.cos(t), np.sin(t)
    px, py = pivot
    M = np.array([[sx * c, sx * s, 0], [-s, c, 0], [0, 0, 1]])
    T = np.array([[1, 0, px], [0, 1, py], [0, 0, 1]]) @ M @ np.array([[1, 0, -px], [0, 1, -py], [0, 0, 1]])
    Mi = np.linalg.inv(T)
    return im.convert("RGBa").transform(im.size, Image.AFFINE, tuple(Mi[:2].reshape(-1)), Image.BICUBIC).convert("RGBA")


def loop_seam(frames, sample_every=6):
    """frames: list of equal-size images. Returns (seam, step): mean absolute grey difference from the
    last frame to the first, and the mean of normal consecutive steps. A seam close to the step
    (knee push-up v1: 1.18 against 1.07) loops cleanly; a seam several times larger is a jump."""
    g = [np.asarray(f.convert("L")).astype(float) for f in frames]
    steps = [np.abs(g[i] - g[i + 1]).mean() for i in range(0, len(g) - 1, sample_every)]
    return float(np.abs(g[-1] - g[0]).mean()), float(np.mean(steps))
