# Requirements: photographic video-first exercise playback

Status: Draft — engineering implementation staged; release HOLD
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

## Open questions

- Owner review of this engineering specification before any release decision.
- Which trusted external owner-approval event will generate the first nonempty
  registry? Until established, all media entries remain absent.
