# Design: Workout Mixer photographic review prototype

Status: **Implementation design following Charles's approval (2026-11-25)**

## Surfaces

Keep the existing production Sprite Boy mixer untouched. Add an independent
**Photographic experiments** section immediately before the existing
**Take it apart** viewer. This avoids changing production rendering and hue
recolor logic.

The new section has:

- Chart and exercise selectors populated from the generated `data.json` chart
  inventory, not hard-coded 5BX content.
- A browser-local multi-file picker (PNG/JPEG/WebP/MP4/WebM). Files chosen while
  an exercise is selected belong to that exercise **only for this page session**.
- A media picker per exercise, in original selection order. Images and videos
  display inline at native aspect ratio with no server upload.
- A background selector (**track colors**, **light studio**, **dark stage**).
  Reusable cutouts float above these composited stage colors; opaque pictures
  and videos keep their embedded scenery.
- A transparency detection note for selected still images. This verifies the
  alpha channel is actually used; it does not certify clean edges or identity.
- Links to the current numbered-card archive and video QA as source material;
  links are not treated as publicly embeddable images.

## Client behavior

All state (exercise -> browser File object URLs) is local to the page.
Always build labels using `textContent` so imported filenames cannot inject
markup. Reject unsupported file types. `URL.revokeObjectURL` releases imported
media when the page unloads. The viewer never calls a file-upload endpoint.

The original cartoon viewer's `data.json` fetch and render loop remain
independent: an error in the photo UI should not break the workout mixer.
Photographic preview does **not** run the cartoon's HSV recolor algorithm.

For a still, draw its original image above CSS-scene backgrounds using
`object-fit:contain`; preserve alpha. Use a small, separate canvas only to
check whether any sampled pixel is nonopaque. When a file is opaque, explain
that switching the scene changes only the area *around* its embedded backdrop.
For video, preserve native playback controls/scrubbing and pause playback when
the selected item changes.

## Deliberate omissions

No pose synthesis, limb editing, identity repair, automatic art registration,
raw candidate image commits, photographic garment recoloring, or live deployment.
Transparent single frames are a viable first proof, but complete photographic
motion requires registered, consistently aligned per-frame cutouts later.

## Testing

- A Playwright browser fixture serves the actual demo HTML, minimal generated
  `data.json`, and local test files.
- Check chart/exercise selectors, empty/existing file views, PNG alpha status,
  opaque JPEG status, background switching, video playback control, HTML-safe
  filenames, and absence of file-upload requests.
- Re-run the existing 5BX sprite unit tests and a syntax check on new JS.
- If locally restored production sprite sheets are absent, do not claim the
  full generated site was rebuilt or deployed.
