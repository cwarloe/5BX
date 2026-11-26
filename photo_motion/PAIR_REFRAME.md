# Optional paired A/C photographic headroom experiment

This is a **future framing-only diagnostic**, not the current V6/V7 scissor
source authority or Flow attempt. Video #21 cropped the boy's hair at 59 of
144 decoded frames. If a later controlled two-pose video succeeds at physical
scissor exchange but still clips the head or shoes, *framing* can be tested as
one isolated new variable. Do not spend credits merely because this helper
created a more generously framed still.

Run the deterministic transform on **two byte-pinned, privately retained,
RGB 1280×720 photographic PNGs** (A start and C opposite-grounded contact):

```bash
mkdir /private/new-empty-pair-output
python3 -m photo_motion.pair_reframe \
  /private/verified-A.png /private/verified-C.png /private/new-empty-pair-output \
  --a-sha256 FULL_VERIFIED_A_SOURCE_SHA256 \
  --c-sha256 FULL_VERIFIED_C_SOURCE_SHA256 \
  --scale-percent 80
```

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
