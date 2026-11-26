"""Tests use tiny actual MP4s so decoder behavior is verified, not mocked."""

import json
import math
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import photo_motion.temporal_qa as temporal_module
from photo_motion.temporal_qa import _cadence_consistency, _cuts, _holds, analyze, main


FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


@unittest.skipUnless(FFMPEG, "ffmpeg and ffprobe required")
class TestTemporalVideoQA(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def encode(self, filter_source, name="test.mp4", **options):
        output = self.root / name
        args = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                "-i", filter_source]
        args += options.get("other_inputs", [])
        args += options.get("filters", [])
        args += ["-an", "-c:v", "mpeg4", "-q:v", "3", "-pix_fmt", "yuv420p", str(output)]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return output

    def test_static_clip_is_not_approved_and_reports_stillness(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=2")
        original = video.read_bytes()
        report = analyze(video)
        self.assertEqual(video.read_bytes(), original)
        self.assertEqual(report["decoded_frame_count"], 48)
        self.assertEqual(report["near_identical_frame_transitions"], 47)
        self.assertEqual(report["exercise_form_and_release_approval"], "NOT_EVALUATED")
        self.assertTrue(any(s["classification"] == "REVIEW_STILLNESS" for s in report["sustained_stillness"]))
        self.assertTrue(any("static" in w for w in report["technical_warnings"]))

    def test_nonfinite_configuration_cannot_disable_stillness_detection(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=2")
        for bad in (math.nan, math.inf, -math.inf):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(ValueError, "finite"):
                    analyze(video, still_threshold=bad)
                with self.assertRaisesRegex(ValueError, "finite"):
                    analyze(video, minimum_hold_seconds=bad)
                with self.assertRaisesRegex(ValueError, "finite"):
                    analyze(video, expected_holds=[(0, bad)])
        destination = self.root / "should_not_exist.json"
        self.assertEqual(main([str(video), "--report", str(destination), "--still-threshold", "nan"]), 2)
        self.assertFalse(destination.exists())

    def test_replaced_source_cannot_receive_sha_for_old_decoded_frames(self):
        original = self.encode("color=c=red:s=320x180:r=24:d=2", name="original.mp4")
        replacement = self.encode("testsrc2=size=320x180:rate=24:duration=2", name="replacement.mp4")
        real_frame_times = temporal_module._frame_times

        def replace_after_decoding(path):
            timestamps = real_frame_times(path)
            shutil.copyfile(replacement, original)
            return timestamps

        with patch.object(temporal_module, "_frame_times", side_effect=replace_after_decoding):
            with self.assertRaisesRegex(RuntimeError, "source video changed"):
                analyze(original)

    def test_expected_hold_does_not_create_false_warning(self):
        video = self.encode("color=c=blue:s=320x180:r=24:d=2")
        report = analyze(video, expected_holds=[(0, 2)])
        self.assertTrue(report["sustained_stillness"])
        self.assertEqual(report["sustained_stillness"][0]["classification"], "DECLARED_HOLD")
        # Entirely static is still suspicious for an exercise even if marked a hold.
        self.assertTrue(any("static" in w for w in report["technical_warnings"]))

    def test_continuously_moving_clip_has_no_long_stillness(self):
        video = self.encode("testsrc2=size=320x180:rate=24:duration=2")
        report = analyze(video)
        self.assertEqual(report["decoded_frame_count"], 48)
        self.assertFalse(report["sustained_stillness"])
        self.assertGreater(report["median_frame_difference"], 0.5)
        self.assertEqual(report["frame_pacing_anomalies_total"], 0)

    def test_optional_motion_reversal_screen_flags_mirrored_sequence(self):
        video = self.encode(
            "testsrc2=size=320x180:rate=24:duration=1.5", name="palindrome.mp4",
            filters=["-filter_complex",
                     "[0:v]split=2[a][b];[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];"
                     "[a]setpts=PTS-STARTPTS[f];[f][r]concat=n=2:v=1:a=0[c];[c]fps=24[v]",
                     "-map", "[v]"])
        baseline = analyze(video)
        self.assertEqual(baseline["motion_reversal_screen_space_verdict"], "NOT_REQUESTED")
        self.assertFalse(any("mirrored" in w for w in baseline["technical_warnings"]))
        report = analyze(video, check_motion_reversal=True)
        self.assertEqual(report["motion_reversal_screen_space_verdict"], "REVIEW_NEAR_MIRRORED_SEQUENCE")
        self.assertGreaterEqual(report["motion_reversal_candidates_total"], 1)
        candidate = report["motion_reversal_candidates"][0]
        self.assertEqual(candidate["center_frame_index"], 35)
        self.assertEqual(candidate["mirrored_pair_count"], 5)
        self.assertLess(candidate["velocity_cosine"], -.9)
        self.assertEqual(report["exercise_form_and_release_approval"], "NOT_EVALUATED")

    def test_reversal_screen_does_not_flag_static_or_progressing_video(self):
        static = self.encode("color=c=red:s=320x180:r=24:d=2", name="static.mp4")
        progressing = self.encode("testsrc2=size=320x180:rate=24:duration=2", name="progressing.mp4")
        for video in (static, progressing):
            with self.subTest(video=video.name):
                report = analyze(video, check_motion_reversal=True)
                self.assertEqual(report["motion_reversal_screen_space_verdict"],
                                 "NO_NEAR_MIRRORED_SEQUENCE_DETECTED")
                self.assertEqual(report["motion_reversal_candidates_total"], 0)

    def test_symmetric_bounce_is_documented_false_positive_not_form_failure(self):
        bounce = self.encode(
            "color=c=black:s=320x180:r=24:d=3", name="idealized-bounce.mp4",
            other_inputs=["-f", "lavfi", "-i", "color=c=white:s=20x20:r=24:d=3"],
            filters=["-filter_complex",
                     "[0:v][1:v]overlay=x=150:y=90-50*abs(sin(PI*t/2)):eval=frame[v]",
                     "-map", "[v]"])
        report = analyze(bounce, check_motion_reversal=True)
        # Perfectly symmetric up/down motion is physically possible. This
        # intentionally records a false positive for *bad exercise physics*.
        self.assertEqual(report["motion_reversal_screen_space_verdict"],
                         "REVIEW_NEAR_MIRRORED_SEQUENCE")
        self.assertEqual(report["exercise_form_and_release_approval"], "NOT_EVALUATED")

    def test_traveling_jump_avoids_mirrored_replay_warning(self):
        traveling = self.encode(
            "color=c=black:s=320x180:r=24:d=3", name="traveling-bounce.mp4",
            other_inputs=["-f", "lavfi", "-i", "color=c=white:s=20x20:r=24:d=3"],
            filters=["-filter_complex",
                     "[0:v][1:v]overlay=x=80+20*t:y=90-50*abs(sin(PI*t/2)):eval=frame[v]",
                     "-map", "[v]"])
        report = analyze(traveling, check_motion_reversal=True)
        self.assertEqual(report["motion_reversal_screen_space_verdict"],
                         "NO_NEAR_MIRRORED_SEQUENCE_DETECTED")

    def test_cut_between_two_solid_colours_flagged(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=1", name="cut.mp4",
                            other_inputs=["-f", "lavfi", "-i", "color=c=blue:s=320x180:r=24:d=1"],
                            filters=["-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]"])
        report = analyze(video)
        self.assertGreaterEqual(report["potential_abrupt_cuts_total"], 1)
        self.assertTrue(any(.9 <= cut["at_seconds"] <= 1.1 for cut in report["potential_abrupt_cuts"]))

    def test_loop_seam_is_measured_but_warns_only_if_requested(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=1", name="not-loop.mp4",
                            other_inputs=["-f", "lavfi", "-i", "color=c=blue:s=320x180:r=24:d=1"],
                            filters=["-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]"])
        normal = analyze(video)
        self.assertGreater(normal["first_last_seam_mae_0_to_255"], 20)
        self.assertFalse(normal["expect_loop"])
        self.assertFalse(any("loop seam" in warning.lower() for warning in normal["technical_warnings"]))
        loop = analyze(video, expect_loop=True)
        self.assertTrue(loop["expect_loop"])
        self.assertTrue(any("loop seam" in warning.lower() for warning in loop["technical_warnings"]))
        self.assertEqual(loop["loop_seam_screen_space_verdict"], "REVIEW_DISCONTINUITY")
        self.assertEqual(loop["exercise_form_and_release_approval"], "NOT_EVALUATED")

    def test_static_loop_has_zero_seam_but_never_form_pass(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=2")
        report = analyze(video, expect_loop=True)
        self.assertLess(report["first_last_seam_mae_0_to_255"], .2)
        self.assertEqual(report["loop_seam_screen_space_verdict"], "SCREEN_SPACE_ALIGNED_NOT_FORM_APPROVAL")
        self.assertEqual(report["exercise_form_and_release_approval"], "NOT_EVALUATED")

    def test_static_background_roi_reports_framewise_change_and_terminal_drift(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=1", name="region-change.mp4",
                            other_inputs=["-f", "lavfi", "-i", "color=c=blue:s=320x180:r=24:d=1"],
                            filters=["-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]"])
        report = analyze(video, background_rois=[(0.01, 0.01, .20, .20)])
        self.assertEqual(len(report["background_roi_diagnostics"]), 1)
        roi = report["background_roi_diagnostics"][0]
        self.assertEqual(roi["normalized_xyxy"], [0.01, 0.01, .2, .2])
        self.assertGreater(roi["first_last_mae_0_to_255"], 20)
        self.assertGreater(roi["maximum_frame_transition_mae_0_to_255"], 20)
        self.assertTrue(any("background ROI" in warning for warning in report["technical_warnings"]))

    def test_bad_background_rois_fail_closed_before_writing_report(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=1")
        for bad in ((0, 0, 0, .5), (-.1, 0, .1, .2), (0, 0, 2, 1),
                    (0, 0, math.nan, .2), (True, 0, .5, .5), (.2, .1, .2, .5)):
            with self.subTest(roi=bad):
                with self.assertRaisesRegex(ValueError, "background ROI"):
                    analyze(video, background_rois=[bad])

    def test_cli_writes_json_away_from_source(self):
        video = self.encode("testsrc2=size=320x180:rate=24:duration=1")
        path = self.root / "report.json"
        self.assertEqual(main([str(video), "--report", str(path)]), 0)
        self.assertTrue(path.exists())
        self.assertEqual(json.loads(path.read_text())["exercise_form_and_release_approval"], "NOT_EVALUATED")
        self.assertEqual(main([str(video), "--report", str(video)]), 2)

    def test_cli_accepts_explicit_loop_and_background_regions(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=1")
        destination = self.root / "loop-and-background.json"
        self.assertEqual(main([str(video), "--expect-loop", "--background-roi", "0.1:0.1:0.25:0.25",
                               "--report", str(destination)]), 0)
        report = json.loads(destination.read_text())
        self.assertTrue(report["expect_loop"])
        self.assertEqual(len(report["background_roi_diagnostics"]), 1)
        self.assertEqual(report["loop_seam_screen_space_verdict"], "SCREEN_SPACE_ALIGNED_NOT_FORM_APPROVAL")
        invalid_destination = self.root / "not-created.json"
        self.assertEqual(main([str(video), "--background-roi", "0.1:bad:0.25:0.25",
                               "--report", str(invalid_destination)]), 2)
        self.assertFalse(invalid_destination.exists())

    def test_cli_motion_reversal_opt_in_and_bool_validation(self):
        video = self.encode("testsrc2=size=320x180:rate=24:duration=1")
        destination = self.root / "reversal-screen.json"
        self.assertEqual(main([str(video), "--check-motion-reversal", "--report", str(destination)]), 0)
        self.assertTrue(json.loads(destination.read_text())["motion_reversal_check_requested"])
        with self.assertRaisesRegex(ValueError, "check_motion_reversal"):
            analyze(video, check_motion_reversal=1)


class TestTemporalLogic(unittest.TestCase):
    def test_nominal_rate_disagrees_with_real_timestamps_after_bad_concat(self):
        # Real failure mode: 142 displayed frames span 5.875 seconds although
        # their presentation timestamps still advance at 24 fps. An MP4
        # declares 142/5.875 = ~24.17 fps instead of the actual 24-fps cadence.
        points = [i / 24 for i in range(142)]
        result = _cadence_consistency(points, 142 / 5.875, 5.875, 142)
        self.assertEqual(result["verdict"], "REVIEW_RATE_OR_DURATION_MISMATCH")
        self.assertAlmostEqual(result["timestamp_cadence_fps"], 24)
        self.assertAlmostEqual(result["reported_duration_frame_discrepancy"], 1)

    def test_exact_cfr_has_consistent_timestamp_rate_and_duration(self):
        points = [i / 24 for i in range(142)]
        result = _cadence_consistency(points, 24, 142 / 24, 142)
        self.assertEqual(result["verdict"], "SCREEN_SPACE_TIMING_ALIGNED_NOT_FORM_APPROVAL")
        self.assertLess(result["reported_duration_frame_discrepancy"], 0.01)

    def test_missing_true_timestamps_cannot_prove_cadence(self):
        result = _cadence_consistency([], 24, 1, 24)
        self.assertEqual(result["verdict"], "NOT_EVALUATED")

    def test_holds_require_min_duration(self):
        # Three low-change transitions at 10 fps are only 0.3 s.
        self.assertEqual(_holds([0, 0, 0, 9, 0, 0], [], 10, .5, .5, []), [])

    def test_declared_hold_is_distinguished_from_unexpected_freeze(self):
        runs = _holds([0] * 10 + [20] + [0] * 8, [], 10, .5, .5, [(0, 1)])
        self.assertEqual([run["classification"] for run in runs], ["DECLARED_HOLD", "REVIEW_STILLNESS"])

    def test_cut_is_not_reported_from_normal_small_change(self):
        self.assertEqual(_cuts([0.1, .3, 1.3, 2, 3.2], [], 24), [])


if __name__ == "__main__":
    unittest.main()
