# Test 25B — Chart 2 toe-touch + press, framing correction QA

**Output:** `25B_C2_EX1_ToeTouch_Bounce_4Phase_HEADROOM_CANDIDATE.png`, 1448×1086 PNG, SHA-256 `e4dbf00d284a90bb9444d5af9d6fc731807838ddd733f438e17e4155871d3980`.

**Method:** One conservative built-in imagegen edit of Test25 plus approved v2 identity and the successful Chart1 15B full-frame start as framing-only reference. Verbatim prompt in `PROMPT_25B_HEADROOM_EXACT.md`. No video, retries, or external writes.

## Visual comparison to Test25

| Criterion | Test25 source | Test25B corrected | Assessment |
| --- | --- | --- | --- |
| A arms-up top clearance | Fingertips within roughly 2–3% of tile top | Fingertips roughly **11%** below tile top | **PASS**; usable safety margin |
| D back-stretch top clearance | Similarly tight | Hands roughly **10%** below tile top | **PASS** |
| Shoes and track | Full soles but lower edge comparatively close | Entire shoes with roughly 8–11% bottom clearance | **PASS** |
| Figure proportions | Natural 13–14yo, slightly larger tile scale | Uniform modest zoom-out, no grotesque lengthening, teen remains proportionate | **PASS** |
| Garments / identity | Blue tank, charcoal shorts, dark socks, gray-yellow trainers, fair soft build | Retained; small photographic hair/face detail regeneration expected | **PASS/conditional identity** |
| B and C toe-touch stages | Both touches in central floor zone, small stated press | Both feet still planted and both hands touch center track, but **B and C remain almost visually identical** | **INCOMPLETE** for visibly distinct press/bounce |
| D gentle spinal arch | Present | Present, no impossible flexibility | **PASS** |
| Camera/location | Static nearly frontal track/forest | Similar angle, scale consistent across tiles, background repainted moderately | **PASS/conditional registration** |

The source-to-output normalized full-image ImageMagick MAE is ~0.08439 (8.4% color-range), much more than Test25's 2.1% edit. This is expected from reframing/rebuilding background. It does **not** establish pixel-level registration, but all motion-critical figure geometry remains plausible by visual inspection.

**Key caveat:** The contact sheet now solves the cropping problem but still does not demonstrate the single short press temporally; B and C may read as duplicated bottom photographs. Do not present this still as proof of the extra bounce or as an accepted video endpoint. Timing can be instructed in a future one-start-frame video prompt, with independent review of motion amplitude and planted shoes. Avoid making the boy's arms artificially long or knees deeply bent merely to make the press exaggerated.

**Assistant verdict: GOOD PHOTO-FRAMING / CONDITIONAL EXERCISE CARD.** Prefer Test25B over 25 as the full-figure card, but label the bounce-specific evidence incomplete until actual video QA. Both the original and corrected candidates are kept for traceability. No human exercise-form approval inferred.
