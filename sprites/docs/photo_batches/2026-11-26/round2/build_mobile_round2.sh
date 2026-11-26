#!/usr/bin/env bash
set -euo pipefail

# Reproducible, mechanical-only mobile contact sheets. No image pixels are AI-edited.
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
base="$(cd -- "$here/../../.." && pwd)"
src="$base/artifacts/parallel_batch_20261126"
new="$base/artifacts/next_batch_20261126"

title_card() {
  local title="$1" out="$2"
  magick -size 1168x110 xc:'#142431' -gravity center \
    -font DejaVu-Sans-Bold -fill white -pointsize 40 \
    -annotate +0+0 "$title" "$out"
}

note_card() {
  local title="$1" out="$2" color="${3:-#243540}"
  magick -size 1168x108 xc:white -gravity center \
    -font DejaVu-Sans-Bold -fill "$color" -pointsize 31 \
    -annotate +0+0 "$title" "$out"
}

image_card() {
  local input="$1" out="$2" fit="$3" canvas="$4"
  magick "$input" -resize "$fit" -background white -gravity center \
    -extent "$canvas" -quality 90 "$out"
}

title_card 'CHART 3 — ELBOW SAFETY REVIEW' "$here/ch3_title.png"
magick "$src/00_CHART3_TESTS26-29_MOBILE_QA_CONTACT.jpg" \
  -fill '#a70c1a' -draw 'rectangle 600,720 1160,820' \
  -fill white -font DejaVu-Sans-Bold -pointsize 39 -gravity northwest \
  -annotate +625+730 '29E SAFETY HOLD' \
  -pointsize 26 -annotate +630+777 'UNNATURAL ELBOW ANGLE' \
  -fill '#a70c1a' -draw 'rectangle 580,955 1166,1068' \
  -fill white -pointsize 30 -annotate +605+962 'DO NOT ANIMATE 29E' \
  -pointsize 23 -annotate +605+1009 'Older conditional label superseded' \
  "$here/ch3_safety_stage.png"
magick "$new/v_pike_elbow/29H_PoseLocked_Photographic_CANDIDATE.png" \
  -resize 566x318 -background white -gravity center -extent 566x320 "$here/ch3_29h_tile.png"
magick "$here/ch3_safety_stage.png" \
  -fill white -draw 'rectangle 0,1090 585,1601' \
  "$here/ch3_29h_tile.png" -geometry +9+1110 -compose over -composite \
  -font DejaVu-Sans-Bold -gravity northwest \
  -fill '#215c35' -pointsize 28 -annotate +11+1453 '29H: INDEPENDENT GEOMETRY PASS' \
  -fill '#a70c1a' -pointsize 29 -annotate +11+1498 'IDENTITY HOLD — NO VIDEO' \
  -fill '#253440' -pointsize 22 -annotate +11+1543 'Replaces old 29C reference tile' \
  "$here/ch3_annotated.png"
note_card 'CHART 3: POSITIONS 26–28 CONDITIONAL; 29E ON HOLD' "$here/ch3_footer.png" '#9a101b'
magick "$here/ch3_title.png" "$here/ch3_annotated.png" "$here/ch3_footer.png" \
  -append -sampling-factor 4:4:4 -quality 90 \
  "$here/00_CHART3_MOBILE_ROUND2_V_PIKE_SAFETY_HOLD.jpg"

title_card 'CHART 4 — SKEPTICAL IDENTITY GATE' "$here/ch4_title.png"
note_card '32S: WIDE-HAND PUSH-UP — IDENTITY HOLD' "$here/ch4_sub1.png" '#9a101b'
image_card "$src/chart4_ex4/32S_C4_EX4_WideHandPushup_SoftDefinition_IdentityLocked_CANDIDATE.png" \
  "$here/ch4_image1.png" '1100x730' '1168x760'
note_card '32S UPPER ARMS STILL TOO DEFINED; MECHANICS DIAGNOSTIC' "$here/ch4_status1.png" '#9a101b'
note_card '34B: HIGH-KNEE RUN — CONDITIONAL DIAGNOSTIC' "$here/ch4_sub2.png" '#a45c00'
image_card "$new/chart4_high_knee_arms/34B_C4_HighKneeCoupledArms_CLEAN_CONDITIONAL.png" \
  "$here/ch4_image2.png" '900x945' '1168x970'
note_card '34A TAGGED CARD REQUIRED FOR LEG IDENTITY' "$here/ch4_status2.png" '#a45c00'
note_card 'STILLS ONLY · NO VIDEO / FINAL FORM APPROVAL' "$here/ch4_footer.png" '#9a101b'
magick "$here/ch4_title.png" "$here/ch4_sub1.png" "$here/ch4_image1.png" "$here/ch4_status1.png" \
  "$here/ch4_sub2.png" "$here/ch4_image2.png" "$here/ch4_status2.png" "$here/ch4_footer.png" \
  -append -sampling-factor 4:4:4 -quality 89 \
  "$here/00_CHART4_MOBILE_ROUND2_32S_34B.jpg"

title_card 'CHART 2 — NEW IDENTITY REFINEMENT' "$here/ch2_title.png"
note_card '24R: STANDARD PUSH-UP — SOFTER DELTOID SHADING' "$here/ch2_sub.png"
image_card "$new/24R_C2_StandardPushup_ShoulderSoftness_CANDIDATE.png" \
  "$here/ch2_image.png" '1100x730' '1168x760'
note_card 'PASS AS STILL VIDEO-TEST INPUT · VIDEO NOT VERIFIED' "$here/ch2_footer.png" '#246032'
magick "$here/ch2_title.png" "$here/ch2_sub.png" "$here/ch2_image.png" "$here/ch2_footer.png" \
  -append -sampling-factor 4:4:4 -quality 89 \
  "$here/00_CHART2_MOBILE_ROUND2_24R.jpg"

title_card 'CHART 6 — IDENTITY / FLIGHT SAFETY GATE' "$here/ch6_title.png"
note_card '41S: CHEST-SLAP PUSH-UP — IDENTITY HOLD' "$here/ch6_sub.png" '#9a101b'
image_card "$new/41S_C6_FarHandClearance_R2_CANDIDATE.png" \
  "$here/ch6_image.png" '1100x730' '1168x760'
note_card 'HANDS CLEAR IN STILL; BALLISTIC MOTION UNVERIFIED' "$here/ch6_status.png" '#a45c00'
note_card 'HOLD: UPPER BODY TOO ATHLETIC FOR MASTER IDENTITY' "$here/ch6_footer.png" '#9a101b'
magick "$here/ch6_title.png" "$here/ch6_sub.png" "$here/ch6_image.png" "$here/ch6_status.png" "$here/ch6_footer.png" \
  -append -sampling-factor 4:4:4 -quality 89 \
  "$here/00_CHART6_MOBILE_ROUND2_41S.jpg"

identify -format '%f  %wx%h  %b\n' "$here"/00_CHART?_MOBILE_ROUND2_*.jpg
