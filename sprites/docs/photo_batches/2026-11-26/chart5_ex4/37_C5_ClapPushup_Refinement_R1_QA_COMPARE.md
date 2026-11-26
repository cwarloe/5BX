# Test 37 R1 targeted refinement — QA comparison

**Exercise:** 5BX Chart 5 Ex 4 CLAP PUSH-UP  
**Source:** `37_C5_EX4_ClapPushup_FourPhase_35mm_CANDIDATE.png`  
**Refined:** `37_C5_EX4_ClapPushup_FourPhase_35mm_REFINED_R1.png`  
**Status:** **R1 PREFERRED over original as experimental still reference**; remains **conditional**, pending motion QA. Original is retained.

## What changed, independently by panel

| Panel | Original | R1 | Verdict |
| --- | --- | --- | --- |
| A low planted | Good low body alignment, both palms grounded | Visually near-identical | **Preserved** |
| B simultaneous release | Both hands off track, but torso/head climbed steeply | Body substantially LOWER and nearer horizontal while both hands still show air gap under fingertips; no planted extra arm | **Improved** |
| C clap | Palms meet midair, but shoulders/trunk visibly high | Lower, flatter trunk; palms still MEET EACH OTHER near sternum and are **both unsupported by track**; elbows connect to shoulders | **Improved**; hand overlap means exact count of all 10 fingers is not verifiable |
| D high planted | Good straight-arm support | Visually near-identical | **Preserved** |

### Strict rejection checks

- **Both hands airborne in B:** yes. Red track clearly visible below each hand.
- **Both hands airborne and actual palm-to-palm clap in C:** yes, pair of hands joined away from track, without a floor-contacting third arm. This may visually resemble a held prayer gesture if an animation overdwells; require quick transient clap.
- **Full anatomy:** no obvious extra arms/forearms, knees remain up, footwear toes remain on track, no extreme hyperextension or body lengthening. Natural slim-soft teenage arms still a little athletic, but no sudden overdeveloped muscle.
- **Continuity:** all four show same blue tank, charcoal shorts, shoes, face/hair and 25–30° static track camera. A and D extremely similar, not pixel-identical.
- **Safety/physics:** C no longer requires the unusually high suspended chest. Hands lift momentarily; should still be demonstrated only as instant event, not a static exercise hold.

### Quantitative full-image drift check (diagnostic, not anatomy proof)

Per-panel ImageMagick normalized RMSE comparing original vs edit, 768×512 crops:
A **0.0226**, B **0.1113**, C **0.1114**, D **0.0250**. Changes concentrate in intended B/C motion panels, while A/D are comparatively preserved.

### Decision

**Prefer R1.** Key semantics survive, and hovering is reduced markedly. Not yet an approved instructional video; test animation only with close attention to C fingers, timing and unsupported torso.

**R1 SHA-256:** `43a4817ad1085acd7a7d67c8d0c969b33922fa71c4284b4ad42e7a7670b391eb`  
**Exact edit prompt:** `37_C5_ClapPushup_Refinement_R1_ExactPrompt.md`.  
**Imagegen edit calls:** one. No external writes or video.

