# 5BX round 5 — 34B high-knee rear-hand handedness

## New human diagnosis

The rear arm length in **34B** may be a little long, but the more important error is **handedness and finger-surface orientation**. In the **lower-left C pose**, the far/background trailing arm visually ends with a **right-hand-shaped fist**, knuckles toward the camera. The correct anatomical **left hand** ought to expose the finger side of the curled fist toward the viewer, matching the other frames' hand appearance. The user explicitly noticed that fingers face the camera in top-left, top-right, and bottom-right frames.

The earlier **34C** attempt edited the rear-arm swing instead of the hand and accidentally froze the foreground arm between opposite knee lifts; it stays **REJECTED**. The immediate new correction should target only the lower-left far trailing fist. Keep **34B** as source, with all legs and A/C near-arm swing already correct.

## Controlled 34E test

Source: 34B clean four-panel photograph; **not** 34C nor 34D. See `34E_ExactSubmittedPrompt.md`.

Observed in 34E: bottom-left trailing fist now has more visible curled-finger surface and reads closer to a left-hand orientation. The rest of the running mechanics remain recognizably intact: A near arm backswing and C near arm forward swing, A/C knee alternation. **Collateral change:** the far trailing fist/wrist shifted slightly closer to his torso and the rear forearm looks a little shorter, despite an explicit unchanged-length instruction. Assistant cannot certify exact left-vs-right anatomy from this low-resolution small fist alone. **Review candidate only; do not auto-animate or claim human approval.**

## Transferable production lesson

When an arm silhouette looks wrong, test the low-level **handedness, palm-versus-knuckle side, thumb placement and finger occlusion** before changing elbow angles or upper-arm length. A right hand attached to a left arm can create the subjective impression of excessive arm length or unnatural movement. This is a separate gate from arm swing and leg alternation.

Keep a one-frame limb anatomy table in QA: `anatomical arm identity → wrist → correct left/right hand → palm/knuckle orientation`. Preserve successful cross-frame hand/leg ownership.

## Artifacts

- `34E_HighKnee_LeftHandOrientation_Review.png`
- `34B_vs_34E_Handedness_MobileCompare.jpg`
- `34B_vs_34E_Hand_Closeup.jpg`
- `34E_ExactSubmittedPrompt.md`

No new video was generated for this test. The older 34B, 34C, 34D and all diagnostics remain intact.
