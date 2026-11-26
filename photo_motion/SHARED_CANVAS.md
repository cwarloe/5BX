# Experimental paired photographs on one generated outpaint canvas

`python3 -m photo_motion.shared_canvas` is an optional **photographic still**
experiment. It accepts two exact pinned RGB 1280×720 A/C source PNGs, **one**
separately generated RGB 1344×756 JPEG background extension, and three
source-hash-bound conservative person-box annotations. It produces two
1344×756 PNGs with a common photographic background and a reproducible
manifest. It never calls Google Flow or spends generation credits.

This was developed to investigate a specific observed defect: independently
outpainting A and C gave plausible individual images but changed the trees,
track and the subject's size. A single canvas plus one identical affine
transform and blending window can retain the original paired pose content
and background registration without mirrored border duplicates.

## Authority and controls

- The surviving prepared A/C PNG **bytes** are the only older source authority;
  this tool does not reconstruct or verify the unrecoverable V6 parent crop.
- The generated JPEG is explicitly a derived experimental **background**,
  not an identity master or evidence of historical form.
- The exact SHA-256 for **all three inputs** is required. Decode must prove
  RGB, expected dimensions and exact source format before any output is written.
- Each bound annotation has `schema_version: 1`, `role: A|C|canvas`,
  `source_image_sha256`, `image_size`, `subject_bounds_half_open: [left,top,right,bottom]`,
  `reviewer`, `coverage: ALL_VISIBLE_PERSON_PIXELS`, and
  `confidence: OPERATOR_DECLARED`. Annotations are **operator claims**;
  the tool cannot determine whether a box truly encloses the whole person.
- One uniform rational scale, explicit translation and the same horizontal/
  vertical feathered window apply to A and C. Every annotated person box
  must fit in the **fully opaque** part of that shared source region, including
  the generated canvas's original person; otherwise the run fails closed.
  This limits faint ghosting but does not prove its absence.
- Outputs must be made in a new existing non-symlink directory; exclusive
  writes never silently replace existing evidence. The manifest includes
  exact PNG hashes, input/annotation hashes, geometry, Pillow/Numpy versions,
  and an unambiguous `HOLD` status.

After a run, independent evidence must inspect marker/limb preservation,
identity, natural seams, missing/repeated body parts, ground contact, head/
shoe margins and registered background. Pixel matching cannot establish
historical exercise form, future airborne motion, audio policy, or loop.
**A separate versioned precredit authority is necessary before Flow video use.**

## Scratch-only invocation

Paths here are placeholders. Keep the actual photo bytes, output, annotations
and full private run manifest in the authorized private archive, not GitHub.

```bash
python3 -m photo_motion.shared_canvas \
  /private/A.png /private/C.png /private/generated-background.jpg /private/new-output-dir \
  --a-sha FULL_SHA256 --c-sha FULL_SHA256 --canvas-sha FULL_SHA256 \
  --a-annotation /private/A-bounds.json \
  --c-annotation /private/C-bounds.json \
  --canvas-annotation /private/canvas-bounds.json \
  --scale-num 37 --scale-den 50 --x 200 --y 172 \
  --window 355 172 1020 705 --feather 55 5 18
```

The example geometry is a controlled candidate-specific value, **not** a
universal camera registration formula. Image and annotation hashes, exact
geometry and pixel-boundary QA must be separately qualified for every new
source trio. `Pillow LANCZOS` introduces a recorded spatial resampling but
does not synthesize new person movement. The JPEG canvas itself was generated
and thus can contain nondeterministic scene changes or identity artifacts;
only subsequent composition is deterministic.

## Reproducibility verification

`photo_motion.shared_canvas.replay_verify(manifest_path, a_path, c_path,
canvas_path, a_output, c_output, a_annotation=..., c_annotation=...,
canvas_annotation=...)` rehashes and decodes the exact three source inputs
and both archived output PNGs, replays the transform in a fresh temporary
directory, byte-compares both outputs and the complete recorded manifest.
It returns `EXACT_BYTE_REPLAY_VERIFIED_EXPERIMENTAL_ONLY` on match—not
permission to spend, publish, approve form or use it in player playback.

Synthetic regression tests: `python3 -m unittest photo_motion.tests.test_shared_canvas -v`.
