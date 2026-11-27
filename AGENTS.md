# 5BX photographic production — agent working guide

## Purpose

Create a consistent, believable, high-quality 5BX workout series and carry it through to playable finished video. The real photographic Mark character is our current direction; the historical cartoon pipeline remains available as background reference.

The team has learned a great deal from experiments. The productive habit now is **use what works, finish the next stage, and keep the exercises moving**. A good reference card and its major-pose images form a handoff to video production. They can remain settled while we work on motion, editing, timing, and the final workout. We can revisit a still when a meaningful production issue emerges.

## Creative judgment and momentum

- Begin by locating the strongest existing asset, exact prompt, and most recent practical assessment. Current Chart 1 Google Drive exercise folders and loop-review links are the best starting points. Grok, Flow, and archives can fill a genuine discovery gap.
- Make routine creative, technical, and quality decisions autonomously. Good, usable movement and very high visual quality matter more than endlessly exploring alternate camera angles or trying to eliminate tiny aesthetic differences.
- Work on independent exercise activities in parallel. The existing engineering workflow currently tracks a maximum of two *registered active release jobs*; asset recovery, useful preparation, and editing on other exercises can progress alongside them.
- When a meaningful defect affects motion, anatomy, identity, usability, or final presentation, make a focused correction and resume the production flow. Keep a short factual note of the issue and outcome.
- Share concise progress with Charles: what is ready, where it lives, what is moving into the next stage, and any decision that materially changes the exercise. His early feedback is welcome, while routine intermediate choices can be completed independently.

## Production path

1. **Recover and reuse:** Find the card, individual high-resolution poses, clean exact prompts, raw video, and any three-repetition loop already created.
2. **Complete the useful reference packet:** A card can contain as many major phases as the exercise needs; create individual high-resolution poses for genuine gaps. Maintain Mark's identity, believable anatomy and joints, clear direction, shoes, and consistent scene intent.
3. **Generate or recover motion:** Use the best available Flow/Grok references and practical video settings. Approximately three coherent repetitions give the editor room to select a natural cycle.
4. **Edit and assemble:** Trim flawed frames, normalize scale, build loops and workout-length segments, place standing/floor poses in the gym, and add the editable exercise title, tip, and timer overlays.
5. **File and hand off:** Keep the current assets and clean prompts in the exercise folder, with the versioned QA note and historical alternatives accessible. Make the final playable video and relevant evidence easy for Charles to review.

The original 5BX movement description and the photographic motion contracts are useful guides for form and sequencing. Character poses may use natural, age-appropriate range rather than an unnecessarily extreme demonstration.

## Evidence, review, and ownership

The existing versioned QA note and `5bx-production` handoff comment are the shared production record. Record the source asset, exact submitted prompt, provider/model/settings, relevant media link or hash, practical form observations, and next action there. Use the existing photographic index for output links.

`READY_FOR_REVIEW` describes a specific **playable MP4** with technical, identity, form, and looping evidence summarized for Charles. `DONE` is reserved for Charles's explicit acceptance of that exact finished video. A technical test and a convincing still are useful evidence, while the final visual judgment belongs to the finished motion.

Protect private source media and treat publication as a separate, explicitly accepted step. Bring a material safety, rights, access, payment, or release decision to Charles as one concrete question while other work progresses.

## Engineering references

- `sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md`: detailed historical engineering controls and QA templates; consult relevant portions when a technical question calls for them.
- `photo_motion/README.md` and `photo_motion/CHART1_MOTION_CONTRACTS.md`: motion specs, provenance, and inspection tooling.
- For repository code changes, the available verification commands are:
  - `python3 -m photo_motion validate photo_motion/specs/*.json`
  - `python3 -m unittest discover -s photo_motion/tests`
  - `python3 -m unittest discover -s sprites/tests -p 'test_photo_*.py'`
  - `python3 sprites/kit/photo_workflow.py --repo-root . --check`
  - `python3 -m photo_motion.privacy_preflight --cached --check`

These checks support reliable engineering handoffs; the creative production decisions still require human judgment, momentum, and a finished video.
