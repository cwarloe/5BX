"""Build a full 5BX chart video from generated pose sheets.

Every timing, target and label is read from data/5bx-charts.json - the same file
the app runs on. Nothing about the plan is retyped here.
"""
import os, sys, json, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, '..', 'data', '5bx-charts.json')))
# The one-camera stage and the Fraser overlay are shared with sprites/kit/build.py (sprites/kit/staging.py,
# numbers in sprites/config/theme.json), so both builders stage and label the boy the same way.
sys.path.insert(0, os.path.join(HERE, '..', 'sprites', 'kit'))
import staging
THEME = json.load(open(os.path.join(HERE, '..', 'sprites', 'config', 'theme.json')))
FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_M = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
NAVY_TOP, NAVY_BOT, ORANGE, GRID = (8, 11, 16), (18, 24, 33), (255, 107, 53), (26, 34, 46)

FORMATS = {
    'landscape': dict(W=1920, H=1080, ground=.845, box=(1250, 660), body=660,
                      kicker=24, title=50, target=40, clock=74, bar=14),
    'portrait':  dict(W=1080, H=1920, ground=.78, box=(950, 1000), body=1000,
                      kicker=34, title=74, target=62, clock=118, bar=20),
}

def backdrop(F):
    W, H, gy = F['W'], F['H'], int(F['H'] * F['ground'])
    im = Image.new('RGBA', (W, H), NAVY_BOT + (255,))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = min(1.0, y / gy)
        d.line([(0, y), (W, y)], fill=tuple(
            int(NAVY_TOP[i] + (NAVY_BOT[i] - NAVY_TOP[i]) * t) for i in range(3)) + (255,))
    step = W // 8
    for gx in range(0, W + 1, step):
        d.line([(gx, gy - int(H * .33)), (gx, gy)], fill=GRID + (255,))
    for n in range(6):
        d.line([(0, gy - int(H * .33 * (1 - n / 6) ** 1.8)),
                (W, gy - int(H * .33 * (1 - n / 6) ** 1.8))], fill=GRID + (255,))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    for r in range(int(W * .32), 0, -6):
        g.ellipse([W / 2 - r * 1.5, gy - r / 3, W / 2 + r * 1.5, gy + r / 3],
                  fill=ORANGE + (int(26 * (1 - r / (W * .32)) ** 1.6),))
    im.alpha_composite(glow)
    ImageDraw.Draw(im).rectangle([0, gy, W, gy + 2], fill=ORANGE + (255,))
    return im

def key_and_split(src):
    """Chroma-key the magenta sheet and split it into floor-aligned poses."""
    im = Image.open(src).convert('RGB')
    a = np.array(im).astype(int)
    ink = ~((a[:, :, 0] > 170) & (a[:, :, 1] < 110) & (a[:, :, 2] > 170))
    e = ink.copy()                                   # erode the anti-aliased rim
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        e &= np.roll(ink, (dy, dx), axis=(0, 1))
    ink = e
    rgb = np.array(im, dtype=np.int16)               # despill: magenta needs R and B over G
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    ex = np.where((r > g) & (b > g), np.minimum(r, b) - g, 0)
    rgb[:, :, 0] = np.clip(r - ex, 0, 255); rgb[:, :, 2] = np.clip(b - ex, 0, 255)
    full = Image.fromarray(np.dstack([rgb.astype(np.uint8), (ink * 255).astype(np.uint8)]), 'RGBA')

    cols = ink.sum(axis=0) > 3
    spans, start = [], None
    for i, c in enumerate(list(cols) + [False]):
        if c and start is None: start = i
        elif not c and start is not None:
            if i - start > 30: spans.append((start, i))
            start = None
    floor = max(np.where(ink[:, x0:x1].any(axis=1))[0][-1] for x0, x1 in spans)
    out = []
    for x0, x1 in spans:
        rows = np.where(ink[:, x0:x1].any(axis=1))[0]
        out.append(full.crop((max(0, x0 - 6), max(0, rows[0] - 6),
                              min(im.size[0], x1 + 6), floor + 6)))
    return out

def compose(sheet, outdir, F, strip=None):
    """Render each pose of a sheet onto the backdrop on the approved one-camera stage.

    One fixed camera, no zoom: every standing exercise uses the same scale (frame pixels per sheet pixel), and a
    lying exercise is scaled UP by the stage's lying_scale_multiplier so the boy reads at a comparable size on the
    floor. Feet sit on floor_y, the figure is centred on foot_x, and the head is never cropped. All numbers come
    from sprites/config/theme.json "stage". This replaces the old body-length fit with DEPTH 0.88 for floor work.
    A tall format has no calibrated stage yet and keeps the old body-length fit.
    """
    os.makedirs(outdir, exist_ok=True)
    poses = key_and_split(sheet)
    sg = staging.stage_geom(THEME, F)
    bg, (bw, bh) = backdrop(dict(F, ground=sg['floor_y'] / F['H']) if sg else F), F['box']   # the drawn floor line follows the stage floor
    wmax, hmax = max(p.size[0] for p in poses), max(p.size[1] for p in poses)
    if sg:
        s, lying, notes = staging.stage_scale(sg, strip, wmax, hmax)
        for n in notes: print(f'  {os.path.basename(sheet)}: {n}')
        floor_y, cx = int(round(sg['floor_y'])), sg['foot_x']
    else:
        s = min(F['body'] / max(wmax, hmax), bw / wmax, bh / hmax)
        floor_y, cx = int(F['H'] * F['ground']), F['W'] / 2
    for n, p in enumerate(poses, 1):
        w, h = (max(1, int(round(v * s))) for v in p.size)
        f = bg.copy()
        # key_and_split pads each pose by 6 sheet pixels below the shared floor
        f.alpha_composite(p.resize((w, h), Image.LANCZOS), (int(round(cx - w / 2)), int(round(floor_y - h + 6 * s))))
        f.convert('RGB').save(os.path.join(outdir, f'p{n}.png'))
    return len(poses)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise SystemExit(f'ffmpeg failed:\n{" ".join(cmd[:12])}...\n{r.stderr[-1200:]}')

def esc(t):
    return t.replace('\\', '\\\\').replace(':', r'\:').replace("'", r"\\\'")

def overlay(F, n, name, target, allot, off=0.0, tip=None):
    """The Fraser overlay (sprites/config/theme.json "overlay"): name card plus one tip top left, ring timer top
    right. Returned as a spec; segment() renders it as its own layer."""
    return {'name': name, 'tip': tip or target, 'allot': allot, 'off': off}

def segment(posedir, cycle, cycle_s, dur, F, ov, out, offset=0.0, fps=30):
    """One continuous stretch of a looping pose cycle, hold-and-cut (no crossfade), starting on cycle[0], with the
    overlay laid over it as a separate layer (a card PNG plus one ring PNG per frame)."""
    per = cycle_s / len(cycle); n = max(1, int(round(dur * fps)))
    seq = out + '.frames'; shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
    for k in range(n):
        p = cycle[int((k / fps) // per) % len(cycle)]
        os.symlink(os.path.abspath(os.path.join(posedir, f'p{p}.png')), os.path.join(seq, f'f_{k:05d}.png'))
    lay = out + '.overlay'; os.makedirs(lay, exist_ok=True)
    card, _ = staging.card_layer(THEME, F, ov['name'], ov.get('tip', '')); card.save(os.path.join(lay, 'card.png'))
    ring = staging.ring_frames(THEME, F, ov['allot'], ov.get('off', 0.0), n, fps, os.path.join(lay, 'ring'))
    rx, ry, _ = staging.ring_box(THEME, F)
    run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(seq, 'f_%05d.png'),
         '-loop', '1', '-framerate', str(fps), '-i', os.path.join(lay, 'card.png'), '-framerate', str(fps), '-i', ring,
         '-filter_complex', f'[0:v][1:v]overlay=0:0[c];[c][2:v]overlay={rx}:{ry}[v]', '-map', '[v]',
         '-frames:v', str(n), '-pix_fmt', 'yuv420p', '-r', str(fps), out + '.mp4'])
    shutil.rmtree(seq, ignore_errors=True)
    return out + '.mp4'

def breakcard(secs, nxt, F, out):
    W, H = F['W'], F['H']
    vf = (f"drawtext=fontfile={FONT_B}:text='BREAK':fontcolor=0xff6b35:"
          f"fontsize={F['title']}:x=(w-tw)/2:y={int(H*.30)},"
          f"drawtext=fontfile={FONT_M}:text='%{{eif\\:ceil({secs}-t)\\:d}}':fontcolor=white:"
          f"fontsize={int(F['clock']*2.2)}:x=(w-tw)/2:y={int(H*.38)},"
          f"drawtext=fontfile={FONT_B}:text='NEXT':fontcolor=0x7d8a9c:"
          f"fontsize={F['kicker']}:x=(w-tw)/2:y={int(H*.68)},"
          f"drawtext=fontfile={FONT_B}:text='{esc(nxt.upper())}':fontcolor=white:"
          f"fontsize={F['target']}:x=(w-tw)/2:y={int(H*.68)+F['kicker']+16}")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi',
         '-i', f'color=c=0x0d1117:s={W}x{H}:d={secs}:r=30', '-vf', vf,
         '-pix_fmt', 'yuv420p', out + '.mp4'])
    return out + '.mp4'

def jump_overlay(F, allot, off, count, name):
    return {'name': f'{count} {name}', 'tip': 'jump now', 'allot': allot, 'off': off}

SLOTS = ('ex1', 'ex2', 'ex3', 'ex4', 'run', 'jump')

# Pose sheets per chart. The exercises change from chart to chart - chart 1's
# knee push-up becomes a chin-forehead push-up by chart 3 - so a sheet is only
# ever valid for the chart it was drawn for. A chart with no entry here cannot
# be rendered, and says so rather than borrowing another chart's figures.
SHEETS = {
    1: {'ex1': 'ex1-toe-touching.png',       'ex2': 'ex2-partial-sit-up.png',
        'ex3': 'ex3-alternate-leg-raise.png', 'ex4': 'ex4-knee-push-up.png',
        'run': 'ex5-stationary-run.png',      'jump': 'ex5-scissor-jumps.png'},
}

# How a movement reads as a loop, independent of how many poses it was drawn in.
#   pingpong  a there-and-back rep:  1 2 3 4 3 2
#   centre    pose 1 is the neutral the body returns through: 1 2 1 3 1 4
#   loop      a continuous gait that wraps:  1 2 3 4
CYCLE_KIND = {'ex1': 'centre', 'ex2': 'pingpong', 'ex3': 'centre',
              'ex4': 'pingpong', 'run': 'loop', 'jump': 'pingpong'}

# Staging: the old DEPTH table (floor work at 0.88) is gone. Since 2026-11-21 one fixed camera stages every
# exercise and lying figures are scaled UP (sprites/config/theme.json "stage", via compose()).

def cycle_for(kind, n):
    """Build the pose order for a movement drawn in n poses."""
    if n < 2:
        raise SystemExit(f'a movement needs at least 2 poses, got {n}')
    if kind == 'loop':
        return list(range(1, n + 1))
    if kind == 'pingpong':
        return list(range(1, n + 1)) + list(range(n - 1, 1, -1))
    if kind == 'centre':
        out = []
        for i in range(2, n + 1):
            out += [1, i]
        return out
    raise SystemExit(f'unknown cycle kind {kind!r}')

def sheets_for(chart_id):
    if chart_id not in SHEETS:
        have = ', '.join(str(c) for c in sorted(SHEETS))
        raise SystemExit(
            f'no pose sheets drawn for chart {chart_id} - only chart(s) {have} can be '
            f'rendered.\nChart {chart_id} prescribes different movements, so another '
            f'chart\'s figures would show the wrong exercise.')
    return SHEETS[chart_id]

def main(fmt, chart_id, level, srcdir, workdir, out):
    F = FORMATS[fmt]
    chart = next(c for c in DATA['charts'] if c['id'] == chart_id)
    lv, timing = chart['levels'][level], DATA['timing']['secondsPerExercise']
    ex5 = chart['exercises'][4]
    os.makedirs(workdir, exist_ok=True)

    cycles = {}
    for key, sheet in sheets_for(chart_id).items():
        n = compose(os.path.join(srcdir, sheet), os.path.join(workdir, key), F)
        cycles[key] = cycle_for(CYCLE_KIND[key], n)
        print(f'  {key}: {n} poses -> cycle {cycles[key]}')

    parts = []
    for i in range(4):                                  # exercises 1-4
        name, allot, reps = chart['exercises'][i]['name'], timing[i], lv['reps'][i]
        cyc = cycles[f'ex{i+1}']
        # ex1 and ex3 cover two reps per cycle (out-and-back, or one leg each)
        cycle_s = reps and allot / reps * (2 if i in (0, 2) else 1)
        ov = overlay(F, i + 1, name, f'{reps} reps', allot, tip=staging.tip_for(None, chart['exercises'][i]))
        parts.append(segment(os.path.join(workdir, f'ex{i+1}'), cyc, cycle_s, allot, F, ov,
                             os.path.join(workdir, f'seg{i+1}')))
        parts.append(breakcard(DATA['appDefaults']['transitionSeconds'],
                               chart['exercises'][i + 1]['name'], F,
                               os.path.join(workdir, f'brk{i+1}')))

    # Exercise 5: run in blocks of jumpEvery steps, a jump window after each.
    allot, steps = timing[4], lv['steps']
    every, jcount = ex5['jumpEvery'], ex5['jumpCount']
    window = ex5.get('jumpWindowSeconds', 12)
    sets = steps // every
    step_s = (allot - sets * window) / steps            # seconds per step
    print(f'  ex5: {steps} steps, {sets} jump sets, {step_s:.3f}s/step, '
          f'{60/step_s:.0f} steps/min')
    off, done, k = 0.0, 0, 0
    while done < steps:
        block = min(every, steps - done)
        dur = block * step_s
        parts.append(segment(os.path.join(workdir, 'run'), cycles['run'], 2 * step_s * 2, dur, F,
                             overlay(F, 5, ex5['name'], f'{steps} steps', allot, off),
                             os.path.join(workdir, f'run{k}'), off))
        off += dur; done += block
        if done < steps:
            parts.append(segment(os.path.join(workdir, 'jump'), cycles['jump'],
                                 window / (jcount / 2), window, F,
                                 jump_overlay(F, allot, off, jcount, ex5['jumpName']),
                                 os.path.join(workdir, f'jmp{k}'), off))
            off += window
        k += 1

    lst = os.path.join(workdir, 'all.txt')
    with open(lst, 'w') as f:
        for p in parts: f.write(f"file '{p}'\n")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
         '-c', 'copy', '-movflags', '+faststart', out])
    print('wrote', out)

if __name__ == '__main__':
    argv, chart_id = sys.argv[1:], 1
    if '--chart' in argv:
        i = argv.index('--chart')
        chart_id = int(argv[i + 1]); del argv[i:i + 2]
    if len(argv) < 3:
        raise SystemExit('usage: chart.py <landscape|portrait> <level> <out.mp4> '
                         '[sheets_dir] [work_dir] [--chart N]')
    fmt, level, out = argv[0], argv[1], argv[2]
    sheets = argv[3] if len(argv) > 3 else os.path.join(HERE, 'sheets')
    work = argv[4] if len(argv) > 4 else os.path.join(HERE, '.work')
    main(fmt, chart_id, level, sheets, work, out)
