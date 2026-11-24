# Historical 5BX animation failure brief (not a proposed fix)

**Source:** [For Chief of Staff — 5BX mistakes with no build yet](https://docs.google.com/document/d/1uKSIYUezociFfpmhmdz-_6sAcg4M6UFqpiqrWBiTfZY/edit), user-owned Drive document, preserved as historical source on 2026-11-24. This note requested a **read-only** repo search and warned against modifying `video/design/NOTES.md`; its dates/status refer to its earlier research time, not current implementation state. Where it says “not built,” verify against current repo before acting.

# For Chief of Staff — replace the earlier note

The earlier note listed fixes. Ignore it. This one is only the mistakes, what we saw, and the causes we still have no build for. Please assign Repo Scout to search the GitHub repos for anything that already speaks to these open causes. Do not invent a solution. Do not push. Do not edit `5BX` `video/design/NOTES.md`.

Repos: `cwarloe/lessons-learned`, `cwarloe/5BX`, `cwarloe/5bx-video-game`.

## Still no build

### 1. We tried to get movement by making a new body

**Mistake.** To go from the white booklet figures to a moving picture, we built a second app: a code-drawn stick figure, one skeleton, poses stored as angles.

**What we saw.** It was rejected. One body, and it was the wrong person. Before that, a new generated drawing for each pose made a different person every frame. The booklet also changes camera in the middle of a move, so copying each booklet drawing in order would still jump.

**Cause.** Likeness and consistency were treated as the same problem. A shared skeleton keeps proportions. It does not keep the drawing. A new image per pose keeps neither, because each image is a fresh guess. Nothing we built takes the figure we already chose and changes only the pose.

**Not built.** A way to move the kept figure — the booklet figure, or the grey-tank / orange-shorts one — from pose data, without redrawing it and without replacing it.

### 2. We called it correct because the numbers passed

**Mistake.** Booklet sentences were turned into angle checks. The check run printed ALL PASS, and that was treated as done.

**What we saw.** Shoulders left the torso. "Arms up" was overhead in the math and cut off the top of the canvas, so on screen it looked like arms at the sides. Hands went through the floor by a few pixels and the check still passed. A "straight arm" was still bent. The check looked at the keyframe, not the in-between the eye sees.

**Cause.** The test read pose numbers, not pixels. The draw scale and the floor anchor could hide a right pose or show a broken one. Side view and front view do not share a zero: on the side, 0° is forward; on the front, 0° is down. Passing was defined before anyone looked.

**Not built.** A check that fails when the drawn figure is wrong — off the canvas, through the floor, a limb off the body — on a contact sheet of the character we are keeping, seen by a person. We know the test has to see the picture. That test does not exist for that character.

### 3. We stored the booklet moves on the wrong body

**Mistake.** The form notes were solved as joint angles on the stick figure: run height, toe touches from the front, knee push-ups, sit-up arms, one straight leg on the back raise, the scissor jump in the air.

**What we saw.** The angles could be tuned until the checks passed, and the picture was still the wrong person. The sprite game in `cwarloe/5bx-video-game` names those beats and has Chart 1 frames, but its levels are only Chart 1 (D−, D, D+), and the code says charts 4–6 jumps are not sprite-ready and fall back to the scissor. Naming the beat is not showing it. Those sprites have not been compared to the booklet frame by frame.

**Cause.** The review described the booklet. We answered in another character's coordinates. Pose data without the right body does not meet the review.

**Not built.** These moves, on the kept character, for the chart that asks for them, looked at on a contact sheet:

- Feet about 4 inches up on charts 1–3. Knees waist-high on charts 4–6.

- Chart 3 and up, toe touch from the front: outside the left foot, between the feet, outside the right foot.

- Knee push-up with knees and chest down and hands under the shoulders.

- Chart 1 sit-up with arms at the sides and legs straight.

- Chart 1 back raise of one straight leg.

- Scissor jump in the air, opposite arm and opposite leg.

We do not have a fix for these. We only know the pictures we made were not them.

## Known, not an unbuilt feature

### 4. We saved the wrong game

**Mistake.** Asked to keep the original 5BX as what opens, and to save the arcade, the stick figure was the thing that got archived.

**What we saw.** The arcade you meant is the one already in `cwarloe/5bx-video-game`.

**Cause.** Two builds existed. The newest one in the sandbox was assumed to be the arcade.

A copy of that repo is saved. That does not build the missing pictures.

### 5. We wrote the lesson into your notes

**Mistake.** "Capture that" was done by editing `video/design/NOTES.md`.

**What we saw.** You wanted that file put back.

**Cause.** A lesson for the next attempt was treated as an edit to your design log.

Don't do that again. Not something to build.

## Already fixed — leave these out of the search

Blank screen (the page looked for a `#boot` element that was gone). Unstyled page (a shortened CSS file stayed in the service-worker cache). Preview link that dropped the host prefix. Those have a fix.
