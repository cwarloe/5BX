# 29H — pose-locked edit from original “almost there”

Generator: built-in `image_gen.imagegen`, **ONE** attempted edit. `transparent_background: false`.

Reference order:

1. `artifacts/parallel_tests/v_pushup_realistic/02_almost_there.png` — the **TARGET PHOTO FOR AN EDIT**, preserve all pose geometry and camera coordinates.
2. `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` — **APPEARANCE ONLY**.

## Exact submitted prompt

```text
Use case: precise-image-edit, photorealistic-natural.
Edit IMAGE 1 itself rather than composing a new pike pose. It is the precise spatial, body-pose, camera, and setting TARGET. Do a minimal character-identity and anatomy-softening correction with reference IMAGE 2 supplying the identity, age, hair shape, face/ears/nose, skin tone and clothing colors ONLY. All geometry from IMAGE 1 has absolute priority over any pose in IMAGE 2.

Critical pixel-composition lock: retain the same 35mm side-oblique camera view, same grass/trees, red track and white lane marks, exact grounded locations of LEFT and RIGHT shoe forefoot, LEFT and RIGHT full palm/wrist contacts, head/forehead location, pelvis apex, shoulder endpoints, and knee contour. Keep the same full silhouette of the triangular inverted V and the boy's ordinary original arm length, torso length, hip/seat size, leg length, and entire body footprint. In particular preserve the original hand-to-head spatial relation: forehead naturally hovers just above red track and is behind the planted hands (toward the shoes), without touching his palms. Do not lower his head further; do not raise his hips or move his shoes to compensate. Keep the near arm's current gentle natural elbow line and the far arm's existing natural elbow line. Do NOT add any elbow flexion, rotate an elbow out, invent a hinge, exaggerate reach, hyperextend a joint, or alter the shoulder-to-elbow-to-wrist chains. Both arms must remain one anatomically possible regular adolescent's arms, naturally braced on open flat palms.

Make only the minimum photographic refinements needed for IMAGE 1 to depict the exact boy in IMAGE 2: pale Caucasian 13–14-year-old middle-schooler, dark brown naturally messy short hair with modest volume (not curly/fluffy, not styled high), small button-ish nose and unchanged ears, smooth youthful face, modest regular undeveloped shoulders, upper arms, thighs and calves, no pronounced deltoid/biceps/triceps outlines, no V-taper or six-pack, neither skinny nor thick. Keep normal average waist and soft youth proportions. Clothing should be his blue athletic tank and charcoal-gray running shorts; gray/yellow running sneakers, dark short socks and black wristband. No extra body hair or facial hair. Retain natural overcast lighting, photographic textile textures, and authentic 35mm documentary appearance. Never age him up or give an adult athlete's musculature.

Output ONE polished original-frame edit at high resolution, not a contact sheet, not an altered exercise pose. If appearance adjustments conflict with the original pose silhouette, preserve original pose silhouette, every limb contour, contact point and elbow angle over appearance. No text, captions, props or additional people.
```
