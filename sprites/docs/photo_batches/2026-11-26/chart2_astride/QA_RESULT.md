# 22 — Chart 2 Astride Jumps, 35mm photographic pose card

**Date:** 2026-11-26 UTC. **Method:** ONE built-in imagegen generation, joint four-phase 2×2 photographic card; no local crop/post-processing beyond copying generated PNG to project. No Flow spend, no external writes.

**Output:** `22_C2_AstrideJump_FourPhase_35mm_CANDIDATE.png` · **1199×1312 PNG** · SHA-256 `de40a2c68fd73957244030658fb06136aa17bd32900ee1adf2ed7444a15c77fb`.

**Exact full prompt, ordered reference roles:** `PROMPT_EXACT.md`.

**Source movement:** `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md` Chart 2 jump — feet together/arms sides; jump to feet astride/arms out sideways a little above shoulder; jump back feet together, one count. Distinct from Chart 1 scissor jump: astride moves both legs laterally, not front/back; no dancer toes. Historical RCAF 1959 still `artifacts/parallel_tests/astride_jump/rcaf_1959_astride_jump_ref.png` is a secondary pose-only authority.

## Four-panel QA

| Panel / criterion | Visual observation | Gate |
| --- | --- | --- |
| A top-left start | Feet closely together on track, arms down by hips, two shoes full frame; normal waist and teen proportions | **PASS** |
| B top-right outbound hop | Two shoes airborne and displaced sideways with clear lateral V, arms straight and broadly horizontal, one dark near wristband stays near; running shoes naturally flexed, no en pointe | **PASS**; arm height near horizontal rather than a few degrees above shoulder |
| C bottom-left wide landing | Distinct left and right shoes planted far apart on track, knees relaxed, arms horizontal or only slightly above shoulder, no fore-aft running split; head/torso same heading | **PASS**; arm-height precision **MINOR PARTIAL** |
| D bottom-right return | Feet together, soles firmly flat, arms down, reproduces opening relaxed body direction after inward hop | **PASS** |
| Age, face, body | Same ordinary 13–14-year-old fair boy, dark subtly messy hair, modest nose/ear size, soft unmuscular arms and legs, no apparent body hair, matching light blue tank, charcoal loose shorts, gray-yellow trainers, black socks and wristband | **PASS / STRONG CANDIDATE** |
| Camera and environment | Near-frontal slight oblique, perhaps 10–20° offset; lateral spread obvious; static looking track/trees and correct footwear framing; entire body/fingertips in all panels | **PASS**, small inter-panel background/figure-registration differences inherent to generated contact sheet |
| Physical anatomy | No extra legs/arms/heads, two shoes in all frames, no ballerina ankle or foot stretch, hips/shoulders not unnaturally twisted; hands are small and natural | **PASS** |
| Animation readiness | Two grounded endpoints plus one outward midair and wide landing imply return hop but do not show it airborne; Flow still may invent dancers' foot angle or reverse/crossfade sequence | **UNTESTED** |

## Verdict

**STRONG PROVISIONAL still-image candidate, NOT owner-approved form and NOT motion-verified.** The critical lateral leg spread and full arms, natural small hop, age-appropriate physique and photographic fidelity all look good. The arms are approximately shoulder-level; strict booklet wording is *slightly above* shoulder and the historical adult photo reflects that, so one improvement could raise the hands ~5–10° in midair/landing without changing age or anatomy. That is a small refinement, not a mechanics reject.

## Controlled lessons

1. A slight near-frontal oblique is enough to distinguish a correct side-straddle/astride from a fore-aft scissor jump. This is the opposite of prone back-extension, where a side view emphasizes torso lift.
2. Asking for the fourth pose as **grounded return** with sneakers flat is more reliable than an airborne return: the prior `astride_lock/03_oblique20_grounded_return_PASS.png` control had the same advantage. The return flight can be described to the video model between C and D, and checked independently later.
3. Keep all four stages in one contact sheet to reduce identity drift; still, the rendered figure and background registration is approximate, so video QA must watch for rotation/face drift and realistic shoe landing.

**Not yet production-approved.** No Drive/GitHub upload or Flow video generation was performed.
