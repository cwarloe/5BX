# Chart 1 scissor jump — independent V4 form and identity QA

Reviewed 2026-11-26. This is a skeptical visual inspection of
`scissor_2x2_V4_ankle_wrist_COUPLED_DIAGNOSTIC.png`, not an image-generation
attempt. Appearance authority: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png`.
Movement authority: `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md` line 40:
"Stand with right leg and left arm extended forward, and left leg and right arm
extended backward; Jump up - change position of arms and legs before landing.
Repeat (arms shoulder high)."

## Physical limb tracking

| V4 panel | Orange apparent near leg | Orange near arm | Teal apparent far leg | Teal far arm | Opposite arm/leg topology |
| --- | --- | --- | --- | --- | --- |
| A, top-left | Trailing screen-left, planted | Forward screen-right, orange wrist tag | Leading screen-right, planted | Back screen-left, teal wrist tag | **PASS** |
| B, top-right | Leading screen-right, airborne | Back screen-left, orange wrist tag | Trailing screen-left, airborne | Forward screen-right, teal wrist tag | **PASS** |
| C, bottom-left | Leading screen-right, planted | Back screen-left, orange wrist tag | Trailing screen-left, planted | Forward screen-right, teal wrist tag | **PASS** |
| D, bottom-right | Trailing screen-left, planted | Forward screen-right, orange wrist tag | Leading screen-right, planted | Back screen-left, teal wrist tag | **PASS** |

**Four-limb visual tracking: YES, diagnostic pass.** Marker colors remain on the
same *apparent* near/far physical wrist and ankle across all tiles, instead of
relabeling whichever hand or shoe is forward. A and D match; B and C present
the inverse lead-leg stance; B contains an airborne transition. No obvious
phantom limbs or missing shoes. This is a meaningful improvement over the V3
card, which switched legs without switching arms.

**Proof of anatomical left/right from a real source video: NO.** Near-pure
profile makes hip and shoulder depth difficult to see. Colored bands demonstrate
internal visual consistency of this generated card but do not substitute for a
fully visible, marked, anatomical video reference. B has a relatively sharply
bent front knee and reads partly as a running hop, rather than an unequivocally
straight-legged scissor flight; its ordinary non-ballet sneaker angle is fine.

## Strict historical 5BX form issue — material

**FAIL against booklet arm extension.** Every tile shows elbows substantially
bent, with front fists around chest/shoulder level and rear fists near hip
level. Both hands and forearms are in a running-arm pump configuration. The
booklet, however, calls for one arm *extended forward* and the other *extended
backward*, with arms *shoulder high*. Therefore, correct opposite arm/leg
**ownership does not yet equal correct Chart 1 scissor-jump posture**. A running
arm-pump interpretation might be an intentional child-friendly modification,
but cannot silently be labeled faithful 1950s 5BX demonstration.

## Identity / photographic consistency

- **Age and build:** Plausible 13–14-year-old normal undeveloped runner, soft
  arms, moderate waist; no six-pack/oversized muscles, no obvious body hair.
- **Face/hair:** Fair complexion, shortish messy dark brown hair, medium ears,
  mostly recognizable relative to v2 master. There is some generated side-profile
  facial simplification; not a strong identity drift.
- **Wardrobe:** Saturated light-blue tank and charcoal shorts, gray/gold sneakers
  match the master broadly. Orange/teal bands are *temporary QA markers only*.
- **Setting / camera:** All four panels preserve the track and green trees.
  Subject size is similar, but static exact registration is unproved. Angle is
  close to **90-degree profile**, not the desired 20–30-degree oblique viewpoint;
  the side view does make the arm/leg trajectories easy to read.

## Independent verdict and next gate

**DIAGNOSTIC PASS for physical opposite-arm/leg switching; STRICT 5BX FORM FAIL
for bent arms and low backward hand. NOT production approved and NOT a Flow-ready
complete-cycle reference.**

Best next controlled test: while orange/teal ankle/wrist identity markers are
still present, adjust arm geometry to the booklet's **nearly straight,
shoulder-height forward/backward extensions** in A, B, C, D, preserving the
already-correct opposite limb correspondence. Then compare all four panels
again and only afterward try band removal. If user explicitly prefers an
accessible bent-arm school exercise variation, retain this version separately
as a variation rather than retroactively calling it source-faithful.
