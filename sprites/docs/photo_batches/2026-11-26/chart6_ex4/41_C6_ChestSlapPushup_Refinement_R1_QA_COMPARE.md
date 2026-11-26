# Test 41 R1 targeted refinement — QA comparison

**Exercise:** 5BX Chart 6 Ex 4 CHEST-SLAP PUSH-UP  
**Source:** `41_C6_EX4_ChestSlapPushup_FourPhase_35mm_CANDIDATE.png`  
**Refined:** `41_C6_EX4_ChestSlapPushup_FourPhase_35mm_REFINED_R1.png`  
**Status:** **R1 PREFERRED over original as experimental still reference**; remains **conditional**, pending motion QA. Original retained.

## What changed, independently by panel

| Panel | Original | R1 | Verdict |
| --- | --- | --- | --- |
| A low planted | Correct low position on two palms/toes | Visually near-identical | **Preserved** |
| B explosive release | Both palms off track but torso high | Lower, more nearly-horizontal torso with **two hands visibly clear of track simultaneously** | **Improved** |
| C double chest slap | Two hands touch separate chest locations while airborne, but chest/head too elevated | Both hands STILL touch **separate left/right upper chest shirt spots** while completely away from track, arms continuous; head/chest notably lowered | **Improved** |
| D high planted | Correct two-palm straight high plank | Visually near-identical | **Preserved** |

### Strict rejection checks

- **B simultaneous clear palms:** yes, both visible hands hover above red track with no third planted wrist.
- **C correct specific chest-slap, not clap:** yes. Two hands stay apart on two portions of blue tank, not pressed palm to palm. Neither hand supports the ground. Static contact could read as shirt-touch or shirt-grab rather than a dynamic slap—animation must be brief.
- **Limbs:** two credible arms and two planted sneaker toes; forearms attach naturally, hands slightly overlap torso but no obvious extra forearm or phantom planted support. Exact individual finger count partially occluded at C.
- **Age/fidelity:** appears broadly the same junior-high boy. Slightly firm-looking shoulders are still a minor watch item; no marked body-builder growth, body hair or age drift.
- **Physically plausible range:** R1 lowers shoulders closer to normal high-plank elevation instead of near-gymnast hover; still a high-difficulty movement and not a recommendation of suitability for all 13–14-year-olds.
- **Registration:** coherent 2x2 photo static camera; start/recovery background and wardrobe stable.

### Quantitative full-image drift check

Per-panel ImageMagick normalized RMSE comparing original vs edit, 768×512 crops:
A **0.0198**, B **0.1148**, C **0.1019**, D **0.0253**. Difference distribution is concentrated in target B/C panels; A/D largely unchanged in appearance but not pixel-identical.

### Decision

**Prefer R1** for an animation trial and reference still; no second edit needed. Reject the eventual video if C becomes a hovering hold, palms merge into clapping, or a third hand appears.

**R1 SHA-256:** `fdb438f842923f9262107c97c65b70ffc786f8f09cda8578321b5a1df4020c16`  
**Exact edit prompt:** `41_C6_ChestSlapPushup_Refinement_R1_ExactPrompt.md`.  
**Imagegen edit calls:** one. No external writes or video.

