# 5BX independent identity audit — muscle/age drift

**2026-11-26.** Visual second opinion on selected *existing photographic stills* only. Not a medical or anthropometric measurement, not a video-motion test, and not a human approval. Baseline: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`, the approved four-view boy. Desired character reads as an ordinary fair-skinned, proportionate, softly developed 13–14-year-old, **not leaner or heavier** than the master. A dynamically braced push-up can naturally show tension; a new deltoid/biceps silhouette or sculpted quadriceps is a different, unwanted identity change.

## Ranked visual findings (worst apparent drift first)

| Priority | Candidate | Observed difference from approved v2 | Disposition |
|---|---|---|---|
| **1 — highest** | **32R Chart4 wide-hand push-up** | Shoulder cap and upper-arm contour are noticeably fuller in both bent and extended panels than in the standing v2. Triceps/deltoid shading makes him read older and athletic; face has a stronger angular profile. Existing 32R already softened the original a little and preserves visible wide hands/elbows. | **Identity conditional; strongest next softness candidate.** Fix *surface definition only*, no narrower arms or altered hand spacing. |
| **2** | **41R Chart6 chest-slap push-up** | Rounded shoulder and upper-arm shape, sharper facial angle, and chest/upper-body tension persist even in planted A/D. R1 successfully lowered the implausible airborne torso, but that is a separate movement correction. | **Identity conditional.** Further reduce hard shading/sculpted shoulder edge only if two distinct airborne hands and chest contacts survive; far palm clearance is already visually subtle, so mechanics take priority. |
| **3** | **37R Chart5 clap push-up** | Rounded deltoid, comparatively defined triceps and slightly older/athletic jaw in multiple panels. R1 improved lower torso and actual two-hand clap; do not risk that rare contact event for cosmetic change. | **Identity conditional.** Prefer lighting/texture softening over any limb-outline edit. |
| **4** | **24 Chart2 standard push-up** | Some prominent near upper arm and shoulder tension; however the pose itself normally loads these muscles. Hair/face may read slightly older than v2. Less persistent bulk than 32R. | **Low-priority conditional**; do not confuse natural bracing with muscular hypertrophy. |
| **5** | **34 V3 Chart4–6 high-knee run** | Front elevated thigh can seem somewhat large against slim lower leg; compression and strong camera-side profile partly explain that. No obvious separated quadriceps heads or bodybuilding definition. Hair/facial profile look somewhat more styled/mature. | **Monitor**, not an automatic thinning operation. Physical alternate-knee lineage is valuable; preserve successful V2 orange/teal proof and V3 clean. |
| **6** | **35R Chart5 twisting sit-up** | Flexed near arm has a visible shoulder bulge, and bent thigh appears larger because closer to camera. Both still look within plausible normal middle-school proportions; hair is a little full. | **Mild conditional**; preserve proven opposite knee/contralateral elbow tracking. No strong thigh-circumference correction indicated. |
| **7** | **18 Chart1 kneeling push-up** | Loaded upper arm shows modest straight triceps contour. Face and soft body remain close to reference. No exaggerated chest or shoulder bulk. | **Reasonable identity pass** for this stage, mechanics require their own QA. |
| **8** | **38 Chart5 semi-spread-eagle jump** | Limbs generally smooth and age-appropriate; arms spread overhead reveal some shoulder shading but not an obviously sculpted adult upper arm. Thighs slim/moderate and continuous. | **Good identity match**; no anatomy edit justified. |
| **9** | **39 Chart6 pike sit-up** | Arms and legs stay smooth without strongly separated muscle contours; body looks soft, although face/hair and posture vary slightly. | **Good identity match**. Keep natural toe gap rather than stretching anatomy to perfect form. |
| Supplemental | **33 Chart4 semi-squat jump; 40 Chart6 overhead back extension** | Both look broadly close to v2 in upper arms, leg softness and proportional body; no serious muscle drift seen. | **Good controls** for future before/after comparison. |

### The distinction that matters

- **Expected exercise tension:** shadows near elbow when bending, mild shoulder rounding under load, subtle thigh compression when the hip is flexed, and lighting changing because a limb rotates. These are not by themselves reasons to reject a photo.
- **Unwanted character drift:** an added *persistent* shoulder cap or triceps/biceps bulge across both action and rest phases, hard lines between quad muscle groups, a narrower V-shaped torso, an older/angular face, extra height, or a much smaller waist. The v2 master has an ordinary smooth standing arm and softly continuous thighs. Be more skeptical when a new sculpted edge also appears in unloaded panels.
- **No strong objective evidence yet of oversized *muscular* thighs** in the reviewed preferred cards. #34's raised thigh is the main appearance concern, but it can be legitimate foreshortening/shorts tension. If changed, use a gentle local shading pass only, *never* shrink overall thigh diameter or length without a measured side-by-side basis.

## Release-oriented image-stage gates

1. **Master comparison:** always display approved v2 head/three-quarter/full-body crop next to *each* new card, matching approximate size. Review shoulder cap/upper-arm, chest breadth, waist, hip/seat, upper-thigh smoothness, skin tone, ear/nose/hair, and clothing. Do not reference a later drifted card as sole identity authority.
2. **Across-phase invariant:** a bent arm can show temporary tension; the underlying same character's arm/shoulder bulk should not change visibly between A/B/C/D, apart from perspective. A resting phase that has bodybuilder-like deltoid caps fails even if its movement pose is attractive.
3. **Keep geometry:** any softness edit must preserve head-to-hip/hip-to-ankle lengths, shoulder and waist width, pelvis/rear and thigh circumference, foot/hand support points, near/far limb ownership, and every exercise-specific contact. An edit that improves aesthetics but makes the clap/chest slap or alternate leg wrong is **rejected**.
4. **Surface-first edit:** prioritize reducing sculpted highlights, hard separation lines and contrast while retaining body outline, ordinary skin texture and natural fabric creases. Avoid prompts that demand "skinny," "smaller thighs," "slimmer waist," "less body fat," "muscular teen," or "athletic V shape."
5. **Physical lineage:** preserve source diagnostics for alternate limbs (34 orange/teal ankle bands; 35R wrist+ankle bands). After color removal and any identity edit, inspect B/C limb ownership afresh rather than inheriting an unconditional pass.
6. **Motion gate remains independent:** still-card face/body consistency cannot validate the actual Flow/Grok video. Re-check age, arm/thigh shape, contact, phase order, foot glide and scene registration *within video frames*.

## Copy-ready identity-lock edit prompt (minimal)

```text
Use case: identity-preserve
Asset type: 5BX photographic multi-pose exercise card, one controlled identity correction only.
Image 1 — EDIT TARGET: [the current four-panel preferred card].
Image 2 — IMMUTABLE APPEARANCE AUTHORITY: the approved four-view v2 middle-school boy; use his face, natural shoulder/upper-arm softness, waist, and unsculpted thighs. The original 5BX pose remains exercise-mechanics authority.

Change ONLY the overly hard muscular contour/shading on shoulders and upper arms and, if clearly needed, the front of the thighs. Make the skin look naturally soft and slightly less sharply modeled, like the approved ordinary 13–14-year-old; do not add or remove body volume. Preserve every body outline, width and limb length. Do not make him skinny, fat, taller, bodybuilder-like, leaner-waisted, or more V-shaped. Keep face/nose/ears, messy low-volume dark hair, fair untanned skin, smooth face/underarms/legs, blue tank, charcoal shorts, dark socks, gray/yellow shoes and black wristband unchanged.

Most importantly: preserve each frame's exact anatomical action and panel order. Both palms/elbows and each leg must remain attached to the same physical shoulder/hip; preserve all planted points, airborne gaps, actual claps/contacts, knee ownership, hip angle, camera and fixed red running track. No new arms, no new shoes, no posture changes, no added background objects. Change only muscle shading/texture; keep everything else as identical as possible.
```

**Suggested next experiment:** Compare 32R (highest drift) with a single-variable *shading-only* edit, scored separately for (a) shoulder texture softness and youth appearance, (b) unchanged *silhouette and wide-palm geometry*, and (c) unchanged per-panel identity. If any motion/lineage worsens, keep 32R and record the failed edit. A high-quality original beats a cosmetically prettier but mechanically incorrect derivative.
