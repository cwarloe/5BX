"""Extract every pose of every sheet as a standalone transparent PNG.

The sheets are strips: all poses of one movement drawn in one image so the
character stays consistent. That is right for generating but wrong for using -
you cannot hand someone a strip and say "pose 3". This writes each pose out on
its own, numbered in movement order, on a transparent background.

Within one movement every pose is written on an identical canvas, standing on a
shared floor line, so the files can be stacked, flipped through or assembled
into a cycle without any further registration.

    python3 extract_poses.py [--chart N] [--outdir DIR]
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from chart import SHEETS, CYCLE_KIND, cycle_for, DATA   # noqa: E402

BG = (250, 3, 240)                                  # the chroma key
INKS = ((255, 255, 255), (245, 125, 15), (150, 150, 150))   # skin, shorts, tank
PAD = 8                                             # breathing room on the canvas

# Exercise 5 is drawn as two movements; everything else is one slot per exercise.
SLOT_EXERCISE = {'ex1': 1, 'ex2': 2, 'ex3': 3, 'ex4': 4, 'run': 5, 'jump': 5}

def ink_mask(rgb):
    """True where the pixel is figure, not background.

    The art is four flat colours, so 'not the key colour' is exact rather than a
    threshold. One pixel of erosion then removes the anti-aliased rim, which is
    a blend of magenta and skin and reads as a pink halo if it survives.
    """
    d = np.abs(rgb.astype(int) - np.array(BG)).sum(axis=2)
    m = d > 90
    e = m.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        e &= np.roll(m, (dy, dx), axis=(0, 1))
    return e

def snap_to_inks(rgb, mask):
    """Force every figure pixel to one of the three inks.

    Edge pixels are blends carrying some key colour. Snapping to the nearest ink
    guarantees no magenta survives anywhere in the file, at any zoom.
    """
    out = rgb.copy()
    px = rgb[mask].astype(int)
    if len(px):
        d = np.stack([np.abs(px - np.array(c)).sum(axis=1) for c in INKS])
        out[mask] = np.array(INKS, dtype=np.uint8)[d.argmin(axis=0)]
    return out

def bleed(rgb, mask, iters=3):
    """Push figure colour outward into the transparent margin.

    The soft alpha below feathers a pixel or two beyond the mask. Those pixels
    still hold the key colour, so without this the magenta comes straight back
    as a faint halo - invisible at 100% and obvious the moment anyone scales
    the file up or drops it on a light background.
    """
    out, m = rgb.copy(), mask.copy()
    for _ in range(iters):
        grown = m.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            src = np.roll(m, (dy, dx), axis=(0, 1))
            tgt = src & ~m
            out[tgt] = np.roll(out, (dy, dx), axis=(0, 1))[tgt]
            grown |= src
        m = grown
    return out, m

def soft_alpha(mask):
    """Anti-alias the cut edge. The source has hard pixel steps; a sub-pixel
    blur makes the silhouette read cleanly when the file is scaled up."""
    a = Image.fromarray((mask * 255).astype(np.uint8), 'L')
    return a.filter(ImageFilter.GaussianBlur(0.6))

def poses_from(path):
    """Split a sheet into poses, left to right, which is movement order."""
    rgb = np.array(Image.open(path).convert('RGB'))
    mask = ink_mask(rgb)
    bled, grown = bleed(rgb, mask)
    rgba = np.dstack([snap_to_inks(bled, grown), np.array(soft_alpha(mask))])
    im = Image.fromarray(rgba, 'RGBA')

    cols = mask.sum(axis=0) > 3
    spans, start = [], None
    for i, c in enumerate(list(cols) + [False]):
        if c and start is None:
            start = i
        elif not c and start is not None:
            if i - start > 30:
                spans.append((start, i))
            start = None
    if not spans:
        raise SystemExit(f'no poses found in {path}')
    floor = max(np.where(mask[:, a:b].any(axis=1))[0][-1] for a, b in spans)

    boxes = []
    for a, b in spans:
        rows = np.where(mask[:, a:b].any(axis=1))[0]
        cs = np.where(mask[:, a:b].any(axis=0))[0]
        boxes.append((a + cs[0], rows[0], a + cs[-1] + 1, floor + 1))

    # One canvas for the whole movement: widest pose, tallest pose, shared floor.
    cw = max(x1 - x0 for x0, _, x1, _ in boxes) + PAD * 2
    ch = max(y1 - y0 for _, y0, _, y1 in boxes) + PAD * 2
    out = []
    for x0, y0, x1, y1 in boxes:
        c = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        c.paste(im.crop((x0, y0, x1, y1)),
                (cw // 2 - (x1 - x0) // 2, ch - PAD - (y1 - y0)))
        out.append(c)
    return out

def slug(fname):
    return os.path.splitext(os.path.basename(fname))[0]

def main(chart_id, srcdir, outdir):
    chart = next(c for c in DATA['charts'] if c['id'] == chart_id)
    root = os.path.join(outdir, f'chart{chart_id}')
    manifest = {'chart': chart_id, 'movements': []}

    for slot, sheet in SHEETS[chart_id].items():
        name = slug(sheet)
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        poses = poses_from(os.path.join(srcdir, sheet))
        for n, p in enumerate(poses, 1):
            p.save(os.path.join(d, f'{n}.png'))
        ex = chart['exercises'][SLOT_EXERCISE[slot] - 1]
        label = ex['jumpName'] if slot == 'jump' else ex['name']
        manifest['movements'].append({
            'slot': slot, 'exercise': SLOT_EXERCISE[slot], 'name': label,
            'folder': f'chart{chart_id}/{name}', 'poses': len(poses),
            'canvas': list(poses[0].size),
            'order': list(range(1, len(poses) + 1)),
            'loop': cycle_for(CYCLE_KIND[slot], len(poses)),
        })
        print(f'  {name}: {len(poses)} poses, canvas {poses[0].size[0]}x{poses[0].size[1]}')

    with open(os.path.join(outdir, f'chart{chart_id}.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    print('wrote', os.path.join(outdir, f'chart{chart_id}.json'))

if __name__ == '__main__':
    argv, chart_id = sys.argv[1:], 1
    if '--chart' in argv:
        i = argv.index('--chart'); chart_id = int(argv[i + 1]); del argv[i:i + 2]
    out = argv[argv.index('--outdir') + 1] if '--outdir' in argv else os.path.join(HERE, 'poses')
    if chart_id not in SHEETS:
        raise SystemExit(f'no sheets drawn for chart {chart_id}; have {sorted(SHEETS)}')
    main(chart_id, os.path.join(HERE, 'sheets'), out)
