"""Synthetic-only QA tests: no user photographs or private MP4s in Git."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion.v8_postflight import main, measure
from photo_motion.video_qa import file_sha256


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg tools needed")
class V8PostflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.video = self.root / "synthetic.mp4"
        command = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                   "-f", "lavfi", "-i", "color=c=red:s=1280x720:r=24:d=3",
                   "-f", "lavfi", "-i", "sine=frequency=440:duration=3:sample_rate=48000",
                   "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-shortest", str(self.video)]
        subprocess.run(command, check=True, capture_output=True)
        for number, name in ((0, "a.png"), (71, "c.png")):
            subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                            "-i", str(self.video), "-vf", f"select=eq(n\\,{number})",
                            "-frames:v", "1", str(self.root / name)], check=True, capture_output=True)
        self.a, self.c = self.root / "a.png", self.root / "c.png"
        self.spec = self.root / "segment.json"
        self.data = {"schema_version": 1, "authority": "V8_FRAMES_DIRECT_A_C_SEGMENTS",
                     "segment_role": "A_TO_C", "start_pose": "A", "end_pose": "C",
                     "fps": 24, "duration_seconds": 3,
                     "start_sha256": file_sha256(self.a), "end_sha256": file_sha256(self.c)}
        self.spec.write_text(json.dumps(self.data), encoding="utf-8")

    def test_exact_endpoints_and_forbidden_audio_reported_without_approval(self):
        result = measure(self.spec, self.a, self.c, self.video)
        self.assertEqual(result["decoded_frames"], 72)
        self.assertEqual(result["start_frame_mae_0_to_255"], 0)
        self.assertEqual(result["end_frame_mae_0_to_255"], 0)
        self.assertIn("generated output includes forbidden audio stream(s)", result["technical_warnings"])
        self.assertIsNotNone(result["audio_levels"][0]["peak_volume_dbfs"])
        self.assertEqual(result["motion_form_identity_and_release"], "NOT_EVALUATED")

    def test_changed_source_is_rejected(self):
        self.data["start_sha256"] = "0" * 64
        self.spec.write_text(json.dumps(self.data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "start image SHA-256"):
            measure(self.spec, self.a, self.c, self.video)

    def test_role_reversal_requires_correct_contract(self):
        self.data["segment_role"] = "C_TO_A"
        self.spec.write_text(json.dumps(self.data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "ordered endpoint poses"):
            measure(self.spec, self.a, self.c, self.video)

    def test_existing_report_is_not_overwritten(self):
        report = self.root / "report.json"
        report.write_text("preserve", encoding="utf-8")
        with self.assertRaises(SystemExit):
            main([str(self.spec), str(self.a), str(self.c), str(self.video), "--report", str(report)])
        self.assertEqual(report.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
