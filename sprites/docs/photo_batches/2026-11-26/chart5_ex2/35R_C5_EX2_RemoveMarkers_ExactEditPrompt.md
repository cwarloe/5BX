# ID35R color-marker removal — one-variable edit request

## Exact prompt

Perform a STRICT MINIMAL RETOUCH of the supplied 2×2 35mm photographic contact sheet. The reference image is the master to preserve pixel-for-pixel except for four small temporary color-tracking elastic marker bands in EACH panel, sixteen total across the card. REMOVE ONLY the four conspicuously colored diagnostic bands on the boy in EACH panel A, B, C, D: the bright ORANGE and TEAL bands around his two upper elbows, plus the ORANGE and TEAL bands around his two ankles. Replace elbow-band strips with seamless natural pale skin matching adjacent forearm and upper arm. Replace ankle bands with seamless dark grey sock fabric of the same texture and shading as the rest of the sock. Do not change any other skin, anatomy, clothing, expression, hair, shoes, ground or background. If an ankle band in one pose is partially covered by a shoe, only retouch the visible strip. No colored bands or newly added wristband remain anywhere.

ABSOLUTELY PRESERVE four original photographs' compositions, exact subject identity and age, side and angle, lighting, lens, label A/B/C/D, whitespace/gutters, image quality. Especially freeze all four exercise poses and their biomechanics: Panel A both legs straight, hands behind head; Panel B FAR LEFT knee bent, NEAR RIGHT leg fully extended, RIGHT elbow moved toward LEFT knee; Panel C NEAR RIGHT knee bent, FAR LEFT leg fully extended, LEFT elbow moved toward RIGHT knee, torso rotated the other way; Panel D supine both legs straight. DO NOT mirror, swap legs, redraw arms, rotate his head, or reshape any joint. The left/right switch and elbow-to-knee orientation is now correct in reference; the ONLY intended change is removing colored elastic strips. Keep blue shirt, charcoal shorts, gray-yellow running shoes, dark gray socks, normal soft child physique, fair skin, slightly messy dark brown hair, the same track and grassy tree background.

This is image restoration/inpainting of tiny accessories, not a new composition or a new pose generation. Produce one clean unmarked 2x2 card of the SAME FOUR PHOTOGRAPHS.

## Input

`artifacts/parallel_batch_20261126/chart5_ex2/35R_C5_EX2_TwistSitup_ColorTracking_35mm_DIAGNOSTIC_PASS.png` (single reference, all four panels)

## Invocation

`image_gen__imagegen` edit via `referenced_image_paths=[image]`, `transparent_background=false`.
