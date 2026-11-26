# Test 24 — Chart 2 standard push-up: one 35mm photo card, QA

2026-11-26 UTC. **Assistant verdict: STRONG CONDITIONAL STILL CANDIDATE**, not production/video approved. No external publication, no Google Flow video. One built-in `image_gen` generation, no edits/retries.

## Source and exact reproduction

- Photographic identity reference: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` (character appearance and clothing only).
- Original 5BX Chart 2 Ex4 from `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`: front-lying, palms under shoulders, **straighten arms to lift body supported by only palms and toes; back straight**. This is **not** the Chart 1 kneeling push-up.
- Verbatim generated prompt and image reference roles: `24_C2_EX4_StandardPushup_ExactPrompt.md` (the `text` code block, used without modification).
- Output: `24_C2_EX4_StandardPushup_FourPhase_35mm_CANDIDATE.png`, **1536×1024**, SHA-256 `d4e5883abc6ecc92f4b90853e95e243096dae4be9a37edc42e62cfa9c2ce4b5b`.

## Four-panel anatomical QA

| Tile | Intended 5BX phase | Observed result | Verdict |
|---|---|---|---|
| A upper left | Starting near-low press from prone | Both straight legs extended back; toes appear grounded; chest low but clear of track, elbows flexed, two palms beneath shoulders; knees off track. Face and one black wristband present. | PASS candidate |
| B upper right | Full high plank | Two palms, both toe tips grounded; elbows extended; shoulders, hips, knees and ankles form approximately one straight incline; knees lifted, no sagging/piking. Both hands visible. | PASS candidate |
| C lower left | Controlled lowered push-up | Near elbow bends substantially, chest a few inches above track, straight torso/hip/knee line and feet/toes planted. Far palm remains visible beside chest but far elbow is partly occluded behind the torso, making its exact flexion angle unprovable. | CONDITIONAL |
| D lower right | Return to same high plank | Correct return to same hand/toe positions and extended elbows; image very close to B in outfit, face, body scale and background. | PASS candidate |

**Anatomical count:** Exactly two visible natural forearms/hands and two legs/shoes in B/D. At low C the far elbow is partly hidden but there is **no obvious spider third arm, duplicate hand, detached limb, inverted shoe, extra knee, or changed wristband side**. Distinct fingers are too small to certify exactly five on each hand; no obvious hand deformity. Do not claim machine-verified finger counts.

**Critical mechanics:** Unlike the kneeling variant, all panels show knees **off** ground and feet supported on toes. Full B/D plank appears straight and load-bearing. Low C holds a plausible adolescent range of motion without extreme flex or joint stretch. Static near-lateral camera facilitates seeing the straight line.

## Identity and generation limitations

- Consistent pale/neutral untanned skin, dark messy but not overlarge hair, blue tank, charcoal shorts, gray/yellow shoes, dark socks, black wristband. Photorealistic 35mm track/grass/trees, no text/artifact border apart from narrow white panel separators. Normal early-teen non-bodybuilder shape. Shirt and hair have small fabric/strand variations, no major inter-tile age drift apparent.
- Model **did not achieve the requested 25–30° angle**: it reverted close to exact side profile. Far shoulder, upper arm and bent elbow consequently overlap in low C. A slight oblique may improve the pedagogical silhouette but also risks broken arm geometry; do not automatically assume it is better.
- In B/D the fingers appear resting on flat palms; C far arm movement is occluded rather than independently verifiable. No motion continuity beyond still arrangement has been verified.
- Shoes overlap at feet due side view; both footwear silhouettes remain inside each tile. Background texture changes subtly across cards, so don't assume pixel-perfect registration for direct video interpolation.

## Decision and recommended next step

Retain this as **Test 24 / strong conditional**. It is substantially more credible as Chart 2 full push-up stills than many prior knee-push-up tries, but **do not declare exercise-form approval** while far elbow C remains obscured and no actual video has been checked. If testing Flow, use a dedicated high-resolution starting **high-plank** frame generated with this card and approved identity v2; supply **one start frame** instead of trying to force all four tiles into a three-input Flow sequence. Fix camera and verify hands/toes don't slide, elbows move symmetrically, body line stays straight, and boy does not grow muscles or get older. Log the exact Flow prompt and inspect actual downloaded frames before accepting.
