"""Make a verifiably video-bitstream-identical silent photographic review copy.

This is post-processing, not evidence that the *raw* generated video obeyed a
no-audio prompt, nor an exercise-form or production-release approval.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__
from .video_qa import file_sha256, probe


HOLD = "HOLD_FOR_HUMAN_FORM_AND_RELEASE_REVIEW"
DERIVED = "SILENT_DERIVATIVE_ONLY_RAW_GENERATION_UNCHANGED"


def _run(args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed ({result.returncode}): {result.stderr[-600:]}")
    return result.stdout


def _packet_identity(path):
    """Hash *ordered encoded video packet bytes*, not MP4 container bytes.

    ffprobe emits one SHA-256 hash per encoded packet. The concatenation is
    length-delimited to avoid ambiguous sequences; missing hashes fail closed.
    This detects transcoding and packet reordering, though it does not assess
    temporal pose quality or player-level visual correctness.
    """
    raw = _run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_packets", "-show_data_hash", "sha256",
                "-show_entries", "packet=data_hash", "-of", "json", str(path)])
    packets = json.loads(raw).get("packets")
    if not isinstance(packets, list) or not packets:
        raise ValueError("could not enumerate video packets")
    digest = hashlib.sha256()
    for packet in packets:
        stamp = packet.get("data_hash")
        if not isinstance(stamp, str) or not re.fullmatch(r"SHA256:[0-9a-fA-F]{64}", stamp):
            raise ValueError("video packet lacks ffprobe SHA256 verification")
        digest.update(bytes.fromhex(stamp.split(":", 1)[1]))
    return {"packet_count": len(packets), "ordered_packet_hashes_sha256": digest.hexdigest()}


def _frame_count(path):
    raw = _run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                "-show_entries", "stream=nb_read_frames", "-of", "json", str(path)])
    streams = json.loads(raw).get("streams", [])
    if len(streams) != 1:
        raise ValueError("could not count exactly one video stream")
    value = streams[0].get("nb_read_frames")
    if not isinstance(value, str) or not value.isdigit() or int(value) <= 0:
        raise ValueError("video decoded-frame count unavailable")
    return int(value)


def create_silent_derivative(source_file, output_dir, expected_source_sha256):
    """Create a new evidence directory, never edit the input or prior output."""
    source = Path(source_file).resolve(strict=True)
    out = Path(output_dir).absolute()
    if not source.is_file():
        raise ValueError("source is not a regular file")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_source_sha256):
        raise ValueError("--source-sha256 must be a 64-character SHA256 digest")
    actual_source_hash = file_sha256(source)
    if actual_source_hash != expected_source_sha256.lower():
        raise ValueError("source SHA256 mismatch: no derivative created")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe binaries are required")
    if out == source or out in source.parents or out.exists():
        raise ValueError("output must be a new directory disjoint from the source")

    source_probe = probe(source)
    source_packets = _packet_identity(source)
    source_frames = _frame_count(source)
    if source_probe["fps"] <= 0:
        raise ValueError("input FPS is unknown")
    ffmpeg_version = _run(["ffmpeg", "-version"]).splitlines()[0]

    # Only one video stream survives; deliberately drop audio, subtitle, data,
    # metadata and chapters. Stream copy preserves encoded video packet bytes.
    output = out / "silent_review.mp4"
    command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-n",
               "-i", str(source), "-map", "0:v:0", "-c:v", "copy",
               "-an", "-sn", "-dn", "-map_metadata", "-1", "-map_chapters", "-1",
               "-movflags", "+faststart", str(output)]
    out.mkdir(parents=True, exist_ok=False)
    _run(command)
    derived_probe = probe(output)
    derived_packets = _packet_identity(output)
    derived_frames = _frame_count(output)
    if derived_probe["audio_stream_count"] != 0:
        raise ValueError("DERIVATIVE FAIL: audio stream remains")
    if derived_packets != source_packets:
        raise ValueError("DERIVATIVE FAIL: encoded video packet stream changed")
    if derived_frames != source_frames:
        raise ValueError("DERIVATIVE FAIL: decoded frame count changed")
    for property_ in ("width", "height", "codec", "pixel_format"):
        if derived_probe[property_] != source_probe[property_]:
            raise ValueError(f"DERIVATIVE FAIL: {property_} changed")
    if abs(derived_probe["duration_seconds"] - source_probe["duration_seconds"]) > 1 / source_probe["fps"]:
        raise ValueError("DERIVATIVE FAIL: duration drift exceeds one frame")

    report = {
        "schema_version": 1,
        "tool_version": __version__,
        "derivative_status": DERIVED,
        "raw_generation_audio_policy_result": (
            "FAIL_AUDIO_PRESENT_IN_RAW" if source_probe["audio_stream_count"] else "NO_AUDIO_IN_RAW"
        ),
        "form_and_release_approval": HOLD,
        "source": {"path": str(source), "sha256": actual_source_hash,
                   "probe": source_probe, "decoded_frames": source_frames,
                   "video_packets": source_packets},
        "derivative": {"path": str(output), "sha256": file_sha256(output),
                       "probe": derived_probe, "decoded_frames": derived_frames,
                       "video_packets": derived_packets},
        "verification": {"audio_streams_removed": derived_probe["audio_stream_count"] == 0,
                         "encoded_video_packets_identical": derived_packets == source_packets,
                         "decoded_frame_count_identical": derived_frames == source_frames,
                         "duration_delta_seconds": round(derived_probe["duration_seconds"] - source_probe["duration_seconds"], 9)},
        "reproducibility": {"ffmpeg_version": ffmpeg_version, "exact_command": command},
        "warnings": ["This derivative does not cure motion, anatomical continuity, framing or loop defects.",
                     "The original provider output and its recorded audio-policy failure must be retained."],
    }
    with (out / "silent_derivative_manifest.json").open("x", encoding="utf-8") as file:
        json.dump(report, file, indent=2, sort_keys=True)
        file.write("\n")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create a verified silent review derivative; never approve exercise form")
    parser.add_argument("source", type=Path, help="original raw MP4; never modified")
    parser.add_argument("--source-sha256", required=True, help="verified exact raw MP4 digest")
    parser.add_argument("--out", required=True, type=Path, help="new, nonexisting evidence directory")
    args = parser.parse_args(argv)
    try:
        report = create_silent_derivative(args.source, args.out, args.source_sha256)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"derivative": report["derivative"]["path"],
                      "manifest": str(args.out.absolute() / "silent_derivative_manifest.json"),
                      "source_sha256": report["source"]["sha256"],
                      "derivative_sha256": report["derivative"]["sha256"],
                      "verification": report["verification"],
                      "form_and_release_approval": HOLD}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
