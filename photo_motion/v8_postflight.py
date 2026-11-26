"""Read-only postflight measurements for a V8 direct-endpoint photographic MP4.

Endpoint pixel agreement and technical format are evidence, never a verdict
on anatomical continuity, airborne exercise form, or release approval.
"""

import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

from .video_qa import _audio_levels, _verify_full_video_decode, file_sha256, probe


def _extract_endpoints(video, count, directory):
    pattern = str(directory / "endpoint_%02d.png")
    expression = f"select=eq(n\\,0)+eq(n\\,{count - 1})"
    proc = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-xerror",
         "-i", str(video), "-vf", expression, "-vsync", "0", "-frames:v", "2", pattern],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode:
        raise RuntimeError(f"endpoint extraction failed: {proc.stderr[-400:]}")
    paths = [directory / "endpoint_01.png", directory / "endpoint_02.png"]
    if not all(path.is_file() for path in paths):
        raise ValueError("could not decode both the first and final video frames")
    return paths


def _mae(reference, frame):
    with Image.open(reference) as src, Image.open(frame) as actual:
        if src.size != actual.size:
            raise ValueError(f"reference/frame dimensions differ: {src.size} vs {actual.size}")
        difference = ImageChops.difference(src.convert("RGB"), actual.convert("RGB"))
        return round(sum(ImageStat.Stat(difference).mean) / 3, 4)


def measure(spec_path, start_image, end_image, video_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    if spec.get("authority") != "V8_FRAMES_DIRECT_A_C_SEGMENTS" or spec.get("segment_role") not in {"A_TO_C", "C_TO_A"}:
        raise ValueError("requires a V8 direct-endpoint segment contract")
    if (spec.get("start_pose"), spec.get("end_pose")) != (("A", "C") if spec["segment_role"] == "A_TO_C" else ("C", "A")):
        raise ValueError("segment role and ordered endpoint poses disagree")
    start, end, video = (Path(p).resolve() for p in (start_image, end_image, video_path))
    for role, path in (("start", start), ("end", end)):
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = file_sha256(path)
        if digest != spec.get(f"{role}_sha256"):
            raise ValueError(f"{role} image SHA-256 does not match the V8 contract")
    if not video.is_file():
        raise FileNotFoundError(video)
    info = probe(video)
    _verify_full_video_decode(video)
    fps, duration = float(info["fps"]), float(info["duration_seconds"])
    count = info["frame_count_reported"]
    if not count or not str(count).isdigit() or int(count) < 2:
        raise ValueError("an explicit decoded video frame count is needed for exact endpoints")
    count = int(count)
    warnings = []
    if (info["width"], info["height"]) != (1280, 720):
        warnings.append("video dimensions differ from V8 1280x720")
    if not math.isclose(fps, spec["fps"], abs_tol=0.01):
        warnings.append("frame rate differs from V8 target")
    if count != spec["duration_seconds"] * spec["fps"]:
        warnings.append("decoded frame count differs from V8 target")
    if not math.isclose(duration, spec["duration_seconds"], abs_tol=0.15):
        warnings.append("video duration differs from V8 target")
    if info["audio_stream_count"]:
        warnings.append("generated output includes forbidden audio stream(s)")
    with tempfile.TemporaryDirectory(prefix="v8-endpoint-qa-") as temp:
        first, last = _extract_endpoints(video, count, Path(temp))
        first_mae, last_mae = _mae(start, first), _mae(end, last)
    return {
        "schema_version": 1,
        "authority": "V8_FRAMES_DIRECT_A_C_SEGMENTS",
        "segment_role": spec["segment_role"],
        "spec_sha256": file_sha256(spec_path),
        "start_source_sha256": file_sha256(start),
        "end_source_sha256": file_sha256(end),
        "raw_video_sha256": file_sha256(video),
        "video": info,
        "decoded_frames": count,
        "duration_seconds": duration,
        "start_frame_mae_0_to_255": first_mae,
        "end_frame_mae_0_to_255": last_mae,
        "audio_levels": _audio_levels(video, info["audio_stream_count"]),
        "technical_warnings": warnings,
        "motion_form_identity_and_release": "NOT_EVALUATED",
        "interpretation": "Pixel agreement proves neither correct physical limb exchange nor safe form; this is one segment, not a loop.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec")
    parser.add_argument("start_image")
    parser.add_argument("end_image")
    parser.add_argument("video")
    parser.add_argument("--report", required=True)
    args = parser.parse_args(argv)
    report = Path(args.report).resolve()
    source_paths = {Path(p).resolve() for p in (args.spec, args.start_image, args.end_image, args.video)}
    if report in source_paths or report.exists():
        parser.error("report must be new and must not replace any input")
    try:
        result = measure(args.spec, args.start_image, args.end_image, args.video)
        report.parent.mkdir(parents=True, exist_ok=True)
        with report.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps({"report": str(report), "technical_warnings": result["technical_warnings"],
                      "motion_form_identity_and_release": "NOT_EVALUATED"}, indent=2))


if __name__ == "__main__":
    main()
