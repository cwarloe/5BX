# Test 38 — Chart 5 semi-spread eagle jump: visual QA

## Verdict

**PROVISIONAL ACCEPT / strong candidate for prototype.** One generation; no second variation requested. The four frames show the correct crouch → airborne outward jump + arm rise → wide airborne overhead V → feet-together crouch recovery. Manual reviewer may decide whether the wide airborne phase is high enough for the eventual video keyframe. Do not treat this still contact sheet as a verified successful animation.

## Four-panel movement audit

| Panel | Required | Observed | QA |
|---|---|---|---|
| A top left | Feet together, half crouch, straight arms hands on knees | Feet nearly touching, knees moderately bent, both hands rest on own knee, elbows largely straight | **Pass** |
| B top right | Upward takeoff, both feet airborne, legs begin spreading laterally, arms leave knees and sweep upward | Both shoes well above track; feet apart laterally; hands/arms extended out and slightly down from shoulder height, consistent with upward sweep | **Pass**, arm arc not yet over shoulder |
| C bottom left | Wide airborne apex, arms overhead, neutral athletic foot angle | Shoes airborne with visible shadow gap; leg spread moderate (not split); both arms overhead V; normal shoe angle | **Pass** |
| D bottom right | Direct return to initial feet-together half crouch and hands on knees | Feet close together and planted; hands on own knees; moderate crouch, reproduces A | **Pass** |

## Identity and anatomical QA

- Age reads approximately **13–14**, rather than elementary age or physically mature adult; consistent with v2.
- Soft, typical middle-school build; no V-cut abs, pronounced arm/shoulder muscles, excessive lean or oversized glutes.
- Light skin, short messy dark brown hair, blue tank, charcoal-gray shorts, dark socks, gray-yellow runners, right/left orientation and dark wristband largely preserved across all four.
- Face and hairstyle remain quite consistent; minor lighting/scale differences are inherent to full-body generation.
- Two arms, two hands, two legs, two shoes; no obvious extra limbs or conspicuous visual artifacts.
- Wide track field and treeline match across panels. Camera is slightly oblique frontal (rather than exactly 90° side), keeping the lateral foot separation visible.
- Shoes show natural, neutral toe angle rather than ballet-pointed feet.

## Known caveats and prompt implications

1. The phase B arm trajectory is low and broad; motion can be inferred as hands rising to panel C, but an intermediate above-shoulder frame would make *sweeping overhead* clearer. This is a small continuity risk for future frame interpolation.
2. The source document has an unfinished trailing word “Raise”; retain only the complete directions and do not manufacture the missing clause.
3. A possible source interpretation would be a momentary **feet-astride landing** before directly gathering into crouch. This four-frame prototype represents the feet-astride moment **in air**, then direct recovery landing. This is faithful to “return directly to starting position on landing”; should 5BX historical form explicitly require astride foot-contact, generate a five-phase version with a contact frame.
4. All four pose frames are a static instructional reference, not proof of continuous physical trajectory or ground-contact timing in motion-video output.
5. The person is AI-generated and synthetic; do not describe as an authentic 1959 documentary photograph.

## Assets

- `38_C5_SemiSpreadEagleJump_FourPhase_35mm_CANDIDATE.png`
- `38_C5_SemiSpreadEagle_ExactPrompt.md`
- `38_C5_SemiSpreadEagle_QA_RESULT.md`

No cloud uploads, PRs, video generation, or destructive changes were made.

