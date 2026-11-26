# V14 A*→grounded C* endpoint video — independent diagnostic HOLD

**Verdict: `V14_GROUNDED_ONE_FLIGHT_DIAGNOSTIC_FAIL`.** The single 3-second
Frames-to-Video segment did contain actual simultaneous dual-shoe flight
and ended in a C*-like opposite grounded stance. But **grounded walking/running
steps preceded the jump**, contradicting the narrow V14 hypothesis. Its
arms also failed the observed diagnostic geometry. It is **not** a correct
Chart 1 Exercise 5 segment, a two-exchange A→C→A loop, an approved exercise
form, or a release candidate.

| Evidence | Exact SHA-256 / observation |
| --- | --- |
| Exact A* PNG input | `777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38` |
| Exact grounded C* PNG input | `04eb4f9d9fe1d1944da36ba007fb7611329d19c19bddebfe983c8182a583e72b` |
| Held-out B*002 (not a Flow input) | `c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886` |
| Unmodified V14 raw MP4 | `667be2bc8665e6fc427384c293a4d87c61254f6f695598192c3057b42fc45e44` |
| V14 final independent QA report | `753f6ca0d3d2d22a3b3484bbf7768025a228d1fe63031b74f73edeb26b2b8b20` |
| Actual video | H.264 640×360, 24 fps, 72 frames/3 s, non-silent AAC; **3 credits** |

**Preregistered question:** can replacing V12's airborne B*002 endpoint
with the exact opposite **grounded C*** endpoint eliminate grounded
walking/running steps between A* and one actual airborne exchange? The
V14 gate requires at least two consecutive both-shoes-clear frames,
an opposite planted end stance and **no intervening grounded gait**.
This is a single A*→C* experiment, never a proposed full scissor cycle.

| Zero-based frame (24 fps) | Independent observation |
| --- | --- |
| 0 | Grounded A*-like start, full subject visible |
| **18 / 24 / 30** | **Grounded running/lunge contacts before takeoff — falsifies the hypothesis** |
| **35–36** | Two consecutive independently inspected frames with both shoes airborne; f36 approximate clearances **11 px** and **34 px** above planted track line |
| 39–56 (sampled) | Prolonged oversized split/bound, not a controlled stationary scissor exchange |
| 57 | First visible front-shoe landing after the large leap |
| 71 | Opposite C*-like grounded end, **no C*→A* return flight** |

Against a **25-pixel** wrist-below-shoulder screen-space engineering limit,
independent AI visual annotations observed **six violations in five sampled
frames**: frame 18 teal **83 px**; frame 30 orange **47 px**, teal **35 px**;
frame 36 orange **73 px**; frame 42 orange **63 px**; frame 48 orange
**29 px**. The arm metric returned `FAIL_OBSERVED_GEOMETRY`; elbow shape,
anatomical right/left, fine finger orientation, all-frame framing and
historical exercise correctness were **not** certified. The color-component
tracker was ambiguous in occluded/mixed-color frames and cannot prove
marker teleport or limb assignment. There is no defensible positive finding
of an extra or reversed hand from these frames.

All 72 video frames decoded. A full-stream temporal comparison found no
technical cuts, holds or reverse-pivot alerts, and selected background
regions remained stable. The first/last subject-region pixel errors against
the respective stills were approximately **14.87/255** and **14.74/255**;
these are relative appearance measurements, not exact endpoint matches or
anatomical validation. Original AAC was **not silent** despite the silent
setting. Technically successful video decoding and genuine flight cannot
override the observed grounded-gait failure.

**Stop rule:** no blind A*/C* endpoint- or prompt-only retake under this
method. Keep the exact raw MP4, submitted prompt, annotated frames, full QA,
settings and cost receipt **privately** in the existing production record;
only hashes and safe observations are public here. Next qualify a
consented first-party adult physical motion reference and verify actual
provider motion conditioning before spending further credits. See the
[V14 original precredit gate](../V14_GROUNDED_ENDPOINT_PRECREDIT.md) and
[motion-capture protocol](../FIRST_PARTY_SCISSOR_MOTION_CAPTURE.md).
