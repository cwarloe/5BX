# Test 36 — Chart 5 Exercise 3, overhead-arm back extension — QA

**Disposition: STRONG CONDITIONAL CANDIDATE.** Anatomical movement and requested arm direction pass visual inspection. Retain for review and possible image-to-video test; do **not** mark as a validated animation or production master without human judgment.

## Files and generation audit

- Contact sheet: `36_C5_EX3_BackExtension_ArmsOverhead_FourPhase_35mm_CANDIDATE.png`
- Exact submitted prompt: `36_C5_EX3_ExactPrompt.md`
- Source generated file: `generated_images/exec-61793813-8a32-4217-93d7-ed866ed9d393.png`
- Dimensions: **1672 × 941 px**, 2×2 four-frame card.
- SHA-256: `f41ed81f8c8a97e69a95669e03dbcfa227b843a1f3b6594813d2f30702c712db`
- Generated once, no retouching.
- Booklet authority: `repo_5bx_brightboy/sprites/docs/CHARTS-2-6.md`, Chart 5 Exercise 3: *“Front lying, arms extended overhead”*; movement *“Raise arms, head, chest and both legs as high as possible.”*

## Panel-level biomechanics

| Phase | Overhead arms | Head and chest | Both straight legs | Pelvis supported | Finding |
| --- | --- | --- | --- | --- | --- |
| A / upper-left prone start | **Pass:** both arms reaching past head, close and parallel, hands visible | Low and near ground | Both grounded | Yes | Pass |
| B / upper-right early lift | **Pass:** both arms visibly above ground, not sideways or T-shaped | Modestly raised | Both feet elevated, separate enough to identify | Yes | Pass |
| C / lower-left controlled peak | **Pass:** both arms straight overhead and elevated, hands separated | Moderate realistic arch, not an extreme Superman | Both legs lifted, knees nearly straight; shoes visible | Yes | Pass |
| D / lower-right recovery | **Pass:** both arms still overhead | Lowered close to ground | Both lowering/near ground | Yes | Pass |

## Character, photographic and continuity observations

- **Age/body:** Looks broadly like a normal 13–14-year-old, fair complexion, not a bodybuilder and not a visibly younger elementary-school child. Forearms and shoulders retain somewhat more tone than the softest approved reference; acceptable for an exploratory card, worth comparing side by side to the master.
- **Face/hair:** Brown curly-messy hair is slightly fuller and facial angles subtly change with raised head, but the face remains plausibly the same character. Not a lock-quality identity validation.
- **Outfit:** Bright blue tank, charcoal shorts, gray socks and gray-yellow shoes remain consistent. Foreground wristband visible where the wrist angle permits.
- **Hands/limbs:** Two overhead arms and hands, two legs and shoes; no observed extra or fused limbs. In B, the far shoe overlaps the near shoe slightly, but both feet exist.
- **View/scene:** Stationary low-elevated side-oblique frame, red running track/white stripe, green field and tree line, daylight consistent. Subtle composition and track line shifts are natural image-generation continuity changes.
- **Photorealism:** Good photographic texture and believable body proportions; slight generated-art smoothness visible on close inspection. Output resolution 1672×941 total means each frame has limited independent pixel detail; use full-resolution originals for future video if single-frame derivations become available.
- **Framing:** Full figure visible in each. B's fingertips approach the right edge; preserve extra lead room on image-to-video crops.
- **Motion QA:** Static card only. No claim yet about intermediate transitions, temporal stability or Google Flow output.

## Lessons and next experiment

1. Using the same character identity reference and an earlier prone back-extension card produced unusually good four-frame pose coherence.
2. Explicitly naming the forbidden Chart 4 **sideways T-arm** direction avoided a likely prompt-transfer mistake. All frames instead have **both arms overhead**.
3. A **modest, age-appropriate** double-leg and chest lift avoided unrealistic child flexibility/elongation; this is more valuable than a spectacular high arch.
4. For video, consider using A and C as endpoints or C alone to avoid sequence inversion; check whether both feet lift together and whether hands remain overhead, rather than allowing the engine to turn it into an airplane pose.
5. If refining, reduce arm definition slightly, leave more lead space beyond the hands, and keep hair/facial age even closer to approved v2. Do not independently change outfit, camera or body width.

**Recommendation:** Keep, move to human comparative review as strong conditional; no automatic publish/video generation was done by this subagent.

