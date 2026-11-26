# ID35 Chart 5 Exercise 2 — independent QA

**Status: REJECT for accurate 5BX instructional animation (useful diagnostic only).**

Candidate: [`35_C5_EX2_TwistSitup_FourPhase_35mm_CANDIDATE.png`](35_C5_EX2_TwistSitup_FourPhase_35mm_CANDIDATE.png)

Generated with one 2×2 joint prompt using the v2 identity sheet and two supporting sit-up cards. Exact prompt, sources and invocation: [`35_C5_EX2_ExactPrompt.md`](35_C5_EX2_ExactPrompt.md).

## Strict panel inspection

| Panel | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| A | Neutral: straight legs together, clasped hands behind head | Plausible photograph, torso and legs down, feet adjacent, arms behind head | **PASS** neutral, with minor uncertainty about individually seeing all fingers |
| B | **Anatomical RIGHT elbow toward anatomical LEFT raised knee**, anatomical RIGHT leg extended | One knee bends up and opposite-appearing leg extends. Chest rises, but almost no credible transverse spinal/shoulder twist toward a specific knee. The limb silhouette is too overlapping to establish anatomical side ownership independently. | **FAIL / unverified contralateral elbow** |
| C | Reverse: **anatomical LEFT elbow toward anatomical RIGHT raised knee**, anatomical LEFT leg extended | Knee/extended leg layout looks virtually identical to B, along with head and elbow orientation. The shoulder rotation does not visibly reverse. This is not a demonstrably different alternate-side repetition. | **FAIL**, critical error |
| D | Neutral supine return | Credible return, legs and feet adjacent, hands behind head | **PASS** neutral |

## Anatomical and consistency inspection

- **Knee ownership:** B and C cannot be confidently assigned to opposite anatomical knees from the image; same near-side knee silhouette in both, and the lifted leg's hip connection is partly occluded. This is a rejection criterion, independent of aesthetic quality.
- **Elbow target:** Neither B nor C shows a strong, unambiguous diagonally crossing elbow. B/C look like conventional sit-ups with one bent knee, not the opposite-elbow twist required by the booklet. They cannot be rescued with a frame label.
- **Limb integrity:** Both hands plausibly behind head with two arms in each panel; one extended and one bent leg in B/C; no obvious extra arms or legs, no clearly missing hands or feet. Exact five fingers per hand cannot be independently verified because clasped hands overlap behind head. Mild hand-position occlusion is acceptable by itself.
- **Age and proportions:** Fair skin, smooth face, realistic soft arms and thighs, plausible early teenage height; no overt adult hypertrophy. However hair is slightly fluffy/curly and chest looks a little more developed than v2. This is a lesser character drift.
- **Wardrobe/background:** Blue shirt, dark grey shorts, grey-yellow shoes, dark socks and track/grass match broadly; shirt somewhat brighter than master. Same setting across four images, 35mm photographic look.
- **Camera:** Frame and ground line reasonably consistent. Side-oblique angle is still too close to flat profile to prove which knee belongs to which side and where opposite elbow travels.
- **Exercise physics:** No excessive flexibility or impossibly long limbs, which is good. Do not force fingertip/elbow-to-knee contact in next trial; visual *direction* of cross-body rotation matters more than contact.

## Lesson for next iteration (NOT executed in this test)

Attempt **one coherent joint card** again, but explicitly distinguish the near and far anatomical legs and require shoulder rotation to face toward or away from the viewer in opposing reps. Use a slightly higher 30–35° three-quarter camera angle to see both thigh-to-hip connections. If necessary, generate an intermediate mechanics proof with **different temporary ankle-band colors** (one consistent band color on LEFT leg and a second color on RIGHT leg in every panel); reject any panel where the raised band color does not alternate. After mechanics pass, remove marker bands via targeted edit without regenerating anatomy.

Another option: temporarily use a ghosted overlay or instructor-style schematic of the **two cross-body elbow arrows**, then photorealize from a strictly validated image. A pose change should never be labeled successful solely because one knee is raised.

**No video, Drive upload, GitHub commit, or further generation was run from this test.**
