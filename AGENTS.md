# 5BX photographic production — agent working guide

## Purpose

Create a consistent, believable, high-quality 5BX workout series and carry it through to playable finished video. The real photographic Mark character is our current direction; the historical cartoon pipeline remains available as background reference.

The team has learned a great deal from experiments. The productive habit now is **use what works, finish the next stage, and keep the exercises moving**. A good reference card and its major-pose images form a handoff to video production. They can remain settled while we work on motion, editing, timing, and the final workout. We can revisit a still when a meaningful production issue emerges.

## Active production-source gate (Charles directive, 2026-11-27)

**Mandatory before starting ANY new production task or Grok/Flow/image-generation job.** These are current decisions, not optional style preferences.

**Start-of-task refresh (STOP if skipped):** (a) fetch current GitHub `main` HEAD, recent commits and open PRs; (b) read current `AGENTS.md`, `CLAUDE.md`, applicable merged production docs and the newest Drive Chart 1 traveler/exercise-folder QA; (c) check whether newer completed work already solves the task, and whether open PRs contain relevant changes; (d) compare instructions and asset versions, resolve conflicts using Charles's newest explicit decisions and the approved white-reference set; (e) record the commit SHA, Drive file IDs and selected references in the handoff BEFORE submitting a generation. Do not treat open PRs as merged or auto-merge them merely because they are newer; only merge compatible, tested engineering PRs within prior authorization. No new generation or archive selection until this refresh completes.

1. **Source order:** Charles's latest explicit direction > current Google Drive `00_CHART1_TRAVELER__OPEN_FIRST.md` and its per-exercise working folder > current approved image/card and clean prompt > historical experiments. Search recent Drive and GitHub first; do not pick a reference merely because it appears in Flow/Grok history.
2. **Approved image family:** Use the current **white-background, photorealistic Mark** exercise cards and individual high-resolution poses from the designated Drive exercise folder. For Chart 1 Exercise 5b, the current set is the **six accepted white-background pose PNGs**, six-phase card, two leg-leading cards, and clean scissor prompt linked by the traveler and `QA_SCISSOR.txt`. Existing verified white-background loop footage is the first editing candidate. Verify the actual images before submission.
3. **Hard exclusion:** Do not upload, reference, condition on, regenerate from, or reuse any outdoor running-track/grass/trees assets, old marker-based track images, legacy Flow scene/video history, or rejected/archived images for new video runs. The older original V2 identity sheet with track scenery may be consulted solely for **visual comparison** while preparing a clean-background identity reference; never send the track-containing original to a video model. A new four-view white-background V2 derivative is under owner visual review and must not silently replace the immutable identity authority. These remain diagnostic history only. This overrides any older traveler line or prompt suggesting outdoor references as extra conditioning.
4. **Motion:** Small, modest schoolboy exercise movements; scissor hop about 3–4 inches, correct physical near/far leg exchange, compact relaxed arm swing rather than straight shoulder-height/90-degree arms, no ballet, gymnastics, extreme split, sprint, long leap, or unnatural anatomy. Same youthful character identity, shorts, footwear, and stable camera.
5. **Presentation (current):** Finish **white-background exercise footage first**; gym integration is explicitly deferred and is not a prerequisite for the current cut. If a gym is revisited later, its back wall is **cream** with no permanent logo. Olive drab, burnt orange and cream belong on the cue cards. Put the **exercise title and instructional tip upper LEFT** and the **countdown timer upper RIGHT**. Lower-left/right CFC mark, Charles portrait or a combination remain **open design choices**; do not lock one in or cover exercise motion.
6. **Preflight evidence:** Before spending credits, record the exact Drive URL/file IDs of each chosen approved reference, prompt text and exercise/version, plus a short visual check confirming WHITE background and correct identity/poses. If any input conflicts with these rules, **do not generate**; locate the correct current working asset or report the gap. Once generated, record provider, output link and a frame-level pass/reject result. No generated video is final until Charles approves the exact output.

## Creative judgment and momentum

- Begin by locating the strongest existing asset, exact prompt, and most recent practical assessment. Current Chart 1 Google Drive exercise folders and loop-review links are the best starting points. Grok/Flow history and archives may be inspected for diagnostic context only; they are not sources of new-generation image inputs.
- Make routine creative, technical, and quality decisions autonomously. Good, usable movement and very high visual quality matter more than endlessly exploring alternate camera angles or trying to eliminate tiny aesthetic differences.
- Work on independent exercise activities in parallel. The existing engineering workflow currently tracks a maximum of two *registered active release jobs*; asset recovery, useful preparation, and editing on other exercises can progress alongside them.
- When a meaningful defect affects motion, anatomy, identity, usability, or final presentation, make a focused correction and resume the production flow. Keep a short factual note of the issue and outcome.
- Share concise progress with Charles: what is ready, where it lives, what is moving into the next stage, and any decision that materially changes the exercise. His early feedback is welcome, while routine intermediate choices can be completed independently.

## Production path

1. **Recover and reuse:** Find the card, individual high-resolution poses, clean exact prompts, raw video, and any three-repetition loop already created.
2. **Complete the useful reference packet:** A card can contain as many major phases as the exercise needs; create individual high-resolution poses for genuine gaps. Maintain Mark's identity, believable anatomy and joints, clear direction, shoes, and consistent scene intent.
3. **Generate or recover motion:** Use the best available Flow/Grok references and practical video settings. Approximately three coherent repetitions give the editor room to select a natural cycle.
4. **Edit and assemble:** Trim flawed frames, normalize scale, build loops and workout-length segments, retain the current white-studio footage, and add separate editable exercise title/tip (upper left), countdown (upper right), and optional subtle lower-corner branding overlays. Gym integration is deferred.
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
