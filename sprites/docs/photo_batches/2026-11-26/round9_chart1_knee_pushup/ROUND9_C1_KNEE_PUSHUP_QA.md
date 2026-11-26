# 5BX Chart 1 Ex4 — high-fidelity kneeling-push-up experiment 43A–43D

Date: 2026-11-26 UTC. Separate task stream (no shared review-index mutation). All prompts preserved verbatim in sibling files. These are TEST assets; no human form approval or final animation validation.

## Inputs

- **Identity and exact UP-pose authority:** `artifacts/parallel_batch_20261126/knee_pushup/C1_E4_UP_FULLRES_V2_IDENTITY_CORRECTED_REVIEW.png` (1672×941, single 35mm-style image).
- **Motion/phase authority:** `artifacts/parallel_batch_20261126/knee_pushup/C1_E4_KNEELING_4PHASE_V2_REVIEW.png` (1774×887 four-panel sequence).
- Both are prior repo/project images, not a new 1959 film frame. The 1959 Chart 1 knee push-up is intended as form provenance, not necessarily the face/wardrobe authority.

## Outputs and QA

| ID | Output | Result | Specific finding |
| --- | --- | --- | --- |
| **43A** | `43A_C1_KneePushup_4Phase_IdentityAnchored_PROVISIONAL.png` (1774×887) | **PROVISIONAL** | Four full-body panels UP → MID → LOW → UP, consistent character within sheet; hands and knees planted approximately, lower legs lifted, back–hips–knees fairly straight and natural, near elbow visibly bends across sequence. Far elbow and far palm are partly occluded at 90° side view, which is preferable to manufacturing a spider arm. Exact contact point registration and identity against master still need automated check. |
| **43B** | `43B_C1_KneePushup_LOW_FullRes_DIAGNOSTIC.png` (1672×941) | **ANATOMY CONDITIONAL, IDENTITY HOLD** | Single 16:9 low pose maintains bent near arm and a plausible support base, but hair volume, skin warmth and upper-arm fullness drift upward versus approved UP master. Do not promote as video end anchor until identity/color check. |
| **43C** | `43C_C1_KneePushup_MID_FullRes_REJECT.png` (1672×941) | **REJECT** | Mid source generated a visible near elbow close to 90° at full resolution despite 50–65° flexion instruction. It is too similar to LOW to define a smooth movement midpoint. |
| **43D** | `43D_C1_KneePushup_MID_ElbowAngleRetry_REJECT.png` (1672×941) | **REJECT** | Explicit correction to 140–145° *included* elbow angle also returned a near-90° visual elbow. Some shoulder/hip raise happened, but failure to achieve separated mid pose persists. Avoid cycling this prompt further without stronger spatial control. |

## Safety/body and video gates

- **Master (UP) photograph** still best single-frame Flow image-to-video start; user previously reported one UP frame works better than supplying inconsistent middle/last frames.
- Treat **43A** as a visual phase traveler, not four source images simultaneously fed to a video generator.
- Dynamic video prompt should describe *bend elbows gradually, lower shoulder–hip–knee as one rigid line while knees/palms stay fixed, return to up, no camera movement, only two arms*. Check resulting actual frames independently for location of palms/knees, proximal elbow angles, age/face and outfit.
- **No body mechanics substitutions:** do not allow toe-supported standard push-up, hips perched up, third arm, extra hand, hyperextension, or adult-defined arms.

## Process lesson

Image generation may satisfy a phrase such as *midway down* visually yet ignore a measured **elbow included angle** (140° requested, ~90–100° visually realized). Frame count alone does not prove temporal phase separation. Use joint-angle and ground-contact QA before accepting a generated still as a video waypoint. Generating an entire card together improves face and garment consistency but does not guarantee identical pixel coordinates or full-resolution quality for each crop.

## Next production recommendation

Keep 43A as a provisional sheet; use the **already identity-corrected 1672×941 UP master** as the one image-to-video input. Save 43B only as a pose/quality diagnostic. Evaluate actual video mid-frame after generation instead of passing rejected 43C or 43D to the model. If an aligned high-res three-anchor sequence becomes essential, collect a real-body 90° filmed reference and enforce silhouette/joint coordinates before further generation.
