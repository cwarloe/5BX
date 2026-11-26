# ID32R — Chart 4 wide-hand push-up — original vs softened-youth edit QA

**Visual disposition: CONDITIONAL IMPROVEMENT.** Prefer #32R for the next *character-identity comparison*, but retain the original #32 for a biomechanics fallback and do not declare final animation approval.

## Asset audit

| Item | Original ID32 | Revised ID32R |
| --- | --- | --- |
| File | `32_C4_EX4_WideHandPushup_FourPhase_35mm_CANDIDATE.png` | `32R_C4_EX4_WideHandPushup_SoftYouthEdit_CANDIDATE.png` |
| Native size | 1536 × 1024 | 1536 × 1024 |
| SHA-256 | `e9941a0cb97950e2544181153d58b1e8630b6964bf22b736e02745be2c9c7c1f` | `aa962fd98754b7f8f3308568fc907f8c2691b999d435fd437ce355d6e7de7c86` |
| Intended treatment | Original four-phase 35mm candidate | One local shoulder/upper-arm contour-softening pass |
| Pixel comparison | — | Normalized ImageMagick `compare -metric MAE` = **0.0201651** (about 2.02% average channel difference), consistent with visually small but not pixel-identical generative editing |

Generated image source: `generated_images/exec-33547ed6-15a5-4aa1-80af-7e73e3a6232c.png`. Exact submitted edit prompt: `32R_C4_EX4_ExactEditPrompt.md`. Reference roles were (1) source image edit target, (2) approved v2 master as identity/softness authority. One edit attempt, no additional retouching.

## Skeptical side-by-side visual gates

| Gate | Before (#32) | After (#32R) | Verdict |
| --- | --- | --- | --- |
| **Shoulder/deltoid definition** | Broad, harder shoulder caps and deep upper-arm separation, boy can read athletic/older | Edges and highlights are slightly smoother and more uniform; upper arms still full enough to support body | **Modest improvement**, not an entirely different physique |
| **Age/face/hair** | Face early-to-mid teen, a little angular; short full wavy hair | Nose, cheeks, gaze, ear size, face contour and hair shape appear essentially unchanged | **Pass preservation**; does not fully solve age impression |
| **Waist/chest/thighs and limb lengths** | Natural proportion in low/high plank; somewhat athletic taper from shoulder load | No discernible inflation/shrinkage, no retapered waist or altered bone lengths | **Pass visually** |
| **A upper-left low phase** | Both bent elbows visible, palms widely planted outside shoulders | Same hand positions and elbow bend, foreground and background arm topology retained | **Pass** |
| **B upper-right high phase** | Broad palm stance, both elbows extended | Same laterally separated palms, straight supporting elbows; pelvis/back aligned | **Pass** |
| **C lower-left low phase** | Two bent elbows and two separated hands | Same visible far/near elbows and hand locations; no new limb artifact | **Pass** |
| **D lower-right high phase** | Return to high wide-hand plank | High support and shoes retained; no apparent hand narrowing | **Pass** |
| **Clothing / shoes / wrists** | Bright blue tank, charcoal shorts, dark socks, gray shoes with muted yellow, wristband | All visibly retained; no unapproved wardrobe swap | **Pass** |
| **Track / camera / layout** | Four 2×2 tiles, thin white dividers, red lane and tree/field background | Same framing, ground plane and overall composition at same dimensions | **Pass visually**, not pixel registration |
| **Extraneous limbs / image defects** | Two arms and two legs per panel, complete visible hands and shoes | No new extra or missing arms, palms, elbows, feet or distortion seen | **Pass at card scale** |

### Honest limits

1. The softness improvement is **subtle**. Compared directly to v2, the boy still has broader upper arms than in the neutral standing master; some of that is legitimate load-bearing pose and camera compression. Further de-muscling could make the biomechanics worse or make the boy unnaturally thin.
2. A generative image edit can repaint textures and small details outside the requested region. A 2.02% average pixel difference does **not** prove a perfectly localized retouch. Full geometric registration was not measured; the four poses merely appear preserved by visual review.
3. The edit did **not** adjust jaw/nose, hair volume or age. That was intentional, to avoid multiplying identity variables and compromising the existing hand/arm topology.
4. The prior original #32 remains an explicit saved fallback. There is no proof that #32R will animate better, nor a human exercise-form approval.

**Decision:** Keep both. Label #32R as **conditional preferred identity-softness variant** for review because wide-hand width, near/far elbow visibility, four phases and face appear retained and surface tone is a little more age-appropriate. Use original #32 if a higher-resolution mechanics or video comparison reveals a hidden hand/elbow regression. No external uploads or video generation performed.

