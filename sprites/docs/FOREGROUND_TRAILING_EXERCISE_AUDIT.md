# Foreground-trailing-leg applicability audit: all six 5BX charts

**Date:** 2026-11-24  
**Sources of truth:** [RCAF 5BX data](../../data/5bx-charts.json) (all 30 chart/exercise entries), [source prompt recipes](../prompts/strips.json), [strip registry](../config/strips.json), [conditional overlap rule](FOREGROUND_TRAILING_LEG_RULE.md), and user-reviewed scissor-jump experiment.

## Definitions and accepted control

In a right-facing three-quarter view, **near / foreground** is camera-relative, not a synonym for *rightmost*, *forward*, or *leading*. The user approved the [six-pose near-trailing sheet](https://drive.google.com/file/d/10-yl-i3xjLPJulv7tImmCAW4QP_-DJJ3/view) on 2026-11-24 **for the visual depth arrangement**: near/light leg trails toward screen-left but its thigh/shorts cuff occludes **in front of** the far/dark leading leg at the viewer-facing hip. The [independent near-leading candidate sheet](https://drive.google.com/file/d/1kHIR9Lg5R2MCPpcFmj96fHW-zn9W5_Aw/view) illustrates the opposite role but has not received a matching human form/identity verdict. A [mixed A/B sheet](https://drive.google.com/file/d/1tRxbi4nNx94FmKJnIUpmPP8kG_owggQW/view) **failed**: the two columns largely repeated one hip topology. The third sheet's acceptance is **not** acceptance of a full alternating cycle, stable anatomical left/right IDs, or released exercise art.

Use **separate endpoint contact sheets** for near-leading and near-trailing states before demanding a composite or tween. Keep identical camera, avatar, split amplitude and actual joint identities for subsequent pairing. When the athlete faces left, swap the screen-direction labels, **not** the near-over-far depth rule. A different camera angle or front view needs a fresh assessment.

## Complete chart/exercise inventory

**YES = needs both depth arrangements in a sagittal foot-switch; CONDITIONAL = check only if the far limb actually leads forward in the chosen view; NO = do not inject this special scissor/stride instruction.** A NO can still need other near/far or crossed-limb QC.

| Chart / exercise | Official activity | Near-trailing card? | Evidence / why |
|---|---|---|---|
| 1 / 1 | Toe touching | NO | Feet astride, floor touch and backward stretch; no alternating forward/back step. |
| 1 / 2 | Partial sit-up | NO | Legs remain straight on floor. |
| 1 / 3 | Alternate leg raise | NO | Alternate **raised** prone leg; track near/far identity separately, no lead/trail stride. |
| 1 / 4 | Knee push-up | NO | Knees stay supported; no alternating stride. |
| **1 / 5a** | **Stationary run** | **CONDITIONAL** | Far foot may appear slightly ahead in a frame; near supporting leg must retain foreground overlap. Official lift only about **4 inches**, not a sprint. |
| **1 / 5b** | **Scissor jumps** | **YES — priority 1** | Booklet alternates right/left leg forward with opposite arms. In pose 3 (`scissor-jumps-c1` stance B), **far/dark leads and near/light trails**; pose 1 is the inverse. Two separate endpoint cards before transitions. |
| 2 / 1 | Toe touching with press | NO | Both feet remain astride. |
| 2 / 2 | Sit-up | NO | Both feet on floor, slight knee bend allowed. |
| 2 / 3 | Back extension | NO | Both straight legs raise together. |
| 2 / 4 | Push-up | NO | Toes and palms support body, no foot switch. |
| **2 / 5a** | **Stationary run** | **CONDITIONAL** | Reuses the Chart 1 low-run strip; preserve four-inch lift. |
| 2 / 5b | Astride jumps | NO | Sideways feet-apart/together from a FRONT view, not a sagittal opposing stride. |
| 3 / 1 | Toe touching outside feet | NO | Side/center toe reaches while feet remain astride. |
| 3 / 2 | Sit-up, hands behind head | NO | Legs do not alternate front/back. |
| 3 / 3 | Back extension, hands behind back | NO | Both legs rise together. |
| 3 / 4 | Chin–forehead push-up | NO | Upper-body changes, no foot switch. |
| **3 / 5a** | **Stationary run** | **CONDITIONAL** | Reuses the same low-run strip. |
| 3 / 5b | Half knee bends | NO | Feet stay together, knees bend and heels rise. |
| 4 / 1 | Toe touching, circle bend | NO | Feet astride while trunk circles. |
| 4 / 2 | Sit-up, toe touch | NO | Feet together, no foot alternation. |
| 4 / 3 | Back extension, arms sideways | NO | Both legs rise together. |
| 4 / 4 | Wide-hand push-up | NO | Static toe contact, no lead/trail swap. |
| **4 / 5a** | **High-knee stationary run** | **CONDITIONAL** | Far knee can drive ahead of near planted support leg; check camera-near support thigh stays foreground at hip. **Knees waist high**, not four-inch low run. |
| **4 / 5b** | **Semi-squat jumps** | **YES — priority 2** | Official instruction reverses which foot is slightly ahead. In `semi-squat-jumps-c4` pose 3 **and first hop pose 2**, far/dark leads, near/light trails. Half crouch with straight back/hands on knees; low athletic hop. |
| 5 / 1 | Toe touching, hands clasped | NO | Feet stay astride. |
| 5 / 2 | Sit-up with twist | NO | Cross-body elbow/knee tracking is difficult but **not** this sagittal leg-trailing condition. |
| 5 / 3 | Back extension, arms overhead | NO | Both legs extend together. |
| 5 / 4 | Clap push-up | NO | No sagittal leg switch. |
| **5 / 5a** | **High-knee stationary run** | **CONDITIONAL** | Reuses Chart 4 high-knee strip; see its far-knee-up pose. |
| 5 / 5b | Semi-spread-eagle jumps | NO | From front view, both legs spread sideways, then return; different occlusion rule. |
| 6 / 1 | Toe touching, reverse clasp | NO | Feet stay astride. |
| 6 / 2 | Pike sit-up | NO | Both legs rise together into a V, no alternating leader. |
| 6 / 3 | Back extension with press | NO | Both legs lift together. |
| 6 / 4 | Chest-slap push-up | NO | No alternating foot stance. |
| **6 / 5a** | **High-knee stationary run** | **CONDITIONAL** | Reuses Chart 4 high-knee strip. |
| 6 / 5b | Jack jumps (pike/tuck type) | NO | Both legs rise together forward to waist height; not a foot-switch/stride. |

## Four unique prompt recipes to update

| Priority | Recipe | Pose(s) | Specific hip-overlap instruction | Action |
|---|---|---|---|---|
| **1** | `scissor-jumps-c1` | 1 near-leading; **3 near-trailing** | Near **trailing** thigh (screen-left) must cover far **leading** thigh (screen-right) at red shorts; reverse topology in pose 1 | Two independent accepted endpoint cards, then physically identified A/B pair and low-hop transitions |
| **2** | `semi-squat-jumps-c4` | 1/4 near-leading; **2/3 near-trailing** | Far-foot-ahead crouch/hop must show the camera-near trailing thigh in foreground even with the far shoe farther to screen-right | Separate crouched endpoint cards; check hip topology under flexion |
| **3** | `high-knee-run-c4` | **3 far knee up** (if far knee leads screen-right) | Near planted support thigh may trail in image direction while remaining camera-near at hip | Conditional text only, preserve waist-high rise and no travel |
| **4** | `stationary-run-c1` | **3 far foot up** (if lifted far foot advances) | Near support thigh foreground even if shoe appears farther back | Conditional text only; never manufacture a long stride in the four-inch run |

The same run recipes are reused across charts: **low run in 1–3; high-knee run in 4–6**. Do not create six separate conflicting prompts. Check `sprites/config/strips.json` coverage separately; currently Chart 4 lacks an explicit `jump` mapping and other later-chart mappings may be partial, as already flagged in production requirements. This audit does **not** silently wire missing assets.

## Copy-paste insert for applicable far-leg-ahead pose

> **DEPTH LOCK — FAR leg forward, NEAR leg trailing, right-facing camera:** The camera-NEAR (lighter) leg trails toward IMAGE-LEFT yet remains the foreground limb at the viewer-facing hip. Its rearward thigh and shorts hem must overlap **IN FRONT OF** the camera-FAR (darker) leg. The far leg leads toward IMAGE-RIGHT, but its upper thigh comes from the far hip and is partly **occluded behind** the near trailing thigh at the crotch/shorts seam. Screen-right means leading, **not** camera-near. Two complete anatomically plausible legs, stable limb lengths, visible distinct shoes, no lunge or ballet interpretation. Match the user-accepted [six-pose trailing-depth reference](https://drive.google.com/file/d/10-yl-i3xjLPJulv7tImmCAW4QP_-DJJ3/view) for **occlusion only**, not its motion amplitude or alternate avatar. Preserve official arm/leg opposition where applicable.

**Do not apply to a pose where the near leg leads, to a frontal lateral jump, or to fixed-leg floor exercise.** Reversed orientation requires remapping screen-left/right.

## Release and learning guardrails

1. **Depth silhouette passing is separate from physical left/right leg identity** through a switch, and both are separate from official form review. The near-trailing sheet only has Charles's *depth depiction* acceptance.
2. Inspect individual endpoint sheets first. The paired sheet failure showed that simply asking for A and B on one card can reproduce the same hip drawing twice.
3. For real tracking, a unique marker must stay attached to a **physical source leg**, not a shoe at a particular screen location; the failed white-shoe post-coloring experiment proved this.
4. Low-run and high-knee-run source form differs by chart; use `data/5bx-charts.json` for height and timing. No migration of an exaggerated reference running stride into 5BX.
5. No generated image, source video, renderer setting, strip registration, released art, or human form approval was changed by this prompt/documentation audit.
