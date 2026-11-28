# Video finishing: white-background clip → looping gym video

Turns a white-background exercise clip of Mark (from Flow or Grok) into a looping review MP4 on the Charles Fit Club
gym plate, at the same proportion for every exercise. Built and tested on the six Chart 1 white clips, 2026-11-27.

- **Settings and per-clip data:** [`config.json`](config.json). Every number in it was measured, and each says how.
  Change a value there, never in the code.
- **Tool:** [`video_finish.py`](video_finish.py). Tests: `python3 -m unittest discover -s tools/video_finish/tests`.
- **Needs:** `pip install -r tools/video_finish/requirements.txt` and ffmpeg. The first cut-out downloads the
  `u2net_human_seg` model (~176 MB).

## The sequence

1. **Get the source.** Download the clip by its `drive_id` (in `config.json`) to `work/<clip>/src.mp4`.
   Use the original white Flow clip, not a review edit (edits are re-encoded and may already be trimmed).
2. **Measure Mark** (new clips only): `python3 video_finish.py measure --clip <clip> --src work/<clip>/src.mp4`.
   Record `body_length_px` and `body_kind` (`standing` = head-to-feet height with arms not raised;
   `lying` = head-to-feet length lying straight). If he is never straight, estimate from the shin:
   shin length / 0.194, then check it against the matching figure in the proportion reference (the knee push-up
   needed that correction). Write how you measured it in `measured`.
3. **Find the loop:** `python3 video_finish.py loops --clip <clip> --src work/<clip>/src.mp4 --out work/<clip>`.
   It prints the best cut and a ready `"loop"` entry for `config.json`, and writes white test loops
   (`white_loop_cut.mp4`, `white_loop_pingpong.mp4`). Watch both and pick `cut` or `pingpong`.
4. **Composite on the gym:** `python3 video_finish.py composite --clip <clip> --src work/<clip>/src.mp4 --out out/<clip>.mp4`,
   or every clip at once with `python3 video_finish.py all --work work --out out` (two at a time).
   Each MP4 gets a `.json` report next to it.
5. **Check the report before anyone watches:** `head_visible` must be true and `visible_cut_lines` empty.
   Then a person watches the loop joint and the form. A passing report is not approval; Charles accepts each final video.

## Rules (with the reason for each)

| Rule | Value | Why |
|---|---|---|
| Standing height | 50% of frame height | Charles's proportion reference (Drive `1bN2nxYXNHUsX0zWDCo3nK2FvME5kNWOC`): standing boy 0.501. "I don't want them to be any bigger than that." |
| Lying length | 58% of frame height | Same reference: prone boy at the same depth is 0.581 long (feet and head extend the line) |
| Contact line | 83.6% down the frame | Feet (or body on the floor) of the reference figures at the front of the mat |
| Position | centred, one depth for every exercise | Front and centre; same depth means the same scale rule applies to every move |
| One transform per clip | fixed scale and offset | Tracking per frame makes Mark slide around the mat |
| Head and hair | always inside the frame | Hands may leave the top of the screen; the head may not. The report checks every frame |
| No mid-air cut lines | source edges stay off-canvas | If Mark touches an edge of the source frame and that edge lands inside the canvas, the body ends at a straight line in mid-air |
| Cut-out | person-segmentation model (`u2net_human_seg`) | Brightness keying fails: grey shoes (~220) match the studio white (216-230), so it keeps the floor shadow and loses the shoes |
| Edge colour | remove the studio white from part-transparent edge pixels | Otherwise Mark has a white halo on the dark gym |
| Loop joint | under 1.5x a normal frame step = smooth; 1.5-3 slight hitch; over 3 visible | Measured; matches what you see |
| Loop score | compares 5 frames each side of the joint | Matching one frame lets a loop join poses that are moving in opposite directions |
| Whole movement in the loop | cycle must reach half the clip's largest pose change | Otherwise the finder picks a short still stretch |
| Parallel jobs | 2 | Six at once ran out of memory (7 GB) |

## Mistakes already made (do not repeat)

- **Cross-fading the loop joint.** Blending the end into the start made a ghosted double head when the head
  turned slightly. Use a clean cut at the best-matching frame, or ping-pong.
- **One repetition is not enough** for a clean loop (toe touch, sit-up). Ask for more in the render (below).
- **Alternating exercises** (leg raise): the shortest good loop held one leg only. Set `min_cycle_seconds` long
  enough for both sides.
- **Frames after a scene change** (the sit-up source flips him round at ~frame 104): set `usable_until_frame`.
- **Hair detection fooled by the wristband** (both dark): the check uses the largest dark-brown area.
- **Too big.** 79% of frame height looked dramatic but broke proportion; the reference caps it at 50%.

## What to ask for in a render (so finishing just works)

- **2-3 full repetitions**, and **start and end in the same resting pose, held still for half a second**:
  that hold is where the loop joins.
- **Full body with empty space on every side, including above raised hands** (toe touch arms-up, scissor hops).
  Anything cropped by the frame shows as a straight cut once Mark is placed in the gym.
- **Camera far enough back that a floor move fits with room to spare.** Floor moves came back 1.35-3x too
  large (knee push-up worst); shrinking works but loses sharpness.
- **Plain white background, one person, fixed camera**, no zoom or pan.

## Chart 1 status (2026-11-27)

See each clip's `notes` in `config.json`. In short: run loops smoothly; toe touch, knee push-up and scissor have a
slight hitch; leg raise has a slight hitch with both legs in each loop; sit-up uses ping-pong. The toe touch needs a
re-render with room above the hands; the scissor clip is a bounce, not the split-leg exchange.
