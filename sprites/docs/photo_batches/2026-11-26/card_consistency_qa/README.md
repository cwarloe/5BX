# Photographic 5BX card continuity screen — pilot

This is a non-generative, read-only QC helper for a **2×2 contact card**.
It screens the two recurring drift issues the user identified:

1. **Fixed camera/background:** measure the first row where red running track occupies most of each panel. Compare four track lines and adjacent generations.
2. **Wardrobe color:** find the largest saturated-blue tank-top blob per panel and compare median RGB. Pose-specific cloth shading can trigger a review flag; it is not automatically an identity failure.

The script deliberately does **not** claim to recognize limbs, shoulders, age, sex, hands, safe joints, or exercise correctness. Those gates remain separate manual QC checks. Color bands on anatomical wrists/ankles are useful controlled diagnostics, but pixel color alone is not proof of which limb is attached.

## Run

```sh
python3 photo_card_consistency.py BASE.png --compare CANDIDATE.png --out report.json
python3 -m unittest discover -s . -p 'test_*.py' -v
```

Requires Python, Pillow, NumPy, SciPy. No network/model credits.

The first implementation scanned only entire rows, which falsely marked the
Chart 2 prone back-extension card as 32 px out of registration: the long torso
occluded much of the track. The corrected scan prefers left/right 8% strips,
where the track edge is visible, then falls back to the original full-row
method. On `C2BE01`, the corrected spread is **1 px PASS**, and the blue
shirt median range is **4/255 PASS**. A synthetic prone-occlusion regression
test prevents this false positive from silently returning.

## Verified local example: 34J → 34K

| Check | 34J | 34K | Result |
| --- | ---: | ---: | --- |
| Track boundary spread among all four panels | 1 px | 1 px | camera registration passes |
| Maximum per-panel track boundary shift from 34J | — | 0 px | unchanged track edge |
| Biggest blue-shirt median-channel shift vs same 34J panel | — | 7/255 | low between-version color drift |
| Maximum within-card blue-shirt median-channel range | 17/255 | 22/255 | 34K flagged REVIEW at conservative 18 threshold |
| Limb geometry, hidden far hand, identity, age | manual | manual | **never automatically approved** |

Because cloth lighting and occlusion change with arm position, the within-card shirt color warning for 34K is a *review*, not a rejection; it should be visually assessed alongside the exact reference.

The upper-arm issue in 34J was identified by human spatial review (far elbow lower than near elbow, too much visible upper arm). 34K was edited to raise only that small far-elbow silhouette; this script cannot validate that anatomy and should not be used to waive a human pose gate.

## Manufacturing process use

Run this report for every new four-panel generation before discussing whether the intended pose worked. Any red-track or major outfit-color outlier goes back for a quick visual check; biomechanical, anatomical, and character-identity passes are documented independently. Never substitute the automated optical screen for the 5BX exercise-form review.
