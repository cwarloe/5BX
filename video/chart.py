"""Build a full 5BX chart video from generated pose sheets.

Every timing, target and label is read from data/5bx-charts.json - the same file
the app runs on. Nothing about the plan is retyped here.
"""
import os, sys, json, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, '..', 'data', '5bx-charts.json')))
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

def compose(sheet, outdir, F, depth=1.0):
    """Render each pose of a sheet onto the backdrop at a consistent body size.

    Scale is set by how long the body is, not by how much of the box it fills.
    Fitting the box makes the same person double in size when he lies down: a
    prone figure is wide and short, so box-fitting stretches it to the box
    width while a standing figure is only ever as tall as the box.

    `depth` then stages the exercises front to back on purpose - floor work sits
    slightly further from camera than standing work, which keeps the apparent
    size steady without pretending a kneeling push-up is as long as a man is tall.
    """
    os.makedirs(outdir, exist_ok=True)
    poses = key_and_split(sheet)
    bg, (bw, bh) = backdrop(F), F['box']
    gy = int(F['H'] * F['ground'])
    # Longest extent of the body in any pose: standing height, or prone length.
    reach = max(max(p.size) for p in poses)
    s = F['body'] * depth / reach
    # Never let a pose leave the box, whatever the depth asks for.
    s = min(s, bw / max(p.size[0] for p in poses), bh / max(p.size[1] for p in poses))
    for n, p in enumerate(poses, 1):
        w, h = (max(1, int(round(v * s))) for v in p.size)
        f = bg.copy()
        f.alpha_composite(p.resize((w, h), Image.LANCZOS), (F['W'] // 2 - w // 2, gy - h + 2))
        f.convert('RGB').save(os.path.join(outdir, f'p{n}.png'))
    return len(poses)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise SystemExit(f'ffmpeg failed:\n{" ".join(cmd[:12])}...\n{r.stderr[-1200:]}')

def esc(t):
    return t.replace('\\', '\\\\').replace(':', r'\:').replace("'", r"\\\'")

def overlay(F, n, name, target, allot, off=0.0):
    """Title block, countdown and progress bar — all driven by the data file."""
    W = F['W']; gy = int(F['H'] * F['ground'])
    cy = gy + int((F['H'] - gy) * .18)
    return (
        f"drawtext=fontfile={FONT_B}:text='EXERCISE {n} OF 5':fontcolor=0x7d8a9c:"
        f"fontsize={F['kicker']}:x=(w-tw)/2:y={int(F['H']*.035)},"
        f"drawtext=fontfile={FONT_B}:text='{esc(name.upper())}':fontcolor=white:"
        f"fontsize={F['title']}:x=(w-tw)/2:y={int(F['H']*.035)+F['kicker']+14},"
        f"drawtext=fontfile={FONT_B}:text='{esc(target)}':fontcolor=0xff6b35:"
        f"fontsize={F['target']}:x=(w-tw)/2:y={int(F['H']*.035)+F['kicker']+F['title']+26},"
        f"drawtext=fontfile={FONT_M}:"
        f"text='%{{eif\\:floor(({allot}-{off}-t)/60)\\:d}}\\:%{{eif\\:mod(floor({allot}-{off}-t)\\,60)\\:d\\:2}}':"
        f"fontcolor=white:fontsize={F['clock']}:x=(w-tw)/2:y={cy},"
        f"drawtext=fontfile={FONT_B}:text='LEFT':fontcolor=0x7d8a9c:"
        f"fontsize={int(F['kicker']*.85)}:x=(w-tw)/2:y={cy+F['clock']+12},"
        f"drawbox=x=0:y={F['H']-F['bar']}:w='{W}*(({off}+t)/{allot})':h={F['bar']}:color=0xff6b35@1:t=fill"
    )

def segment(posedir, cycle, cycle_s, dur, F, ov, out, offset=0.0):
    """One continuous stretch of a looping pose cycle, with overlays."""
    per = cycle_s / len(cycle)
    lst = out + '.txt'
    with open(lst, 'w') as f:
        for _ in range(math.ceil(dur / cycle_s) + 1):
            for p in cycle:
                f.write(f"file '{posedir}/p{p}.png'\nduration {per:.4f}\n")
        f.write(f"file '{posedir}/p{cycle[0]}.png'\n")
    vf = f"fps=30,{ov}" if offset == 0 else f"fps=30,{ov}"
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
         '-t', f'{dur:.3f}', '-vf', vf, '-pix_fmt', 'yuv420p', '-r', '30', out + '.mp4'])
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
    cy = int(F['H'] * F['ground']); cy += int((F['H'] - cy) * .18)
    return (
        f"drawtext=fontfile={FONT_B}:text='PAUSE THE RUN':fontcolor=0x7d8a9c:"
        f"fontsize={F['kicker']}:x=(w-tw)/2:y={int(F['H']*.035)},"
        f"drawtext=fontfile={FONT_B}:text='{count} {esc(name.upper())}':fontcolor=0xff6b35:"
        f"fontsize={F['title']}:x=(w-tw)/2:y={int(F['H']*.035)+F['kicker']+14},"
        f"drawtext=fontfile={FONT_M}:"
        f"text='%{{eif\\:floor(({allot}-{off}-t)/60)\\:d}}\\:%{{eif\\:mod(floor({allot}-{off}-t)\\,60)\\:d\\:2}}':"
        f"fontcolor=white:fontsize={F['clock']}:x=(w-tw)/2:y={cy},"
        f"drawtext=fontfile={FONT_B}:text='LEFT':fontcolor=0x7d8a9c:"
        f"fontsize={int(F['kicker']*.85)}:x=(w-tw)/2:y={cy+F['clock']+12},"
        f"drawbox=x=0:y={F['H']-F['bar']}:w='{F['W']}*(({off}+t)/{allot})':h={F['bar']}:"
        f"color=0xff6b35@1:t=fill")

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

# Staging, front to back. Floor work sits a little further from camera than
# standing work so the figure does not swell when he lies down.
# SUPERSEDED 2026-11-21: the approved stage scales lying figures UP
# (1.537548 x the standing scale, head-landmark calibrated, one camera, no
# zoom). See sprites/config/theme.json 'stage'. Values left as-is until this
# builder is ported or retired.
DEPTH = {'ex1': 1.0, 'ex2': .88, 'ex3': .88, 'ex4': .88, 'run': 1.0, 'jump': 1.0}

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
        n = compose(os.path.join(srcdir, sheet), os.path.join(workdir, key), F, DEPTH[key])
        cycles[key] = cycle_for(CYCLE_KIND[key], n)
        print(f'  {key}: {n} poses -> cycle {cycles[key]}')

    parts = []
    for i in range(4):                                  # exercises 1-4
        name, allot, reps = chart['exercises'][i]['name'], timing[i], lv['reps'][i]
        cyc = cycles[f'ex{i+1}']
        # ex1 and ex3 cover two reps per cycle (out-and-back, or one leg each)
        cycle_s = reps and allot / reps * (2 if i in (0, 2) else 1)
        ov = overlay(F, i + 1, name, f'{reps} reps', allot)
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
