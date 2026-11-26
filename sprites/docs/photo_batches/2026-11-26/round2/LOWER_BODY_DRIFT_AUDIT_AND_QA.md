# 5BX lower-body muscle drift audit — 2026-11-26

## Scope and identity baseline

Compared five existing photographic exercise cards against the approved identity/anatomy reference `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`. The invariant is a normally proportioned **13–14-year-old middle-school boy** with smooth, untrained upper thighs and calves, no muscle striation, no enlarged seat, and no alteration to waist/chest or leg length. He is not to be made thinner, taller, younger, more tanned or more athletic.

## Visual audit

| Card | Lower-body observation vs. approved identity | Decision |
|---|---|---|
| `33_C4_SemiSquatJump_FourPhase_35mm_CANDIDATE.png` | Knees, thighs and seat are ordinarily soft; quad contours are largely hidden by shorts and natural pose lighting. | **Keep as-is.** |
| `34_C4_HighKneeStationaryRun_V3_CLEAN_CANDIDATE.png` | Most conspicuous upper-thigh exposure among these cards. The raised thigh in panel A, and exposed planted thigh in C, read a little firmer/more athletic than master. Some impression comes from high-knee pose and daylight. | **One-variable local edit trial, 34R**, limited to softening skin/muscle shadow. Preserve original. |
| `38_C5_SemiSpreadEagleJump_FourPhase_35mm_CANDIDATE.png` | Thighs remain modest; any maturity drift is predominantly **arms/shoulders**, not legs. | **Keep lower body as-is.** |
| `35R_C5_EX2_TwistSitup_CLEAN_35mm_CANDIDATE.png` | Extended and flexed legs read as soft, proportionate middle-school anatomy; shorts and bent-knee folds plausible. | **Keep as-is**; preserve separate diagnostic for limb tracking. |
| `39_C6_EX2_PikeSitup_FourPhase_35mm_CANDIDATE.png` | Long extended legs are smooth; no visible thigh muscle striations. Pose creates leg-raise foreshortening, not true quadriceps enlargement. | **Keep as-is.** |

The audit separated **muscle tone/contrast** from **leg circumference or perspective**. The existing master is the body-size authority; the exercise pose is the limb-geometry authority. Do not globally apply a “smaller thighs” or “slimmer boy” prompt. That would undermine the already good knee and ankle geometry.

## Controlled 34R edit

**Source (unchanged):** `../chart4_run/34_C4_HighKneeStationaryRun_V3_CLEAN_CANDIDATE.png`

**Provisional replacement:** `34R_C4_HighKneeStationaryRun_SOFTER_THIGHS_PROVISIONAL.png`

**Exact prompt:** `34R_C4_HighKnee_SofterThighs_ExactEditPrompt.md`

Edited the four-panel photographic card using the approved v2 identity reference. Only requested 10–15% softer local quadriceps/tendon shadow rendering while explicitly preserving outer leg/seat/waist silhouettes and all action landmarks.

### Before/after QA

- **Upper thigh:** At 2× inspection of panel A, the new thigh shading is visibly a little more even/soft; no obvious lean-muscle incision is introduced.
- **Leg silhouette and proportions:** Raised knee, exposed thigh circumference, hip/shorts seam, calf length and shoe positions appear unchanged at card-view and 2× crop. No artificial leg thinning or extra bulk.
- **Sequence:** Four panels and original temporal order survive. A/C still visually depict alternating raised-knee frames; original arm positions preserved. This is a *cosmetic edit*, not a new confirmation of the 5BX motion mechanics.
- **Character:** Same broad identity, apparent middle-school age and fair skin; same face, hair, blue shirt, gray shorts, dark socks, shoes, wristband and school track. Background likewise preserved.
- **Quantitative whole-image sanity check:** ImageMagick RMSE of after vs source is `1928.69/65535 = 2.94%` (image-global normalized). This indicates limited image change, **not** guaranteed pixel or anatomical landmark identity.
- **No marker contamination:** Orange/teal diagnostic card `../chart4_run/34_C4_HighKneeStationaryRun_V2_ORANGE_TEAL_DIAGNOSTIC.png` untouched. None of its tracking bands appear on 34R.
- **Quality caveat:** This is a very small gain because 34 was already reasonably soft. Arm/shoulder definition remains a separate issue; do not promote solely for this minor cosmetic change without whole-card identity/mechanics review.

**Disposition:** **34R provisional QA pass** for the single lower-body softness variable; retain V3 clean card as a known candidate and the separate V2 marker diagnostic. No other exercise cards modified; no external uploads or repository operations performed.
