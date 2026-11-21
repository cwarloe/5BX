#!/usr/bin/env python3
"""The approved one-camera stage and the Fraser-style overlay, shared by kit/build.py and video/chart.py.

Everything is read from config/theme.json:
  "stage"    one fixed camera, no zoom: one standing scale for every exercise, lying figures scaled up by
             lying_scale_multiplier, feet on floor_y, centred on foot_x, the head never cropped.
  "overlay"  a slanted name card plus one tip in the top left, a minimal white ring timer in the top right.

The overlay is its own layer: a frame-sized transparent card PNG plus one small ring PNG per video frame, laid over
the pose frames by ffmpeg. Nothing here is drawn into the boy or the backdrop.
"""
import math, os

KIT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(KIT)


# ---------- stage ----------
def stage_geom(theme, F):
    """Stage numbers in this format's pixels, or None when the stage does not apply (no stage block, disabled, or a
    tall format, which was never calibrated)."""
    st = theme.get("stage")
    if not st or st.get("enabled", True) is False or F["W"] < F["H"]: return None
    fw, fh = st["frame"]; k = F["H"] / fh
    return {"k": k, "floor_y": st["floor_y"] * k, "foot_x": st["foot_x"] * F["W"] / fw, "head_top_min": st.get("standing_head_top_min", 45) * k,
            "standing_scale": st["standing_scale"] * k, "mult": st["lying_scale_multiplier"], "ref_head": st.get("reference_head_px"),
            "margin": st.get("side_margin", 40) * k, "W": F["W"], "H": F["H"]}


def is_lying(strip, width, height):
    """strips.json "posture": "lying" | "standing" wins; otherwise a figure wider than it is tall (by 20%) is lying."""
    p = (strip or {}).get("posture")
    return p == "lying" if p in ("lying", "standing") else width > 1.2 * height


def stage_scale(sg, strip, width, height):
    """Frame pixels per sheet pixel for this strip. width, height: the figure's extent over all poses, in sheet pixels.
    Returns (scale, lying, notes). The head-landmark normalisation applies when the strip declares "head_px" (its
    hairline-to-chin in sheet pixels); the chart 1 sheets are the calibration sheets and need none."""
    s = sg["standing_scale"]; notes = []
    hp = (strip or {}).get("head_px")
    if hp and sg["ref_head"]: s *= sg["ref_head"] / hp
    lying = is_lying(strip, width, height)
    if lying: s *= sg["mult"]
    room_h = sg["floor_y"] - sg["head_top_min"]                      # the head is never cropped
    if height * s > room_h: s = room_h / height; notes.append("scaled down to keep the head in frame")
    room_w = sg["W"] - 2 * sg["margin"]
    if width * s > room_w: s = room_w / width; notes.append("scaled down to keep the body inside the frame")
    return s, lying, notes


# ---------- overlay ----------
def _font(name, size):
    from PIL import ImageFont
    p = name if os.path.isabs(name) else os.path.join(ROOT, name)
    return ImageFont.truetype(p, max(8, int(round(size))))


def _rgba(spec, default=(255, 255, 255, 255)):
    """'0xRRGGBB' or '0xRRGGBB@0.8' or 'white' -> RGBA."""
    if not spec: return default
    named = {"white": "0xffffff", "black": "0x000000"}
    col, _, a = str(spec).partition("@"); col = named.get(col, col).replace("#", "").replace("0x", "")
    return (int(col[0:2], 16), int(col[2:4], 16), int(col[4:6], 16), int(round(float(a or 1) * 255)))


def overlay_cfg(theme, F):
    o = theme.get("overlay") or {}; k = F["H"] / 1080.0
    return o, k


def card_layer(theme, F, name, tip):
    """Frame-sized transparent PNG: the slanted name card and its one tip, top left."""
    from PIL import Image, ImageDraw
    o, k = overlay_cfg(theme, F); c = o.get("name_card", {}); col = c.get("colors", {}); fonts = o.get("fonts", {})
    tf = _font(fonts.get("title", "assets/fonts/BarlowCondensed-BoldItalic.ttf"), c.get("title_px", 69) * k)
    pf = _font(fonts.get("tip", "assets/fonts/BarlowCondensed-Medium.ttf"), c.get("tip_px", 30) * k)
    name = name.upper(); m = c.get("margin_px", 42) * k; slant = c.get("slant_px", 30) * k
    px, pt, gap, pb = 27 * k, 14 * k, 4 * k, 16 * k
    tb, pbb = tf.getbbox(name), pf.getbbox(tip) if tip else (0, 0, 0, 0)
    tw, th, pw, ph = tb[2] - tb[0], tb[3] - tb[1], pbb[2] - pbb[0], pbb[3] - pbb[1]
    w = max(tw, pw) + 2 * px + slant; h = pt + th + (gap + ph if tip else 0) + pb
    im = Image.new("RGBA", (F["W"], F["H"]), (0, 0, 0, 0))
    S = 3; card = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.polygon([(slant * S, 0), (w * S, 0), ((w - slant) * S, h * S), (0, h * S)], fill=_rgba(col.get("bar"), (0, 0, 0, 230)))
    card = card.resize((int(w), int(h)), Image.LANCZOS); d = ImageDraw.Draw(card)
    d.text((slant + px - tb[0], pt - tb[1]), name, font=tf, fill=_rgba(col.get("text")))
    if tip: d.text((slant * 0.5 + px - pbb[0], pt + th + gap - pbb[1]), tip, font=pf, fill=_rgba(col.get("tip"), (225, 225, 225, 255)))
    im.alpha_composite(card, (int(m), int(m)))
    return im, (int(m), int(m), int(m + w), int(m + h))


def ring_box(theme, F):
    o, k = overlay_cfg(theme, F); r = o.get("timer", {}); d = int(round(r.get("diameter_px", 192) * k)); m = r.get("margin_px", 42) * k
    return int(F["W"] - m - d), int(m), d


def ring_image(theme, F, frac, secs_left):
    """The minimal ring timer: a translucent dark disc, a faint track, a white arc for the time left, seconds in the middle."""
    from PIL import Image, ImageDraw
    o, k = overlay_cfg(theme, F); r = o.get("timer", {}); col = r.get("colors", {}); fonts = o.get("fonts", {}); _, _, D = ring_box(theme, F)
    S = 4; im = Image.new("RGBA", (D * S, D * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pad = 4 * k * S; box = (pad, pad, D * S - pad, D * S - pad); tw = max(6, int(r.get("track_px", 16) * k * S))
    d.ellipse(box, fill=_rgba(col.get("disc"), (0, 0, 0, 150)))
    d.ellipse(box, outline=_rgba(col.get("track"), (255, 255, 255, 50)), width=tw)
    if frac > 0.0005: d.arc(box, start=-90, end=-90 + 360 * min(1.0, frac), fill=_rgba(col.get("ring")), width=tw)
    im = im.resize((D, D), Image.LANCZOS); d = ImageDraw.Draw(im)
    nf = _font(fonts.get("timer", "assets/fonts/BarlowCondensed-Bold.ttf"), D * 0.42); sf = _font(fonts.get("tip", "assets/fonts/BarlowCondensed-Medium.ttf"), D * 0.12)
    cx, cy = D / 2, D / 2
    d.text((cx + 1, cy - D * 0.04 + 1), str(secs_left), font=nf, fill=(0, 0, 0, 160), anchor="mm")
    d.text((cx, cy - D * 0.04), str(secs_left), font=nf, fill=_rgba(col.get("text")), anchor="mm")
    d.text((cx, cy + D * 0.22), r.get("unit", "SEC"), font=sf, fill=(220, 220, 220, 230), anchor="mm")
    return im


def ring_frames(theme, F, allot, off, nframes, fps, outdir):
    """One ring PNG per video frame (ring_00000.png ...). Identical frames are written once and hard-linked."""
    from PIL import Image
    os.makedirs(outdir, exist_ok=True); seen = {}
    for i in range(nframes):
        left = max(0.0, allot - off - i / fps); key = (math.ceil(left - 1e-6), round(left / allot, 3))
        fn = os.path.join(outdir, f"ring_{i:05d}.png")
        if os.path.exists(fn): continue
        if key in seen:
            try: os.link(seen[key], fn)
            except OSError: Image.open(seen[key]).save(fn)
        else:
            ring_image(theme, F, left / allot, key[0]).save(fn); seen[key] = fn
    return os.path.join(outdir, "ring_%05d.png")


def tip_for(strip, exercise):
    """The card's one tip: strips.json "tip", else the booklet's first note when it is short, else ''."""
    if (strip or {}).get("tip"): return strip["tip"]
    notes = (exercise or {}).get("notes") or []
    return notes[0].rstrip(".") if notes and len(notes[0]) <= 44 else ""


# ---------- loops ----------
def pinned_loop(cycle, cycle_s, n_cycles, fps):
    """Frame-by-frame pose list for a seamless loop of n_cycles cycles, hold-and-cut, no crossfade.
    The first pose's hold is split in half, so the clip starts AND ends on the approved first pose: the last frame and
    the first frame are the same picture, and played on repeat the seam is one unbroken hold of pose 1."""
    n = max(1, int(round(cycle_s * n_cycles * fps))); per = n / (len(cycle) * n_cycles); half = per / 2
    out = []
    for i in range(n):
        t = (i + half) % n                                  # shift the timeline back by half a hold
        step = int(t // per) % len(cycle)
        out.append(cycle[step])
    out[-1] = cycle[0]                                      # pin: the last frame is the first pose, exactly
    return out


def choose_loop(cycle_s, lo=6.0, hi=10.0, target=8.0):
    """How many whole cycles make a loop of lo..hi seconds, and the cycle length to use. The loop decides the pace: if no
    whole number of cycles at the booklet pace lands in the window, the cycle is stretched or squeezed to the target."""
    best = None
    for n in range(1, 50):
        d = cycle_s * n
        if lo <= d <= hi and (best is None or abs(d - target) < abs(best[0] * cycle_s - target)): best = (n, cycle_s)
    if best: return best
    n = max(1, round(target / cycle_s)); return n, target / n


# ---------- render profiles ----------
def apply_profile(theme, F, fps, name="default"):
    """theme.json "profiles": "default" keeps the format as it is; "test" (1280x720, 24 fps) scales every pixel size of a
    wide format to the smaller frame. Returns (F, fps)."""
    prof = (theme.get("profiles") or {}).get(name)
    if prof is None: raise SystemExit(f"unknown profile '{name}' (theme.json 'profiles': {', '.join(theme.get('profiles') or {})})")
    if F["W"] < F["H"] or (prof["W"], prof["H"]) == (F["W"], F["H"]): return F, prof.get("fps", fps)
    k = prof["H"] / F["H"]; G = dict(F, W=prof["W"], H=prof["H"])
    for key in ("kicker", "title", "target", "clock", "bar"):
        if key in G: G[key] = max(1, int(round(G[key] * k)))
    if "box" in G: G["box"] = [int(round(v * k)) for v in G["box"]]
    if isinstance(G.get("hud"), dict): G["hud"] = {a: (int(round(v * k)) if a in ("margin", "gap", "free_h") else v) for a, v in G["hud"].items()}
    return G, prof.get("fps", fps)
