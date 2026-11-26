"""Synthetic-only regression coverage for a single shared photographic canvas."""

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
from PIL import Image, ImageDraw

from photo_motion.shared_canvas import compose, replay_verify


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class SharedCanvasTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(prefix='5bx-shared-canvas-synthetic-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.out=self.root/'output'
        self.out.mkdir()
        self.a=self.root/'a.png'; self.c=self.root/'c.png'; self.canvas=self.root/'canvas.jpg'
        self.ann={}
        for role,path,color in [('A',self.a,(211,54,38)),('C',self.c,(46,175,118))]:
            image=Image.new('RGB',(1280,720),(80,128,100))
            draw=ImageDraw.Draw(image)
            draw.rectangle((350,30,960,670),fill=color)
            image.save(path)
            self.ann[role]=self._annotation(role,path,(309,10,982,684))
        image=Image.new('RGB',(1344,756),(30,120,195))
        draw=ImageDraw.Draw(image)
        draw.rectangle((430,190,915,670),fill=(140,33,201))
        image.save(self.canvas,quality=91)
        self.ann['canvas']=self._annotation('canvas',self.canvas,(427,184,924,682))
        self.kw=dict(a_sha=sha(self.a),c_sha=sha(self.c),canvas_sha=sha(self.canvas),
                     a_annotation=self.ann['A'],c_annotation=self.ann['C'],
                     canvas_annotation=self.ann['canvas'],
                     scale_num=37,scale_den=50,x=200,y=172,
                     window=[355,172,1020,705],feather=[55,5,18])

    def _annotation(self,role,path,bounds):
        ann=self.root/f'{role}-bounds.json'
        ann.write_text(json.dumps({'schema_version':1,'role':role,
           'source_image_sha256':sha(path),
           'image_size':[1280,720] if role!='canvas' else [1344,756],
           'subject_bounds_half_open':list(bounds),'reviewer':'synthetic-test-operator',
           'coverage':'ALL_VISIBLE_PERSON_PIXELS','confidence':'OPERATOR_DECLARED'}))
        return ann

    def test_opaque_people_shared_background_and_exact_replay(self):
        manifest=compose(self.a,self.c,self.canvas,self.out,**self.kw)
        self.assertEqual(manifest['flow_suitability'],'HOLD_UNTIL_INDEPENDENT_VISUAL_AND_PRE_CREDIT_GATE')
        self.assertEqual(manifest['transform']['rounded_image_size'],[947,533])
        self.assertNotEqual(manifest['outputs']['A']['sha256'],manifest['outputs']['C']['sha256'])
        output_a=np.asarray(Image.open(self.out/'A_shared_canvas.png').convert('RGB'))
        output_c=np.asarray(Image.open(self.out/'C_shared_canvas.png').convert('RGB'))
        self.assertTrue(np.array_equal(output_a[:120,:],output_c[:120,:]))
        self.assertTrue(np.array_equal(output_a[:, :200],output_c[:, :200]))
        # Both roles replace the generated canvas's different-colored person.
        # Fully opaque subject centers must equal independently resized source.
        for role,source,out in [('A',self.a,output_a),('C',self.c,output_c)]:
            independently_resized=np.asarray(Image.open(source).resize((947,533),Image.Resampling.LANCZOS))
            self.assertTrue(np.array_equal(out[200:660,450:900],independently_resized[28:488,250:700]))
        replay=replay_verify(self.out/'shared_canvas.manifest.json',self.a,self.c,self.canvas,
                             self.out/'A_shared_canvas.png',self.out/'C_shared_canvas.png',
                             a_annotation=self.ann['A'],c_annotation=self.ann['C'],
                             canvas_annotation=self.ann['canvas'])
        self.assertEqual(replay['status'],'EXACT_BYTE_REPLAY_VERIFIED_EXPERIMENTAL_ONLY')

    def test_fail_closed_on_incomplete_subject_bounds(self):
        self.ann['C']=self._annotation('C',self.c,(309,0,982,684))
        self.kw['c_annotation']=self.ann['C']
        with self.assertRaisesRegex(ValueError,'annotated person may enter canvas/feather'):
            compose(self.a,self.c,self.canvas,self.out,**self.kw)
        self.assertEqual(list(self.out.iterdir()),[])

    def test_reject_substituted_source(self):
        self.kw['a_sha']='0'*64
        with self.assertRaisesRegex(ValueError,'A bytes do not match pin'):
            compose(self.a,self.c,self.canvas,self.out,**self.kw)
        self.assertEqual(list(self.out.iterdir()),[])

    def test_reject_preexisting_destination(self):
        (self.out/'C_shared_canvas.png').write_bytes(b'user-existing-evidence')
        with self.assertRaises(FileExistsError):
            compose(self.a,self.c,self.canvas,self.out,**self.kw)
        self.assertEqual((self.out/'C_shared_canvas.png').read_bytes(),b'user-existing-evidence')

    def test_replay_rejects_altered_output(self):
        compose(self.a,self.c,self.canvas,self.out,**self.kw)
        # Record byte tampering without mutating the private originals.
        (self.out/'C_shared_canvas.png').write_bytes(b'not-the-output')
        with self.assertRaisesRegex(ValueError,'C output bytes do not match pin'):
            replay_verify(self.out/'shared_canvas.manifest.json',self.a,self.c,self.canvas,
                          self.out/'A_shared_canvas.png',self.out/'C_shared_canvas.png',
                          a_annotation=self.ann['A'],c_annotation=self.ann['C'],
                          canvas_annotation=self.ann['canvas'])

    def test_manifest_annotation_cannot_be_swapped(self):
        compose(self.a,self.c,self.canvas,self.out,**self.kw)
        with self.assertRaisesRegex(ValueError,'annotation is not bound'):
            replay_verify(self.out/'shared_canvas.manifest.json',self.a,self.c,self.canvas,
                          self.out/'A_shared_canvas.png',self.out/'C_shared_canvas.png',
                          a_annotation=self.ann['C'],c_annotation=self.ann['A'],
                          canvas_annotation=self.ann['canvas'])


if __name__=='__main__':
    unittest.main()
