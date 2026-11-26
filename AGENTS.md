# 5BX agent operating contract

This repository is an ongoing photographic workout-video production line.
**The current creative target is real photographic 5BX motion, not the legacy
cartoon sprite assets.** The old cartoon pipeline is retained for regression
and must not become the default for new photographic work.

## Autonomous production

- Work independently within the established exercise/motion contracts,
  identity references, QA rules and existing permissions. Make ordinary
  technical/prompt/test decisions, preserve failed examples, and test a
  specific defect before changing its supposed solution.
- Do **not** ask Charles to inspect an incomplete still, card, draft prompt,
  partial clip, or routine intermediate correction. Early feedback is optional
  and never substitutes for independent QA. Continue other ready work while
  waiting for a final owner decision.
- Consult `sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md` and
  `photo_motion/README.md` before new media work. The original booklet and
  physical motion evidence take precedence over AI-generated appearance.
- Keep the agent-production WIP limit to **two exercises**; independent
  exploratory work stays labeled `EXPERIMENTAL`. Mark current work in its
  existing QA note using the structured `5bx-production` handoff comment;
  see `sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md` for the template.
- Do not create a second approval ledger. Store the exact output, submitted
  prompt, model, input identity, QA, defects and next action beside the
  existing versioned production QA record. Register output links in the
  canonical photographic mobile index/inventory.

## Review versus done

- `READY_FOR_REVIEW` means the complete **playable MP4** is linked, technical
  intake and independent form/motion/loop/identity checks are documented,
  exact hashes/provenance are retained, and one concise owner review packet
  is ready. It exits active agent-production WIP and enters the owner buffer.
- `DONE` requires **Charles's explicit acceptance of that exact video**.
  Agents may prepare or validate a proposed review packet but never create
  owner acceptance or publish media on his behalf. A rejected version returns
  to rework with a named defect.
- A technical `PASS`, successful command, attractive image, or authored
  owner-looking field cannot prove form safety or a real owner's decision.

## Escalate only when genuinely blocked

Escalate a specific unanswerable historical-form/safety requirement, missing
required asset/access, permission boundary, newly proposed paid usage, or
material change of product scope/identity/release rules. State the evidence,
alternatives and recommended option as **one concrete question**. Continue
unrelated safe work instead of idling the production line.

## Verification and ownership

Run `python3 -m photo_motion validate photo_motion/specs/*.json`,
`python3 -m unittest discover -s photo_motion/tests`,
`python3 -m unittest discover -s sprites/tests -p 'test_photo_*.py'`, and
`python3 sprites/kit/photo_workflow.py --repo-root . --check` before handoff.
The last command validates owner-ready evidence and the declared two-item WIP
limit; it **cannot** prove what an inaccessible private MP4 actually depicts.
Do not overwrite another active agent's media or draft. Prefer small tested
PRs, exact asset hashes, and safe metadata in GitHub; keep private raw videos
in the existing controlled review archive.
