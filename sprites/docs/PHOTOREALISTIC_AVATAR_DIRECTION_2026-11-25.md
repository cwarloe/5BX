# 5BX photographic avatar: approved direction and release status

**Decision owner:** Charles Warloe. **Direction approved:** 2026-11-25.

## Read this before generating images, editing a sprite, or publishing a video

**The creative target is now a realistic, photographic middle-school boy (roughly
12–14 years old). The original cyan-tank/red-shorts cartoon Sprite Boy is legacy
prototype art, not the requested style for new production.** Keep the existing
cartoon implementation functioning as an engineering baseline, but do not treat
its appearance or colors as the target for new exercise cards.

The technical workbench and Mixer currently use cartoon layers for their
registered exercise cycles. The newer photographic identity, position cards,
and generated video attempts remain experimental. **An approved visual direction
is not approval of every image, exercise form, or video.** Publishing source
code does not automatically replace the live Cloudflare site's character.

## Character and camera lock

- Natural-looking American middle-schooler, not an elementary-school child
  and not a mature high-school athlete. Normal proportional waist and chest;
  arms, thighs, and seat are soft, not muscular or artificially skinny.
- Fair/pale untanned skin; smooth face, no facial, chest, underarm, or visible
  leg hair; small natural button-ish nose and stable ear size.
- Dark, slightly messy, modest-volume hair. No exaggerated spiky/fluffy mass,
  tight sculpted curls, or too-close skin fade. Eyes may be naturally open,
  looking toward the movement rather than at the camera.
- Start with a genuine photo-like **35 mm documentary photograph** and a
  slightly posterized but still realistic partner view when testing geometry.
  Posterization is an optional later output treatment, not the base anatomy.
- Preserve identity, stature, body proportions, footwear, camera scale,
  and viewpoint across the **entire movement card**. Generate a complete
  three-/four-pose card together to reduce age and background drift.
- A slight three-quarter angle (often around 30 degrees) usually reveals
  mechanics better than strict side view. Toe-touch tests may require a more
  frontal angle. Use the original 1959 RCAF 5BX film/booklet and successful
  reference cards as the ground truth for body position.
- Do not lengthen arms, legs, or torso to force the theoretical maximum range
  of motion; accept anatomically plausible partial range. Avoid ballet-pointed
  toes in jumps, mature muscles, duplicate limbs, bent backs in knee push-ups,
  and camera-near/far leg swaps. For a runner facing right with near leg trailing,
  that thigh stays visibly in front of the far-side leading thigh at the hip.
- Clothing colors are flexible test variables. Favor readable, contrasting
  light shirts and somewhat darker shorts as recent trials did. Preserve
  the same outfit *within* a movement card and label color experiments.

## Workflow and what counts as a good take

1. Define the pose from the 1959 instructional film, the 5BX booklet, or a
   Charles-approved photographic reference; write the actual prompt down.
2. Generate the entire movement card at photo quality, with a locked identity
   and perspective; only then test slightly more posterized/illustrated views.
3. Verify body mechanics (support points, hips and knees, near/far limb
   overlap, hand count, plausible flexibility) and identity continuity.
4. Label each result `REVIEW`, `CANDIDATE`, `PARTIAL`, or `REJECT` with a brief
   reason. Neither a technically correct cutout nor a plausible Grok/Flow
   animation proves exercise-form accuracy or production approval.
5. Upload reviewable **individual MP4s** into the named Google Drive review
   folder, not just contact JPGs or a ZIP. Include date, movement, and QA
   status in the filename. Keep experimental media private unless Charles
   explicitly authorizes public release.
6. Only after movement-level signoff should frames become registered, anchored
   transparent production strips and replace the legacy cartoon in the video.

## Where to review media on a phone

- **[Start here: photographic video review — 2026-11-25](https://drive.google.com/drive/folders/1W9dWViCZENv2UvoZ_k0EME8h9xRUWNKY)**
  has the four original playable photographic MP4 tests, clearly named by
  assistant QA status. `01_REVIEW` is the strongest kneeling-push-up candidate;
  the other three include one rejected ghosting take and two partial sit-ups.
- [Experimental photographic cards and prompts](https://drive.google.com/drive/folders/1YBinWrduQDdMDyCKTI_7FyyxkpFP1Cfo)
  remain owner-only; the [54-card text-only review index](PHOTO_EXPERIMENT_REVIEW_2026-11-25.md)
  records why takes passed, failed or need another attempt.
- [Existing contact JPGs and video QA notes](https://drive.google.com/drive/folders/1hFNKKoRaDi2xrhu0TUA0-JUZat3wqaVK)
  are secondary references, not substitutes for the playable videos.

## Publication and version truth

| Component | Status as of 2026-11-25 |
| --- | --- |
| Photographic creative direction | **Approved as the target** |
| 54 photo cards, four video tests | **Private experimental review assets**; statuses not human form signoff |
| Standing and kneeling cutouts | True-alpha **candidates**, alignment and edge QA outstanding |
| Existing cartoon strips and Mixer | Operational **legacy prototype** for test/playback; not the target appearance |
| Fully registered photographic movement cycles | **Not yet complete** |
| Live `workout-mixer.pages.dev` | Must be checked/deployed separately; merging source docs does not publish a new site |

See [the older pose-fix lessons](POSE_FIX_LESSONS.md) for geometry and compositing
techniques, and [the current photographic test review](PHOTO_EXPERIMENT_REVIEW_2026-11-25.md)
for numbered evidence. These are complementary, not competing character
standards.
