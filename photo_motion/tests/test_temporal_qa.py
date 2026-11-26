"""Tests use tiny actual MP4s so decoder behavior is verified, not mocked."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion.temporal_qa import _cuts, _holds, analyze, main


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

    def test_cut_between_two_solid_colours_flagged(self):
        video = self.encode("color=c=red:s=320x180:r=24:d=1", name="cut.mp4",
                            other_inputs=["-f", "lavfi", "-i", "color=c=blue:s=320x180:r=24:d=1"],
                            filters=["-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]"])
        report = analyze(video)
        self.assertGreaterEqual(report["potential_abrupt_cuts_total"], 1)
        self.assertTrue(any(.9 <= cut["at_seconds"] <= 1.1 for cut in report["potential_abrupt_cuts"]))

    def test_cli_writes_json_away_from_source(self):
        video = self.encode("testsrc2=size=320x180:rate=24:duration=1")
        path = self.root / "report.json"
        self.assertEqual(main([str(video), "--report", str(path)]), 0)
        self.assertTrue(path.exists())
        self.assertEqual(json.loads(path.read_text())["exercise_form_and_release_approval"], "NOT_EVALUATED")
        self.assertEqual(main([str(video), "--report", str(video)]), 2)


class TestTemporalLogic(unittest.TestCase):
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
