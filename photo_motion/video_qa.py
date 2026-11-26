"""Read-only inspection of photographic MP4s; no automatic exercise approval.

Requires ffprobe/ffmpeg, plus Pillow only for contact sheets and seam metrics.
All generated output goes to an explicit --out directory, never into source media.
"""

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import __version__


def _run(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{command[0]} exited {result.returncode}: {result.stderr[-600:]}")
    return result.stdout


def file_sha256(path):
    hash_ = hashlib.sha256()
    with open(path, "rb") as file:
        for piece in iter(lambda: file.read(1024 * 1024), b""):
            hash_.update(piece)
    return hash_.hexdigest()


def read_recipe(path):
    """Check the record of what was actually submitted to a video generator.

    Missing model parameters or inaccessible remote assets remain explicitly
    unknown; this metadata does not imply deterministic AI generation.
    """
    recipe_path = Path(path).resolve()
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    required = ("schema_version", "provider", "model", "generation_id", "submitted_prompt_file", "input_images", "settings")
    missing = [field for field in required if field not in recipe]
    if missing:
        raise ValueError(f"generation recipe missing {', '.join(missing)}")
    if recipe["schema_version"] != 1:
        raise ValueError("unsupported generation recipe schema_version")
    if not isinstance(recipe["input_images"], list) or not recipe["input_images"] or not isinstance(recipe["settings"], dict):
        raise ValueError("generation recipe input_images must be a nonempty array and settings an object")
    for field in ("provider", "model", "generation_id"):
        if not isinstance(recipe[field], str) or not recipe[field].strip():
            raise ValueError(f"generation recipe {field} must be nonempty text")
    prompt_path = (recipe_path.parent / recipe["submitted_prompt_file"]).resolve()
    if not prompt_path.is_file():
        raise ValueError(f"exact submitted prompt not found: {prompt_path}")
    warnings = []
    images = []
    for index, item in enumerate(recipe["input_images"]):
        if not isinstance(item, dict) or not item.get("role") or not item.get("locator"):
            raise ValueError(f"generation recipe input_images[{index}] needs role and locator")
        file_ref = Path(item["locator"])
        if not file_ref.is_absolute():
            file_ref = recipe_path.parent / file_ref
        actual_hash = file_sha256(file_ref) if file_ref.is_file() else None
        expected = item.get("sha256")
        if expected is not None and (not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected)):
            raise ValueError(f"generation recipe image {index} sha256 must be a 64-character hex digest")
        if expected and actual_hash and expected != actual_hash:
            raise ValueError(f"generation recipe image {index} hash mismatch")
        if not actual_hash:
            warnings.append(f"Input image {index} ({item['role']}) was not locally available for SHA-256 verification; a recorded digest or URL is not proof of recoverability")
        images.append({"role": item["role"], "locator": item["locator"],
                       "sha256": expected or actual_hash, "hash_reverified_locally": actual_hash is not None})
    if not recipe["settings"]:
        warnings.append("Provider settings were not recorded; rerun equivalence cannot be established")
    return {
        "recipe_file": str(recipe_path), "recipe_sha256": file_sha256(recipe_path),
        "provider": recipe["provider"], "model": recipe["model"],
        "generation_id": recipe["generation_id"], "settings": recipe["settings"],
        "exact_submitted_prompt_file": str(prompt_path),
        "exact_submitted_prompt_sha256": file_sha256(prompt_path),
        "input_images": images,
        "warnings": warnings
    }


def _fraction(value):
    try:
        if "/" in value:
            a, b = value.split("/", 1)
            return float(a) / float(b) if float(b) else 0.0
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def probe(video):
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe is required; install ffmpeg")
    raw = _run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)])
    data = json.loads(raw)
    streams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    audio_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if len(streams) != 1:
        raise ValueError(f"expected exactly one video stream, found {len(streams)}")
    stream = streams[0]
    duration = _fraction(stream.get("duration") or data.get("format", {}).get("duration"))
    if duration <= 0:
        raise ValueError("video duration could not be read")
    return {
        "duration_seconds": duration,
        "width": stream.get("width"),
        "height": stream.get("height"),
        "fps": _fraction(stream.get("avg_frame_rate")),
        "codec": stream.get("codec_name"),
        "pixel_format": stream.get("pix_fmt"),
        "frame_count_reported": stream.get("nb_frames"),
        "audio_stream_count": len(audio_streams),
        "audio_codecs": [s.get("codec_name") for s in audio_streams]
    }


def _audio_levels(video, stream_count):
    """Read audio levels without writing or modifying media.

    A finite PCM peak means some decoded sample was nonzero, *not* that the
    sound is perceptually audible. An audio stream violates a forbid policy
    regardless of its level, including a perfectly silent track.
    """
    results = []
    for index in range(stream_count):
        cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "info",
               "-i", str(video), "-map", f"0:a:{index}", "-vn", "-af",
               "volumedetect", "-f", "null", "-"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        entry = {"stream_index": index, "mean_volume_dbfs": None,
                 "peak_volume_dbfs": None, "has_nonzero_pcm_samples": None}
        if proc.returncode:
            entry["analysis_warning"] = "Could not decode audio stream for volume screening"
        else:
            for metric, key in (("mean_volume", "mean_volume_dbfs"),
                                ("max_volume", "peak_volume_dbfs")):
                matches = re.findall(rf"{metric}:\s*(-?inf|-?\d+(?:\.\d+)?)\s*dB", proc.stderr)
                if matches and matches[-1] != "-inf":
                    entry[key] = float(matches[-1])
                elif not matches:
                    entry["analysis_warning"] = "Audio decoder returned no volume metric"
            if "analysis_warning" not in entry:
                entry["has_nonzero_pcm_samples"] = entry["peak_volume_dbfs"] is not None
        results.append(entry)
    return results


def _phase_samples(spec, info):
    # A planned phase at t=duration is a TARGET, not a frame that exists at t=duration.
    # Use the last decodable nominal frame and record its true approximate timestamp.
    last = max(0.0, info["duration_seconds"] - 1 / max(info["fps"], 1))
    return [(p["id"], min(p["time_seconds"], last), p["pose"], p.get("still_evidence", "")) for p in spec["phases"]]


def _extract(video, at, out):
    # -n is defense in depth: even if a symlink appears inside the fresh
    # output directory during extraction, ffmpeg must not follow/overwrite it.
    _run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-n", "-ss", f"{at:.4f}",
          "-i", str(video), "-frames:v", "1", "-vf", "scale=640:-2", str(out)])
    if not out.is_file() or not out.stat().st_size:
        raise RuntimeError(f"ffmpeg did not extract a frame at {at:.3f}s")


def _verify_full_video_decode(video):
    """Reject a clip with damaged frames outside the sparse phase samples.

    ffprobe can read valid container metadata while the payload has corrupt
    frames. Decode the *entire* video stream to a null sink, treating decoder
    errors as fatal, without modifying the source or creating output media.
    This is a technical intake gate, not a motion/form judgment.
    """
    _run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
          "-xerror", "-err_detect", "explode", "-i", str(video),
          "-map", "0:v:0", "-an", "-f", "null", "-"])


def _contact_sheet(samples, out, name):
    from PIL import Image, ImageDraw

    thumbs = []
    for sample in samples:
        im = Image.open(out / sample["file"]).convert("RGB")
        im.thumbnail((640, 420))
        thumbs.append(im)
    margin, tile_w, tile_h = 16, 672, 480
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), "#17212a")
    draw = ImageDraw.Draw(sheet)
    for idx, (im, sample) in enumerate(zip(thumbs, samples)):
        x = (idx % cols) * tile_w + margin
        y = (idx // cols) * tile_h + margin
        sheet.paste(im, (x, y + 25))
        draw.text((x, y), f"{sample['phase']} @ {sample['sample_time_seconds']:.3f}s", fill="white")
    path = out / name
    # Exclusive output: never follow an attacker/accidentally placed symlink
    # or overwrite old evidence even if it appears during this run.
    with path.open("xb") as handle:
        sheet.save(handle, format="PNG")
    return path


def _seam_metric(a, b):
    """Screen-space endpoint difference only; no anatomy/identity verdict."""
    from PIL import Image, ImageChops, ImageStat

    with Image.open(a) as first, Image.open(b) as last:
        im0 = first.convert("RGB").resize((320, 180))
        im1 = last.convert("RGB").resize((320, 180))
    return round(sum(ImageStat.Stat(ImageChops.difference(im0, im1)).mean) / 3, 3)


def inspect(spec, spec_path, video_path, out_dir, recipe_path=None):
    video, out = Path(video_path).resolve(), Path(out_dir).resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    if out == video or out in video.parents:
        raise ValueError("output directory cannot replace or contain the source video")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required")
    video_sha256 = file_sha256(video)
    spec_sha256 = file_sha256(spec_path)
    info = probe(video)
    _verify_full_video_decode(video)
    audio_policy = spec.get("audio_policy", "unspecified")
    if audio_policy not in {"unspecified", "forbid"}:
        raise ValueError(f"unsupported audio_policy {audio_policy!r}")
    audio_levels = _audio_levels(video, info["audio_stream_count"])
    provenance = read_recipe(recipe_path) if recipe_path else None
    # Never replace a previous diagnostic, even if a caller accidentally
    # reuses the same output path. Each run needs its own evidence directory.
    out.mkdir(parents=True, exist_ok=False)
    samples = []
    for phase_id, at, pose, evidence in _phase_samples(spec, info):
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", phase_id)
        filename = f"frame_{len(samples) + 1:02d}_{safe_id}.png"
        _extract(video, at, out / filename)
        samples.append({"phase": phase_id, "sample_time_seconds": round(at, 4),
                        "target_pose": pose, "still_evidence": evidence, "file": filename})
    board = _contact_sheet(samples, out, "phase_contact_sheet.png")
    seam = _seam_metric(out / samples[0]["file"], out / samples[-1]["file"])
    pairwise = [{"from": samples[i - 1]["phase"], "to": samples[i]["phase"],
                 "screen_space_mae_0_to_255": _seam_metric(out / samples[i - 1]["file"], out / samples[i]["file"])}
                for i in range(1, len(samples))]
    warnings = []
    duration_diff = abs(info["duration_seconds"] - spec["duration_seconds"])
    if duration_diff > 0.25:
        warnings.append(f"Clip duration differs from planned {spec['duration_seconds']:.3f}s by {duration_diff:.3f}s")
    if info["fps"] < 20:
        warnings.append("Clip has fewer than 20 frames/sec; inspect motion cadence")
    if min(info["width"], info["height"]) < 360:
        warnings.append("Clip has a frame dimension below 360px")
    if all(row["screen_space_mae_0_to_255"] < 0.5 for row in pairwise):
        warnings.append("All sampled phases look nearly identical at thumbnail resolution; verify the video contains real movement")
    if audio_policy == "forbid" and info["audio_stream_count"]:
        warnings.append(f"Audio policy forbids sound, but MP4 contains {info['audio_stream_count']} audio stream(s); inspect or remove audio in a separate derived deliverable")
    for item in audio_levels:
        if item.get("analysis_warning"):
            warnings.append(f"Audio stream {item['stream_index']}: {item['analysis_warning']}")
    # FFprobe and each FFmpeg sample are separate readers. Reject results if
    # a concurrent producer/rename replaces the source or movement contract.
    if file_sha256(video) != video_sha256:
        raise RuntimeError("source video changed during frame inspection; discard these results")
    if file_sha256(spec_path) != spec_sha256:
        raise RuntimeError("motion specification changed during frame inspection; discard these results")
    manifest = {
        "tool": "photo_motion.video_qa", "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_video": str(video), "source_video_sha256": video_sha256,
        "spec_file": str(Path(spec_path).resolve()), "spec_sha256": spec_sha256,
        "video": info,
        "audio": {"policy": audio_policy, "streams": audio_levels,
                  "interpretation": "A nonzero decoded PCM sample is not proof of audibility; an existing audio track breaches a forbid policy even when silent."},
        "contact_sheet": board.name, "frames": samples,
        "screen_space_start_end_mae_0_to_255": seam,
        "consecutive_sample_screen_space_differences": pairwise,
        "screen_space_metric_warning": "A low pixel difference does not prove correct anatomy, continuity or a smooth loop; a high difference may come from background compression or lighting.",
        "technical_warnings": warnings,
        "generation_provenance": provenance,
        "provenance_warning": None if provenance else "No generation recipe supplied. Model, exact submitted prompt and input-image lineage are NOT recorded by this inspection.",
        "human_review_required": [
            "Actual anatomical limb identity across every intermediate video frame",
            "Two genuine airborne exchanges for scissor jump, not a hidden pose teleport",
            "Accurate exercise form, realistic joint range and planted contact points",
            "Same photographic character, clothing, camera, scale and environment",
            "No ghost limbs, dissolves, stutters or discontinuous loop seam at normal speed"
        ],
        "form_and_release_approval": "NOT_EVALUATED"
    }
    with (out / "inspection.json").open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, indent=2) + "\n")
    return manifest
