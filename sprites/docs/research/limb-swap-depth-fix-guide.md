# Fixing Limb-Swapping and Depth-Ordering Glitches in AI Running and Exercise Animation

A production workflow for keeping the near (foreground) leg in front and the far (background) leg behind across running, walking, and exercise cycles in diffusion-based image and video generation.

Last updated: November 24, 2026

---

## Contents

1. [What the glitch actually is](#1-what-the-glitch-actually-is)
2. [Diagnose before you fix](#2-diagnose-before-you-fix)
3. [Stage 0: Shot and source design](#3-stage-0-shot-and-source-design)
4. [Stage 1: Pose extraction and swap repair](#4-stage-1-pose-extraction-and-swap-repair)
5. [Stage 2: ControlNet OpenPose configuration](#5-stage-2-controlnet-openpose-configuration)
6. [Stage 3: Depth map conditioning](#6-stage-3-depth-map-conditioning)
7. [Stage 4: 3D-aware conditioning](#7-stage-4-3d-aware-conditioning)
8. [Stage 5: Prompt engineering](#8-stage-5-prompt-engineering)
9. [Multi-view consistency](#9-multi-view-consistency)
10. [Exercise-specific recipes](#10-exercise-specific-recipes)
11. [QA and frame-level repair](#11-qa-and-frame-level-repair)
12. [Quick-reference checklist](#12-quick-reference-checklist)

---

## 1. What the glitch actually is

In a side-view run, the two legs cross twice per stride. At the crossing frames, a 2D system sees two overlapping shapes and has to guess which is which. The failures show up in three related forms:

| Failure | What you see | Where it starts |
|---|---|---|
| **Label swap** | The skeleton's "left" and "right" legs trade places for a few frames | Pose estimator |
| **Depth inversion** | The far leg is drawn over the near leg, or the near leg goes behind the torso | Generator: a 2D skeleton has no depth |
| **Leg fusion / ghosting** | Legs merge into one shape, or a third leg shows up mid-stride | Generator: weak conditioning at the crossing point |

There are two separate root causes, and you need to fix both:

- **The control signal is wrong.** Pose estimators flip labels when limbs cross. One ComfyUI pose toolkit says outright that DWPose "swaps whole limbs for a few frames when the legs cross in a side view" ([Eloque/PoseCapture](https://github.com/Eloque/PoseCapture)). Another sprite-animation pipeline points out that estimators assign left/right labels "by appearance and flip between frames" ([JatCool/AI-Sprite-Animation](https://github.com/JatCool/AI-Sprite-Animation/blob/main/package/README.md)). A 2017-era OpenPose user guide adds that OpenPose_full "struggles with differentiating between left and right, leading to issues with overlapping" ([Andy Tu](https://andyhtu.com/how-to-use-openpose-in-controlnet/)).
- **The control signal has no depth.** A standard OpenPose map is a flat stick figure on black. Even with correct labels, nothing in it says which leg is in front. That's why newer animation research moves to 3D-aware signals. SCAIL, for example, renders bones as 3D cylinders specifically "to retain depth and occlusion" ([SCAIL paper](https://arxiv.org/html/2512.05905)).

The workflow below fixes the signal first (Stages 0 and 1), then adds depth (Stages 3 and 4), then reinforces both through settings and prompts (Stages 2 and 5).

---

## 2. Diagnose before you fix

Before you change any generation setting, find out which layer is failing. The DWPose acceptance guide from tasarim.ai makes the same point: when left and right look exchanged, check the joint-index mapping first, and for flicker, "inspect adjacent maps before claiming the issue is solved by image-generation settings" ([tasarim.ai DWPose guide](https://tasarim.ai/en/models/dwpose)).

**Triage procedure**

1. Export the pose sequence as images and step through it frame by frame. Pay special attention to the frames around each leg crossing (about 2 per stride).
2. Watch one leg's color, such as the right knee-to-ankle segment, the whole way through.
3. Decide which case you have:

| Observation | Diagnosis | Go to |
|---|---|---|
| Skeleton colors jump between legs at the crossing | Estimator label swap | Stage 1 |
| Skeleton is clean, but the output swaps legs | Generator ignoring or misreading the pose | Stages 2, 3, 5 |
| Skeleton is clean and the legs stay correct, but the far leg renders in front | Depth-ordering failure | Stages 3, 4 |
| Legs merge into one shape | Weak conditioning, too much motion, or ambiguous clothing | Stages 0, 2, 5 |
| Swaps only appear between context windows | Temporal or context-window seam | Stage 2 (sliding context), Stage 11 |

---

## 3. Stage 0: Shot and source design

Many swaps can be prevented before any model runs.

**Camera angle**
- A pure 90° side profile gives the most ambiguous crossings, because the legs overlap completely. A 3/4 view (about 30–45° off profile) gives the estimator and the generator real horizontal separation between near and far limbs. Hailuo's fitness guidance recommends adding "side profile" or "45-degree angle" to help the model understand "the 3D volume of the limb" ([Hailuo AI](https://hailuoai.video/pages/knowledge/biomechanical-accuracy-ai-fitness-video)).
- For walking clips, MagicBoat suggests a "cleaner side profile, slower pace, or clothing with stronger leg separation" when legs merge ([MagicBoat](https://www.magicboat.net/mobile/en/blog/believable-ai-walking-video)).

**Visual separation of the legs**
- Use asymmetric clothing or color: one knee sleeve, contrasting socks, or a shoe with a bright colorway on one side. This gives the estimator (when it works from appearance) and the generator (when it works from a reference image) a way to tell the legs apart.
- Avoid long shorts, skirts, or baggy pants that hide where the knees are.
- Keep the background plain behind the legs. MagicBoat warns that furniture, crowds, railings, or complex shadows "could merge with the legs" ([MagicBoat](https://www.magicboat.net/mobile/en/blog/believable-ai-walking-video)).

**Framing and motion**
- Use full-body framing with headroom and floor visible, a single subject, and nothing in front of the body. Kling's motion-control requirements call for a character with "entire body and head clearly visible and not obstructed" ([AI Prompt Geneer](https://aipromptgeneer.com/articles/fix-ai-video-flicker-morphing/)).
- Use a locked or slow tracking camera. Fast camera motion plus fast limb motion multiplies ambiguity.
- For loops, shoot or render on a treadmill (or remove travel in post) so the hips stay in place and only the legs cycle.

**Driving footage alternatives**
- If you can, drive the animation from a 3D rig such as Blender, Mixamo, or a 3D pose editor instead of live video. Those sources have correct labels and true depth by construction. Several ComfyUI 3D pose editors output OpenPose, depth, normal, and canny maps from the same posed mannequin ([FK 3D Openpose Editor](https://comfy.icu/node/FK_3dpose), [ComfyUI-OpenPoseEditor](https://github.com/LordTaylor/ComfyUI-OpenPoseEditor)).

---

## 4. Stage 1: Pose extraction and swap repair

### 4.1 Choose the estimator

| Estimator | Notes for running/exercise |
|---|---|
| **DWPose** | Default choice. 133 COCO-WholeBody keypoints, including 6 foot points; more robust on difficult poses and foreshortened limbs than OpenPose ([dwpose.org](https://dwpose.org/dwpose-vs-openpose/)). Output uses the OpenPose color scheme, so existing OpenPose ControlNets accept it ([dwpose.org](https://dwpose.org/)). |
| **OpenPose (CMU)** | Fine on clean, upright, fully visible subjects ([dwpose.org](https://dwpose.org/dwpose-vs-openpose/)). Weaker on crossings. Licensed for non-commercial research only ([Fora Soft](https://www.forasoft.com/learn/ai-for-video-engineering/articles-ai/openpose-mediapipe-rtmpose-pose-tracking)). |
| **ViTPose / RTMPose** | Higher COCO accuracy (ViTPose-G 80.9 AP) ([Fora Soft](https://www.forasoft.com/learn/ai-for-video-engineering/articles-ai/openpose-mediapipe-rtmpose-pose-tracking)). Use when you can convert the output to OpenPose format. |
| **3D estimators (NLF, SMPL fitters)** | Give true depth per joint. Needed for Stage 4. |

Keep the foot keypoints. Heel and toe points make swaps much easier to detect, because the near foot's toe direction and ground contact stay consistent through the stride. PoseCapture's video scan keeps "the 6 foot points (heel, big toe, small toe), which the usual DWPose keypoints drop" ([Eloque/PoseCapture](https://github.com/Eloque/PoseCapture)).

### 4.2 Know the index convention

In the OpenPose COCO-18 layout, 8–10 are right hip/knee/ankle and 11–13 are left hip/knee/ankle. "Right" means the subject's right, which appears on the left of the image when the subject faces the viewer ([bonepose README](https://github.com/hisashi-ito/bonepose/blob/main/README.md)). BODY_25 inserts a mid-hip at index 8, which shifts the legs to 9–11 and 12–14 ([VNCCS import script](https://huggingface.co/spaces/iueieur/image999-recovery/raw/main/pose_studio/vnccs_openpose_import.js)). Mixing the two layouts is a common hidden cause of "swaps."

### 4.3 Repair swapped labels temporally

Never trust per-frame labels in a run cycle. Enforce temporal continuity instead:

- **Ready-made nodes:** PoseCapture's `Repair Pose Scan` node has a `fix_swaps` option that runs a Viterbi pass to pick "the labelling with the smoothest motion," plus a `flip_cost` threshold. Without that threshold, a stretch between two crossings could be relabeled for free ([Eloque/PoseCapture](https://github.com/Eloque/PoseCapture)). Its preview colors near = orange and far = blue, so you can check the result visually.
- **Constant-velocity tracking:** The AI-Sprite-Animation pipeline makes labels "continuous in time with a constant-velocity tracker" and maps the camera-facing side to the rig's near side ([JatCool/AI-Sprite-Animation](https://github.com/JatCool/AI-Sprite-Animation/blob/main/package/README.md)).
- **Manual edit:** For short clips, fix the few bad frames in an OpenPose editor. This is the fallback the Opii Blender rig author describes for when "the legs or arms swap place" ([r/sdforall](https://www.reddit.com/r/sdforall/comments/11cy9jt/updated_opii_my_blender_control_net_rig_and_now/)).

**Minimal Python swap-repair script** (COCO-18 JSON from DWPose/controlnet_aux, one person per frame):

```python
import json, glob, numpy as np

LEG_R = [8, 9, 10]    # r_hip, r_knee, r_ankle (COCO-18)
LEG_L = [11, 12, 13]  # l_hip, l_knee, l_ankle
ARM_R = [2, 3, 4]
ARM_L = [5, 6, 7]

def load(frames_glob):
    seq = []
    for f in sorted(glob.glob(frames_glob)):
        d = json.load(open(f))
        kp = np.array(d["people"][0]["pose_keypoints_2d"]).reshape(-1, 3)
        seq.append((f, d, kp))
    return seq

def swap(kp, a, b):
    kp = kp.copy()
    kp[a], kp[b] = kp[b].copy(), kp[a].copy()
    return kp

def cost(pred, cur, idx):
    # Confidence-weighted distance between predicted and observed joints
    w = np.minimum(pred[idx, 2], cur[idx, 2]) + 1e-3
    return float((np.linalg.norm(pred[idx, :2] - cur[idx, :2], axis=1) * w).sum())

def repair(seq, pairs=((LEG_R, LEG_L), (ARM_R, ARM_L)), margin_frac=0.005):
    fixed = [seq[0][2]]
    height = np.ptp(seq[0][2][:, 1][seq[0][2][:, 2] > 0.1]) or 1.0
    margin = margin_frac * height          # like PoseCapture's flip_cost
    for i in range(1, len(seq)):
        cur = seq[i][2]
        prev = fixed[-1]
        prev2 = fixed[-2] if len(fixed) > 1 else prev
        pred = prev.copy()
        pred[:, :2] = prev[:, :2] + (prev[:, :2] - prev2[:, :2])  # constant velocity
        for a, b in pairs:
            idx = a + b
            keep = cost(pred, cur, idx)
            flipped = swap(cur, a, b)
            if cost(pred, flipped, idx) + margin < keep:
                cur = flipped
        fixed.append(cur)
    return fixed

def save(seq, fixed, out_suffix="_fixed.json"):
    for (f, d, _), kp in zip(seq, fixed):
        d["people"][0]["pose_keypoints_2d"] = kp.flatten().tolist()
        json.dump(d, open(f.replace(".json", out_suffix), "w"))

seq = load("poses/frame_*.json")
save(seq, repair(seq))
```

Notes:
- This greedy version works for most treadmill-style loops. For long or noisy clips, a full Viterbi pass over both labelings (as PoseCapture does) is more robust, because it can look ahead past an ambiguous crossing.
- Run it on the legs and arms separately. Arms swing opposite to legs, and the two errors are independent.
- After repair, apply a light temporal filter (a 3-frame median for lost points, as PoseCapture does) ([Eloque/PoseCapture](https://github.com/Eloque/PoseCapture)), but don't smooth across a real direction change.

### 4.4 Re-render the skeleton with depth order

Once labels are correct, re-draw the skeleton so occlusion is explicit:
- **Draw the far side first and the near side last,** so near limbs overwrite far limbs where they cross. RoBorg's 3D poser applies the same "farther drawn first" rule for whole people ([comfyui-poser](https://github.com/RoBorg/comfyui-poser)). Apply it per limb.
- Keep the standard OpenPose colors. ControlNet OpenPose models were trained on that exact palette ([bonepose README](https://github.com/hisashi-ito/bonepose/blob/main/README.md)), so recoloring or dimming the far leg can weaken pose adherence. Put depth in a separate depth map (Stage 3), not in the skeleton colors.
- If you have 3D joints, a cylinder-style render like SCAIL's carries depth and occlusion natively. Use it only with models trained on that representation.

---

## 5. Stage 2: ControlNet OpenPose configuration

### 5.1 Baseline settings

| Parameter | Starting value | Why |
|---|---|---|
| Preprocessor | `none` if you're feeding a repaired skeleton; `dw_openpose_full` if you're extracting | Preprocessing again would discard your fixes |
| Strength / weight | 0.8–1.0 for keyframes; 0.75–0.9 for animated sequences | A strength around 0.8–0.9 is "strict; pose almost-exact" and useful for animation keyframes ([AIOFM](https://aiofm.info/en/guides/controlnet-openpose-tutorial)); about 0.8–0.9 for animation helps avoid robotic artifacts ([The Neural Base](https://theneuralbase.com/controlnet/learn/beginner/pose-for-animation/)) |
| start_percent | 0.0 | The legs' layout is decided in the earliest, noisiest steps |
| end_percent | 0.8–1.0 | If the pose fades late, extend the ending step ([Generative Labs](https://www.generativelabs.com/insights/using-openpose-with-controlnet)) |
| Pixel Perfect / resolution | On; match the generation resolution | Keeps thin lower-leg segments from being lost to downscaling |

In ComfyUI, `start_percent` and `end_percent` set the fraction of the diffusion process over which ControlNet is applied ([ComfyUI docs](https://docs.comfy.org/tutorials/controlnet/controlnet)).

### 5.2 Timestep scheduling

Leg ordering is mostly decided early in sampling. Texture and detail are decided late. Use that:
- With [ComfyUI-Advanced-ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet/), use Timestep Keyframe Interpolation to ramp OpenPose strength from high (about 1.0) at `start_percent 0.0` down to moderate (about 0.6) by `end_percent 0.7`. This locks the layout early and lets the model render clean anatomy late.
- Run depth on the opposite curve: moderate early, a bit higher in the middle steps where occlusion boundaries form.

### 5.3 Video and sliding context

- AnimateDiff-style pipelines process frames in overlapping context windows. Advanced-ControlNet nodes "fully support sliding context sampling" and are required for the Advanced ControlNet versions to work with it ([Advanced-ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet/)).
- Increase context overlap (for example, from 4 to 8 frames in a 16-frame window) if swaps appear at window boundaries.
- If you can, align window boundaries with mid-stance frames, where legs are clearly separated, not with crossing frames.
- Lock everything (seed, weights, prompt) once the first frame works. The Opii rig author's advice: decide your settings on the first image of the animation "and don't change it again until all the frames are done" ([r/sdforall](https://www.reddit.com/r/sdforall/comments/11cy9jt/updated_opii_my_blender_control_net_rig_and_now/)).

### 5.4 Multi-ControlNet stack for running

The values below come from community stacking guides. Treat them as starting points to tune, not fixed rules.

| Unit | Character focus (fix limbs) | Scene focus (background stable) |
|---|---|---|
| OpenPose / DWPose | 0.8 | 0.65 |
| Depth | 0.6 | 0.75 |
| Lineart / SoftEdge / Canny | 0.3 | 0.5 |

- One ComfyUI motion-transfer guide starts at 0.8 OpenPose, 0.6 depth, and 0.3 Canny ([Visual Prompt Hub](https://visualprompthub.com/comfyui-multi-controlnet-motion-transfer/)). Apatero reports a sweet spot near 0.75 depth and 0.65 pose for dance and action, and notes that a pose-dominant mix improves character consistency while letting backgrounds wobble ([Apatero](https://apatero.com/blog/video-controlnet-stacking-depth-pose-edge-advanced-guide-2025)).
- Keep the total combined weight under about 2.5–3.0, or the ControlNets "fight each other" ([Apatero](https://apatero.com/blog/comfyui-controlnet-combinations-nobody-talking-about-2025)).
- An edge or HED unit restricted to the legs helps with crossings because it carries the outline of which leg is in front. The Opii rig author used a third HED ControlNet at about 0.5 weight for this purpose ([r/sdforall](https://www.reddit.com/r/sdforall/comments/11cy9jt/updated_opii_my_blender_control_net_rig_and_now/)).

### 5.5 Masked or regional control

If only the legs swap, mask the leg region and apply a higher-strength OpenPose plus depth just there (Advanced-ControlNet supports attention masks ([Advanced-ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet/))). Leave the upper body and background at normal strength so the image doesn't turn stiff.

---

## 6. Stage 3: Depth map conditioning

The depth map is what tells the generator which leg is in front.

### 6.1 Use a temporally consistent depth estimator

Per-frame depth flickers. In a run cycle, flicker at the crossing is exactly when the near/far order wobbles.

| Option | Why |
|---|---|
| **Video Depth Anything** | Built on Depth Anything V2 with a spatial-temporal head and a temporal gradient-matching loss ([Video Depth Anything paper](https://ar5iv.labs.arxiv.org/html/2501.12375)). ComfyUI's TS Video Depth node runs it over a sliding window so each frame "is informed by its neighbors" ([TS Video Depth](https://comfy.icu/node/TS_VideoDepthNode)). |
| **DepthCrafter** | Temporally consistent long depth sequences without camera poses or optical flow. The authors show Depth-Anything and NVDS exhibiting "zigzag artifacts" (flicker) in temporal profiles where DepthCrafter does not ([DepthCrafter](https://arxiv.org/html/2409.02095v2)). |
| **Depth Anything 3** | ComfyUI node built for "temporally stable, geometrically accurate" depth sequences for Wan, CogVideoX, HunyuanVideo, SVD, and ControlNet Depth ([ComfyUI-Depth-Anything-3](https://github.com/1038lab/ComfyUI-Depth-Anything-3)). |

For acceptance, check that static background areas keep consistent grayscale values and that "high-contrast silhouette edges" don't crawl ([fxroom.ai](https://fxroom.ai/blog/video-depth-anything-in-comfyui-temporal-consistency-and-node-workflows)).

### 6.2 Make the near/far legs separable in depth

Monocular depth often flattens the two legs into nearly the same value, because they're only 15–25 cm apart. Fixes:
- **Re-normalize per subject.** Mask the runner (with SAM2 or similar), then stretch the depth range inside the mask so the near-far leg difference becomes visible. Composite back over the background depth.
- **Use rendered depth instead of estimated depth.** If you drove the motion from a 3D rig (Stage 0) or fit an SMPL body (Stage 4), render depth from that geometry. It is exact and never flips.
- **Hybrid approach:** estimated depth for the scene, and SMPL or mannequin depth for the body.

### 6.3 Depth strength guidance

- Depth ControlNet conditioning strength of 0.6–0.85 is the common range. Too much locks surface texture; too little causes spatial drift ([fxroom.ai](https://fxroom.ai/blog/video-depth-anything-in-comfyui-temporal-consistency-and-node-workflows)).
- If depth is too strong, it can copy the driving actor's body shape onto your character. Lower depth weight or switch to a blurred or low-detail depth map when the character's proportions differ from the source.

### 6.4 Video models with native depth or pose control

- **Wan2.1 VACE** accepts a pose, depth, or edge control video through `WanVaceToVideo` ([ComfyUI VACE docs](https://docs.comfy.org/tutorials/video/wan/vace), [nomadoor guide](https://comfyui.nomadoor.net/en/basic-workflows/wan-2-1-vace/)). Its preprocessing annotators include SAM2, Depth-Anything-V2, and DWPose ([AI FILMS Studio](https://studio.aifilms.ai/blog/vace-wan-2-1-open-source-all-in-one-video-editing)). For running, try depth control first (it carries occlusion), then pose if limbs drift.
- **Wan2.1 Fun Control** supports Canny, Depth, OpenPose, MLSD, and trajectory control, at up to 81 frames at 16 fps ([ComfyUI Fun Control docs](https://docs.comfy.org/tutorials/video/wan/fun-control)).
- With Alibaba Cloud's hosted VACE API, set `control_condition: "depth"` and disable prompt rewriting with `prompt_extend=false` for consistency ([Alibaba Cloud Model Studio](https://docs.bailian.console.aliyun.com/en/model-studio/wan-vace-guide)).

---

## 7. Stage 4: 3D-aware conditioning

When 2D skeleton plus depth isn't enough (fast sprints, burpees, cartwheels, bike pedaling), move to a control signal that is 3D by construction.

| Approach | What it gives you | Source |
|---|---|---|
| **SMPL-based guidance (Champ)** | Renders depth, normal, and semantic part maps from a fitted SMPL body, alongside DWPose. The semantic map helps with "interactions between different components of the human body" | [Champ](https://arxiv.org/html/2403.14781) |
| **SCAIL** | Rasterizes bones as 3D cylinders to keep depth and occlusion; its ComfyUI workflow uses NLF 3D pose plus ViTPose and preserves "depth cues and occlusions" | [SCAIL paper](https://arxiv.org/html/2512.05905), [RunComfy SCAIL workflow](https://www.runcomfy.com/comfyui-workflows/scail-model-in-comfyui-pose-based-character-animation-workflow) |
| **Uni3C** | Puts a SMPL-X body and a scene point cloud in one 3D world space for joint camera and human motion control on Wan2.1 | [Uni3C](https://arxiv.org/html/2504.14899), [AI FILMS Studio](https://studio.aifilms.ai/blog/recammaster-uni3c-open-source-camera-video-ai) |
| **DensePose + DWPose (XPose)** | Adds dense body-surface correspondence alongside the skeleton for contour control | [XPose](https://eudl.eu/pdf/10.4108/eai.21-11-2024.2354584) |

**Practical SMPL workflow for a run cycle**
1. Fit SMPL or SMPL-X to the driving video, or pose it directly in Blender.
2. Check the leg labels in 3D. In 3D they don't swap at crossings because the legs are separated along the depth axis.
3. Render per frame: DWPose-style skeleton (projected from 3D joints, near side drawn last), depth, normal, and a semantic part map that gives the left and right legs different IDs.
4. Feed the skeleton, depth, and optionally normal to your ControlNet stack, or use a model trained on these signals, such as Champ.
5. If your character's build differs from the actor's, swap in your reference character's SMPL shape parameters while keeping the actor's pose. This "shape alignment" is the core idea in Champ ([Champ](https://arxiv.org/html/2403.14781)).

The semantic part map is the most direct fix for limb swapping, because it gives the generator a per-pixel label for "right leg" versus "left leg." Use it whenever your pipeline accepts it.

---

## 8. Stage 5: Prompt engineering

Prompts can't override a bad control signal, but they shift the generator's priors toward correct anatomy and away from fusion.

### 8.1 Principles

- **Describe the mechanics, not just the verb.** Hailuo warns that a bare "running" prompt often produces "syncopated" limbs where both arms move forward together ([Hailuo AI](https://hailuoai.video/pages/knowledge/biomechanical-accuracy-ai-fitness-video)). Kling's own guide says running prompts should go beyond the single verb and describe "speed, effort, body posture, surface contact, and camera relationship" ([Kling AI](https://kling.ai/blog/kling-ai-motion-prompts-guide)).
- **Name the contact event.** Writing out the heel strike, such as "her heel strikes the pavement, weight rolling forward onto the ball of the foot," gives the model a contact moment to render ([Prompt Architects](https://prompt-architects.com/blog/642-physics-failures-in-ai-video-and-how-to-prompt-around-them)).
- **Keep it short and add one element at a time.** Hailuo recommends a "subtractive" approach that starts from a lean base such as "Athletic man running on track, side view, emphasis on foot plant" ([Hailuo AI](https://hailuoai.video/pages/knowledge/physics-gait-prompting-natural-character-movement)). Runway likewise recommends starting simple and adding one element at a time ([the-ai-future.com](https://the-ai-future.com/how-to/ai-video-prompt)).
- **Keep clips to one or two strides** for text-to-video. Prompt Architects advises keeping a walk clip to "about one stride" ([Prompt Architects](https://prompt-architects.com/blog/642-physics-failures-in-ai-video-and-how-to-prompt-around-them)).
- **Lock or simplify the camera.** Fast camera moves add ambiguity.

### 8.2 Positive prompt building blocks

Use the depth-ordering vocabulary explicitly. Diffusion text encoders understand "near," "far," "in front of," and "behind" loosely, but repeating them alongside a 3/4 view helps.

```
[Subject], [camera angle], [gait phase / mechanics], [depth cue], [contact], [camera], [stability]
```

Example (open-source, with ControlNet):
```
athletic woman running, three-quarter side view from her left,
left leg nearest the camera, right leg behind her body,
arms swinging in opposition, right arm forward,
distinct leg separation, visible stride, clear knee definition,
contrasting red left sock and white right sock,
heel strike then toe-off, firm ground contact,
locked camera, plain track background, sharp focus
```

Example (Kling / Veo / Runway text-to-video):
```
Full-body three-quarter side view of a runner on an outdoor track.
She runs at a steady jogging pace. Her left leg is nearest the camera
and always stays in front of her right leg. Arms swing in opposition
to the legs. Each heel strikes the ground, weight rolls forward, toe pushes off.
Camera tracks smoothly at the same speed. No camera shake. Plain background.
```

Useful phrases from vendor and community guides:
- "distinct leg separation," "visible stride" ([PromptCollections on Kling](https://promptcollections.com/blog/kling-ai-video-prompts-for-realistic-human-movement))
- "arms swinging in opposition," "weight shifting," "natural gait" ([WearView](https://www.wearview.co/blog/walking-video-from-single-photo))
- "right arm forward, left leg extended back, controlled rhythmic motion, side view" ([Hailuo AI](https://hailuoai.video/pages/knowledge/biomechanical-accuracy-ai-fitness-video))
- "firmly planted feet," "slightly flexed knees" ([Hailuo AI](https://hailuoai.video/pages/knowledge/realistic-limbs-posture-ai-video-guide))

### 8.3 Negative prompt

```
extra limbs, extra legs, fused legs, merged legs, swapped legs,
legs crossing through each other, backward knee, reversed feet,
distorted legs, foot sliding, floating, morphing, flickering, blurry legs
```

This draws on standard negatives for walking clips such as `distorted legs, extra limbs ... foot sliding, floating` ([WearView](https://www.wearview.co/blog/walking-video-from-single-photo)). Negatives help with fusion and extra limbs but do little for pure label swaps. Those need Stage 1.

### 8.4 Commercial tool settings

| Tool | Settings that reduce swaps |
|---|---|
| **Kling** | Use the Professional model; moderate motion intensity (around 5) for walking cycles, since settings above 8 suit fast action "but may increase the risk of physical distortions" ([PromptCollections](https://promptcollections.com/blog/kling-ai-video-prompts-for-realistic-human-movement)). For Motion Control, use a full-body, unobstructed reference with a mostly still camera ([Open Your AIs](https://openyourais.com/blog/kling-3-0-motion-control-multi-shot-director-review/)), and match framing between the image and the reference ([ComfyUI Kling docs](https://docs.comfy.org/tutorials/partner-nodes/kling/kling-motion-control)). In Runway's Kling 3.0 Motion Control integration, check the Character orientation setting if you get unwanted motion ([Runway Help](https://help.runwayml.com/hc/en-us/articles/50280558448147-Creating-with-Kling-3-0-Motion-Control)). |
| **Kling first/last frame** | Don't span big pose changes in one clip. Generate an intermediate keyframe to shorten the action path, or lower motion sensitivity, to avoid "melted limbs" ([Montagea](https://montagea.com/blog/kling-first-last-frame-workflow/)). |
| **Runway Gen-4.x** | Upload the reference image first and describe motion and camera only; keep character descriptions identical across shots ([Lumen Kiln](https://lumenkiln.com/ai-video-prompting-guide/)). |
| **All** | Add "no camera shake"; all three default to slight camera movement ([Vani Aggarwal](https://vaniaggarwal.com/youre-prompting-ai-video-wrong-heres-the-fix/)). |

For hosted tools without pose input, the most reliable trick is **image-to-video from a clean start frame** in which the legs are clearly separated (mid-stance or full flight, never at the crossing). Start frames at the crossing invite the model to guess.

---

## 9. Multi-view consistency

When the camera orbits a runner, or you need the same exercise from several angles, the near/far relationship changes with the view. The control signals have to change in step.

**Work in 3D, then project.** Pose the motion once in 3D (rig, SMPL, or 3D pose editor) and render every view's skeleton, depth, and semantic map from that single source. The RoBorg poser projects 3D keypoints through the same pinhole camera model as three.js, so each view's skeleton is geometrically consistent ([comfyui-poser](https://github.com/RoBorg/comfyui-poser)). Uni3C goes further by putting the body and the scene in one shared world space, so "camera translation and actor movement never conflict" ([AI FILMS Studio](https://studio.aifilms.ai/blog/recammaster-uni3c-open-source-camera-video-ai)).

**Recompute "near side" per view.** Near and far are relative to the camera, not to the body. For each view:
- Compute each hip's camera-space Z; the smaller Z is the near side.
- Draw that side's limbs last in the skeleton render.
- At exactly frontal or exactly rear views, both legs are equidistant. Rely on the semantic part map or clothing asymmetry there.

**Handle the facing flip.** When the subject turns from facing the camera to facing away, image-left and image-right swap even though the labels stay the same. The subject's right is on the image's left when facing the viewer ([bonepose README](https://github.com/hisashi-ito/bonepose/blob/main/README.md)). Estimators frequently "correct" this incorrectly. Lock labels from the 3D source rather than re-detecting from 2D.

**Keep identity anchors constant across views.**
- Use the same reference image (IP-Adapter, reference-to-video, or character LoRA) for every view.
- Use the same asymmetric wardrobe marker (one knee sleeve, one colored shoe) so each leg is identifiable in every view.
- Copy character descriptions word for word between shots ([Lumen Kiln](https://lumenkiln.com/ai-video-prompting-guide/)).

**Generate views as variations, not independent shots.** When possible, generate the hero view first, then condition other views on it through depth, reference image, or first frame, instead of generating each from scratch.

**Turnaround validation.** Render a test turnaround of a single frozen stride (mid-flight) from 0°, 45°, 90°, 135°, and 180°. If the near leg flips at any angle in the controls themselves, fix the projection before generating.

---

## 10. Exercise-specific recipes

### Running / sprinting (side or 3/4 view)
- **Camera:** 3/4 from the near side, locked or treadmill.
- **Controls:** repaired DWPose (feet on) at 0.8, video-consistent depth with subject re-normalization at 0.6, leg-masked SoftEdge at 0.3.
- **Loop:** extract exactly one stride cycle. PoseCapture's walk-cycle mode closes one period into a seamless loop and puts a walk across the frame "on a treadmill first" ([Eloque/PoseCapture](https://github.com/Eloque/PoseCapture)).
- **Key frames to check:** the two mid-stance crossings per stride.

### Walking
- Same as running but slower, with double support (both feet down). Swaps cluster at the double-support phase.
- Prompt "visible heel-to-toe steps" and "subtle vertical weight shift" if the body floats ([MagicBoat](https://www.magicboat.net/mobile/en/blog/believable-ai-walking-video)).

### Treadmill running
- Hips are stationary, which makes constant-velocity swap repair very reliable.
- The treadmill rails often merge with legs. Mask them out of the edge ControlNet or choose a rail-free angle.

### Cycling / spin bike
- The near and far legs are 180° out of phase and cross at the top and bottom of the pedal stroke.
- Repair swaps using the pedal (crank) position as a constraint. The near foot is always on the near pedal.
- Depth matters more than pose here, so weight depth higher (about 0.75).

### Lunges, high knees, butt kicks
- The near and far legs alternate roles each rep. Lock labels at rep start from a clearly separated frame.
- For high knees, the lifted thigh foreshortens toward the camera in a 3/4 view, so DWPose's foreshortening robustness helps here ([dwpose.org](https://dwpose.org/dwpose-vs-openpose/)).

### Jumping jacks, burpees, mountain climbers
- Mostly frontal, so leg crossing is rare. The failure is usually arm-leg confusion or the body flipping during the floor phase.
- Burpees go from vertical to horizontal and back. Use SMPL or 3D conditioning (Stage 4); 2D skeletons fail badly in the plank phase.
- Mountain climbers: front-to-back leg alternation viewed from the side behaves like running. Use the running recipe.

### Rowing, squats, deadlifts
- Symmetric bilateral movements. Swaps are rare, but in pure profile the far leg often vanishes entirely.
- Rotate the camera 15–20° off profile so the far leg stays partially visible.

---

## 11. QA and frame-level repair

**Automated checks** (run on the generated video, re-estimated with DWPose):
- **Label continuity:** run the swap-repair script on the output. Any frame it wants to flip is a frame where the generator swapped legs.
- **Pose fidelity:** per-frame error between the input skeleton and the re-estimated output skeleton. Spikes mark bad frames.
- **Leg-length ratio:** the thigh/shin length ratio should stay nearly constant. Sudden changes indicate fusion. Pose only locks joint positions, not limb lengths, so the model still has freedom in anatomical proportions ([The Neural Base](https://theneuralbase.com/controlnet/learn/beginner/pose-for-animation/)).

**Fixing isolated bad frames**
1. Identify the bad frame range (usually 2–4 frames at a crossing).
2. Correct the skeleton for those frames manually or by repair.
3. Regenerate only those frames with a masked inpaint of the leg region, using the same seed and settings, the neighboring good frames as reference, and slightly higher OpenPose plus depth strength.
4. Or drop the bad frames and interpolate across them with a frame interpolator (RIFE, FILM), as long as the gap is at most about 2 frames. Longer gaps will interpolate through the ghost.

**Last resort: generate the subject separately.** For group running shots, Hailuo's recommended professional approach is to "generate characters separately and composite them in post-production" ([Hailuo AI](https://hailuoai.video/pages/knowledge/physics-gait-prompting-natural-character-movement)). The same logic applies to a single runner against a complex background: generate the runner on a plain background with strong controls, then composite.

---

## 12. Quick-reference checklist

**Before generation**
- [ ] 3/4 view preferred over pure profile
- [ ] Full body in frame, single subject, nothing occluding the legs
- [ ] Asymmetric leg marker (sock, sleeve, shoe color)
- [ ] Locked or slow tracking camera
- [ ] Driving motion from a 3D rig if possible

**Pose signal**
- [ ] DWPose with foot keypoints kept
- [ ] COCO-18 vs BODY_25 index layout confirmed
- [ ] Temporal swap repair run on legs and arms
- [ ] Crossing frames inspected manually
- [ ] Skeleton re-rendered with the near side drawn last, standard colors kept

**Depth signal**
- [ ] Temporally consistent estimator (Video Depth Anything, DepthCrafter, DA3) or rendered depth
- [ ] Subject depth range re-normalized so the legs separate
- [ ] Background flicker and edge crawl checked

**ControlNet**
- [ ] OpenPose about 0.8, depth about 0.6, edge about 0.3 (character-focus starting point)
- [ ] Combined weight under about 2.5
- [ ] OpenPose start 0.0; strength ramped down late
- [ ] Advanced-ControlNet nodes for sliding context; overlap increased if seams swap
- [ ] Settings frozen after the first good frame

**Prompt**
- [ ] Mechanics described (opposition, heel strike, toe-off)
- [ ] Near/far leg stated explicitly
- [ ] Camera locked or "no camera shake"
- [ ] Negatives: fused/extra/swapped legs, foot sliding
- [ ] One or two strides per clip for text-to-video

**After generation**
- [ ] Output re-estimated and swap-checked
- [ ] Bad frames inpainted or interpolated
- [ ] Multi-view shots validated with a turnaround test
