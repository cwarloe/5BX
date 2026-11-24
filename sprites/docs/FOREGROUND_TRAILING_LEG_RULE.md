# Conditional foreground-trailing-leg rule

**Recorded:** 2026-11-24  
**User-accepted visual reference:** [Four-pose running card](https://drive.google.com/file/d/1lSzvp-SjsNDOClhmQquGk7tqUAmb1HAh/view) (Drive file ID `1lSzvp-SjsNDOClhmQquGk7tqUAmb1HAh`).  
**Status:** Charles confirmed the **near/far depth arrangement for running**. This is *not* approval of scissor-jump form, a full alternating sequence, an avatar replacement, or a production sprite asset. The image is reference art held in Drive under [Sprite Art 5BX Workout](https://drive.google.com/drive/folders/1x7ZrBMan7-jSXgYnZeOZzmEc_of0sRzE), not committed binary art.

## What the approved example proves

The figure faces **screen-right**. The leg extending **back toward screen-left** is the **foreground / camera-near / trailing leg**. Its upper thigh emerges from the viewer-facing hip and **overlaps in front of the screen-right-leading leg at the shorts/crotch intersection**. The leading leg extends from the camera-far hip and is partially occluded near the pelvis.

**Crucial correction:** screen-left versus screen-right (or behind/ahead along the running direction) is not the same as camera-near versus camera-far. Never assume the screen-right/leading leg is automatically the foreground leg. Do not infer the anatomical left/right identity from screen position alone.

The earlier failed cards repeatedly drew the screen-right-leading leg as the foreground limb regardless of the required pose. The approved running card resolves **this specific depth relationship**; it does not prove stable physical-leg identity between frames.

## Portable prompt insert — use only for applicable poses

Append the following to the normal exercise-form and canonical-character prompts when the *source/reference pose* calls for the **near leg to trail**:

> **Camera and depth lock:** One consistent three-quarter side camera; subject faces screen-right. The **camera-near (foreground) leg is the TRAILING leg**, extending back toward **screen-left**. The **camera-far (background) leg is the LEADING leg**, extending forward toward **screen-right**. At the pelvis, draw the near trailing thigh **in front of** the far leading thigh: its contour emerges from the viewer-facing hip and visibly occludes the leading thigh/shorts seam. Draw the far leading leg emerging from the opposite hip, partly hidden at the crossing. Keep exactly two correctly articulated legs, two shoes, complete feet and a stable shorts/hip topology. Do not put the forward/screen-right leg in front merely because it leads the motion. Preserve the same camera angle, proportions, character and garment colors across poses; use the supplied approved four-pose running card as the depth example, not as an automatic motion/form template. Far-side shading may be a little darker for legibility.

**When the person faces screen-left:** reverse only the screen-direction words: near trailing leg extends screen-right; far leading leg screen-left. **Do not reverse the near-over-far occlusion rule.**

**When the source pose instead has the near leg leading:** swap the *role* assignment deliberately and use the actual source occlusion—not this trailing-leg insert. The reference determines near/far, not a blanket rule across every pose or exercise.

For the canonical Sprite Boy, retain his existing appearance prompt (cyan-blue sleeveless tank, red shorts, white socks, blue sneakers, warm tan skin, spiky black hair). The approved running reference uses a different curly-haired illustrated person, so **use it to teach hip overlap, not to overwrite the canonical character**. Keep form and amplitude grounded in the original 5BX booklet/film/data; the running illustration must not elongate a gentle Chart 1 scissor jump into a sprint.

## QA gate before extending to another exercise

1. **Determine pose:** from an authoritative reference, label camera-facing direction, which physically tracked leg is near, and which leg leads/trails *at this instant*. If the source is occluded, mark it unknown; do not guess.
2. **Inspect hip crossing:** the specified near trailing thigh must visibly overlap the far leading thigh at the shorts/crotch. A screen-left leg located *behind* at the pelvis is a **failure**, even if its foot extends backward correctly.
3. **Inspect feet and anatomy:** two separately traceable legs with knees/ankles/shoes, no fused or extra limbs, no impossible hip attachment, both feet inside the crop. Hold a fixed view.
4. **Inspect multiple frames:** preserve *physical* left/right limb identity as positions exchange; do not recolor “the left-looking shoe” between poses. A marker must attach to a source limb, not screen position.
5. **Separate approvals:** (a) depth/occlusion silhouette; (b) anatomical identity over time; (c) exercise form/tempo; (d) smooth loop/interpolation. Passing (a) does **not** imply (b)–(d).

**Workflow:** make one accurately occluded pose, have Charles accept its depth, then make its inverse pose if the exercise alternates. Only after each endpoint passes should a sequence or loop be attempted. Reject attractive five-frame cards that repeat the same lead/trail arrangement; do not obscure a defect with crossfade.

## Implementation scope

This page is a **reusable prompt/QA specification**, not a code change. Existing pipeline shading rule `R-NEAR-FAR` differentiates sides by color but does not enforce thigh-over-thigh hip occlusion. If automated prompt injection is later implemented, gate it on explicit per-pose `near_leg_role = trailing` (and facing direction/occlusion evidence), rather than blindly applying it to all exercises. No renderer, exercise data, released sheet, or production QC rule is changed by this documentation.
