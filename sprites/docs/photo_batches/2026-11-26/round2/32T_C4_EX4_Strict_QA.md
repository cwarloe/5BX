# 32T skeptical QA — fresh master-body-first wide-hand push-up

**Status: TEST / NOT APPROVED.** The 2×2 pose/contact structure survived, but there is still visible upper-arm and shoulder bulk relative to the approved relaxed master. Do not make this the production identity anchor without explicit human visual signoff. 32S remains independently vetoed; 32T is a *fresh* attempt, not a replacement acceptance.

## Comparison to 32R and v2 master

| Check | Evidence | Verdict |
|---|---|---|
| Fresh synthesis rather than shallow recolor | 32R→32T whole-frame RMSE 5,046.9 / 65,535 = **7.70%**, vs 32R→32S **2.51%** previously | Fresh but not proof of identity improvement |
| Four exercise phases | A and C low, B and D high; stationary camera and red track | PASS |
| Palm/toe load bearing | In all four panels both hands and toes meet ground; near and far palms are visible | PASS |
| Wide-hand placement | Hands clearly spread beyond torso/shoulder axis in all tiles | PASS |
| Far elbow/hand separation | Far arm appears as separate bent limb in low frames, not an extra limb; no obvious hand duplication | PASS on visual inspection at 1536×1024 |
| Elbow/knee anatomical realism | Reasonably natural in all phases, no knee contact or glaring hyperextension | PASS |
| Age/face/outfit | Continues recognizably junior-high; shirt blue, shorts charcoal, sneakers gray-yellow, wristband dark | PASS, small scene/face differences unavoidable in fresh generation |
| Shoulder/upper-arm silhouette | Some reduction in low-frame arm width is perceptible, but upper arms retain a notably solid/trained appearance vs relaxed standing v2; top-right high plank still shows prominent shoulder curve | **FAIL strict identity-softness threshold / human review needed** |
| Body/thigh/seat size | Does not appear significantly skinnier or bulkier; track angle, horizontal body alignment shifted slightly | PROVISIONAL |

## Decision

Mechanics **PASS**. Anatomical identity softness **NOT YET PASS** under a deliberately strict standard; the current image remains a diagnostic. The dual-reference pose-only instruction successfully avoided obvious contact corruption but did not reliably suppress the model's tendency to add upper-body volume in load-bearing exercise. For a production card, favor the known 32R mechanics until a stronger visual body-identity match is achieved. Human eyes may judge whether 32T's modest shoulder change is sufficient.

## Assets

- `32R_C4_EX4_WideHandPushup_SoftYouthEdit_CANDIDATE.png` — before, pose authority.
- `32S_C4_EX4_WideHandPushup_SoftDefinition_IdentityLocked_CANDIDATE.png` — earlier vetoed soft-definition edit.
- `32T_C4_EX4_WideHandPushup_MasterAnatomyPoseOnly_DIAGNOSTIC.png` — fresh 2×2 test, not approved.
- `32T_C4_EX4_ExactPrompt.md` — exact submitted prompt.
