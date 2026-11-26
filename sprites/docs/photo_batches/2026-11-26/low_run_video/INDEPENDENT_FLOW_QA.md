# Independent Google Flow QA — Chart 1 low stationary run

**Status: CANDIDATE / HUMAN PLAYBACK REQUIRED.** This review did not establish that the motion or loop is correct. No generation credits were spent and no assets were changed.

- **Source:** [Flow video #20](https://flow.google.com/project/21f1691f-1259-4af7-9061-61f0c5c47e23/edit/cfc5982b-03f5-4bc6-a103-afdf05a7558c)
- **Title shown:** `20_REVIEW__C1_LowRun_4in__BlueCharcoal__2026-11-26`
- **Media:** six-second video, Omni 1.2 Flash. Its prompt and generation record are in the adjacent `QA_EXACT_PROMPT.md`.
- **Method:** read-only inspection in an authenticated Google Flow browser. Inspected media UI, played/paused video, sought along timeline, inspected Download and Share menus. No download, video generation, editing, sharing, or Drive export was performed.

## What is visually supported

At the one video image the browser preview reliably exposed (timecode initially `00:05:00`), the boy was shown from the side on a track with grassy trees behind. He wore a light/bright blue tank, dark charcoal shorts, and gray/yellow running shoes. One leg was raised/bent and the other supported him. The image had no **obvious extra limbs in this single frame**. The composition appeared to use a fixed camera. This is only still-frame evidence, **not** evidence of a correctly animated run.

The amount of foot lift could not be measured reliably from this one perspective/frame; four inches is **not verified**. Character identity and color are a candidate chart variant but should be compared to the chart's approved character reference. The frame source inherited an earlier Flow saved/repose frame, rather than being anchored directly to the approved v2 master; character consistency thus remains conditional.

## Failed independent motion verification

The AX/player timecode responded to playback and seeking, but the screenshot captured the same video image:

1. At initial `00:05:00`, captured a visible one-leg-raised frame.
2. Clicked Play; player switched to Pause and timecode progressed to `00:05:03`, but screenshot was visually unchanged.
3. While looping, a later AX state read `00:01:23`, yet screenshot still displayed the original pose.
4. Paused and clicked elsewhere on the timeline; timecode read `00:04:00`, but the displayed pose again did not refresh.

This is an apparent **browser capture/preview limitation**, not proof that the actual video is frozen. Therefore **not independently verified**: alternating left/right foot lifts; approximately four-inch lift; opposite-arm swing and hand anatomy across the cycle; whether the boy runs in place; camera stability over six seconds; age/identity drift, extra arms/legs, foot sliding, or other frame-dependent artifacts; and the first/last frame loop seam. The Loop control was enabled in the player, but an enabled player setting does not establish that the rendered motion itself loops smoothly.

## Export route

Google Flow's **Download media** menu showed `270p Animated GIF`, `720p Original size`, and `1080p Upscaled`, plus disabled `4K Upscaled`. Its **Share** dialog offered options to include inputs, prompt, and input media, with **Copy link**. Neither menu showed a direct **Export to Google Drive** command. This is a finding about the inspected UI, not a claim that Drive transfer is impossible by all other methods.

## Review gate and practical next step

**Owner human eyeballs are warranted for this one video** because the automated browser could not present separate temporal frames or decode the MP4. Watch the direct Flow link at normal speed once, preferably twice and across the repeat boundary, checking foot alternation, tiny foot clearance (not high knees), opposite arm rhythm, planted-foot stability, camera lock, anatomy, and age consistency. If possible, download **720p Original size** to a reachable local asset and sample frames at ~0, 1, 2, 3, 4, 5, 6 seconds or inspect the full video in a standard decoder; this would allow reproducible QA without spending additional video credits. Hold this candidate out of the accepted set until that motion check passes.
