"""Synthetic-only tests of the no-fade photographic segment assembler."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion.segment_join import HOLD, join_segments
from photo_motion.video_qa import file_sha256


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                     "ffmpeg/ffprobe unavailable")
class SegmentJoinTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.first = self.root / "a_to_c.mp4"
        self.second = self.root / "c_to_a.mp4"
        self._make(self.first, "red")
        self._make(self.second, "red")
        self.sha1 = file_sha256(self.first)
        self.sha2 = file_sha256(self.second)

    def tearDown(self):
        self.temp.cleanup()

    def _make(self, path, color, *, width=160, height=90, duration=1, with_audio=False):
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi",
               "-i", f"color=c={color}:s={width}x{height}:r=8:d={duration}"]
        if with_audio:
            cmd += ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono:d={duration}"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "8", "-bf", "0"]
        if with_audio:
            cmd += ["-c:a", "aac", "-shortest"]
        else:
            cmd += ["-an"]
        cmd += ["-metadata", f"title={path.stem}", str(path)]
        completed = subprocess.run(cmd, capture_output=True, check=False)
        if completed.returncode:
            self.fail(completed.stderr.decode("utf-8", "replace")[-600:])

    def _join(self, *, directory="output", **kwargs):
        return join_segments(self.first, self.second, self.root / directory,
                             first_sha256=self.sha1, second_sha256=self.sha2,
                             expected_fps=8, expected_frames_per_segment=8,
                             max_c_seam_mae=1, **kwargs)

    def test_clean_join_preserves_encoded_packets_and_exact_frames(self):
        result = self._join()
        self.assertTrue((self.root / "output/two_segment_preview.mp4").is_file())
        self.assertEqual(result["preview"]["decoded_frames"], 16)
        self.assertAlmostEqual(result["preview"]["probe"]["duration_seconds"], 2, delta=0.125)
        self.assertTrue(result["verification"]["encoded_video_packets_identical_in_source_order"])
        self.assertTrue(result["verification"]["no_output_audio"])
        self.assertEqual(result["c_join"]["last_A_to_C_vs_first_C_to_A_rgb_mae_0_to_255"], 0)
        self.assertEqual(result["form_and_release_approval"], HOLD)
        self.assertEqual(file_sha256(self.first), self.sha1)
        self.assertEqual(file_sha256(self.second), self.sha2)
        stored = json.loads((self.root / "output/two_segment_manifest.json").read_text())
        self.assertEqual(stored["preview"]["sha256"], file_sha256(self.root / "output/two_segment_preview.mp4"))
        self.assertEqual(stored["ordered_photographic_roles"], ["A_TO_C", "C_TO_A"])
        self.assertEqual(stored["role_evidence"], "OPERATOR_DECLARED_ONLY_NOT_VIDEO_VERIFIED")
        self.assertIn("NOT_EVALUATED", stored["c_join"]["manual_pose_identity_and_motion_review"])
        self.assertFalse((self.root / "output/concat.txt").exists())

    def test_wrong_hash_fails_before_output(self):
        with self.assertRaisesRegex(ValueError, "source SHA256 mismatch"):
            join_segments(self.first, self.second, self.root / "failed",
                          first_sha256="a"*64, second_sha256=self.sha2,
                          expected_fps=8, expected_frames_per_segment=8)
        self.assertFalse((self.root / "failed").exists())

    def test_seam_mismatch_fails_before_output(self):
        self._make(self.second, "blue")
        self.sha2 = file_sha256(self.second)
        with self.assertRaisesRegex(ValueError, "C seam.*exceeds"):
            self._join(directory="seam_failed")
        self.assertFalse((self.root / "seam_failed").exists())

    def test_audio_input_fails_including_silent_track(self):
        self._make(self.second, "red", with_audio=True)
        self.sha2 = file_sha256(self.second)
        with self.assertRaisesRegex(ValueError, "zero audio"):
            self._join(directory="audio_failed")
        self.assertFalse((self.root / "audio_failed").exists())

    def test_frame_count_and_fps_mismatch_fails(self):
        self._make(self.second, "red", duration=2)
        self.sha2 = file_sha256(self.second)
        with self.assertRaisesRegex(ValueError, "decoded frames"):
            self._join(directory="length_failed")
        self.assertFalse((self.root / "length_failed").exists())

    def test_geometry_mismatch_fails(self):
        self._make(self.second, "red", width=320, height=180)
        self.sha2 = file_sha256(self.second)
        with self.assertRaisesRegex(ValueError, "incompatible"):
            self._join(directory="geometry_failed")
        self.assertFalse((self.root / "geometry_failed").exists())

    def test_existing_evidence_dir_never_overwritten(self):
        existing = self.root / "exists"
        existing.mkdir()
        (existing / "sentinel").write_text("KEEP")
        with self.assertRaisesRegex(ValueError, "fresh directory"):
            self._join(directory="exists")
        self.assertEqual((existing / "sentinel").read_text(), "KEEP")

    def test_uncertain_seam_threshold_rejected(self):
        with self.assertRaisesRegex(ValueError, "max_c_seam_mae"):
            join_segments(self.first, self.second, self.root / "bad",
                          first_sha256=self.sha1, second_sha256=self.sha2,
                          expected_fps=8, expected_frames_per_segment=8,
                          max_c_seam_mae=float("nan"))
        self.assertFalse((self.root / "bad").exists())

    def test_same_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "two distinct"):
            join_segments(self.first, self.first, self.root / "same",
                          first_sha256=self.sha1, second_sha256=self.sha1,
                          expected_fps=8, expected_frames_per_segment=8)
        self.assertFalse((self.root / "same").exists())

    def test_byte_identical_distinct_paths_rejected(self):
        shutil.copyfile(self.first, self.second)
        self.sha2 = file_sha256(self.second)
        with self.assertRaisesRegex(ValueError, "identical video bytes"):
            self._join(directory="clone")
        self.assertFalse((self.root / "clone").exists())


if __name__ == "__main__":
    unittest.main()
