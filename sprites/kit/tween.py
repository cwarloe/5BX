"""In-between frames for the sprite boy, made at render time from two approved key poses.

Plain optical-flow morphing (ffmpeg minterpolate, OpenCV flow) melts his limbs on these pose gaps: a toe touch
swings the whole upper body through 110 degrees. So the boy is cut into body parts by the colours the
character sheet locks (cyan tank top, red shorts, white socks, blue shoes, skin), and each part is moved as a
rigid piece:

    legs       stay put, with a small optical-flow morph for knee bend and hip shift
    core       tank top: one rotation about the waist (where the tank meets the shorts)
    head       head and hair: the core's rotation plus its own nod about the neck
    arms       a second rotation about the shoulder, on top of the core's rotation
    far arm    follows the near arm, drawn behind the core

Both key poses are carried toward each other and swapped over in about one frame at the middle of the move,
once they line up, so a long see-through double image never shows. Key poses get the same finishing as the
in-betweens (backdrop, a soft floor contact shadow on its own layer, the boy) so a hold never pops.
Needs numpy and opencv-python (renderer only; CI never imports it).
"""
import json, os
import numpy as np
import cv2
from PIL import Image

TWEEN_VERSION = "1"
_K3 = np.ones((3, 3), np.uint8)


# ---------- body parts ----------
def _big(m, min_area):
    """Only the connected pieces of a colour mask with at least min_area pixels (drops lips, eye whites, stray shading)."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, 4] >= min_area; return keep[lab]


def _classes(x):
    a = x[..., 3] > 0.06; rgb = (x[..., :3] * 255).astype(np.uint8)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(int); h, s, v = hsv[..., 0] * 2, hsv[..., 1], hsv[..., 2]
    k = a.sum() / 40000.0                                                      # areas scale with the figure size
    return dict(a=a, cyan=_big(a & (h >= 180) & (h <= 205) & (s > 120) & (v > 120), 400 * k),
                red=_big(a & ((h <= 12) | (h >= 345)) & (s > 120) & (v > 90), 400 * k),
                shoe=_big(a & (h > 205) & (h < 250) & (s > 90) & (v > 70), 150 * k), sock=_big(a & (s < 40) & (v > 170), 120 * k),
                v=v, skin=a & (h >= 12) & (h <= 45) & (s > 60) & (v > 110))


def _grow(a, seeds):
    """Competitive region growing inside the silhouette: every unlabelled pixel joins the nearest seed (through the figure)."""
    lab = np.zeros(a.shape, np.uint8)
    for i, m in enumerate(seeds, 1): lab[m & a & (lab == 0)] = i
    for _ in range(600):
        free = a & (lab == 0)
        if not free.any(): break
        moved = False
        for i in range(1, len(seeds) + 1):
            g = (cv2.dilate((lab == i).astype(np.uint8), _K3) > 0) & free & (lab == 0)
            if g.any(): lab[g] = i; moved = True
        if not moved: lab[free] = 1; break
    return lab


def _axis(m):
    ys, xs = np.nonzero(m); P = np.stack([xs, ys], 1).astype(np.float64); c = P.mean(0)
    w, V = np.linalg.eigh(np.cov((P - c).T)); return c, V[:, 1], P


def parts(x):
    """Label map (1 core, 2 legs, 3 near arm, 4 far arm), waist and shoulder points, arm direction (degrees)."""
    C = _classes(x); a = C["a"]
    if not (C["cyan"].any() and C["red"].any()): return None
    lower = C["red"] | C["shoe"] | C["sock"]
    core = cv2.erode(C["skin"].astype(np.uint8), np.ones((5, 5), np.uint8))   # break thin skin bridges (a hand resting on a shin)
    n, lab, st, _ = cv2.connectedComponentsWithStats(core, connectivity=4)
    big = np.ones((15, 15), np.uint8); dcy, dlo = cv2.dilate(C["cyan"].astype(np.uint8), big) > 0, cv2.dilate(lower.astype(np.uint8), big) > 0
    seed_core, seed_legs, near, far = C["cyan"].copy(), lower.copy(), [], []
    for i in range(1, n):
        if st[i, 4] < 30: continue
        m = lab == i; cu, cl = int((m & dcy).sum()), int((m & dlo).sum())
        c, d, P = _axis(m); proj = (P - c) @ d; el = (proj.max() - proj.min()) / max(1.0, st[i, 4] / max(1.0, proj.max() - proj.min()))
        if el > 5 and cu > 25 and (m & cv2.dilate(C["red"].astype(np.uint8), big).astype(bool)).sum() < cu: near.append((st[i, 4], m))
        elif el > 5 and cl == 0: far.append(m)
        elif cl > 0 and cu <= 25: seed_legs |= m
        else: seed_core |= m                                                   # the face and neck
    hair = cv2.morphologyEx((a & (C["v"] < 70)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8)) > 0   # thick dark mass: hair (outlines are thin)
    hair &= ~(cv2.dilate(lower.astype(np.uint8), big) > 0); seed_core |= hair
    if not near: return None
    near.sort(key=lambda t: -t[0]); arm = near[0][1]
    for _, m in near[1:]: far.append(m)
    farm = np.zeros_like(a)
    for m in far: farm |= m
    lab = _grow(a, [seed_core, seed_legs, arm, farm])
    j = (cv2.dilate(C["cyan"].astype(np.uint8), big) > 0) & (cv2.dilate(C["red"].astype(np.uint8), big) > 0) & a
    ys, xs = np.nonzero(j)
    if not len(xs): return None
    waist = np.array([xs.mean(), ys.mean()])
    nk = cv2.dilate(C["cyan"].astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    head = (lab == 1) & ~nk; nh, hl, hst, _ = cv2.connectedComponentsWithStats(head.astype(np.uint8), connectivity=8)
    if nh > 1:
        keep = np.zeros(nh, bool); keep[1:] = hst[1:, 4] >= max(0.015 * a.sum(), 0.15 * hst[1:, 4].max()); head = keep[hl]   # head and hair, even when an arm splits the hair
        lab = lab.copy(); lab[head] = 5
        ys2, xs2 = np.nonzero(head & (cv2.dilate(C["cyan"].astype(np.uint8), np.ones((21, 21), np.uint8)) > 0))
        neck = np.array([xs2.mean(), ys2.mean()]) if len(xs2) else np.array(np.nonzero(head)[::-1], float).mean(1)
    else: neck = None
    c, d, P = _axis(lab == 3); proj = (P - c) @ d
    tc = np.array(np.nonzero(C["cyan"])[::-1], float).mean(1)
    if (c + d * proj.min() - tc) @ (c + d * proj.min() - tc) > (c + d * proj.max() - tc) @ (c + d * proj.max() - tc): d = -d; proj = -proj
    sh = P[proj < proj.min() + 0.06 * (proj.max() - proj.min())].mean(0)          # the shoulder end of the arm
    return dict(lab=lab, waist=waist, shoulder=sh, neck=neck, arm_deg=float(np.degrees(np.arctan2(d[1], d[0]))))


# ---------- geometry ----------
def _M(piv, deg, dst=None):
    """2x3 affine: rotate about piv by deg (clockwise on screen), then move piv to dst."""
    M = cv2.getRotationMatrix2D((float(piv[0]), float(piv[1])), -deg, 1.0)
    if dst is not None: M[:, 2] += np.asarray(dst, float) - np.asarray(piv, float)
    return M


def _then(M2, M1):
    """M2 after M1."""
    A = np.vstack([M1, [0, 0, 1]]); B = np.vstack([M2, [0, 0, 1]]); return (B @ A)[:2]


def _inv(M): return cv2.invertAffineTransform(M)


def _warp(img, M): return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def _wrap(d): return (d + 180.0) % 360.0 - 180.0


def _best_angle(ma, pa, mb, pb):
    a, b = ma.astype(np.float32), mb > 0
    def iou(t): r = _warp(a, _M(pa, t, pb)) > .5; return (r & b).sum() / max(1, (r | b).sum())
    best = max((iou(t), t) for t in range(-180, 180, 3)); c = best[1]
    return max((iou(t), t) for t in np.arange(c - 3, c + 3.01, .5))[1]


def _pm(x, m=None):
    y = x.copy()
    if m is not None: y[..., 3] *= m
    return np.dstack([y[..., :3] * y[..., 3:], y[..., 3:]])


def _flow(a, b):
    def g(x): return np.clip((0.6 * x[..., :3].mean(2) + 0.4 * x[..., 3]) * 255, 0, 255).astype(np.uint8)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM); dis.setFinestScale(0)
    return dis.calc(g(a), g(b), None)


def _clamp(F, H, most=40):
    """Cap a residual flow at `most` px (at 1080p): a bigger gap is a mismatch the flow cannot fix, and following it tears the drawing."""
    m = most * H / 1080.0; n = np.linalg.norm(F, axis=2, keepdims=True); return (F * np.minimum(1.0, m / np.maximum(n, 1e-6))).astype(np.float32)


def _fwarp(pm, F, t):
    """Forward-splat a premultiplied RGBA image along t * F (bilinear splat, average where pixels land together,
    small holes filled from their neighbours)."""
    if t == 0: return pm
    H, W = pm.shape[:2]; ys, xs = np.nonzero(pm[..., 3] > 0.004)
    qx, qy = xs + F[ys, xs, 0] * t, ys + F[ys, xs, 1] * t
    x0, y0 = np.floor(qx).astype(int), np.floor(qy).astype(int); fx, fy = qx - x0, qy - y0
    acc = np.zeros((H * W, 4), np.float64); wsum = np.zeros(H * W, np.float64); v = pm[ys, xs]
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        X, Y = x0 + dx, y0 + dy; ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H) & (wt > 1e-4); idx = Y[ok] * W + X[ok]
        np.add.at(acc, idx, v[ok] * wt[ok, None]); np.add.at(wsum, idx, wt[ok])
    acc = acc.reshape(H, W, 4).astype(np.float32); wsum = wsum.reshape(H, W).astype(np.float32)
    k = (5, 5); ab = np.dstack([cv2.blur(acc[..., i], k) for i in range(4)]); wb = cv2.blur(wsum, k)
    hole = (wsum < 0.35) & (wb > 0.2)                                   # gaps the splat left inside the shape
    out = np.where(wsum[..., None] >= 0.35, acc / np.maximum(wsum, 1e-6)[..., None], 0)
    out[hole] = (ab / np.maximum(wb, 1e-6)[..., None])[hole]
    return out.astype(np.float32)


def _unpm(pm):
    al = pm[..., 3:]; return np.dstack([np.where(al > 1e-4, pm[..., :3] / np.maximum(al, 1e-4), 0), np.clip(al, 0, 1)])


def _over(top, bot):
    """Premultiplied over."""
    return top + bot * (1 - top[..., 3:])


# ---------- one pair of key poses ----------
ORDER = (4, 1, 5, 3)                                                    # back to front: far arm, core, head, near arm

def _mats(P, who, s):
    """{part label: affine matrix} taking key pose `who` to progress s: core (1), near and far arm (3, 4), head (5)."""
    pa, pb = P["pa"], P["pb"]; waist_t = (1 - s) * pa["waist"] + s * pb["waist"]
    if who == "a": p, f = pa, s
    else: p, f = pb, -(1 - s)
    Mc = _M(p["waist"], f * P["th"], waist_t); Ma = _then(Mc, _M(p["shoulder"], f * P["arm"]))
    Mh = _then(Mc, _M(p["neck"], f * P["head"])) if p["neck"] is not None else Mc
    return {1: Mc, 3: Ma, 4: Ma, 5: Mh}


def plan_pair(A, B):
    """Everything that does not depend on t. A, B: float RGBA (0..1) layers of the same size. None if the parts are not found.
    Each moving part of each pose is first carried rigidly to the halfway pose; what still differs there (a head that
    hangs, a back that rounds) is a small gap, and a dense optical flow closes it."""
    pa, pb = parts(A), parts(B)
    if pa is None or pb is None: return None
    ma, mb = pa["lab"], pb["lab"]
    th = _best_angle((ma == 1) | (ma >= 3), pa["waist"], (mb == 1) | (mb >= 3), pb["waist"])    # whole upper body about the waist
    P = dict(th=th, pa=pa, pb=pb)
    P["arm"] = _wrap(pb["arm_deg"] - pa["arm_deg"] - th)                                         # the arm's own turn, on top of that
    P["head"] = 0.0                                                                              # the head's own nod, on top of the core's turn
    if pa["neck"] is not None and pb["neck"] is not None and (ma == 5).any() and (mb == 5).any():
        P["head"] = 0.0; ha = _warp((ma == 5).astype(np.float32), _mats(P, "a", 1.0)[1]); hb = mb == 5
        nb = pb["neck"]
        def iou(t): r = _warp(ha, _M(nb, t)) > .5; return (r & hb).sum() / max(1, (r | hb).sum())
        best = max((iou(t), t) for t in range(-120, 121, 4)); c = best[1]
        P["head"] = float(max((iou(t), t) for t in np.arange(c - 4, c + 4.01, 1))[1])
    legs_a, legs_b = _pm(A, ma == 2), _pm(B, mb == 2)
    P["legs"] = (legs_a, legs_b, _flow(_unpm(legs_a), _unpm(legs_b)), _flow(_unpm(legs_b), _unpm(legs_a)))
    Ka, Kb = _mats(P, "a", .5), _mats(P, "b", .5); P["mid"] = {}
    for lab_id in ORDER:
        am, bm = _warp(_pm(A, ma == lab_id), Ka[lab_id]), _warp(_pm(B, mb == lab_id), Kb[lab_id])
        if lab_id == 5: z = np.zeros(A.shape[:2] + (2,), np.float32); P["mid"][lab_id] = (am, bm, z, z); continue   # the head turns as one piece: flow tears hair
        P["mid"][lab_id] = (am, bm, _clamp(_flow(_unpm(am), _unpm(bm)), A.shape[0]), _clamp(_flow(_unpm(bm), _unpm(am)), A.shape[0]))
    return P


def frame(P, s):
    """RGBA float layer at eased progress s (0..1)."""
    w = s * s * (3 - 2 * s)                                             # legs: a plain eased crossfade weight (they barely move)
    la, lb, F, F2 = P["legs"]; out = (1 - w) * _fwarp(la, F, s) + w * _fwarp(lb, F2, 1 - s)
    x = min(1.0, max(0.0, (s - .5) * 8 + .5)); wp = x * x * (3 - 2 * x)  # moving parts: swap from pose A to pose B in about one frame mid-move
                                                                        # (a longer crossfade shows a see-through double body)
    to_s = {}
    for who in ("a", "b"):
        K5, K = _mats(P, who, .5), _mats(P, who, s); to_s[who] = {i: _then(K[i], _inv(K5[i])) for i in ORDER}
    xh = min(1.0, max(0.0, (s - .5) * 12 + .5)); wh = xh * xh * (3 - 2 * xh)   # the head swaps faster still: two faces never show at once for long
    for lab_id in ORDER:
        am, bm, F, F2 = P["mid"][lab_id]; w = wh if lab_id == 5 else wp
        a = _warp(_fwarp(am, F, s), to_s["a"][lab_id]) if (1 - w) > 1e-3 else 0
        b = _warp(_fwarp(bm, F2, 1 - s), to_s["b"][lab_id]) if w > 1e-3 else 0
        out = _over((1 - w) * a + w * b, out)
    return _unpm(np.clip(out, 0, 1))


# ---------- the floor shadow, per frame ----------
def contact_shadow(alpha, floor_y, H, opacity=0.55, reach=None, blur=None):
    """Soft shadow under whatever part of the boy is near the floor (feet standing; legs, seat and back lying). Its own layer."""
    k = H / 1080.0; reach = reach or 18 * k; blur = blur or 5 * k; W = alpha.shape[1]
    y0 = int(max(0, floor_y - reach)); band = alpha[y0:int(floor_y) + 1]
    if not band.size: return np.zeros(alpha.shape + (4,), np.float32)
    wts = np.linspace(0.2, 1.0, band.shape[0])[:, None]; prof = (band * wts).max(0)
    prof = cv2.dilate(prof[None].astype(np.float32), np.ones((1, int(26 * k) | 1), np.uint8))[0]   # spreads a little past the feet
    sh = np.zeros(alpha.shape, np.float32); hh = max(3, int(12 * k))
    rows = np.arange(-hh, hh + 1); fall = np.sqrt(np.clip(1 - (rows / hh) ** 2, 0, 1))      # an elliptical cross-section, darkest at the floor line
    y = int(floor_y) + hh // 4; sh[y - hh:y + hh + 1] = fall[:, None] * prof[None]
    sh = cv2.GaussianBlur(sh, (0, 0), blur) * opacity
    out = np.zeros(alpha.shape + (4,), np.float32); out[..., 3] = np.clip(sh, 0, 1); return out


# ---------- frames on disk ----------
def load_layer(path): return np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255


def composite(posedir, layer, shadow=True):
    """Backdrop, props behind, contact shadow, the boy, props in front: one finished RGB frame (PIL)."""
    bg = Image.open(os.path.join(posedir, "backdrop.png")).convert("RGBA"); W, H = bg.size
    g = json.load(open(os.path.join(posedir, "geom.json")))["geom"]
    for name in ("props_behind.png",):
        if os.path.exists(os.path.join(posedir, name)): bg.alpha_composite(Image.open(os.path.join(posedir, name)).convert("RGBA"))
    if shadow: bg.alpha_composite(Image.fromarray((contact_shadow(layer[..., 3], g["gy"] + 10, H) * 255).astype(np.uint8), "RGBA"))
    bg.alpha_composite(Image.fromarray((np.clip(layer, 0, 1) * 255).astype(np.uint8), "RGBA"))
    if os.path.exists(os.path.join(posedir, "props_front.png")): bg.alpha_composite(Image.open(os.path.join(posedir, "props_front.png")).convert("RGBA"))
    return bg.convert("RGB")


def pose_frame(posedir, k, cache, shadow=True):
    """A key pose finished the same way as the in-betweens (so a hold and the next in-between match exactly)."""
    os.makedirs(cache, exist_ok=True); fn = os.path.join(cache, f"key-p{k}{'-sh' if shadow else ''}.png")
    if not os.path.exists(fn): composite(posedir, load_layer(os.path.join(posedir, f"layer_p{k}.png")), shadow).save(fn)
    return fn


def inbetweens(posedir, a, b, progress, cache, shadow=True):
    """Finished frames between key poses a and b at the given eased progress values (0 < s < 1), cached on disk.
    Falls back to holding pose a then pose b if the body parts cannot be found."""
    os.makedirs(cache, exist_ok=True); names = [os.path.join(cache, f"tw-{a}-{b}-{s:.4f}{'-sh' if shadow else ''}.png") for s in progress]
    if all(os.path.exists(n) for n in names): return names
    A, B = load_layer(os.path.join(posedir, f"layer_p{a}.png")), load_layer(os.path.join(posedir, f"layer_p{b}.png"))
    P = plan_pair(A, B)
    for s, n in zip(progress, names):
        if os.path.exists(n): continue
        if P is None: lay = A if s < 0.5 else B
        else: lay = frame(P, s)
        composite(posedir, lay, shadow).save(n)
    if P is not None:
        json.dump({"a": a, "b": b, "core_deg": round(float(P["th"]), 1), "arm_deg": round(float(P["arm"]), 1), "head_deg": round(float(P["head"]), 1)}, open(os.path.join(cache, f"tw-{a}-{b}.json"), "w"))
    return names
