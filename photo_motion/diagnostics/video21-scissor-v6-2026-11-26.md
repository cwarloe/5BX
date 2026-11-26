# Chart 1 scissor jumps — original photographic Flow video #21 diagnostic

**Observed 2026-11-26 UTC. Result: FAIL INTERNAL QA / HOLD; NOT READY FOR OWNER REVIEW.** Video #21 is a genuine 144-frame photographic MP4, **not** a valid two-exchange scissor-jump cycle, seamless loop, or releasable workout exercise. The owner decision remains reserved for an independently checked **final playable version**. This diagnostic does not replace the original, invent an owner approval, add a traveler/board, publish media, or authorize additional credits beyond the existing workstream allowance.

## Immutable source, prompt, generation and cost evidence

| Item | Exact observed / recorded value | Evidence boundary |
| --- | --- | --- |
| Original output | `21-scissor-v6-raw-original.mp4`, **2,919,630 bytes** | Full original privately retained outside Git; independently rehashed and decoded |
| Original SHA-256 | `b135e5ddb195dd585e6cc68c24fa6bdef68456895a7fc34a556d78d0e4679c04` | Never re-encode or silently replace this failed take; all frame/audio findings below refer to these bytes |
| Provider/model | Google Flow, **Omni 1.2 Flash**, one requested output | Recorded in submitted generation recipe; model identity is provider metadata, not encoded proof in H.264 |
| Flow scene | `ce40baa6-cb6c-4c1b-8f96-913c5bc79c5b` | Observable Flow scene locator, **not independently proven** to be an internal model-job ID |
| Actual input | V6 panel-A 16:9 prepared photographic PNG, 1280×720; SHA-256 `7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f` | Exact uploaded source-byte hash documented and verified in the separate [V6 pre-credit check](../V6_PRECREDIT.md); **single diagnostic pose, not motion evidence** |
| Original card | Verified V6 tagged 1536×1024 PNG, SHA-256 `4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2` | Verified A crop `(4,4,764,508)`, 68-pixel mirrored side padding, then Lanczos whole-frame 1280×720 export; mirrored scene detail is not new photographic evidence |
| Prepared-frame manifest | SHA-256 `74ca0c8f1fbb301465fedb5d2bed14c373e7868b9fc343d2b419e98284d56a1a` | Deterministic transformation record, **not identity/form approval** |
| Motion contract | `photo_motion/specs/chart1-scissor-jump.json`, SHA-256 `ee28fda9e4f0701547e7339b0e9efa9943a603f395fc3cddabe0139eceb2170d` | The source-authoritative target is the original Chart 1 Exercise 5 **two distinct airborne exchanges with an opposite grounded landing between**, not the model's observed run-like animation |
| Exact submitted prompt | SHA-256 `8fc31aa3a744e037c036b5d2a18a125c7e115e61df8da1ace7c33c52394e1bdf` | Locally archived verbatim `FINAL-FLOW-SUBMITTED-EXACT.txt`; a filename alone cannot prove provider-side bytes, so retain submission evidence separately |
| Generation recipe | SHA-256 `65136d60aee68c7e2f6d90beb4673479f4fe2f3c753ad6394a7688b7a67505e4` | Provider metadata and exact input/prompt digests recorded in private `generation_recipe.json` |
| Provenance inspection | SHA-256 `ba4dc2c32daf508167e6df600fa9e0762965bbfb5337aff0d0f1a2e632fe8cc8` | Existing `inspection.json` binds this original MP4, contract, recipe, sampled frames and codec; automatic technical warnings were empty **despite the audio stream**, so do not treat empty warnings as a PASS |
| Temporal diagnostic | SHA-256 `bcb5cabbed2eedfffc312ca2ce9cd1ccaa290d5043dc037f3d73f07f2f661d3b` | Existing private `temporal.json`; screen-space timing only, no anatomical form certification |
| Quote / actual charge | **18 quoted, 18 charged Flow credits**; account balance observed **852 → 834** | Provider/account observations recorded in recipe; do not generalize this price to future attempts or assume refund |
| Provider configuration | Six-second target, **16:9**, one output; requested seed and provider FPS **unknown/null** | Unknown parameters stay unknown; identical input/prompt cannot guarantee deterministic AI re-generation |

The original MP4, full-resolution frame audit/contact sheets, source PNG, prompt and generation recipe belong in the controlled **private** video archive. No media bytes, model-generated frames or private audio are committed here. These hashes are an audit trail but **cannot recover** a lost original without an accessible archived copy.

## Independent decoded measurements — actual video, not a pose card

| Check | Observation | Interpretation |
| --- | --- | --- |
| Video stream | H.264/yuv420p, **1280×720**, **24 fps**, **144 decoded frames**, video duration **6.000 s** | Genuine moving video, not a still image or cartoon; container duration ~6.0373 s includes the longer AAC track |
| First-frame/source image | Original input vs decoded frame 0: **RGB MAE 4.264/255**, **PSNR 32.71 dB** | Strong source-frame appearance registration subject to lossy encoding; **not evidence of correct later anatomy** |
| Frame timing and motion | 10 nearly identical transitions / 143; **zero** sustained still spans, cut candidates or frame-pacing anomalies | `temporal_qa` found real pixel motion and ordinary timestamps; **does not infer a correctly executed exercise** |
| Original video loop | Decoded frame 0 vs frame 143: **RGB MAE 9.913/255**, **PSNR 18.90 dB**; inspector's separately scaled seam MAE **8.978/255** | Obvious arm/posture mismatch at wrap; a numeric seam metric cannot certify physical contact/pose closure |
| Audio | **One AAC-LC stereo stream, 48 kHz**, non-silent; FFmpeg `volumedetect` mean **−40.8 dB**, peak **−11.7 dB** | **FAIL `AUDIO`**: submitted prompt prohibits audio. Stripping audio into a *separate derivative* can fix delivery format, but not the original motion; original must remain unchanged |
| Framing/headroom | Full/partial head crosses the top edge in **59 of 144 reviewed frames (~41.0%)**, grouped approximately frames **25–50** and **69–101** | **FAIL `FRAMING`**: the prompt's complete head/framing request did not hold during high motion; counts are from independent full-frame visual review, not a pose detector |
| Appearance | Blue shirt, charcoal shorts, shoes, diagnostic wrist/ankle marker colors and broad photographic identity remain recognizable; some mirrored background-edge features persist | Conditional appearance consistency only. No approved v2 master identity equivalence, physical anatomical left/right, or final photographic release can be inferred from these frames |

**Critical distinction:** The existing `inspection.json` recorded an empty `technical_warnings` array despite showing one AAC stream in its video metadata. That observation only reflects the inspection/policy version used at the time; it is **not** an audio approval or evidence that the video complies with the prompt. The newer audio-intake policy must be applied to this same immutable original on any future release review.

## Required phases versus what all 144 frames actually show

The observer traced the original four colored **physical marker locations** at the target phase times and between them, without equating color pairs to proven anatomical left/right. Frames below are zero-based 24-fps indices. Short flight intervals are visually estimated from shoe/track separation and shadows, **not independently calibrated ground-contact measurements**.

| Target / failure code | Required documented pose | Observed original #21 | Status |
| --- | --- | --- | --- |
| `A` / start, frame 0, 0.000 s | Orange ankle/leg **BACK**, teal ankle/leg **FORWARD**; orange wrist/arm **FORWARD**, teal wrist/arm **BACK**; arms straight near shoulder height | Starts substantially in that source pose; first-frame registration strong | Source start observed |
| `B` / first flight, target 1.4 s | Both shoes leave track while physical legs and opposite arms **exchange fore/aft roles** | First apparent short both-feet-up hop roughly frames **35–39** (1.46–1.63 s), but motions resemble a stride/hop rather than a completed physical-leg exchange | `FLIGHT_2` only partially evidenced; exchange **FAIL** |
| `C` / opposite landing, frame 60, 2.500 s | Physically **orange ankle ahead / teal ankle behind**; arms opposite starting positions; a grounded opposite split stance must separate flights | **Still orange ankle BACK / teal ankle FORWARD**, orange wrist FORWARD / teal wrist BACK, both shoes close to track. The mandatory opposite landing **never materializes** | **FAIL `POSE_A_C_A`, `MOTION`** |
| `D` / second flight, target 3.8 s | Second independent airborne exchange returns physical original fore/aft order | Second apparent two-shoe flight around frames **84–94** (3.50–3.92 s); subject reaches/crosses top frame edge, and no tracked-leg fore/aft reversal is demonstrated | Two hops are **not** two verified scissor exchanges |
| `E` / final, frame 143, 5.958 s | Original starting full-body stance, arms near shoulder height, foot marks/framing matched for seamless loop | Leg order remains originally led, but orange forearm slopes down and teal wrist sits near hip; overall pose differs markedly from frame 0 | **FAIL `ARM_FORM`, `LOOP`** |

Marker observation: orange/teal markers appear to remain attached to their original observed wrists and ankles throughout the inspected frames, **without obvious marker migration**. This is a useful continuity signal, but it does **not** mean the limbs performed the required exchange. **Do not miscode the failure as `LIMB_OWNER`: the demonstrated defect is unchanged physical fore/aft order and lowered arms, with anatomical left/right still unproven.**

The two visible hops do not rescue the video: Chart 1's source motion requires **changing the position of arms and legs before landing**, repeating to return to the start. A repeated same-lead running hop is a different exercise. The contract must **not** be weakened or relabeled to make this visually plausible output pass.

## Repeatable read-only QA (no provider call)

Use a locally recovered private original matching `b135e5dd…e4679c04`. Replace placeholder paths with private non-repository paths; each `--out` directory or JSON report destination must be **new**, so earlier evidence cannot be overwritten.

```bash
sha256sum /private/21-scissor-v6-raw-original.mp4
ffprobe -v error -show_format -show_streams -of json /private/21-scissor-v6-raw-original.mp4
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames,duration,avg_frame_rate,width,height -of json /private/21-scissor-v6-raw-original.mp4
python3 -m photo_motion inspect photo_motion/specs/chart1-scissor-jump.json \
  /private/21-scissor-v6-raw-original.mp4 \
  --recipe /private/generation_recipe.json --out /private/21-qa-new-phase-samples
python3 -m photo_motion.temporal_qa /private/21-scissor-v6-raw-original.mp4 \
  --report /private/21-qa-new-temporal.json
ffmpeg -nostdin -hide_banner -i /private/21-scissor-v6-raw-original.mp4 \
  -map 0:a:0 -af volumedetect -f null -
```

For form review decode **all** 144 frames in order with FFmpeg and inspect full-resolution examples at frames **0, 35–39, 60, 84–94, 143**, plus the head-cropping intervals above. Track each colored ankle and wrist as a *persistent physical point*, not by changing screen-side labels. Compare the first and last frame/subject region; preserve a source-versus-first-frame RGB comparison separately. A contact sheet may help navigation but is **not** itself a video or a complete form approval. If the recovered video bytes differ, **stop** rather than attaching this take's findings to another clip.

## Falsifiable next diagnostic: one change, preserve every other variable

**Observed failure mechanism to test:** A single V6 start photograph plus prose describing “two scissor jumps” induced **two same-lead running-style hops**, not a physically opposite C landing. We cannot prove whether the model's limitation is the term “scissor,” underconstrained middle pose, or the source image; those remain hypotheses.

**Next controlled version #22 hypothesis:** Change **only the motion wording for the intermediate C landing** in the verbatim paid prompt. Explicitly require a visible, briefly *held* opposite grounded split stance at about **2.5 s**: the **same physical orange-tagged ankle in FRONT** and teal-tagged ankle **BEHIND**, orange wrist back / teal wrist forward, before the second separate hop. Keep the exact **prepared PNG hash `7758266c…`**, video model, six-second duration, 16:9 format, one-output count, camera, outfit, and other prompt controls unchanged. This isolates whether the model responds to an unambiguous intermediate pose-lock instead of reverting to jogging priors. Do **not** change headroom, framing method, audio wording or source identity in this same causal test; record those known defects for separate corrections.

**Pass/fail learning criterion:** At the real frame-60 C landing, an independently tracked **physical orange ankle must clearly lead** the teal ankle, with an unambiguous grounding interval between **two** different flights, and arms opposite A. If #22 still repeats the same lead, preserve both failures and move to source-verified pose/keyframe control instead of consuming repeated credits on paraphrases. Even if C succeeds, #22 remains **HOLD** until arm form, full headroom, silent-delivery policy, true loop seam, anatomical identity, and the owner's final exact-video approval are separately satisfied.

The existing approved **200-credit provider-specific diagnostic allowance** may continue to support a **new reserved, uniquely identified and currently quoted** exploratory attempt without treating Charles as a frame-by-frame production station. Record actual charges, source/prompt/output hashes, scene ID and failure codes under the existing private experiment receipts. **No spend, retry, video transformation or release is performed by this report.** Charles alone can accept a final playable version; **#21 is not owner-review-ready** and should not be sent to him as an incomplete decision packet.
