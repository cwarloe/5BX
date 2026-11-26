"""Strict, offline assembly of two photographic A→C and C→A video segments.

This is a *technical preview* for an experimental provider modality. Exact
encoded video packets must survive a no-fade stream-copy concat. Matching
screen pixels at C cannot establish correct physical motion, identity, anatomy,
exercise safety, or a seamless loop; those always require separate review.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import __version__
from .video_qa import file_sha256, probe


HOLD = "HOLD_FOR_HUMAN_FORM_AND_RELEASE_REVIEW"
STATUS = "EXPERIMENTAL_TWO_SEGMENT_PREVIEW_NOT_FORM_APPROVED"


def _run(command, *, binary=False):
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{command[0]} failed ({result.returncode}): "
                           f"{result.stderr.decode('utf-8', 'replace')[-800:]}")
    return result.stdout if binary else result.stdout.decode("utf-8", "replace")


def _stream_info(video):
    raw = _run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(video)])
    streams = json.loads(raw).get("streams", [])
    if not isinstance(streams, list) or len(streams) != 1 or streams[0].get("codec_type") != "video":
        raise ValueError("input must contain exactly one video stream and zero audio/subtitle/data streams")
    s = streams[0]
    if s.get("codec_name") != "h264" or s.get("pix_fmt") != "yuv420p":
        raise ValueError("requires H.264 yuv420p photographic MP4 (no transcoding fallback)")
    if not all(isinstance(s.get(k), int) and s[k] > 0 for k in ("width", "height")):
        raise ValueError("unknown input frame dimensions")
    return {k: s.get(k) for k in ("codec_name", "pix_fmt", "width", "height",
                                "r_frame_rate", "avg_frame_rate", "time_base",
                                "profile", "level")}


def _packet_hashes(video):
    raw = _run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_packets", "-show_data_hash", "sha256",
                "-show_entries", "packet=data_hash", "-of", "json", str(video)])
    entries = json.loads(raw).get("packets")
    if not isinstance(entries, list) or not entries:
        raise ValueError("no hashed encoded video packets")
    hashes = [p.get("data_hash") for p in entries]
    if any(not isinstance(h, str) or
           not re.fullmatch(r"SHA256:[0-9a-fA-F]{64}", h) for h in hashes):
        raise ValueError("incomplete packet hash evidence")
    return hashes


def _decoded_rgb_sequence_sha256(videos):
    """Hash the complete, ordered decoded RGB frame bytes with bounded memory.

    Validating encoded packets alone is insufficient: MP4 remux timestamps,
    H.264 parameter sets, or codec changes could yield different displayed
    frames. Raw RGB24 across all frames establishes exact decoded visual
    equivalence for this ffmpeg decoder/version.
    """
    digest = hashlib.sha256()
    for video in videos:
        command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                   "-i", str(video), "-map", "0:v:0", "-pix_fmt", "rgb24",
                   "-f", "rawvideo", "pipe:1"]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        try:
            while True:
                chunk = proc.stdout.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            errors = proc.stderr.read()
            if proc.wait():
                raise RuntimeError(f"ffmpeg decoded frame verification failed: "
                                   f"{errors.decode('utf-8', 'replace')[-600:]}")
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            proc.stdout.close()
            proc.stderr.close()
    return digest.hexdigest()


def _frame_count(video):
    raw = _run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                "-show_entries", "stream=nb_read_frames", "-of", "json", str(video)])
    streams = json.loads(raw).get("streams", [])
    if len(streams) != 1:
        raise ValueError("could not count frames")
    value = streams[0].get("nb_read_frames")
    if not isinstance(value, str) or not value.isdigit() or int(value) < 1:
        raise ValueError("decoded frame count not verified")
    return int(value)


def _frame_rgb(video, frame_index, width, height):
    command = ["ffmpeg", "-nostdin", "-v", "error", "-i", str(video),
               "-vf", f"select=eq(n\\,{frame_index})", "-vsync", "0",
               "-frames:v", "1", "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"]
    pixels = _run(command, binary=True)
    if len(pixels) != width * height * 3:
        raise ValueError("could not decode exact requested seam frame")
    return pixels


def _seam_mae(first_rgb, second_rgb):
    if len(first_rgb) != len(second_rgb) or not first_rgb:
        raise ValueError("seam frame dimensions differ")
    # Pillow's C-level difference avoids expensive per-byte Python iteration.
    from PIL import Image, ImageChops, ImageStat
    # Use 1×N RGB rather than infer non-square geometry from byte buffers.
    a = Image.frombytes("RGB", (len(first_rgb) // 3, 1), first_rgb)
    b = Image.frombytes("RGB", (len(second_rgb) // 3, 1), second_rgb)
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def _required_sha(value, name):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError(f"{name} must be SHA256 hex")
    return value.lower()


def join_segments(first_file, second_file, output_dir, *,
                  first_sha256, second_sha256, expected_fps=24.0,
                  expected_frames_per_segment=72, max_c_seam_mae=8.0):
    """Join exactly two proven sources, preserving encoded packet sequence.

    Requires no audio in either *input*, including silent audio streams. An
    original generator's audio-policy failure must remain recorded separately;
    callers may use a verified silent derivative as the input if authorized.
    """
    from math import isfinite

    first = Path(first_file).resolve(strict=True)
    second = Path(second_file).resolve(strict=True)
    out = Path(output_dir).absolute()
    if not first.is_file() or not second.is_file() or first == second:
        raise ValueError("two distinct original photographic MP4 source files required")
    if out.exists() or out == first or out == second or out in first.parents or out in second.parents:
        raise ValueError("output must be a fresh directory disjoint from both inputs")
    if not out.parent.is_dir():
        raise ValueError("output parent must already exist")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe required")
    if not isinstance(expected_frames_per_segment, int) or expected_frames_per_segment < 2:
        raise ValueError("expected_frames_per_segment must be at least two")
    if not isfinite(expected_fps) or expected_fps <= 0:
        raise ValueError("expected_fps must be positive and finite")
    if not isfinite(max_c_seam_mae) or not 0 <= max_c_seam_mae <= 255:
        raise ValueError("max_c_seam_mae must be finite and within 0..255")

    expected = [_required_sha(first_sha256, "first_sha256"),
                _required_sha(second_sha256, "second_sha256")]
    initial = [file_sha256(first), file_sha256(second)]
    if initial != expected:
        raise ValueError("source SHA256 mismatch, no join attempted")
    if initial[0] == initial[1]:
        raise ValueError("A_TO_C and C_TO_A cannot be the identical video bytes")

    sources = [first, second]
    infos = [_stream_info(path) for path in sources]
    if infos[0] != infos[1]:
        raise ValueError("segments have incompatible encoded video stream properties")
    widths = infos[0]["width"]
    heights = infos[0]["height"]
    if widths * 9 != heights * 16:
        raise ValueError("this experimental pipeline requires exact 16:9")
    inputs = [probe(path) for path in sources]
    frames = [_frame_count(path) for path in sources]
    for idx, (info, count) in enumerate(zip(inputs, frames)):
        if info["audio_stream_count"]:
            raise ValueError(f"segment {idx+1} contains audio; preserve raw FAIL and create separate verified silent review copy")
        if count != expected_frames_per_segment:
            raise ValueError(f"segment {idx+1} decoded frames {count} != declared {expected_frames_per_segment}")
        if abs(info["fps"] - expected_fps) > 0.000001:
            raise ValueError(f"segment {idx+1} FPS differs from declared {expected_fps}")
        if abs(info["duration_seconds"] - count / expected_fps) > 1 / expected_fps:
            raise ValueError(f"segment {idx+1} has unexpected duration")

    first_last = _frame_rgb(first, frames[0]-1, widths, heights)
    second_first = _frame_rgb(second, 0, widths, heights)
    c_seam_mae = _seam_mae(first_last, second_first)
    if c_seam_mae > max_c_seam_mae:
        raise ValueError(f"C seam screen-space MAE {c_seam_mae:.4f} exceeds "
                         f"declared threshold {max_c_seam_mae:.4f}; manual review required")

    source_packets = [_packet_hashes(path) for path in sources]
    source_decoded_sha = _decoded_rgb_sequence_sha256(sources)
    ffmpeg_version = _run(["ffmpeg", "-version"]).splitlines()[0]
    ffprobe_version = _run(["ffprobe", "-version"]).splitlines()[0]

    with tempfile.TemporaryDirectory(prefix=".two-segment-stage-", dir=out.parent) as stage:
        staging = Path(stage)
        (staging / "part1.mp4").symlink_to(first)
        (staging / "part2.mp4").symlink_to(second)
        (staging / "concat.txt").write_text("file 'part1.mp4'\nfile 'part2.mp4'\n", encoding="utf-8")
        destination = staging / "two_segment_preview.mp4"
        command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-n",
                   "-f", "concat", "-safe", "0", "-auto_convert", "0",
                   "-i", str(staging / "concat.txt"),
                   "-map", "0:v:0", "-c:v", "copy", "-an", "-sn", "-dn",
                   "-map_metadata", "-1", "-map_chapters", "-1",
                   "-movflags", "+faststart", str(destination)]
        _run(command)
        output_info = probe(destination)
        output_stream = _stream_info(destination)
        output_frames = _frame_count(destination)
        packets = _packet_hashes(destination)
        if packets != source_packets[0] + source_packets[1]:
            raise ValueError("join changed encoded video packets or their order")
        joined_decoded_sha = _decoded_rgb_sequence_sha256([destination])
        if joined_decoded_sha != source_decoded_sha:
            raise ValueError("join changed actual decoded RGB frame sequence")
        if output_frames != sum(frames):
            raise ValueError("joined decoded frame count differs from both segments")
        if output_info["audio_stream_count"]:
            raise ValueError("unexpected output audio stream")
        if output_stream != infos[0]:
            raise ValueError("joined stream properties changed")
        if abs(output_info["duration_seconds"] - sum(frames) / expected_fps) > 1 / expected_fps:
            raise ValueError("joined duration differs by more than one frame")
        if [file_sha256(first), file_sha256(second)] != initial:
            raise ValueError("source files changed during join; reject staged artifact")
        output_sha = file_sha256(destination)
        report = {
            "schema_version": 1,
            "tool_version": __version__,
            "status": STATUS,
            "form_and_release_approval": HOLD,
            "ordered_photographic_roles": ["A_TO_C", "C_TO_A"],
            "role_evidence": "OPERATOR_DECLARED_ONLY_NOT_VIDEO_VERIFIED",
            "sources": [
                {"role": role, "path": str(path), "sha256": sha,
                 "decoded_frames": count, "probe": info}
                for role, path, sha, count, info in zip(
                    ["A_TO_C", "C_TO_A"], sources, initial, frames, inputs)
            ],
            "declared_expectations": {"fps": expected_fps,
                                      "frames_per_segment": expected_frames_per_segment,
                                      "max_c_seam_mae_0_to_255": max_c_seam_mae},
            "c_join": {"last_A_to_C_vs_first_C_to_A_rgb_mae_0_to_255": round(c_seam_mae, 6),
                       "screen_space_threshold_passed": True,
                       "manual_pose_identity_and_motion_review": "NOT_EVALUATED"},
            "preview": {"path": str(out / destination.name), "sha256": output_sha,
                        "decoded_frames": output_frames, "probe": output_info,
                        "decoded_rgb_sequence_sha256": joined_decoded_sha},
            "verification": {"encoded_video_packets_identical_in_source_order": True,
                             "decoded_rgb_frames_identical_in_source_order": True,
                             "video_stream_copy_no_fades": True,
                             "no_output_audio": True,
                             "source_bytes_unchanged": True},
            "reproducibility": {"ffmpeg_version": ffmpeg_version,
                                "ffprobe_version": ffprobe_version,
                                "exact_command": command,
                                "source_decoded_rgb_sequence_sha256": source_decoded_sha,
                                "concat_file_content": "file 'part1.mp4'\nfile 'part2.mp4'\n"},
            "warnings": [
                "This is a technical preview, not exercise form or production approval.",
                "A low C-seam pixel difference does not establish the correct opposite stance, limb identity or a natural transition.",
                "Source segment roles and A/C endpoint poses are declared by the operator, not inferred or proven by video pixels.",
                "Opening A/closing A loop seam is NOT evaluated by this tool.",
                "Any raw provider audio defect must remain recorded even if separately derived silent inputs were used.",
                "Current or future Flow credit estimates must be verified in the live interface; this offline tool spends none."
            ]
        }
        (staging / "concat.txt").unlink()
        (staging / "part1.mp4").unlink()
        (staging / "part2.mp4").unlink()
        with (staging / "two_segment_manifest.json").open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        # The entire evidence directory appears only after all checks pass.
        staging.rename(out)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Join two verified photographic motion segments as unapproved preview")
    parser.add_argument("a_to_c", type=Path)
    parser.add_argument("c_to_a", type=Path)
    parser.add_argument("--first-sha256", required=True)
    parser.add_argument("--second-sha256", required=True)
    parser.add_argument("--expected-fps", type=float, default=24.0)
    parser.add_argument("--expected-frames-per-segment", type=int, default=72)
    parser.add_argument("--max-c-seam-mae", type=float, default=8.0)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = join_segments(args.a_to_c, args.c_to_a, args.out,
                               first_sha256=args.first_sha256,
                               second_sha256=args.second_sha256,
                               expected_fps=args.expected_fps,
                               expected_frames_per_segment=args.expected_frames_per_segment,
                               max_c_seam_mae=args.max_c_seam_mae)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"preview": result["preview"]["path"],
                      "sha256": result["preview"]["sha256"],
                      "c_seam": result["c_join"],
                      "form_and_release_approval": HOLD}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
