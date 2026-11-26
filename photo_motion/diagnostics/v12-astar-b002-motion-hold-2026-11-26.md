# V12 A*→B*002 video diagnostic — independent HOLD

**Not exercise-form approved; not a complete two-exchange scissor-jump loop.**
The original provider MP4 was preserved privately, together with a final
independent QA report and per-frame evidence. Only safe byte hashes and
diagnostic observations are reproduced here; private scene/media locators,
submitted prompt and raw frames are not in Git.

| Evidence | Exact SHA-256 / observation |
| --- | --- |
| Unmodified V12 raw MP4 | `5680aff2e5811ef99d52a533a6c24405ad1d92ef66afa7bf9b37fb7e693d3fba` |
| Final independent QA report | `a1477c3d5ca7eae765bbf0d2377a467f4fe29021360805d78e16cea70f128d70` |
| Previous immutable native run | `cd098dc731c35283a78b47f500d357ecb0577654068f2f5fe7d95fe00e5ea14a` |
| Native provider debit | **3 credits**, settled; source gate checks immutable receipt against its actual scene ID |
| Exact video | H.264 640×360, 24 fps, 72 frames/3.0 s, with non-silent AAC |

Independent review: f0 visually matches grounded A*, f71 resembles airborne
B*002, and physical color markers appear to reverse without a clear marker
teleport. However f18/f24/f30 depict grounded walking/running with dropped
arms; f36 is a runner-like bent-arm hop, and clear two-shoe flight does not
appear until approximately f42. The background is stable in sampled regions;
AAC had decoded mean −31.1 dBFS and peak −10.1 dBFS despite the silent setting.
The report marks `FORM`, `CONTACT/FLIGHT`, `ARM_HEIGHT`, and `AUDIO` defects.
There was no every-frame manual framing certification or demonstrated full
A→airborne→C→airborne→A cycle.

V13 is **one experimental correction of arm movement only**, using the raw
V12 clip as Flow Video-to-Video input. Its hypothesis is that explicit arm
edits can repair runner-like upper-limb mechanics while preserving all other
video content. **Even a V13 arm-only result passing its narrow measurement
gate would leave the V12 grounded leg transition unresolved.** The source QA
verdict remains HOLD; neither the edit nor the automated preflight can
approve historical 5BX form, identity, release, or a finished loop.

See [`../V13_V2V_ARM_EDIT_PRECREDIT.md`](../V13_V2V_ARM_EDIT_PRECREDIT.md)
for the one-attempt method and decision rule. Keep further discoveries in the
existing photographic QA and experiment records rather than another board.
