# Design: photographic video-first exercise playback

Status: Engineering implementation after Charles's requirements approval; video release HOLD
Requirements: [requirements.md](requirements.md)

## Boundaries

The released workout remains unchanged until real, individually accepted
photographic MP4s exist. A dev-only build flag enables an isolated video-first
preview with **zero accepted clips**. It renders a clear unavailable state,
never a cartoon fallback. No MP4 file, media URL, owner decision, credit use,
or real video approval is introduced by this feature.

The existing `photo_motion/player_media_gate.py` checks private video bytes and
canonical QA evidence offline. It intentionally emits an empty registry and
`HOLD` even for forged owner-looking markers. UI validation below is a second,
limited line of defense: neither JSON fields nor the browser's video metadata
can authenticate Charles or hash a remote response. A future separately
reviewed trusted build step must bind the actual delivered bytes and approval
event before producing any nonempty registry.

## Components and contracts

| Surface | Purpose | Criteria |
| --- | --- | --- |
| `game/src/lib/photo-video.ts` | Typed empty registry; exact chart/exercise/action identity; strict content-addressed local URL; 40s/5s segment clock; decoded/full-cycle duration policy | R1, R2 |
| `game/src/components/photographic-exercise-video.tsx` | Video staged invisible until metadata and seek prove safe; clock sync, pause, teardown, error/reduced-motion states | R1.2, R2, R3 |
| `game/src/components/workout-app.tsx` | `import.meta.env.DEV && VITE_PHOTO_PLAYER_PREVIEW===1` only; no sprite render/preloads in preview | R3 |
| `game/src/styles.css` | Existing visual language extended to explicit HOLD/preview states | R3 |
| `game/src/lib/photo-video.test.ts` | Fail-closed identity/URLs, timing, playlist isolation and simulation boundaries | R1, R2 |
| Browser/DOM tests | Validate actual preplay visibility, reduced-motion opt-in, pause/change/error/unmount cleanup, sprite-free preview | R2, R3 |
| Independent artifact check | Reject unapproved MP4 bytes in public build even with empty registry, including accidental assets | R1.1, R1.5 |

## Identity and asset path

The admissible exercise actions for Chart 1 are toe, situp, back, pushup, run,
and scissor. The first four bind to exercises 1–4; running and scissor jumps
are **distinct actions** within exercise 5. A candidate must match every
slot field (`chart`, `exercise`, `action`, canonical `exerciseId`), exact revision,
SHA-256, H.264 MP4 type and reviewed duration. A registry key alone cannot
change or reassign that exercise's identity.

For future nonempty entries, URLs have one canonical same-origin shape under
the explicitly controlled `/5BX/game/approved-photo/` path with the lowercase
SHA-256 as filename: `/5BX/game/approved-photo/<sha256>.mp4`. Reject absolute
external URLs, queries, fragments, encoded separators/traversal, noncanonical
characters and filename/hash disagreement. This is **URL-syntax defense**, not
served-byte verification. Real release must separately prove that the deployed
asset at this URL matches the trusted owner-accepted digest.

## Timing and lifecycle

- The simulation owns time and interval transitions. `photoWorkSlot` maps the
  existing 40-second jog/5-second jump cycle; its declared action must match
  the physical phase, and a slot mismatch yields unavailable video.
- Native clip duration and measured metadata must tile a complete slot by a
  whole number of full repeats. No truncation, speed change, fade, or fabricated
  hold is allowed. Reject 5.01s, 5.05s, 6s, and 4.95s for a 5.00s scissor slot.
  A tiny floating representation tolerance does not permit a decoded frame
  beyond the segment. The exact decoded-frame evidence belongs to the gate.
- The video source remains **visually hidden** and must not call `play()` until
  metadata duration, expected identity and clock-aligned seek are valid. It may
  preload metadata invisibly. Error/stale source/segment change/unmount removes
  the source and pauses any prior player.
- Runtime synchronization tolerance is at most one decoded video-frame
  interval (derived from reviewed FPS), with seeks tied to simulation-owned
  elapsed time. Reduced-motion preference holds the demonstration until an
  explicit session opt-in; reset/remount does not inherit approval or opt-in.
- No live photo source is shown in a production build, even with a query
  parameter or `VITE_PHOTO_PLAYER_PREVIEW` set. The public sprite UI remains
  visually unchanged until a future owner-approved release.

## Verification and remaining release gate

Each requirement has a unit/DOM/CI check or a named manual check in
`tasks.md`. The media registry stays empty at all times in this PR. A future
approval integration remains a **separate, owner-gated release change**:
authenticated Charles event, action-specific QA within the canonical authority,
byte-exact served media, revocation/cache invalidation and final exercise-form
review. Synthetic tests are not a substitute for these events.
