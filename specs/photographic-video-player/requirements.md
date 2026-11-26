# Requirements: photographic video-first exercise playback

Status: Approved for engineering implementation by Charles in project chat on 2026-11-26; photographic video release HOLD
Owner: Charles
Last updated: 2026-11-26

## Problem

The legacy workout stage uses cartoon sprite frames, whereas the intended system
uses exercise-specific photorealistic MP4 footage. The first diagnostic motion
pilots have not been owner-approved, so runtime must never mistake them for
release-ready instruction.

## Out of scope

- Generating, approving, publishing, uploading, or declaring complete an exercise video.
- Changing exercise timings, 5BX movements, or the existing public experience.
- Traveler/Kanban/dashboard management and the legacy sprite asset pipeline.

## Requirements

### R1. Explicit release-gated media

**User story:** As the owner, I want every exercise clip intentionally admitted,
so that production cannot inherit an unapproved diagnostic video.

**Acceptance criteria**

1. The registry SHALL ship empty and accept only explicit approved MP4 metadata.
2. An absent, invalid, or failed video SHALL display an informative unavailable
   state, never select a cartoon sprite.
3. Release-gate provenance and file hash remain build-time responsibilities;
   runtime metadata parsing SHALL NOT be mistaken for owner acceptance.
4. Admission SHALL bind every clip to the exact chart, exercise, action,
   revision, and immutable SHA-256 bytes that Charles accepted. The 40-second
   running portion and 5-second scissor-jump portion of Chart 1 Exercise 5
   SHALL have distinct action-level approvals, but share the existing canonical
   exercise QA record and owner decision authority (no duplicate ledger).
5. Playback URLs SHALL be immutable and content-addressed under an explicitly
   owner-controlled same-origin path (or a separately approved strict origin
   allowlist). Arbitrary HTTPS hosts, path traversal, and arbitrary MP4 names
   SHALL fail admission. Deployment SHALL verify served bytes match the exact
   owner-approved local digest; a well-formed SHA-256 string alone is not proof.

### R2. Reliable workout synchronization

**User story:** As an exerciser, I want photographic loops to remain synchronized
to the 5BX movement schedule through pause, skip, and interval changes.

**Acceptance criteria**

1. Every playable clip SHALL loop muted and inline with simulation-owned time.
2. Pause SHALL pause video, and resume/skip SHALL align with the current interval.
3. The 40-second jog and 5-second scissor segment boundaries SHALL be explicit;
   a 6-second clip SHALL NOT silently trim, speed, or loop into a 5-second slot.
4. A mismatch between decoded media duration and reviewed manifest SHALL fail
   closed, and video elements SHALL release old media on unmount/segment change.
5. No photographic frame SHALL become visible and no playback SHALL start
   until the trusted source/byte identity and loaded MP4 metadata/duration have
   both passed checks. On failure the source SHALL remain invisible, be released,
   and present an unavailable state.
6. The **decoded playable** clip duration, not only the declared manifest or
   container duration, SHALL tile the complete slot without truncation. The
   actual decoded duration SHALL NOT exceed the slot, even by one frame; a
   declared or measured 5.01s or 5.05s jump SHALL be rejected for a 5.00s
   slot. Short-ending loops (for example 4.95s in 5.00s) SHALL also be held
   unless they meet a documented, measured sub-frame seam tolerance and have
   independently passed a full-loop A→C→A visual review. Exactly 5.00s passes
   the duration check but still requires all other admission gates.
7. Synchronization tolerance to the simulation clock SHALL be specified,
   measured, and tested; pause, resume, segment swap, reduced-motion opt-in,
   error, and unmount SHALL all pause and release the preceding media correctly.

### R3. Safe staging and accessibility

**User story:** As the owner, I want to develop the new system while keeping the
existing public UI unchanged until approved video footage exists.

**Acceptance criteria**

1. The new stage SHALL be accessible only with an explicit development build
   flag; no production request parameter can enable it.
2. In photo-preview mode there SHALL be no legacy sprite renders or sprite preloads.
3. The preview SHALL communicate unreleased status and media absence to users;
   the video's purpose SHALL be labeled for assistive technology.
4. A user requesting reduced motion SHALL not silently autoplay exercise video;
   deliberate opt-in may enable it for the preview session.

## Approval boundary and remaining question

Charles explicitly approved merging these requirements and proceeding with
engineering in the project chat on 2026-11-26. This records a requirements
decision, **not** authenticated acceptance of any exercise-video revision.

- Which trusted external owner-approval event will generate the first nonempty
  registry? Until established, all media entries remain absent and no exercise
  footage may be published through the photographic player.
