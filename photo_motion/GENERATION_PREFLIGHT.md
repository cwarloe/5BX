# Unpaid photographic generation preflight (Lean 6S / poka-yoke)

This **read-only** control rejects malformed or drifting inputs *before* an
agent spends provider credits. It uses the **existing** private experiment
request format from [EXPERIMENTS.md](EXPERIMENTS.md), the existing motion specs,
and the source-embedded photographic QA handoff. It creates **no new status
ledger, approval database, reserved credits, media, or API request**.

## Integration sequence

1. Assemble a private request using `photo_motion.experiments` fields
   (`attempt_key`, `exercise_id`, `spec_path`, `submitted_prompt_file`, ordered
   `input_assets`, `provider`, `model`, `settings`, `estimated_credits`, etc.).
   The prompt text must be the exact bytes the worker intends to submit, not
   an unnamed or regenerated approximation.
2. Read the provider's **actual remaining, already authorized** budget; do
   not derive it from a subscription price, claim of free API credits, or
   unclaimed voucher. Use the same credit unit as `estimated_credits`.
3. Run preflight with local source-image bytes and digest declarations. Hold on
   any error. This check does not acquire a worker lease or authorize payment.
4. Acquire the runner's exclusive exercise lease and call
   `photo_motion.experiments.reserve(...)` against the **existing immutable
   provider-specific spending policy**. Reservation repeats byte checks and
   rejects duplicate `attempt_key`s and inadequate authorized balance.
5. Only then may an explicitly authorized runner dispatch a provider request.
   Capture actual provider/model/generation ID, promptly settle the charge,
   inspect the **real MP4**, and use the current QA/traveler handoff.

## API

```python
from photo_motion.generation_preflight import evaluate

receipt = evaluate(request, repo_root=".", available_credits="18")
if receipt["status"] != "PASS":
    # Stop before paid generation; errors contains the specific blocking defect.
    raise RuntimeError(receipt["errors"])
# PASS means inputs only. Still requires immutable budget reservation,
# exclusive runner lease, and the provider's supported credentials.
```

The CLI emits sanitized JSON, never the submitted prompt or private image
bytes:

```bash
python3 -m photo_motion.generation_preflight \
  --repo-root . \
  --request /path/to/private/request.json \
  --available-credits 18 --check
```

`--check` returns nonzero on `HOLD`. When credits are unknown, the preflight
**holds**, rather than inventing a free allowance. The caller-supplied credit
number is a consistency check, **not** a grant of spending authority.

## Digital 6S controls

| 6S action | Gate |
| --- | --- |
| Sort | Only versioned photographic Chart 1 contracts under `photo_motion/specs/`; an explicit `HOLD` cannot advance. |
| Set in order | Exact experiment request schema and exercise ID must match the motion-spec filename; files and phase contracts are hashed. |
| Shine | Source inputs must exist as independently decodable local JPEG/PNG/WebP bytes; broken, symlinked or remote-only reference declarations hold. |
| Standardize | Duration, 16:9 start frame, optional declared FPS, original locked camera, and approved photographic identity policy are checked. |
| Sustain | Existing source-embedded QA/WIP records must be consistent; an unseen active agent or missing exclusive lease remains an explicit warning. |
| Safety | Existing motion validator rejects impossible planned topology; an explicit kneeling push-up prompt direction that forbids required chest-floor contact is held before any credit reservation. Audio-policy conflicts and missing/insufficient budget also hold. Form safety and owner approval are **never inferred**. |

### Critical limitations

- **This gate validates the planned motion, not the generated motion.** No
  image inspection can substitute for independent physical-limb and exercise-
  form review of the actual MP4.
- **Prompt contradiction screening is intentionally narrow.** For a kneeling
  push-up contract that specifies `chest_position: touch_floor`, it catches
  some explicit instructions to keep the chest hovering or never touching at
  the bottom. It does not understand every paraphrase, recognize images,
  verify a positive prompt, or establish that the model complied. A top-pose
  instruction to keep the chest off the ground is not itself a contradiction.
  The receipt never quotes the private prompt. Review exact wording and
  physical contact manually even after a `PASS`.
- Model behavior may shift without notice; a successful preflight is not a
  canary test for an AI provider, nor a guarantee that the output will be good.
- An input can change after preflight. The paid runner must reserve/recheck
  exact bytes and acquire a lease immediately before submission; a `PASS`
  receipt does not establish mutual exclusion.
- The existing QA source index admits unregistered external workers; a queue
  with zero declared active records **does not** prove zero real agents.
- The current pilot uses one 16:9 motion format. New aspect ratios and
  providers must introduce an explicit versioned policy rather than silently
  relaxing the check.
- Approved photographic direction is a policy reference, not proof that an
  inaccessible private image is genuinely the same child; independent video
  identity QA remains required.

## Verification

```bash
python3 -m unittest photo_motion.tests.test_generation_preflight -v
python3 -m photo_motion validate photo_motion/specs/*.json
python3 sprites/kit/photo_workflow.py --repo-root . --check
```

These tests use synthetic local images only. They spend no Google Flow,
Grok Imagine, xAI API, Gemini API, or ElevenLabs credits.
