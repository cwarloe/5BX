#!/usr/bin/env python3
"""Assemble Chart 1 white-studio motion workprint from existing three-rep clips.

Put these six already-created source clips in video_inputs/white_prototype_sources
under the simple filenames below (Google Drive file IDs in parentheses):
  toe.mp4      01_Toe_Touch_3x_Loop_QA.mp4 (1_umU6HINKorl3UiKByHNMxMNgyXqQ_eT)
  sit.mp4      02_Mark_White_HeadOnly_3Rep_8p5s_SALVAGE_WORKPRINT.mp4
                (1SKXu1BQ9Bd-vAEfOXwQoRLQ7PnGAHq3v)
  leg.mp4      REVIEW__Mark_Alternate_Leg_Raise_Flow_3Cycles_22_5sec.mp4
                (1FA0bYUeQvd37W9o1Q3zDoZpPgAhP4DE7)
  knee.mp4     04_Knee_Pushup_3x_Loop_QA.mp4 (1jsIHIyiNeVifvZ6k8eV1APrCoyo8L4lg)
  run.mp4      05a_Run_In_Place_3x_Loop_QA.mp4 (1-FQwfPkI-LPtjBcNZxnUGyi5BN-FP969)
  scissor.mp4  05b_Less_Intense_Scissor_3x_Loop_QA.mp4
                (1CPSK6LYCUzuE_Ay5JP9NrmtTKEPgU575)

Run: python render_white_prototype.py
Requires ffmpeg and Pillow. Source motion is preserved: this is a timed visual
prototype, not movement QA. Cards and countdowns are separate from source videos.
The 30-second scissor placement is illustrative; the final trigger is by steps.
"""

from __future__ import annotations

import concurrent.futures
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / "video_inputs").is_dir() else HERE.parent
SRC = ROOT / "video_inputs" / "white_prototype_sources"
BUILD = ROOT / "video_inputs" / "white_prototype_render"
OUT = ROOT / "video_inputs" / "C1_White_Prototype_11m30s.mp4"
W, H, FPS = 1280, 720, 24
GREEN = (35, 61, 39)
OLIVE = (91, 109, 67)
RUST = (180, 78, 31)
CREAM = (247, 247, 240)
MUTED = (107, 119, 105)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def run(args: list[str]) -> None:
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def font(size: int, bold: bool = True):
    return ImageFont.truetype(FONT if bold else FONT_REG, size)


def header(draw: ImageDraw.ImageDraw, index: int, title: str, tip: str):
    draw.text((51, 33), title.upper(), font=font(48), fill=GREEN,
              stroke_width=0)
    draw.text((54, 96), tip.upper(), font=font(21), fill=RUST)
    draw.text((54, 675), "5BX CHART 1   /   WHITE-STUDIO WORKPRINT",
              font=font(14, False), fill=MUTED)


def overlay_frame(title: str, tip: str, remaining: int, total: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    header(d, 0, title, tip)
    cx, cy, r = 1147, 100, 64
    d.ellipse((cx-r+6, cy-r+6, cx+r-6, cy+r-6), fill=(250, 251, 246, 238))
    d.arc((cx-r, cy-r, cx+r, cy+r), 0, 359, fill=(204, 213, 200, 230), width=10)
    progress = max(0, min(1, remaining / total))
    d.arc((cx-r, cy-r, cx+r, cy+r), -90, -90 + int(359 * progress),
          fill=RUST + (255,), width=10)
    stamp = f"{remaining//60}:{remaining%60:02}"
    box = d.textbbox((0, 0), stamp, font=font(37))
    tw, th = box[2]-box[0], box[3]-box[1]
    d.text((cx-tw/2, cy-th/2-7), stamp, font=font(37), fill=GREEN)
    return img


def draw_centered(d, text, y, size, color):
    f = font(size)
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((W-(bb[2]-bb[0]))/2, y), text, font=f, fill=color)


def slate(name: str, kicker: str, title: str, tip: str, foot: str):
    img = Image.new("RGB", (W, H), (250, 250, 246))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 18), fill=GREEN)
    d.rectangle((0, 18, W, 24), fill=RUST)
    d.text((70, 76), kicker, font=font(24), fill=RUST)
    draw_centered(d, title, 250, 78 if len(title)<18 else 62, GREEN)
    draw_centered(d, tip, 374, 30, OLIVE)
    d.line((290, 461, 990, 461), fill=(208, 214, 198), width=2)
    draw_centered(d, foot, 514, 22, MUTED)
    img.save(BUILD / f"{name}.png", optimize=True)


# Name, source, duration, countdown at start, full countdown duration, title, tip
MOVEMENT = [
    ("01_toe", "toe", 120, 120, 120, "TOE TOUCH", "BEND COMFORTABLY"),
    ("02_sit", "sit", 60, 60, 60, "PARTIAL SIT-UP", "LIFT HEAD AND SHOULDERS ONLY"),
    ("03_leg", "leg", 60, 60, 60, "ALTERNATING LEG RAISE", "ONE LEG AT A TIME · FEET DOWN BETWEEN"),
    ("04_knee", "knee", 60, 60, 60, "KNEELING PUSH-UP", "PRESS UP WITH CONTROL"),
    ("05_run_a", "run", 270, 360, 360, "RUN IN PLACE", "SMALL EVEN STEPS · STAY IN PLACE"),
    ("05_scissor", "scissor", 30, 90, 360, "SCISSOR JUMPS", "TEN GENTLE LEG EXCHANGES"),
    ("05_run_b", "run", 60, 60, 360, "RUN IN PLACE", "SMALL EVEN STEPS · STAY IN PLACE"),
]


def make_motion(entry):
    name, source, duration, first_remaining, total, title, tip = entry
    seq_dir = BUILD / name
    seq_dir.mkdir(exist_ok=True)
    for second in range(duration):
        overlay_frame(title, tip, first_remaining-second, total).save(
            seq_dir / f"{second:04}.png", optimize=True)
    segment = BUILD / f"{name}.mp4"
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-stream_loop", "-1", "-i", str(SRC / f"{source}.mp4"),
        "-framerate", "1", "-i", str(seq_dir / "%04d.png"),
        "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=0:repeatlast=1:format=auto,format=yuv420p[v]",
        "-map", "[v]", "-t", str(duration), "-r", str(FPS),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-pix_fmt", "yuv420p", "-an", str(segment)
    ]
    run(cmd)
    return segment


def render_card(name: str, seconds: int):
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-framerate", str(FPS), "-i", str(BUILD / f"{name}.png"),
        "-t", str(seconds), "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "26", "-pix_fmt", "yuv420p", "-an", str(BUILD / f"{name}.mp4")
    ])


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    slate("opening", "CHARLES FIT CLUB  /  5BX CHART 1", "PICK A MISSION.",
          "SHOW UP.", "11 MINUTES.  FIVE EXERCISES.  ONE START.")
    slate("card_01", "EXERCISE 01  /  2 MINUTES", "TOE TOUCH", "BEND COMFORTABLY", "REACH · FOLD · RECOVER")
    slate("card_02", "EXERCISE 02  /  1 MINUTE", "PARTIAL SIT-UP", "LIFT HEAD AND SHOULDERS ONLY", "SMALL CONTROLLED MOVEMENT")
    slate("card_03", "EXERCISE 03  /  1 MINUTE", "ALTERNATING LEG RAISE", "ONE LEG AT A TIME", "RETURN BOTH FEET TO FLOOR BETWEEN LIFTS")
    slate("card_04", "EXERCISE 04  /  1 MINUTE", "KNEELING PUSH-UP", "PRESS UP WITH CONTROL", "KEEP KNEES GROUNDED")
    slate("card_05", "EXERCISE 05  /  6 MINUTES", "RUN + SCISSORS", "RUN IN PLACE · GENTLE SCISSOR JUMPS", "COUNTED STEPS · TEN SMALL EXCHANGES")
    slate("closing", "CHARLES FIT CLUB", "MISSION COMPLETE", "YOU SHOWED UP.", "PICK A MISSION. SHOW UP AGAIN TOMORROW.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs = [pool.submit(make_motion, e) for e in MOVEMENT]
        jobs.extend(pool.submit(render_card, name, 6 if name == "opening" else 4)
                    for name in ["opening", "card_01", "card_02", "card_03", "card_04", "card_05", "closing"])
        for job in concurrent.futures.as_completed(jobs):
            job.result()

    order = ["opening", "card_01", "01_toe", "card_02", "02_sit",
             "card_03", "03_leg", "card_04", "04_knee", "card_05",
             "05_run_a", "05_scissor", "05_run_b", "closing"]
    concat = BUILD / "segments.txt"
    concat.write_text("".join(f"file '{str(BUILD / (name + '.mp4'))}'\n" for name in order))
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(OUT)])
    print(str(OUT), flush=True)


if __name__ == "__main__":
    main()
