# Optional paired A/C photographic headroom experiment

This is a **future framing-only diagnostic**, not the current V6/V7 scissor
source authority or Flow attempt. Video #21 cropped the boy's hair at 59 of
144 decoded frames. If a later controlled two-pose video succeeds at physical
scissor exchange but still clips the head or shoes, *framing* can be tested as
one isolated new variable. Do not spend credits merely because this helper
created a more generously framed still.

**Fail-closed correction after a real image test:** Each source now requires
a separate manually assessed subject bounding-box annotation, bound to that
source's complete SHA-256 and photographic role. The tool blocks any output
unless the entire annotated person lies outside the source regions copied to
all four reflected borders, plus a conservative 16-source-pixel resampling
guard. Missing, unconfirmed, stale, wrong-role or unsafe annotations all
reject the operation. It **cannot prove** that a reviewer drew the bbox
accurately or independently—an actual visual review is still mandatory.

Run the deterministic transform on **two byte-pinned, privately retained,
RGB 1280×720 photographic PNGs** (A start and C opposite-grounded contact):

```bash
mkdir /private/new-empty-pair-output
python3 -m photo_motion.pair_reframe \
  /private/verified-A.png /private/verified-C.png /private/new-empty-pair-output \
  --a-sha256 FULL_VERIFIED_A_SOURCE_SHA256 \
  --c-sha256 FULL_VERIFIED_C_SOURCE_SHA256 \
  --a-annotation /private/A-source-bounds.json \
  --c-annotation /private/C-source-bounds.json \
  --scale-percent 80
```

Each source-specific JSON annotation must contain these fields, with the
correct corresponding source SHA, role `A` or `C`, and a genuinely assessed
half-open pixel rectangle enclosing **every visible part of the person**:

```json
{
  "schema_version": 1,
  "source_image_sha256": "EXACT_SOURCE_SHA256",
  "role": "A",
  "image_size": [1280, 720],
  "reviewer": "ACTUAL_BOUNDARY_OBSERVER",
  "confidence": "CERTAIN",
  "coverage": "ALL_VISIBLE_PERSON_PIXELS",
  "subject_bounds_half_open": [300, 145, 980, 540]
}
```

The illustrative box above is **not** a claim about either real 5BX image.
If the observer cannot establish a complete box, use `confidence: "UNCERTAIN"`
and the tool will reject. The input annotation file's SHA-256 and the exact
declared bbox/reviewer are recorded in the output manifest; its verdict is
always `NOT_FLOW_SAFE_UNTIL_INDEPENDENT_VISUAL_REVIEW`, even after the
numeric safety calculation passes.

The output directory must already exist. The command refuses to replace its
three files and leaves the original sources untouched:

- `A_reframed.png`: 1280×720, only existing A pixels resized / mirrored.
- `C_reframed.png`: identical geometry for the C counterpart.
- `pair.manifest.json`: input and derived SHA-256, Pillow version, exact
  central region and padding, transform method and limitations.

At 80% scale, the full original image is resampled uniformly to 1024×576 and
centered at pixel rectangle `[128,72,1152,648)`. Added borders are
128 px each side and 72 px each top/bottom. They contain only mirrors of
existing background/edge pixels: **no synthetic new sky, grass, track, anatomy
or person**. This creates more screen-space margin, but cannot guarantee 100
pixels of *anatomical* headroom because the subject's original source clearance
is not measured by this tool. The reframe is *replayable*, not mathematically
pixel-reversible (Lanczos resampling alters pixels). Source originals and
their hashes remain the rollback authority.

### Real photographic A/C candidate: rejected before Flow use

The first deterministic 80%-scale replay of the actual A/C photographic
inputs (before the bbox gate existed) yielded valid PNG hashes but **failed
human-visible composition QA**: an upside-down duplicate head appeared in
the top reflection strip, duplicate shoes at the bottom, and repetitive
trees/track texture at the sides. The source head and shoes are already near
the original top/bottom image boundaries. No Flow test or credits were used.

| Item | SHA-256 |
| --- | --- |
| Original preserved A PNG | `7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f` |
| Original preserved C PNG | `c0ede374ee3a65266c19b27fc0f295a44a5a95e9d3aa0c1b41982b64f4a155a0` |
| Derived A, visually REJECTED | `2b058b2131058b2c1f808bf60436c3cef2fdc4bbc7557cc6d86019590035e511` |
| Derived C, visually REJECTED | `ccde8fa3b817159897be3fad40c482c3d1a513b244b3b76b8b11fb67f3e44ca1` |
| Derived pair manifest | `ba1ccb3b7ff5c8616294f73d26e2dec10fd395153fdc8b31879586481d0ee1ca` |

A fresh dry-run with conservative visual source boxes encompassing hair,
hands and shoes now fails with
`A mirrored top strip overlaps or is too close to annotated subject bbox`,
**exit code 2 with no output files created**. At 80%, the safe subject
rectangle in the *source* is `[176,106,1104,614)`; the observed person's
hair/shoes extend outside its vertical limits. This is a source geometry
constraint, not something more prompt wording or extra credits can repair.
Do not feed either visually rejected variant into #22 or later Flow attempts.
Seek a photograph with actual background margin beyond the whole person, or
separately qualify a non-reflective background-safe composition method.

The generated PNGs **are new derivative sources**. V6's original-card
preflight and any separately versioned V7 direct-source gate must not accept
them silently. A paid framing test needs its own versioned source identity,
fresh pre-credit validation, literal submitted prompt and provider cost quote.
Do not interchange A and C, and do not add a third image.

## QA before even considering a framing test

1. Verify the recorded output SHA-256 values match the local derived PNGs and
   both originals still match their input hashes.
2. Look at *both* images, including all four borders; reflected track lines,
   trees, limbs or shoes near the edges may produce conspicuous duplicate
   features or confusing contact shadows. Reject those source images if so.
3. Check that the subject actually has sufficient head and shoe margin in
   both frames. Pixel resampling by itself cannot establish identity or form.
4. Only after the movement result justifies a framing-only test, treat it as
   a separate paid experiment with independently evaluated complete MP4
   motion, physical limb lineage, no crop on all frames, scene continuity and
   loop. **Never promote these stills or a technical PASS to owner approval.**

No cartoon/sprite input, paid provider, video generator, source-authority
change or release operation is part of this command.
