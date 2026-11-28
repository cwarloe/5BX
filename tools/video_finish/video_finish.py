#!/usr/bin/env python3
"""Finish white-background exercise clips: find the loop, measure Mark, cut him out, place him on the gym plate at the
reference proportion, and render a looping review MP4.

Settings and per-clip data live in config.json next to this file. README.md gives the order of steps and the rules.

  python3 video_finish.py measure   --clip toe --src work/toe/src.mp4
  python3 video_finish.py loops     --clip toe --src work/toe/src.mp4 --out work/toe
  python3 video_finish.py composite --clip toe --src work/toe/src.mp4 --out out/1_toe-touch.mp4
  python3 video_finish.py all       --work work --out out          # every clip in config.json, two at a time
"""
import argparse, json, math, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load_config(path=None):
    return json.load(open(path or os.path.join(HERE, "config.json")))


# ---------------------------------------------------------------- video in/out

def probe(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "csv=p=0", src], capture_output=True, text=True, check=True).stdout.strip().split(",")
    num, den = out[2].split("/")
    return int(out[0]), int(out[1]), float(num) / float(den)


def read_frames(src, start=0, end=None, size=None, gray=False):
    """Frames [start, end) as a uint8 array. size=(w, h) resizes; gray=True gives one channel."""
    W, H, _ = probe(src)
    w, h = size or (W, H)
    vf = [f"scale={w}:{h}"] if size else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src] + (["-vf", ",".join(vf)] if vf else []) +
                         ["-f", "rawvideo", "-pix_fmt", "gray" if gray else "rgb24", "-"], capture_output=True, check=True).stdout
    shape = (-1, h, w) if gray else (-1, h, w, 3)
    return np.frombuffer(raw, np.uint8).reshape(shape)[start:end]


def write_video(frames, out, w, h, fps):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    for f in frames: p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError(f"ffmpeg failed writing {out}")


# ---------------------------------------------------------------- loops

def find_loop(G, fps, min_cycle_s=1.0, window=2, cover=0.5):
    """Best loop in grayscale frames G (n, h, w). Returns (start, end, joint_score); the cycle is frames start..end-1.

    The score compares `window` frames either side of the joint, so motion direction must match, not just the pose.
    The cycle must reach at least `cover` of the clip's largest pose change, so it holds the whole movement
    (an alternating exercise needs a longer min_cycle_s so both sides are inside it)."""
    G = G.astype(np.float32); n = len(G)
    step = np.array([np.abs(G[i] - G[i - 1]).mean() for i in range(1, n)]); med = float(np.median(step)) or 1e-6
    span = max(float(np.abs(G[m] - G[0]).mean()) for m in range(n))
    minlen = max(2, int(round(fps * min_cycle_s))); R = window; best = None
    for i in range(R, n - R):
        reach = np.array([np.abs(G[m] - G[i]).mean() for m in range(i, n)])
        for j in range(i + minlen, n - R):
            if reach[: j - i + 1].max() < cover * span: continue
            sc = float(np.mean([np.abs(G[i + k] - G[j + k]).mean() for k in range(-R, R + 1)]))
            if best is None or sc < best[0]: best = (sc, i, j)
    if best is None: raise ValueError("no loop found: clip too short for min_cycle_s, or no full movement")
    _, a, b = best
    joint = float(np.abs(G[b - 1] - G[a]).mean()) / med       # what the viewer sees at the joint
    return a, b, joint


def loop_order(n, mode):
    """Frame order for one pass: 'cut' plays 0..n-1; 'pingpong' plays forward then back without repeating the ends."""
    if mode == "cut": return list(range(n))
    if mode == "pingpong": return list(range(n)) + list(range(n - 2, 0, -1))
    raise ValueError(mode)


def joint_verdict(score, cfg):
    L = cfg["loop"]
    return "smooth" if score < L["joint_smooth_below"] else ("visible jump" if score > L["joint_visible_above"] else "slight hitch")


# ---------------------------------------------------------------- measuring and placing

def body_box(alpha, thresh=0.5):
    """(x0, y0, x1, y1) of the person in one matte, or None."""
    m = alpha > thresh
    if not m.any(): return None
    ys, xs = np.nonzero(m)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def target_length_px(cfg, kind):
    P, H = cfg["proportion"], cfg["canvas"]["height"]
    frac = P["lying_length_frac"] if kind == "lying" else P["standing_height_frac"]
    return frac * H


def placement(cfg, clip_cfg, W, H, union_box):
    """Fixed scale and offset for a clip: its lowest point on the contact line, its extent centred on the mat.
    One transform for the whole clip, so Mark never slides."""
    C = cfg["canvas"]; P = cfg["proportion"]
    s = target_length_px(cfg, clip_cfg["body_kind"]) / float(clip_cfg["body_length_px"])
    x0, y0, x1, y1 = union_box
    ox = round(P["center_x_frac"] * C["width"] - (x0 + x1) / 2 * s)
    oy = round(P["contact_line_frac"] * C["height"] - y1 * s)
    return s, ox, oy, round(W * s), round(H * s)


def cut_lines(union_mask, ox, oy, sw, sh, cw, ch, margin=3):
    """Source-frame edges the person touches that would land inside the canvas: each shows as a straight cut in mid-air."""
    touch = {"top": union_mask[:margin].any(), "bottom": union_mask[-margin:].any(),
             "left": union_mask[:, :margin].any(), "right": union_mask[:, -margin:].any()}
    hidden = {"top": oy <= 0, "bottom": oy + sh >= ch, "left": ox <= 0, "right": ox + sw >= cw}
    return [e for e, t in touch.items() if t and not hidden[e]]


def hair_top(frame, alpha):
    """Highest row of the largest dark-brown area inside the matte (the hair; the black wristband is too small to win)."""
    from scipy import ndimage
    f = frame.astype(int)
    hair = (f.max(2) < 80) & (f[..., 0] > f[..., 2] + 6) & (alpha > 0.5)
    lab, n = ndimage.label(ndimage.binary_opening(hair, iterations=1))
    if not n: return None
    k = 1 + int(np.argmax(ndimage.sum(hair, lab, range(1, n + 1))))
    return int(np.nonzero((lab == k).any(1))[0].min())


# ---------------------------------------------------------------- matting

_SESSION = {}


def mattes(frames, model):
    from PIL import Image
    from rembg import new_session, remove
    if model not in _SESSION: _SESSION[model] = new_session(model)
    return np.stack([np.asarray(remove(Image.fromarray(f), session=_SESSION[model], only_mask=True, post_process_mask=True), np.float32) / 255
                     for f in frames])


# ---------------------------------------------------------------- commands

def cmd_measure(a, cfg):
    W, H, fps = probe(a.src)
    frames = read_frames(a.src)
    idx = list(range(0, len(frames), max(1, len(frames) // 12)))
    al = mattes(frames[idx], cfg["matte"]["model"])
    boxes = [body_box(x) for x in al]
    hs = [b[3] - b[1] + 1 for b in boxes if b]; ws = [b[2] - b[0] + 1 for b in boxes if b]
    print(f"{a.src}: {W}x{H}. Over {len(idx)} sampled frames: height median {np.median(hs):.0f} px (max {max(hs)}), "
          f"width median {np.median(ws):.0f} px (max {max(ws)}).")
    print("For body_length_px use the HEIGHT of a standing pose with the arms not raised, or the WIDTH of a straight lying pose. "
          "If the person is never straight (knee push-up), estimate from a limb: shin length / 0.194.")


def cmd_loops(a, cfg):
    W, H, fps = probe(a.src); c = cfg["clips"].get(a.clip, {})
    end = c.get("usable_until_frame")
    G = read_frames(a.src, 0, end, size=(160, round(160 * H / W)), gray=True)
    mc = c.get("loop", {}).get("min_cycle_seconds", cfg["loop"]["min_cycle_seconds"])
    s, e, j = find_loop(G, fps, mc, cfg["loop"]["window_frames"], cfg["loop"]["must_cover_fraction_of_motion"])
    print(f"{a.clip}: best cut frames {s}..{e - 1} ({(e - s) / fps:.2f}s), joint {j:.2f} ({joint_verdict(j, cfg)}). "
          f'config: "loop": {{"start": {s}, "end": {e}, "mode": "cut", "joint": {j:.2f}}}')
    if a.out:
        F = read_frames(a.src, 0, end); T = cfg["loop"]["target_seconds"]
        for mode, (lo, hi) in (("cut", (s, e)), ("pingpong", (0, len(F)))):
            order = loop_order(hi - lo, mode); N = max(2, math.ceil(T * fps / len(order)))
            write_video((F[lo + k] for _ in range(N) for k in order), os.path.join(a.out, f"white_loop_{mode}.mp4"), W, H, fps)
        print(f"wrote white_loop_cut.mp4 and white_loop_pingpong.mp4 to {a.out}")


def composite(clip, src, out, cfg_path=None):
    cfg = load_config(cfg_path); c = cfg["clips"][clip]; C = cfg["canvas"]
    from PIL import Image
    W, H, fps = probe(src); L = c["loop"]
    F = read_frames(src, L["start"], L["end"])
    A = mattes(F, cfg["matte"]["model"])
    union = (A > 0.5).any(0); ub = body_box(union.astype(np.float32))
    s, ox, oy, sw, sh = placement(cfg, c, W, H, ub)
    cuts = cut_lines(union, ox, oy, sw, sh, C["width"], C["height"])
    # studio colour, to remove the white fringe from edge pixels
    bg = np.median(np.concatenate([F[:, :8].reshape(-1, 3), F[:, :, :8].reshape(-1, 3), F[:, :, -8:].reshape(-1, 3)]), axis=0).astype(np.float32)
    plate = np.asarray(Image.open(os.path.join(HERE, cfg["plate"]["file"])).convert("RGB").resize((C["width"], C["height"]), Image.LANCZOS), np.float32)
    x0, y0, x1, y1 = max(ox, 0), max(oy, 0), min(ox + sw, C["width"]), min(oy + sh, C["height"])
    sub = (slice(y0 - oy, y1 - oy), slice(x0 - ox, x1 - ox))
    comp, tops = [], []
    for f, al in zip(F, A):
        Ah = al[..., None]; ff = f.astype(np.float32)
        fg = np.where(Ah > 0.03, (ff - (1 - Ah) * bg) / np.maximum(Ah, 0.03), ff).clip(0, 255)
        fgs = np.asarray(Image.fromarray(fg.astype(np.uint8)).resize((sw, sh), Image.LANCZOS), np.float32)
        als = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).resize((sw, sh), Image.LANCZOS), np.float32)[..., None] / 255
        o = plate.copy(); o[y0:y1, x0:x1] = als[sub] * fgs[sub] + (1 - als[sub]) * o[y0:y1, x0:x1]
        comp.append(o.clip(0, 255).astype(np.uint8))
        t = hair_top(f, al)
        if t is not None: tops.append(oy + t * s)
    order = loop_order(len(comp), L["mode"]); N = max(2, math.ceil(cfg["loop"]["target_seconds"] * C["fps"] / len(order)))
    write_video((comp[k] for _ in range(N) for k in order), out, C["width"], C["height"], C["fps"])
    head = min(tops) if tops else None
    rep = {"clip": clip, "out": out, "scale": round(s, 4), "placed": [ox, oy, sw, sh], "frames_cut_out": len(comp),
           "loop": f"{L['mode']} x{N}", "seconds": round(N * len(order) / C["fps"], 1),
           "body_height_on_canvas_px": round(target_length_px(cfg, c["body_kind"])),
           "head_top_y": None if head is None else round(head), "head_visible": head is not None and head >= 0,
           "visible_cut_lines": cuts}
    json.dump(rep, open(os.path.splitext(out)[0] + ".json", "w"), indent=1)
    flag = []
    if not rep["head_visible"]: flag.append("HEAD OUT OF FRAME")
    if cuts: flag.append(f"source edge visible as a straight cut: {', '.join(cuts)} (re-render with more room on that side)")
    print(f"{clip}: {rep['seconds']}s, scale {s:.3f}, head top y={rep['head_top_y']}" + (" | " + "; ".join(flag) if flag else " | OK"))
    return rep


def cmd_composite(a, cfg):
    composite(a.clip, a.src, a.out, a.config)


def cmd_all(a, cfg):
    jobs = [(k, os.path.join(a.work, k, "src.mp4"), os.path.join(a.out, f"{k}.mp4")) for k in cfg["clips"]]
    missing = [j[1] for j in jobs if not os.path.exists(j[1])]
    if missing: sys.exit("missing sources (download each clip's drive_id first):\n  " + "\n  ".join(missing))
    with ProcessPoolExecutor(cfg["limits"]["parallel_jobs"]) as ex:
        for r in ex.map(composite, *zip(*jobs), [a.config] * len(jobs)): pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", help="config file (default: config.json next to this script)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("measure"); m.add_argument("--clip"); m.add_argument("--src", required=True)
    l = sp.add_parser("loops"); l.add_argument("--clip", required=True); l.add_argument("--src", required=True); l.add_argument("--out")
    c = sp.add_parser("composite"); c.add_argument("--clip", required=True); c.add_argument("--src", required=True); c.add_argument("--out", required=True)
    al = sp.add_parser("all"); al.add_argument("--work", required=True); al.add_argument("--out", required=True)
    a = ap.parse_args(argv); cfg = load_config(a.config)
    {"measure": cmd_measure, "loops": cmd_loops, "composite": cmd_composite, "all": cmd_all}[a.cmd](a, cfg)


if __name__ == "__main__":
    main()
