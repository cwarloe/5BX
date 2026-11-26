"""Experimental, byte-pinned paired photographic composition on ONE outpaint canvas.

This tool cannot establish real photographic identity, historically correct
exercise form, motion continuity, or Flow suitability. It never calls a model.
"""

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, __version__ as PILLOW_VERSION


SOURCE_SIZE = (1280, 720)
CANVAS_SIZE = (1344, 756)
OUTPUTS = ('A_shared_canvas.png', 'C_shared_canvas.png', 'shared_canvas.manifest.json')


def _sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _pinned(path, expected, label, *, kind, size):
    path = Path(path)
    if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise ValueError(f'{label} requires lowercase SHA-256 pin')
    if not path.is_file() or path.is_symlink():
        raise ValueError(f'{label} must be existing non-symlink file')
    before = _sha(path)
    if before != expected:
        raise ValueError(f'{label} bytes do not match pin')
    with Image.open(path) as image:
        if image.format != kind or image.mode != 'RGB' or image.size != size:
            raise ValueError(f'{label} must be RGB {size[0]}x{size[1]} {kind}')
        image.load()
        loaded = image.copy()
    if _sha(path) != before:
        raise RuntimeError(f'{label} bytes changed during decode')
    return loaded


def _annotation(path, *, role, image_sha, size):
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f'{role} annotation must be an existing non-symlink JSON file')
    before = _sha(path)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f'{role} annotation must be valid JSON') from exc
    if (not isinstance(data, dict) or data.get('schema_version') != 1 or
        data.get('role') != role or data.get('source_image_sha256') != image_sha or
        data.get('image_size') != list(size)):
        raise ValueError(f'{role} annotation is not bound to exact source and role')
    if (not isinstance(data.get('reviewer'), str) or not data['reviewer'].strip() or
        data.get('coverage') != 'ALL_VISIBLE_PERSON_PIXELS' or data.get('confidence') != 'OPERATOR_DECLARED'):
        raise ValueError(f'{role} annotation lacks an explicit conservative full-person bound')
    box = data.get('subject_bounds_half_open')
    if (not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box) or
        not (0 <= box[0] < box[2] <= size[0] and 0 <= box[1] < box[3] <= size[1])):
        raise ValueError(f'{role} annotation has invalid subject bounds')
    if _sha(path) != before:
        raise RuntimeError(f'{role} annotation changed during read')
    return {'sha256': before, 'subject_bounds_half_open': box,
            'reviewer': data['reviewer'].strip(), 'source_image_sha256': image_sha,
            'coverage': data['coverage'], 'confidence': data['confidence']}


def _mask(placed_size, *, x, y, window, feather):
    w, h = placed_size
    left, top, right, bottom = window
    side_fade, top_fade, bottom_fade = feather
    xx = x + np.arange(w, dtype=np.float32) + .5
    yy = y + np.arange(h, dtype=np.float32) + .5
    # A true central fully opaque zone, with one shared placement/window for
    # both poses. The unsourced generated canvas only contributes exterior.
    ax = np.minimum(1, np.minimum((xx-left)/side_fade, (right-xx)/side_fade))
    ay = np.minimum(1, np.minimum((yy-top)/top_fade, (bottom-yy)/bottom_fade))
    return np.clip(np.minimum(ax[None, :], ay[:, None]), 0, 1).astype(np.float32)


def _assert_subject_covered(box, *, original_size, placed_size, x, y, mask, label):
    # Transform a conservative half-open source bbox into a conservative
    # output bbox. The ±1 guard accounts for resampling support/rounding.
    ow, oh = original_size
    pw, ph = placed_size
    l, t, r, b = box
    x1 = max(0, math.floor(l*pw/ow)-1)
    y1 = max(0, math.floor(t*ph/oh)-1)
    x2 = min(pw, math.ceil(r*pw/ow)+1)
    y2 = min(ph, math.ceil(b*ph/oh)+1)
    if x2 <= x1 or y2 <= y1 or float(mask[y1:y2,x1:x2].min()) < 1-1e-6:
        raise ValueError(f'{label} annotated person may enter canvas/feather area')
    return [x+x1, y+y1, x+x2, y+y2]


def _png(image):
    output=io.BytesIO()
    image.save(output, format='PNG', compress_level=6, optimize=False)
    return output.getvalue()


def _exclusive_write(items):
    created=[]
    try:
        for path,payload in items:
            flags=os.O_CREAT|os.O_EXCL|os.O_WRONLY
            if hasattr(os, 'O_NOFOLLOW'):
                flags |= os.O_NOFOLLOW
            fd=os.open(path,flags,0o600)
            created.append(path)
            with os.fdopen(fd,'wb') as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException:
        for path in created:
            try:
                path.unlink()
            except OSError:
                pass
        raise


def compose(a_path, c_path, canvas_path, out_dir, *, a_sha, c_sha, canvas_sha,
            a_annotation, c_annotation, canvas_annotation,
            scale_num, scale_den, x, y, window, feather):
    inputs=[Path(a_path),Path(c_path),Path(canvas_path)]
    if len({p.resolve() for p in inputs}) != 3:
        raise ValueError('three distinct pinned source files required')
    out_dir=Path(out_dir)
    if not out_dir.is_dir() or out_dir.is_symlink():
        raise ValueError('output directory must exist and be a non-symlink')
    destinations=[out_dir/name for name in OUTPUTS]
    if any(dest.exists() or dest.is_symlink() or dest.resolve() in {p.resolve() for p in inputs} for dest in destinations):
        raise FileExistsError('destination already exists or would replace source')
    if (any(type(v) is not int for v in (scale_num,scale_den,x,y,*window,*feather)) or
        scale_den < 1 or not (0 < scale_num < scale_den) or x < 0 or y < 0):
        raise ValueError('invalid integer uniform shrink or offset')
    source_w,source_h=SOURCE_SIZE
    pw=round(source_w*scale_num/scale_den)
    ph=round(source_h*scale_num/scale_den)
    if pw<1 or ph<1 or x+pw>CANVAS_SIZE[0] or y+ph>CANVAS_SIZE[1]:
        raise ValueError('scaled source does not fit inside canvas')
    l,t,r,b=window
    if not (0<=l<r<=CANVAS_SIZE[0] and 0<=t<b<=CANVAS_SIZE[1] and
            all(v>0 for v in feather) and x<=l<r<=x+pw and y<=t<b<=y+ph):
        raise ValueError('invalid bounded window or feather')

    images={'A':_pinned(a_path,a_sha,'A',kind='PNG',size=SOURCE_SIZE),
            'C':_pinned(c_path,c_sha,'C',kind='PNG',size=SOURCE_SIZE)}
    canvas=_pinned(canvas_path,canvas_sha,'canvas',kind='JPEG',size=CANVAS_SIZE)
    annotations={'A':_annotation(a_annotation,role='A',image_sha=a_sha,size=SOURCE_SIZE),
                 'C':_annotation(c_annotation,role='C',image_sha=c_sha,size=SOURCE_SIZE),
                 'canvas':_annotation(canvas_annotation,role='canvas',image_sha=canvas_sha,size=CANVAS_SIZE)}
    mask=_mask((pw,ph),x=x,y=y,window=window,feather=feather)
    cover={role:_assert_subject_covered(annotations[role]['subject_bounds_half_open'],
          original_size=SOURCE_SIZE if role != 'canvas' else CANVAS_SIZE,
          placed_size=(pw,ph) if role != 'canvas' else CANVAS_SIZE,
          x=x if role!='canvas' else 0,y=y if role!='canvas' else 0,
          mask=mask if role!='canvas' else np.pad(mask,((y,CANVAS_SIZE[1]-y-ph),(x,CANVAS_SIZE[0]-x-pw))),label=role)
          for role in ('A','C','canvas')}
    background=np.asarray(canvas,dtype=np.float32)
    result={}
    for role in ('A','C'):
        placed=np.asarray(images[role].resize((pw,ph),Image.Resampling.LANCZOS),dtype=np.float32)
        out=background.copy()
        region=out[y:y+ph,x:x+pw]
        region[:]=placed*mask[...,None]+region*(1-mask[...,None])
        raw=_png(Image.fromarray(np.rint(np.clip(out,0,255)).astype(np.uint8),'RGB'))
        result[role]=raw

    for path,sha in [(a_path,a_sha),(c_path,c_sha),(canvas_path,canvas_sha)]:
        if _sha(path)!=sha:
            raise RuntimeError('input changed during composition')
    for path,role in [(a_annotation,'A'),(c_annotation,'C'),(canvas_annotation,'canvas')]:
        if _sha(path)!=annotations[role]['sha256']:
            raise RuntimeError('annotation changed during composition')
    manifest={'schema_version':1,'tool':'photo_motion.shared_canvas','purpose':'EXPERIMENTAL_PHOTOGRAPHIC_SHARED_CANVAS',
              'source_authority':'ONLY_PINNED_SURVIVING_V7_PNG_BYTES_NOT_V6_PARENT_CROP_REPLAY',
              'pillow_version':PILLOW_VERSION,'numpy_version':np.__version__,
              'source_images':{'A':{'sha256':a_sha,'image_size':list(SOURCE_SIZE)},
                               'C':{'sha256':c_sha,'image_size':list(SOURCE_SIZE)},
                               'canvas':{'sha256':canvas_sha,'image_size':list(CANVAS_SIZE),'format':'JPEG','note':'single generated experimental outpaint, NOT identity-master'}},
              'annotations':annotations,'covered_canvas_subject_boxes':cover,
              'transform':{'scale_numerator':scale_num,'scale_denominator':scale_den,
                           'rounded_image_size':[pw,ph],'offset_xy':[x,y],
                           'window_half_open':list(window),'feather_side_top_bottom':list(feather),
                           'interpolation':'Pillow LANCZOS','blend':'linear alpha minimum of horizontal and vertical window ramps'},
              'outputs':{role:{'filename':OUTPUTS[i],'sha256':hashlib.sha256(result[role]).hexdigest(),
                                'image_size':list(CANVAS_SIZE)} for i,role in enumerate(('A','C'))},
              'photographic_identity_form_motion_and_release':'NOT_EVALUATED',
              'flow_suitability':'HOLD_UNTIL_INDEPENDENT_VISUAL_AND_PRE_CREDIT_GATE',
              'warning':'Subject bounds are operator claims, not verified detections. Checks alpha and hashes, NOT realism, hidden A ghost, seam quality, physical pose, actual video motion or old V6 crop lineage.'}
    manifest_raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode('utf-8')
    _exclusive_write(list(zip(destinations,[result['A'],result['C'],manifest_raw])))
    return manifest


def replay_verify(manifest_path, a_path, c_path, canvas_path, a_output, c_output,
                  *, a_annotation, c_annotation, canvas_annotation):
    """Replay exact source transform, proving generated PNG bytes are reproducible.

    A successful replay proves neither photographic quality nor source approval.
    """
    manifest_path=Path(manifest_path)
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError('manifest must be existing non-symlink JSON')
    prior_sha=_sha(manifest_path)
    try:
        expected=json.loads(manifest_path.read_text(encoding='utf-8'))
    except (ValueError,UnicodeDecodeError) as exc:
        raise ValueError('manifest is not valid JSON') from exc
    if (not isinstance(expected,dict) or expected.get('schema_version')!=1 or
        expected.get('tool')!='photo_motion.shared_canvas'):
        raise ValueError('not a version-one shared-canvas manifest')
    try:
        tr=expected['transform']
        sources=expected['source_images']
        outputs=expected['outputs']
        params={'scale_num':tr['scale_numerator'],'scale_den':tr['scale_denominator'],
                'x':tr['offset_xy'][0],'y':tr['offset_xy'][1],
                'window':tr['window_half_open'],'feather':tr['feather_side_top_bottom']}
        pins=[sources[role]['sha256'] for role in ('A','C','canvas')]
        output_pins=[outputs[role]['sha256'] for role in ('A','C')]
    except (KeyError,IndexError,TypeError) as exc:
        raise ValueError('incomplete shared-canvas manifest') from exc
    for role,path,pin in [('A output',a_output,output_pins[0]),('C output',c_output,output_pins[1])]:
        _pinned(path,pin,role,kind='PNG',size=CANVAS_SIZE)
    with TemporaryDirectory(prefix='5bx-shared-canvas-replay-') as temp:
        actual=compose(a_path,c_path,canvas_path,temp,
            a_sha=pins[0],c_sha=pins[1],canvas_sha=pins[2],
            a_annotation=a_annotation,c_annotation=c_annotation,
            canvas_annotation=canvas_annotation,**params)
        if actual!=expected:
            raise ValueError('manifest differs from deterministic complete replay')
        for role,original in [('A',a_output),('C',c_output)]:
            if _sha(Path(temp)/actual['outputs'][role]['filename'])!=_sha(original):
                raise ValueError(f'{role} output failed byte replay')
    if _sha(manifest_path)!=prior_sha:
        raise RuntimeError('manifest changed during replay')
    return {'status':'EXACT_BYTE_REPLAY_VERIFIED_EXPERIMENTAL_ONLY',
            'manifest_sha256':prior_sha,
            'output_sha256':{'A':output_pins[0],'C':output_pins[1]},
            'form_motion_identity_release':'NOT_EVALUATED'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('a');p.add_argument('c');p.add_argument('canvas');p.add_argument('out_dir')
    for name in ('a_sha','c_sha','canvas_sha','a_annotation','c_annotation','canvas_annotation'):
        p.add_argument('--'+name.replace('_','-'),required=True)
    p.add_argument('--scale-num',type=int,required=True)
    p.add_argument('--scale-den',type=int,required=True)
    p.add_argument('--x',type=int,required=True);p.add_argument('--y',type=int,required=True)
    p.add_argument('--window',type=int,nargs=4,required=True,metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    p.add_argument('--feather',type=int,nargs=3,required=True,metavar=('SIDE','TOP','BOTTOM'))
    args=p.parse_args(argv)
    try:
        manifest=compose(args.a,args.c,args.canvas,args.out_dir,
             a_sha=args.a_sha,c_sha=args.c_sha,canvas_sha=args.canvas_sha,
             a_annotation=args.a_annotation,c_annotation=args.c_annotation,canvas_annotation=args.canvas_annotation,
             scale_num=args.scale_num,scale_den=args.scale_den,x=args.x,y=args.y,
             window=args.window,feather=args.feather)
    except (ValueError,RuntimeError,OSError) as exc:
        p.error(str(exc))
    print(json.dumps({'status':'EXPERIMENTAL_HOLD','outputs':manifest['outputs']},indent=2))


if __name__=='__main__':
    main()
