"""Synthetic MP4 tests: no private Flow footage, no paid generation."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion.silent_derivative import create_silent_derivative
from photo_motion.video_qa import file_sha256, probe


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe needed")
class SilentDerivativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def _fixture(self, with_audio=True):
        source = self.root / ("raw-with-audio.mp4" if with_audio else "raw-silent.mp4")
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi",
               "-i", "testsrc=size=128x72:rate=12:duration=1"]
        if with_audio:
            cmd += ["-f", "lavfi", "-i", "sine=frequency=500:sample_rate=16000:duration=1",
                    "-shortest"]
        cmd += ["-c:v", "mpeg4", "-q:v", "5"]
        if with_audio:
            cmd += ["-c:a", "aac"]
        cmd += [str(source)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return source

    def test_audio_removed_video_bitstream_exact_and_receipt(self):
        source = self._fixture()
        original_bytes = source.read_bytes()
        report = create_silent_derivative(source, self.root / "review", file_sha256(source))
        derivative = self.root / "review" / "silent_review.mp4"
        self.assertEqual(source.read_bytes(), original_bytes)
        self.assertEqual(probe(source)["audio_stream_count"], 1)
        self.assertEqual(probe(derivative)["audio_stream_count"], 0)
        self.assertEqual(report["raw_generation_audio_policy_result"], "FAIL_AUDIO_PRESENT_IN_RAW")
        self.assertEqual(report["derivative_status"], "SILENT_DERIVATIVE_ONLY_RAW_GENERATION_UNCHANGED")
        self.assertEqual(report["form_and_release_approval"], "HOLD_FOR_HUMAN_FORM_AND_RELEASE_REVIEW")
        self.assertTrue(report["verification"]["encoded_video_packets_identical"])
        self.assertTrue(report["verification"]["decoded_frame_count_identical"])
        self.assertEqual(report["source"]["decoded_frames"], 12)
        self.assertEqual(report["derivative"]["decoded_frames"], 12)
        self.assertEqual(report["source"]["video_packets"], report["derivative"]["video_packets"])
        saved = json.loads((self.root / "review" / "silent_derivative_manifest.json").read_text())
        self.assertEqual(saved, report)
        self.assertEqual(saved["derivative"]["sha256"], file_sha256(derivative))
        self.assertIn("ffmpeg", saved["reproducibility"]["exact_command"][0])

    def test_does_not_claim_raw_audio_failure_when_original_has_none(self):
        source = self._fixture(with_audio=False)
        report = create_silent_derivative(source, self.root / "review", file_sha256(source))
        self.assertEqual(report["raw_generation_audio_policy_result"], "NO_AUDIO_IN_RAW")
        self.assertEqual(report["form_and_release_approval"], "HOLD_FOR_HUMAN_FORM_AND_RELEASE_REVIEW")

    def test_wrong_hash_fails_without_writing(self):
        source = self._fixture()
        out = self.root / "review"
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            create_silent_derivative(source, out, "0" * 64)
        self.assertFalse(out.exists())

    def test_no_overwrite_existing_evidence(self):
        source = self._fixture()
        out = self.root / "review"
        create_silent_derivative(source, out, file_sha256(source))
        before = (out / "silent_review.mp4").read_bytes()
        with self.assertRaisesRegex(ValueError, "new directory"):
            create_silent_derivative(source, out, file_sha256(source))
        self.assertEqual(before, (out / "silent_review.mp4").read_bytes())

    def test_same_raw_file_repeats_identical_output_bytes(self):
        source = self._fixture()
        expected = file_sha256(source)
        first = create_silent_derivative(source, self.root / "one", expected)
        second = create_silent_derivative(source, self.root / "two", expected)
        self.assertEqual(first["derivative"]["sha256"], second["derivative"]["sha256"])
        self.assertEqual(first["source"]["sha256"], second["source"]["sha256"])

    def test_requires_valid_digest_and_existing_input(self):
        source = self._fixture()
        with self.assertRaisesRegex(ValueError, "64-character"):
            create_silent_derivative(source, self.root / "review", "not-a-digest")
        with self.assertRaises(FileNotFoundError):
            create_silent_derivative(self.root / "not-present.mp4", self.root / "review", "0" * 64)


if __name__ == "__main__":
    unittest.main()
