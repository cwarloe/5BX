"""Temporal diagnostics for actual photographic exercise videos.

This is a read-only screening instrument. Pixel differences are *not* pose
tracking, form verification, or proof of a continuous anatomical movement.

Needs ffmpeg, ffprobe and numpy. Works on streaming decoded frames, so it can
inspect a full workout without keeping the entire clip in memory.

    python3 -m photo_motion.temporal_qa actual.mp4 --report temporal.json
    python3 -m photo_motion.temporal_qa actual.mp4 --hold 0:1 --report temporal.json
"""

import argparse
from collections import deque
import hashlib
import json
import math
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

import numpy as np

from .video_qa import probe


WIDTH, HEIGHT = 160, 90
REVERSAL_FLANK_FRAMES = 5


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _frame_times(video):
    """Return decoded-frame presentation times, if the container exposes them."""
    result = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "csv=p=0",
        str(video)
    ], capture_output=True, text=True, check=False)
    if result.returncode:
        return []
    times = []
    for line in result.stdout.splitlines():
        try:
            value = float(line.strip().split(",")[0])
            if math.isfinite(value):
                times.append(value)
        except (ValueError, IndexError):
            continue
    return times


def _validate_background_rois(rois, width=WIDTH, height=HEIGHT):
    """Map explicit person-free rectangles to the analysis grid.

    ROI coordinates are normalized to the full original video frame. These
    rectangles must be chosen by the reviewer, never inferred as background.
    """
    if rois is None:
        return []
    if not isinstance(rois, (list, tuple)):
        raise ValueError("background ROIs must be a list of normalized rectangles")
    validated = []
    for index, roi in enumerate(rois):
        if not isinstance(roi, (list, tuple)) or len(roi) != 4:
            raise ValueError(f"background ROI {index} must have four normalized coordinates")
        if any(type(value) not in (int, float) or not math.isfinite(value)
               for value in roi):
            raise ValueError(f"background ROI {index} requires finite numeric coordinates")
        x0, y0, x1, y1 = roi
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            raise ValueError(f"background ROI {index} must satisfy 0 <= min < max <= 1")
        px0, py0 = int(round(x0 * width)), int(round(y0 * height))
        px1, py1 = int(round(x1 * width)), int(round(y1 * height))
        if px1 - px0 < 2 or py1 - py0 < 2:
            raise ValueError(f"background ROI {index} is less than two pixels on the analysis grid")
        validated.append({"normalized_xyxy": [float(v) for v in roi],
                          "pixels_xyxy": [px0, py0, px1, py1]})
    return validated


def _stream_differences(video, width=WIDTH, height=HEIGHT, background_rois=()):
    """Decode all frames in order; return screen-space differences only.

    Each delta belongs to frame i versus i-1. No optical-flow, pose identity,
    external network call, interpolation or manipulation of the source occurs.
    """
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg binary is required")
    command = [
        "ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-xerror", "-err_detect", "explode",
        "-i", str(video),
        "-an", "-sn", "-dn", "-vf", f"scale={width}:{height},format=gray",
        "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    frame_size = width * height
    all_scores, border_scores, count = [], [], 0
    roi_scores = [[] for _ in background_rois]
    # The center contains most of the person in our fixed-camera experiments.
    # The outer border is a background/camera diagnostic, not camera proof.
    border = np.ones((height, width), dtype=bool)
    border[height // 5: 4 * height // 5, width // 5: 4 * width // 5] = False
    previous = None
    first = None
    try:
        while True:
            frame = process.stdout.read(frame_size)
            if not frame:
                break
            if len(frame) != frame_size:
                raise RuntimeError(f"truncated decoded frame: {len(frame)} of {frame_size} bytes")
            current = np.frombuffer(frame, dtype=np.uint8).reshape((height, width))
            count += 1
            if first is None:
                first = current.copy()
            if previous is not None:
                difference = np.abs(current.astype(np.int16) - previous.astype(np.int16))
                all_scores.append(float(difference.mean()))
                border_scores.append(float(difference[border].mean()))
                for roi, scores in zip(background_rois, roi_scores):
                    x0, y0, x1, y1 = roi["pixels_xyxy"]
                    scores.append(float(difference[y0:y1, x0:x1].mean()))
            previous = current.copy()
        errors = process.stderr.read().decode("utf-8", errors="replace")
        if process.wait() != 0:
            raise RuntimeError(f"ffmpeg decoding failed: {errors[-600:]}")
        if count < 2:
            raise ValueError("need at least two decoded video frames")
        difference = np.abs(first.astype(np.int16) - previous.astype(np.int16))
        seam = float(difference.mean())
        seam_border = float(difference[border].mean())
        roi_seams = []
        for roi in background_rois:
            x0, y0, x1, y1 = roi["pixels_xyxy"]
            roi_seams.append(float(difference[y0:y1, x0:x1].mean()))
        return count, all_scores, border_scores, seam, seam_border, roi_scores, roi_seams
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()


def _scan_motion_reversals(video, width=WIDTH, height=HEIGHT):
    """Locate *near-exact mirrored frame sequences*, not anatomical reversal.

    Five consecutive mirrored pairs around a center frame are more specific
    than a single negative velocity cosine. A natural symmetric bounce can
    still trigger this diagnostic, so its output requires human inspection.
    A fixed-size ring buffer keeps memory bounded for long videos.
    """
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg binary is required")
    command = [
        "ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-xerror", "-err_detect", "explode",
        "-i", str(video), "-an", "-sn", "-dn",
        "-vf", f"scale={width}:{height},format=gray",
        "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    flank = REVERSAL_FLANK_FRAMES
    frames = deque(maxlen=2 * flank + 1)
    candidates = []
    count = 0
    frame_size = width * height
    try:
        while True:
            raw = process.stdout.read(frame_size)
            if not raw:
                break
            if len(raw) != frame_size:
                raise RuntimeError(f"truncated decoded frame: {len(raw)} of {frame_size} bytes")
            frames.append(np.frombuffer(raw, dtype=np.uint8).reshape(height, width).astype(np.int16))
            count += 1
            if len(frames) != 2 * flank + 1:
                continue
            transitions = [float(np.abs(frames[k] - frames[k - 1]).mean())
                           for k in range(1, len(frames))]
            movement = statistics.median(transitions)
            if movement < 0.6:
                # Tiny codec/grain changes and static holds are not movement.
                continue
            mirrored = [float(np.abs(frames[flank - k] - frames[flank + k]).mean())
                        for k in range(1, flank + 1)]
            if (statistics.median(mirrored) > max(.3, .18 * movement)
                    or max(mirrored) > max(.5, .40 * movement)):
                continue
            before = (frames[flank] - frames[flank - 1]).astype(np.float64).ravel()
            after = (frames[flank + 1] - frames[flank]).astype(np.float64).ravel()
            norm = float(np.linalg.norm(before) * np.linalg.norm(after))
            cosine = float(np.dot(before, after) / norm) if norm else 0.0
            if cosine > -.9:
                continue
            candidates.append({
                "center_frame_index": count - flank - 1,
                "velocity_cosine": round(cosine, 5),
                "median_mirrored_pair_mae_0_to_255": round(statistics.median(mirrored), 4),
                "max_mirrored_pair_mae_0_to_255": round(max(mirrored), 4),
                "median_local_transition_mae_0_to_255": round(movement, 4),
                "mirrored_pair_count": flank,
            })
        errors = process.stderr.read().decode("utf-8", errors="replace")
        if process.wait() != 0:
            raise RuntimeError(f"ffmpeg decoding failed: {errors[-600:]}")
        return count, candidates
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()


def _holds(deltas, times, fps, threshold, minimum_seconds, expected_holds):
    """Find sustained *screen-space* stillness, not anatomically valid holds."""
    runs = []
    start = None
    for index in range(1, len(deltas) + 2):
        frozen = index <= len(deltas) and deltas[index - 1] <= threshold
        if frozen and start is None:
            start = index
        if start is not None and not frozen:
            last = index - 1
            start_time = times[start - 1] if len(times) > start - 1 else (start - 1) / fps
            end_time = times[last] if len(times) > last else last / fps
            duration = max(0.0, end_time - start_time)
            if duration >= minimum_seconds:
                explained = any(a - .08 <= start_time and end_time <= b + .08 for a, b in expected_holds)
                runs.append({
                    "start_seconds": round(start_time, 3),
                    "end_seconds": round(end_time, 3),
                    "duration_seconds": round(duration, 3),
                    "classification": "DECLARED_HOLD" if explained else "REVIEW_STILLNESS"
                })
            start = None
    return runs


def _cuts(deltas, timestamps, fps):
    """Flag unusually strong discontinuities; never assert scene edits as fact."""
    if not deltas:
        return []
    base = statistics.median(deltas)
    mad = statistics.median(abs(x - base) for x in deltas)
    # Relative *and* absolute gates limit false alarms from noisy running
    # movement. Transparent: a genuine cut can still escape this screening.
    threshold = max(18.0, base * 6, base + 10 * mad)
    return [{"at_seconds": round(timestamps[index + 1] if len(timestamps) > index + 1 else (index + 1) / fps, 3),
             "screen_space_mae_0_to_255": round(score, 3)}
            for index, score in enumerate(deltas) if score > threshold]


def analyze(video_path, *, expected_holds=(), still_threshold=0.5, minimum_hold_seconds=0.5,
            expect_loop=False, background_rois=(), check_motion_reversal=False):
    """Inspect a real video and return JSON-safe evidence, not approval."""
    video = Path(video_path).resolve()
    if not video.is_file():
        raise FileNotFoundError(video)
    if type(expect_loop) is not bool:
        raise ValueError("expect_loop must be a boolean")
    if type(check_motion_reversal) is not bool:
        raise ValueError("check_motion_reversal must be a boolean")
    regions = _validate_background_rois(background_rois)
    # A digest of a *different* later file must never be attached to decoded
    # frames from this take. Check both sides of the multi-process inspection.
    source_sha256 = _sha256(video)
    for label, value in (("still_threshold", still_threshold), ("minimum_hold_seconds", minimum_hold_seconds)):
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError(f"{label} must be a finite number")
    if still_threshold < 0 or minimum_hold_seconds <= 0:
        raise ValueError("stillness threshold must be nonnegative and hold duration positive")
    for start, stop in expected_holds:
        if any(isinstance(t, bool) or not isinstance(t, (float, int)) or not math.isfinite(t) for t in (start, stop)):
            raise ValueError("expected hold endpoints must be finite numbers")
        if start < 0 or stop <= start:
            raise ValueError("expected holds must have 0 <= start < end")
    info = probe(video)
    fps = info["fps"]
    if not fps:
        raise ValueError("video frame rate missing")
    (decoded_count, delta, border, seam, seam_border,
     roi_changes, roi_seams) = _stream_differences(video, background_rois=regions)
    reversal_candidates = []
    if check_motion_reversal:
        reversal_count, reversal_candidates = _scan_motion_reversals(video)
        if reversal_count != decoded_count:
            raise RuntimeError("motion-reversal scan decoded a different frame count; discard results")
    timestamps = _frame_times(video)
    if _sha256(video) != source_sha256:
        raise RuntimeError("source video changed during temporal inspection; discard these results")
    warnings = []
    if len(timestamps) != decoded_count:
        warnings.append("Frame timestamps unavailable or inconsistent with decoded count; time positions use average FPS")
        timestamps = [i / fps for i in range(decoded_count)]
    step = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
    expected_step = 1 / fps
    pacing = [{"at_seconds": round(timestamps[i], 3), "step_seconds": round(gap, 5)}
              for i, gap in enumerate(step, 1)
              if gap <= 0 or gap > 1.5 * expected_step]
    stillness = _holds(delta, timestamps, fps, still_threshold, minimum_hold_seconds, expected_holds)
    cuts = _cuts(delta, timestamps, fps)
    if any(item["classification"] == "REVIEW_STILLNESS" for item in stillness):
        warnings.append("Sustained visually still spans outside declared holds; inspect whether motion froze")
    if cuts:
        warnings.append("Abrupt visual discontinuities were detected; inspect for cut/pose jumps or flashes")
    if pacing:
        warnings.append("Irregular decoded frame timestamps; inspect cadence and dropped/duplicated frames")
    if len(delta) and max(delta) <= still_threshold:
        warnings.append("Entire clip appears nearly static in screen-space metrics")
    if statistics.median(border) > 3:
        warnings.append("Background/border pixels change substantially; inspect for camera motion, relighting or background drift")
    loop_threshold = max(5.0, 3.0 * statistics.median(delta))
    if expect_loop:
        loop_verdict = ("REVIEW_DISCONTINUITY" if seam > loop_threshold
                        else "SCREEN_SPACE_ALIGNED_NOT_FORM_APPROVAL")
        if loop_verdict == "REVIEW_DISCONTINUITY":
            warnings.append("Requested loop seam has excessive first/last screen-space difference; review the actual motion seam")
    else:
        loop_verdict = "NOT_REQUESTED"

    if check_motion_reversal:
        for item in reversal_candidates:
            index = item["center_frame_index"]
            item["at_seconds"] = round(timestamps[index], 4)
        if reversal_candidates:
            warnings.append("Near-mirrored forward/reverse frame sequence detected; inspect for a mechanically reversed segment. Natural symmetric movement may also trigger this warning")
        reversal_verdict = ("REVIEW_NEAR_MIRRORED_SEQUENCE" if reversal_candidates
                            else "NO_NEAR_MIRRORED_SEQUENCE_DETECTED")
    else:
        reversal_verdict = "NOT_REQUESTED"

    region_reports = []
    for roi, values, first_last in zip(regions, roi_changes, roi_seams):
        maximum = max(values)
        median = statistics.median(values)
        # A region may be intentionally empty background yet move because of
        # an errant hand or a matte seam. Report change, not its cause.
        outliers = [{"frame_index": i + 1, "at_seconds": round(timestamps[i + 1], 4),
                     "mae_0_to_255": round(value, 4)}
                    for i, value in enumerate(values) if value > max(8.0, 5.0 * median)]
        if maximum > 10 or first_last > 10:
            warnings.append("Selected static background ROI changed; inspect for scene drift, foreground intrusion or matte artifacts")
        region_reports.append({
            "normalized_xyxy": roi["normalized_xyxy"],
            "analysis_grid_xyxy": roi["pixels_xyxy"],
            "median_frame_transition_mae_0_to_255": round(median, 4),
            "maximum_frame_transition_mae_0_to_255": round(maximum, 4),
            "first_last_mae_0_to_255": round(first_last, 4),
            "large_change_events_total": len(outliers),
            "large_change_events": outliers[:100],
        })
    return {
        "tool": "photo_motion.temporal_qa", "schema_version": 1,
        "source_video": str(video), "source_video_sha256": source_sha256,
        "video": info, "decoded_frame_count": decoded_count,
        "sampling_size": [WIDTH, HEIGHT], "difference_units": "Mean absolute grayscale change per pixel, 0–255",
        "mean_frame_difference": round(statistics.mean(delta), 4),
        "median_frame_difference": round(statistics.median(delta), 4),
        "max_frame_difference": round(max(delta), 4),
        "median_border_difference": round(statistics.median(border), 4),
        "first_last_seam_mae_0_to_255": round(seam, 4),
        "first_last_border_seam_mae_0_to_255": round(seam_border, 4),
        "expect_loop": expect_loop,
        "loop_seam_review_threshold_mae_0_to_255": round(loop_threshold, 4),
        "loop_seam_screen_space_verdict": loop_verdict,
        "motion_reversal_check_requested": check_motion_reversal,
        "motion_reversal_screen_space_verdict": reversal_verdict,
        "motion_reversal_candidates_total": len(reversal_candidates),
        "motion_reversal_candidates": reversal_candidates[:100],
        "background_roi_diagnostics": region_reports,
        "near_identical_frame_transitions": sum(x <= still_threshold for x in delta),
        "total_frame_transitions": len(delta),
        "expected_hold_windows": [{"start_seconds": a, "end_seconds": b} for a, b in expected_holds],
        "sustained_stillness": stillness,
        "potential_abrupt_cuts": cuts[:100],
        "potential_abrupt_cuts_total": len(cuts),
        "frame_pacing_anomalies": pacing[:100],
        "frame_pacing_anomalies_total": len(pacing),
        "technical_warnings": warnings,
        "interpretation": (
            "Screen-space motion screening only. Intentional holds are legitimate; moving backgrounds, grain and lighting "
            "can mask frozen anatomy. Optional static ROIs are reviewer-declared, not automatically discovered; "
            "their changes can be due to camera, matte, body intrusion or lighting. First/last seam alignment "
            "cannot prove anatomical continuity or natural looping. Frame deltas cannot establish physical left/right identity, real exercise form, "
            "single-body coherence, absence of ghost limbs, or seamless anatomical looping. Optional near-mirrored "
            "motion detection can flag legitimate symmetric jumps or other direction changes and can miss edited "
            "reversals; it cannot prove a segment was time-reversed or that its physics are wrong. These need visual review."
        ),
        "exercise_form_and_release_approval": "NOT_EVALUATED"
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only screen-space and timing diagnostics for an actual photographic 5BX MP4")
    parser.add_argument("video", type=Path)
    parser.add_argument("--report", type=Path, required=True, help="JSON report path, outside the source MP4")
    parser.add_argument("--hold", action="append", default=[], metavar="START:END", help="Intentional hold window in seconds; may repeat")
    parser.add_argument("--still-threshold", type=float, default=0.5, help="Max frame-to-frame grayscale MAE counted visually still")
    parser.add_argument("--minimum-hold", type=float, default=0.5, help="Minimum continuous visually still span in seconds")
    parser.add_argument("--expect-loop", action="store_true", help="Warn on large first/last seam (not an exercise/loop approval)")
    parser.add_argument("--check-motion-reversal", action="store_true",
                        help="Screen five mirrored frame pairs around turnarounds; warning only, not form proof")
    parser.add_argument("--background-roi", action="append", default=[], metavar="X0:Y0:X1:Y1",
                        help="Reviewer-selected person-free normalized rectangle; repeatable")
    args = parser.parse_args(argv)
    try:
        if args.video.resolve() == args.report.resolve():
            raise ValueError("report must not overwrite source video")
        windows = []
        for item in args.hold:
            start, stop = (float(v) for v in item.split(":"))
            windows.append((start, stop))
        rois = []
        for item in args.background_roi:
            parts = item.split(":")
            if len(parts) != 4:
                raise ValueError("background ROI needs X0:Y0:X1:Y1")
            rois.append(tuple(float(value) for value in parts))
        result = analyze(args.video, expected_holds=windows,
                         still_threshold=args.still_threshold, minimum_hold_seconds=args.minimum_hold,
                         expect_loop=args.expect_loop, background_rois=rois,
                         check_motion_reversal=args.check_motion_reversal)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"report": str(args.report), "technical_warnings": result["technical_warnings"],
                          "exercise_form_and_release_approval": result["exercise_form_and_release_approval"]}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
