# Audited no-audio review derivative (real photographic MP4)

Flow may produce AAC even when a prompt explicitly says **no audio**. The raw
video then fails an `audio_policy: forbid` inspection. Never erase that failure
or pretend a post-processed file proves the generator obeyed its prompt.

When a genuine clip is otherwise worth reviewing, this offline command creates
an independent **silent review copy** and a machine-verifiable manifest:

```bash
sha256sum /private/5bx/raw-original.mp4
python3 -m photo_motion.silent_derivative /private/5bx/raw-original.mp4 \
  --source-sha256 REAL_64_CHARACTER_SHA256_OF_RAW \
  --out /private/5bx/derived/new-unique-review-directory
```

The output directory must not exist. The command spends **zero Flow credits**
and never edits the input or any existing evidence.

## Recorded controls

- Hash and verify the original MP4 against an explicitly supplied expected
  SHA-256 **before** creating any files.
- Use ffmpeg **video stream copy** (`-map 0:v:0 -c:v copy`) and drop all audio,
  subtitles, data, original metadata and chapters. No visual re-encoding.
- Fail closed unless ffprobe confirms exactly one video stream and **zero**
  audio streams in the derivative, the same ordered SHA-256 packet hashes,
  decoded-frame count, coded dimensions, codec and pixel format, plus duration
  drift within one original frame.
- Write `silent_review.mp4` and `silent_derivative_manifest.json`. The manifest
  records source/output hashes, stream probes, encoded packet sequence digest,
  decoded-frame count, exact ffmpeg command/version and immutable HOLD status.
- Never overwrite a prior review directory. If an exception interrupts the
  operation, discard or quarantine any incomplete directory; **do not** use a
  derivative missing a successful manifest.

An identical encoded packet sequence is stronger than comparing decoded visual
frames, because it detects any video re-encode or packet substitution. It is
not a guarantee that every video player renders identically, and it **does
not** prove proper joint mechanics, opposite landing, no cropping, identity
preservation or a seamless loop.

## Boundaries

`raw_generation_audio_policy_result: FAIL_AUDIO_PRESENT_IN_RAW` remains in the
manifest if the input contained audio. The output only satisfies the narrow
delivery constraint of having no audio stream. It **does not change** the
source experiment's technical outcome or human form/release state. Both #20 and
#21 currently fail other movement or loop criteria, so stripping their AAC
would not turn either into a release candidate.

Keep raw and derivative as separate immutable artifacts with their own hashes
in the private archive. Do not commit either MP4, its prompt or identifying
frames to Git; do not move Flow media to Drive without separately authorized
transfer. No step in this utility publishes, merges, or approves a video.
