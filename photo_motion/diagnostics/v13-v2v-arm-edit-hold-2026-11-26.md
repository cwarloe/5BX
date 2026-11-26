# V13 raw-V12 arm-only video edit — independent diagnostic HOLD

**Verdict: `ARM_EDIT_METHOD_DIAGNOSTIC_FAIL`.** The single V13 Video-to-Video
edit did not materially correct V12's lowered, running-style arm trajectory.
It did not repair the grounded running/stride sequence, and is **not** a
historically correct scissor-jump video, a complete A→C→A cycle, an approved
identity, or a release candidate. This is a narrow engineering-method
finding, not an owner form decision.

| Evidence | Exact SHA-256 / observation |
| --- | --- |
| Unmodified V12 source MP4 | `5680aff2e5811ef99d52a533a6c24405ad1d92ef66afa7bf9b37fb7e693d3fba` |
| Unmodified V13 output MP4 | `c1e63b54a82536a29638a299dd426b711aeabbe6c220901135aeeadc3a2c3d13` |
| V13 final independent QA report | `abb779bc8d2da304d97d87c9c26fe3006521e3b26016e3e24a580834a9ec7f6e` |
| Actual video | H.264 640×360, 24 fps, 72 frames/3 s, non-silent AAC; **3 credits** |

**Preregistered question:** can an arm-only edit of the exact failed V12 raw
replace its pumping/dropped wrists with approximately shoulder-level,
extended reciprocal arms *while preserving* the subject, marker ownership,
leg movement, background, camera and endpoints? The independent comparison
examined the same decoded-frame positions and used the V13 **25-pixel**
wrist-to-shoulder vertical limit. That screen-space limit is an engineering
diagnostic proxy, **not** an original-booklet form tolerance.

| Zero-based frame | V12 bad wrist offset | V13 bad wrist offset | V13 observation |
| --- | ---: | ---: | --- |
| 18, teal/rear | 60 px | **59 px** | Grounded runner/lunge remains |
| 24, orange/forward | 49 px | **48 px** | Supported stride remains; other wrist obscured |
| 30, orange/rear | 67 px | **65 px** | Grounded crossover remains |
| 36, orange/rear | 63 px | **63 px** | Raised-knee runner hop remains |

All four measured failures remain above 25 px. A separate deterministic
72-frame color-component trace co-observed orange wrists in **70 frames**
(median V12→V13 displacement **2.434 px**) and teal wrists in **60 frames**
(median **2.651 px**). These tiny positional changes corroborate little
effective arm redirection; a color centroid is **not** a certified joint
tracker or anatomical left/right proof. Seven selected frames were annotated,
with all other arm positions **UNKNOWN**, every elbow **UNKNOWN**, and no
human form attestation. The analysis therefore cannot claim an all-frame
arm-height or elbow-extension PASS. The late airborne/end pose is broadly
preserved, but the earlier incorrect contacts persist. The original AAC was
non-silent despite the silent setting; a muted derivative cannot change
the raw-output result.

**Stop rule:** do not repeat the same-source arm-edit/prompt paraphrases for
this defect. Preserve raw video, exact submitted prompt, frame-hash-bound
annotations and full QA **privately** in the existing production archive;
none are included here. A separately qualified, consented first-party
physical motion reference or genuinely phase-controlled method is the next
testable direction. See the [V13 original precredit gate](../V13_V2V_ARM_EDIT_PRECREDIT.md)
and [motion-capture protocol](../FIRST_PARTY_SCISSOR_MOTION_CAPTURE.md).
