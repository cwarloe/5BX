# Temporal screening evidence — archived photographic knee-push-up #10

Read-only technical analysis on 2026-11-26, using `photo_motion.temporal_qa`. **No new media was generated, no original changed, and no exercise form was approved.** The archive's existing number/status remains authoritative.

- Archived original: [video 10, blue-shirt kneeling push-up](https://drive.google.com/file/d/1uNvFvPe2VyyWuaHq7gyOCoCQH9Jv12Kp/view)
- SHA-256: `9c9e3da1421adb506567dec0d1daaf46c47568a40f7e4e0f7ed4288561cf474f` (matches previous repository record)
- 1280×720 H.264, 24 fps, six seconds, **144 decoded frames**.
- Scanning: 160×90 grayscale, mean absolute frame-to-frame pixel change; a low-motion threshold of 0.5/255 and minimum continuous duration 0.5 s. Declared start hold: 0.0–1.0 s (as described in the original Flow prompt).
- Results: **75/143** near-identical *screen-space* transitions, median frame delta **0.4803/255**, maximum **1.2049/255**; median background-border delta **0.1286/255**. No potential abrupt scene cut or decoded timestamp anomaly under these thresholds.
- Two stillness intervals require closer visual review: **4.500–5.292 s** (0.792 s), **5.333–5.958 s** (0.625 s). These could be intentional final-position holds after the up stroke, not an interruption. The script cannot distinguish this mechanically.

**What this tells us:** coding only the first/middle/last sample and codec validates too little. A frame may decode correctly while motion stalls or endpoint joints drift. The present screen-space test identifies the moments to inspect but is not an anatomical detector. Before regenerating at paid cost, compare full-resolution knees/palms at start and near 4.5–6.0 s against fixed track marks; view normal-speed playback for ghosting and actual continuous ascent.

Keep the decision in the [existing video 10 pilot record](../../sprites/docs/PHOTO_PILOT_RUN_KNEE_PUSHUP_CURRENT_IDENTITY_2026-11-25.md), not a new release tracker. **Disposition: ENGINEERING DIAGNOSTIC / NOT_EVALUATED FOR FORM.**
