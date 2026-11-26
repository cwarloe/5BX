"""Create a reproducible, explicitly unapproved five-exercise Chart 1 review reel.

This is a media assembly tool, not a motion generator or exercise-form reviewer.
It refuses incomplete manifests and preserves every original input unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


EXERCISES = (
    "toe_touch",
    "partial_situp",
    "alternate_leg_raise",
    "kneeling_pushup",
    "run_and_scissor",
)
TITLES = (
    "01 TOE TOUCH", "02 PARTIAL SIT UP", "03 ALTERNATING LEG RAISE",
    "04 KNEELING PUSH UP", "05 RUN AND SCISSOR",
)


class AssemblyError(ValueError):
    """Fail closed rather than present an incomplete reel as Chart 1."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_video(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise AssemblyError(f"Unreadable source video: {path}")
    try:
        metadata = json.loads(result.stdout)
        streams = [s for s in metadata["streams"] if s["codec_type"] == "video"]
        duration = float(metadata["format"]["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise AssemblyError(f"Incomplete video metadata: {path}") from error
    if len(streams) != 1 or streams[0].get("codec_name") not in {"h264", "hevc", "vp9", "av1", "mpeg4"}:
        raise AssemblyError(f"Expected one real video stream, not a still or extra cover stream: {path}")
    if not 0.25 <= duration <= 120:
        raise AssemblyError(f"Unexpected source duration: {path} ({duration}s)")
    return {"duration_seconds": duration, "codec": streams[0]["codec_name"],
            "width": streams[0].get("width"), "height": streams[0].get("height")}


def preflight(manifest: Path, output: Path) -> list[dict]:
    try:
        record = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise AssemblyError("Cannot read a valid JSON manifest") from error
    if record.get("schema_version") != 1 or record.get("chart") != 1:
        raise AssemblyError("Only schema version 1 for Chart 1 is supported")
    clips = record.get("clips")
    if not isinstance(clips, list) or len(clips) != 5:
        raise AssemblyError("Require five actual video clips, one for each Chart 1 exercise")
    if output.exists() or output.with_suffix(".evidence.json").exists():
        raise AssemblyError("Output or evidence file already exists; choose a new revision")
    if not output.parent.is_dir():
        raise AssemblyError("Output directory must already exist")
    validated = []
    for index, (clip, expected) in enumerate(zip(clips, EXERCISES, strict=True), 1):
        if not isinstance(clip, dict) or clip.get("exercise") != index or clip.get("role") != expected:
            raise AssemblyError(f"Slot {index} must be {expected} in original 5BX order")
        raw = clip.get("file")
        if not isinstance(raw, str) or not raw:
            raise AssemblyError(f"Missing media path for exercise {index}")
        path = (manifest.parent / raw).resolve()
        if not path.is_file() or path.suffix.lower() != ".mp4":
            raise AssemblyError(f"Exercise {index} requires an existing MP4: {path}")
        if output.resolve() == path or output.with_suffix(".evidence.json").resolve() == path:
            raise AssemblyError("Output cannot overwrite a source")
        media = inspect_video(path)
        validated.append({"exercise": index, "role": expected, "path": str(path),
                          "sha256": sha256(path), "media": media,
                          "source_url": clip.get("source_url"), "qa_status": clip.get("qa_status", "UNVERIFIED")})
    if len({c["path"] for c in validated}) != 5:
        raise AssemblyError("Each exercise needs a distinct source video; duplicate file reuse is not evidence")
    return validated


def assemble(manifest: Path, output: Path, *, width: int = 1280, height: int = 720,
             fps: int = 24) -> dict:
    if width < 160 or height < 90 or width % 2 or height % 2 or not 1 <= fps <= 60:
        raise AssemblyError("Width/height must be even and reasonable; FPS must be 1–60")
    clips = preflight(manifest, output)
    input_args = [item for c in clips for item in ("-i", c["path"])]
    filters = []
    for i in range(5):
        filters.append(
            f"[{i}:v:0]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1,fps={fps},format=yuv420p,setpts=PTS-STARTPTS,"
            f"drawbox=x=0:y=0:w=iw:h=30:color=black@0.7:t=fill,"
            f"drawtext=text='EXPERIMENTAL - NOT APPROVED':fontcolor=white:fontsize=16:x=8:y=6,"
            f"drawbox=x=0:y=ih-32:w=iw:h=32:color=black@0.7:t=fill,"
            f"drawtext=text='{TITLES[i]}':fontcolor=white:fontsize=18:x=8:y=h-26[v{i}]"
        )
    filters.append("".join(f"[v{i}]" for i in range(5)) + "concat=n=5:v=1:a=0[vout]")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n", *input_args,
           "-filter_complex", ";".join(filters), "-map", "[vout]", "-an",
           "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(output)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode:
        # Preserve the original five videos and report the specific encoder failure.
        raise AssemblyError(f"FFmpeg assembly failed: {result.stderr[-600:]}")
    evidence = {
        "schema_version": 1,
        "purpose": "EXPERIMENTAL_CHART1_REVIEW_ONLY_NOT_INSTRUCTIONAL_OR_OWNER_APPROVED",
        "source_manifest": str(manifest.resolve()), "source_manifest_sha256": sha256(manifest),
        "output": str(output.resolve()), "output_sha256": sha256(output),
        "output_media": inspect_video(output), "clips": clips,
        "limitations": ["Technical assembly does not validate 5BX form, identity, loop or safety.",
                        "No footage here is considered owner-approved or published."],
    }
    output.with_suffix(".evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--size", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"), default=(1280, 720))
    parser.add_argument("--fps", type=int, default=24)
    args = parser.parse_args()
    try:
        evidence = assemble(args.manifest, args.output, width=args.size[0], height=args.size[1], fps=args.fps)
    except AssemblyError as error:
        parser.exit(2, f"Chart 1 assembly HOLD: {error}\n")
    print(json.dumps({"output": evidence["output"], "sha256": evidence["output_sha256"],
                      "status": evidence["purpose"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
