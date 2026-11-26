# Chart 1 Exercise 3 — alternate single-leg raise (photorealistic)

2026-11-26. Assistant-only controlled imagegen test. Not Charles-approved. The original booklet's Chart 1 EX3 requires raising ONE leg at a time while prone with palms under thighs. Chart 2 is a DIFFERENT both-leg back extension.

## Inputs / method

- Binding identity master: `artifacts/character_master_candidates/2026-11-25/identity_sheet_v2_hair_arm_refinement.png` (approved middle-school boy, not a pose reference).
- Tool: built-in OpenAI image_gen. First pass: jointly generated 2×2 four-phase 35mm photo card. Second pass: localized image edit, same card and master.
- Camera: requested fixed low 20-degree side-oblique; actual outputs look nearly perfect side profile.

## Output 01 — original

- File: `01_C1_EX3_AlternateLegRaise_FirstCandidate.png`
- QA: Visible coherent prone rest -> one straight leg lifted -> rest -> other leg intended lifted. Both knees remain straight, pelvis/belly grounded, hands along thighs, no added limbs or toe pushup.
- Main defect: at this near-side view, it is NOT clear which physical near/far leg lifts in each working tile. The two lifts may still be the same leg in appearance even though both have the correct vertical movement. Do not call opposite-leg ownership validated.

### Exact prompt, first generation

```text
Use case: photorealistic-natural.
Asset: 5BX Chart 1 exercise 3, one photographic 2×2 four-phase motion reference card, not a video.
Reference image 1: the provided four-view photo character sheet is the binding authority for the boy's EXACT face, apparent 13–14-year-old middle-school age, soft unmuscular arms and legs, fair untanned skin, modestly messy dark-brown hair, proportions, blue tank, loose dark charcoal shorts, gray socks, gray running sneakers with restrained yellow accents, black wristband, and realistic photography. Disregard the STANDING POSES in the reference. Generate new lying poses while preserving the same person and outfit exactly.

Create ONE unified high-resolution 35mm documentary photograph contact card, a 2×2 grid with four equal horizontal-landscape panels separated by narrow plain white gutters. The same ordinary 13–14-year-old middle-school boy performs the original Royal Canadian Air Force 5BX CHART 1 ALTERNATE SINGLE LEG RAISE, NOT a both-leg back extension. Fixed locked-off low camera at a slight ~20° oblique side angle, boy lying BELLY DOWN ON THE RED RUNNING TRACK, head to IMAGE RIGHT, feet to IMAGE LEFT; same photo-real grass, trees, track lines, daylight, identity and camera scale in each frame. Every panel shows the ENTIRE boy including both shoes, both complete legs and both hands, with room for small upward lifts. Arms extended BACK ALONG THE SIDES, hands slipped palm-up UNDER THE FRONT OF HIS THIGHS, wrists resting on the track; hands NEVER planted ahead under the shoulders and NEVER push upper body up. Forearms traceable along his side. Pelvis, belly and the nonworking thigh remain fully grounded in all four phases.

TOP LEFT (phase 1 — REST): prone start. Both legs and gray/yellow sneakers straight behind him on the track, knees at near-180° extension, hips grounded. Arms back by sides with both palms tucked under upper thighs, head relaxed near the ground.
TOP RIGHT (phase 2 — LEFT LEG ONLY): boy gently raises his head and his ANATOMICALLY LEFT LEG slightly UP from his hip, about 10 cm vertically; entire raised left leg remains STRAIGHT from thigh through knee to ankle, toes in neutral athletic-shoe position. His anatomically RIGHT leg, knee, shoe remain FLAT and grounded. The two feet visibly separate in height, not in horizontal foot position. Arms still under thighs, pelvis grounded.
BOTTOM LEFT (phase 3 — RETURN TO REST): head and raised leg gently lower to the exact same initial prone rest, two straight grounded legs, palms still underneath thighs.
BOTTOM RIGHT (phase 4 — RIGHT LEG ONLY): head gently lifts, his ANATOMICALLY RIGHT LEG rises vertically at hip by around 10 cm, straight knee, while anatomically LEFT leg, foot, knee remain planted. This must be the OPPOSITE leg from the top-right panel. Near and far shoe overlap should clearly change: in one working panel the CAMERA-NEAR leg is raised, in the other the CAMERA-FAR leg is raised; never repeat the same leg lift. Hands remain beneath thighs.

Authentic 35mm documentary photography, subtle natural grain, believable track rubber, textile seams, grass and hair strands, real skin texture; no illustration, CGI, cartoon, text, numbers or pose labels. Soft undeveloped ordinary middle-school anatomy: do not give mature athletic shoulders, defined biceps, visible body hair, enlarged buttocks, enlarged arms, pinched waist or elongated elastic limbs. All four tiles exactly the same boy and outfit. In each tile there are exactly two legs and two arms; no bent kicking knee, no hamstring curl, no feet moving backward sideways instead of UP, no two-legged lift, no child floating above track, no changes in shoes or limb lengths. The movement is small, plausible, and consistent with the original Chart 1 5BX exercise.
```

## Output 02 — targeted edit

- File: `02_C1_EX3_AlternateLegRaise_FarNearSwitchEdit.png`
- Revision asked only for BOTTOM-RIGHT opposite raised leg identity and overlap. Frame and body stayed visually consistent, and shoe/leg overlap subtly changed; however the near/far ownership is still ambiguous and not independently traceable to the pelvis.
- Verdict: **CONDITIONAL / DIAGNOSTIC**, not a production pass. Strong body mechanics for mild hip-driven straight leg lift; opposite-leg assignment remains uncertain. This likely needs a further 25–35° camera oblique or diagnostic ankle bands, followed by a clean no-marker generation. Do NOT solve by exaggerated leg height or impossible hip rotation.
- No video generated; still contact-sheet only.

### Exact prompt, second edit

```text
Use case: identity-preserve.
Input image 1 is the EXACT original 2×2 generated photographic exercise card and EDIT TARGET. Input image 2 is the approved four-view middle-school character identity authority (face, build, outfit).
This is a highly localized one-defect correction for Chart 1 exercise 3 ALT SINGLE-LEG RAISE. Preserve the ENTIRE existing contact card, 2×2 arrangement, all three other panels, same subtle film grain, red track, forest background, daylight, boy's recognizable face, hair, softness of body, sky-blue tank, dark shorts, dark socks, gray/yellow shoes, and exact fixed oblique camera. Keep panel TOP LEFT REST, TOP RIGHT LEFT-LEG RAISE, and BOTTOM LEFT REST as they are. Keep the head, chest and arms of BOTTOM RIGHT as they are.

CHANGE ONLY BOTTOM-RIGHT PANEL'S LEG OWNERSHIP so it unambiguously lifts the OPPOSITE PHYSICAL LEG relative to TOP RIGHT, instead of repeating the same foreground leg. In TOP RIGHT the upper leg is the CAMERA-FAR leg; in BOTTOM RIGHT the upper leg must be the CAMERA-NEAR leg. The two legs can be visually distinguished by which straight thigh occludes the other at the shorts and which shoe is foreground; in BOTTOM RIGHT the straight lifted foreground leg visibly overlaps the still-grounded background calf/ankle while remaining fully anatomically attached at the boy's hip. Ensure exactly TWO separate shoes and the stationary shoe flat on track in both working tiles. A lifted leg rises only 10 cm from HIP EXTENSION, knee locked almost straight; no knee curl, no backward shoe movement, pelvis stays planted. Do NOT turn the camera, move scenery, enlarge the boy, reshape his body, change shirt/shorts colors, edit unaffected panels, distort hip/leg proportions or create a third leg. Same camera 20–30° side oblique view and same photo identity across all four panels. No labels, text, arrows, or decorative markers. This is a localized anatomical switch only.
```

## Lessons

1. Strictly naming Chart 1 ALTERNATE leg raise avoided the recurrent wrong Chart 2 both-leg back extension.
2. Explicit palms under the thighs and arms extending back avoided a push-up arm posture.
3. Vertical hip-driven 10-cm lift with knees almost 180° yielded realistic anatomy, no knee curl, no feet retracting.
4. Nearly 90° side view hides which upper leg belongs to which hip. A text-only correction while holding camera locked may be insufficient. Solve the *view and occlusion information*, not the stretch range.
5. Do not accept a plausible single-leg pose as a complete alternating movement until both leg identities are verifiable.
