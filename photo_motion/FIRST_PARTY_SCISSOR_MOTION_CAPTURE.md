# First-party human scissor-jump motion reference — field capture protocol

**Status: EXPERIMENTAL CAPTURE STANDARD, NOT A FILMED ASSET OR FORM APPROVAL.**
This is a reproducible way to obtain *real human motion* for a possible later
photographic video-conditioning experiment. It does not authorize a model call,
change the source authority of the V6/V7 photographic A/C stills, or approve
exercise instruction. No third-party film, cartoon sprite, or copyrighted
stock clip is an input to this procedure.

## 1. Source of truth and scope

- Exercise: **RCAF 5BX Chart 1, Exercise 5, interspersed scissor jumps**.
  Use the original Chart 1 booklet description in `data/5bx-charts.json`
  and `photo_motion/specs/chart1-scissor-jump.json` for movement. The
  archival 1959 film is **not** a verified Chart 1 scissor demonstration.
- The starting grounded stance has the **right leg and left arm forward**,
  **left leg and right arm backward**; arms remain approximately straight,
  shoulder high. A jump switches these *physical* limb positions before the
  next landing. Continue until the original stance returns, then repeat.
- Capture **two complete A→airborne→C→airborne→A cycles in one continuous
  uncut take**. This means four separate two-shoes-airborne events, two
  clearly grounded opposite C landings, and three grounded A stances, not
  merely two hops that never exchange limb order.
- The generator's six-second target and colored V7 tags are **experimental**.
  Do not artificially rush human movement to 6 s or assert that an orange
  wrist and orange ankle are the same anatomical side. A separately filmed
  performer establishes their own right/left limbs, not V7 provenance.
- Use a freely consenting **adult movement demonstrator** (18+); no minor is
  required or requested. This footage conveys **mechanics only**. It does not
  change the youthful photographic target, and does not authorize face,
  voice, identity, or biometric/likeness transfer from the demonstrator.

## 2. Set up the inexpensive physical recording

| Control | Operating target | Reject / record if |
| --- | --- | --- |
| Camera | Phone or camera recording **native 1920×1080 or better, 60 fps**, landscape 16:9; tripod fixed throughout | Vertical/low-resolution clip, digital pan/auto-follow, variable subject framing, camera bumped |
| View | True side-on, lens perpendicular to the plane of forward/backward limb travel; tripod about hip/chest height, level horizon | Three-quarter angle hides foot exchange or near/far limbs |
| Lens / distance | Prefer ordinary 35–50 mm-equivalent perspective if available; step backward until full arm extension fits, rather than using ultra-wide distortion | Foreshortened limbs, feet beyond edge, cropped fingertips |
| Safe margins | At rest, **at least 15% frame height above hair**, **10% below both soles**, and **10% width beyond outstretched hands** on either side; verify again during trial jumps | Any hair, whole shoe, finger, or jump apex outside the frame |
| Focus / exposure | Lock focus, exposure, white balance and zoom; bright even light, shutter around 1/250 s or faster if manually controllable, no artificial portrait blur | Focus hunting, motion smearing shoes, lighting pulses, shifting crop |
| Ground | Flat, dry, stable, safe nonslip surface with an unoccluded horizontal shoe-contact line; unobtrusive front/back ground landmarks if needed | Shadow/reflection hides shoe clearance or footing is unsafe |
| Scene | Static uncluttered background, no bystanders, no cutaways, no digital stabilization that changes crop, no on-camera captions | Other bodies/limbs, moving background, distractions |

The margins are **minimum capture goals**, not proof. Verify *every* frame
after recording. A ground surface, height, and jump amplitude should be
chosen conservatively by the adult performer; stop if form or balance is
unsafe. No medical or training claim is made here.

### Before the first take

1. Set phone/camera to its native 1080p/60 mode and verify in a short test
   recording, not merely the camera-settings screen. Record the camera
   make/model, lens setting, nominal frame rate, resolution, stabilization
   mode, orientation, and local time zone in a private capture note.
2. Record a short **slate** in a separate clip: private capture ID, UTC time,
   camera side relative to the performer's right/left, and take number. Do
   not put a real name, address or consent signature in a Git commit or
   generated-video prompt.
3. Have the performer rehearse the physically correct opposing arm/leg
   movement at comfortable amplitude. Capture the camera's entire field,
   including the floor plane, when both shoes leave the ground. Place
   fingertips in frame even at maximum horizontal extension.
4. If physical limb tracking is uncertain, film a **separate diagnostic take**
   with temporary visibly distinct *right* wrist/ankle markers and *left*
   wrist/ankle markers; document the verified mapping. Keep the clean motion
   take unmarked unless the experiment explicitly requires marks. Do not
   silently transfer a marker mapping from one take to another.

## 3. Record the required phase sequence

Begin with a stable grounded A, execute four actual jumping switches, finish
on grounded A, then leave a brief natural hold. Prefer **at least 10–15 s
of continuous footage** to leave selection room; do not insert a transition,
fade, cut, repeat or synthetic frame. If the performer moves too quickly
for useful airborne evidence, retake at a controlled attainable cadence
instead of postulating a midair pose.

The reviewer must locate these **nine events in this strict order**:

| Checkpoint | Support | Physical limb evidence |
| --- | --- | --- |
| A0 | Both whole shoes grounded | Right leg forward, left leg back; left arm forward, right arm back |
| B0 | Both shoes **entirely airborne** | First real physical exchange toward opposite stance |
| C0 | Both shoes grounded | Left leg now forward, right leg back; right arm forward, left arm back |
| D0 | Both shoes **entirely airborne** | Second independent exchange returning to A |
| A1 | Both shoes grounded | Same anatomical ordering as A0 |
| B1 | Both shoes **entirely airborne** | Third separate exchange |
| C1 | Both shoes grounded | Same opposite anatomical ordering as C0 |
| D1 | Both shoes **entirely airborne** | Fourth separate exchange |
| A2 | Both shoes grounded | Same ordering as A0/A1, natural recovery |

For each airborne checkpoint, identify a **contiguous interval of at least
two decoded frames** where *both entire shoe outsoles* are demonstrably clear
of the ground. Record the first/last frame of that interval and their
timestamps; one motion-blurred still or a single lifted heel is insufficient.
Capture each grounded checkpoint as an identifiable frame with both shoes
visibly contacting the same plane. Check head and shoes in **all** frames,
not only the nine samples. Record any ambiguous near/far occlusion as
`NOT_EVALUATED`, never a technical pass.

If the clean footage does not show anatomical left/right distinctly,
use the diagnostic marked take to understand the action, but do not claim
it proves the clean take's hidden anatomy. If no usable take shows the
required movement continuously, the filming trial **fails and is preserved
as an example**, not quietly spliced or corrected by animation.

## 4. Rights and privacy stop gate (before model upload)

Keep a signed, dated **adult-performer release** in the owner's private
archive, specifying whether the granted uses include:

1. Filming and private storage of the raw performance.
2. Editing, cropping, frame extraction, and technical analysis.
3. Uploading the performance to named third-party AI video-generation
   providers as *motion-conditioning input* and making AI derivatives.
4. Use in the planned 5BX educational/commercial product and public
   distribution **if intended**.
5. A clear permitted-purpose limit: **motion-only conditioning**, not an
   identity, face, voice, or biometric master. Do not use model output to
   reconstruct or impersonate the real demonstrator's likeness.
6. The withdrawal/revocation procedure, contact route, any contractual
   limitations once derivatives have been created/distributed, and what
   happens to retained originals after withdrawal. Do not assume consent is
   perpetual or that a requested withdrawal can erase previous provider use.
7. Permission boundaries, compensation/consideration if any, and a contact
   for license questions. Never assume a generic “okay to film” covers AI
   uploads or publication.

Record a separate property/location permission or a documented finding that
none is required. Exclude bystanders, children, recognizable branding and
private conversations. Retain the actual signed release privately; Git may
contain only its SHA-256, opaque archive locator and permissions summary.
If any required provider-upload or derivative-use right is absent/unknown,
**do not upload the real-human reference to Flow, Grok or another generator**.
No silence or apparent availability on YouTube is permission.

This is an evidence checklist, not a legal sufficiency determination; obtain
appropriate review for public/commercial reuse when needed.

## 5. Byte-level intake and immutable evidence

Preserve the camera-original MP4/MOV unmodified, in an owner-only private
archive. Never rewrite its rotation metadata, strip its audio, frame-rate
convert it or create a clipped “original.” Derivatives have new filenames,
new SHA-256 values and parent-source hashes. Use `sha256sum` or an
independent byte-hashing implementation on the exact original:

```bash
sha256sum /private/chart1-ex5-human-capture-001-original.mp4
ffprobe -v error -count_frames -show_entries \
  format=filename,format_name,duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,pix_fmt,field_order,rotation \
  -of json /private/chart1-ex5-human-capture-001-original.mp4
```

Save the command outputs alongside the raw file as private read-only
receipts, and verify that the uploaded private-archive file size and
downloaded bytes match the source hash. Treat phone-reported 60 fps as a
claim until actual stream timing is checked; some phones record variable
frame rate. The 60 fps target is a capture preference, not license to
reinterpret the 24 fps generator contract.

The private intake JSON should identify **one exact camera original**, not
a rendition or third-party clip. Example *shape* (all values placeholders):

```json
{
  "schema_version": 1,
  "capture_id": "C1-EX5-HUMAN-MOTION-001",
  "status": "EXPERIMENTAL_NOT_FORM_APPROVED",
  "captured_at_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "recorded_local_timezone": "Area/City",
  "source": {
    "locator": "private://5bx/motion/c1-ex5/001/original",
    "sha256": "REPLACE_WITH_REAL_64_HEX_SHA256",
    "bytes": null,
    "codec": "REPLACE_FROM_FFPROBE",
    "width": 1920,
    "height": 1080,
    "fps_reported": "60/1",
    "fps_measured": "REPLACE_FROM_FFPROBE",
    "decoded_frames": null,
    "duration_seconds": null,
    "rotation_degrees": null
  },
  "setup": {
    "camera_model": "REPLACE",
    "camera_side_relative_to_performer": "REPLACE",
    "camera_locked": "MANUALLY_ATTESTED_OR_NOT_EVALUATED",
    "focus_exposure_white_balance_locked": false,
    "full_body_margin_review": "NOT_EVALUATED"
  },
  "human_motion_evidence": {
    "reviewer": "REPLACE_WITH_VERIFIED_REVIEWER",
    "nine_checkpoints_frame_numbers": null,
    "four_distinct_both-shoes-airborne_frame_intervals": null,
    "all_frames_head_and_shoes_visible": "NOT_EVALUATED",
    "anatomical_side_continuity": "NOT_EVALUATED",
    "technical_motion_verdict": "NOT_EVALUATED",
    "form_and_safety_verdict": "NOT_EVALUATED"
  },
  "rights": {
    "performer_release_locator": "private://5bx/consents/opaque-id",
    "performer_release_sha256": "REPLACE_WITH_REAL_64_HEX_SHA256",
    "permitted_ai_provider_upload": "NOT_EVALUATED",
    "permitted_derivatives": "NOT_EVALUATED",
    "permitted_public_use": "NOT_EVALUATED",
    "permitted_likeness_transfer": false,
    "withdrawal_terms_recorded": "NOT_EVALUATED",
    "location_permission_status": "NOT_EVALUATED"
  },
  "release": "HOLD_FOR_CHARLES_EXACT_VIDEO_REVIEW"
}
```

The actual record must also retain the individual frame numbers/timestamps
for A0/B0/C0/D0/A1/B1/C1/D1/A2, and the start/end frame numbers for each
verified airborne window. The JSON above is a receipt outline, **not a
validator-produced PASS**, a real consent release, or an instruction to fill
unknown values with guesses.

## 6. Trial disposition and future supplier experiment

Log one immutable trial record per take in the **existing photographic QA
note/production record**: capture ID, file hash, date, model/geometry,
rights evidence hash, measured frame count, nine event times, four intervals,
observed defect codes, and next specific countermeasure. Keep the raw source
and private release in the controlled archive, not Git. Do not open a
parallel Kanban/traveler or a second approval ledger.

| Decision | Evidence and next action |
| --- | --- |
| `CAPTURE_REFERENCE_CANDIDATE` | Complete private consent, geometry, metadata and all nine phase events independently reviewed; only then may a separately authorized, source-pinned provider-conditioning experiment be proposed |
| `RETAKE_REQUIRED` | Any cropped head/shoe, ambiguous real flight, missing opposite grounded stance, camera movement, exposure/focus pumping, insufficient rights or corrupted/variable frame timing; preserve failure and change one capture variable |
| `NOT_EVALUATED` | Original, complete frame inspection, rights document or verified metadata unavailable; never call it a pass |

Even a `CAPTURE_REFERENCE_CANDIDATE` is **not** a validated 5BX instruction
video, proof that a provider will preserve bodily physics, or Charles's final
production acceptance. The later synthetic output must independently pass
the current photographic motion, identity, loop, framing and release gates.

For a later provider test, specify the exact hash and consent scope of this
human video *in a new versioned input contract*; do **not** silently replace
the V7 A/C still authorities or mix the diagnostic marker take with the
clean take. Preserve provider/model, quoted credit cost and actual submitted
prompt as separate immutable evidence.
