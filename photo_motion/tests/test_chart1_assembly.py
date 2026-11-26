"""Chart 1 review assembly must not silently accept a missing or false video."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion.chart1_assembly import AssemblyError, EXERCISES, assemble, preflight


class Chart1AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / "new_review.mp4"
        self.clips = []
        for i, role in enumerate(EXERCISES, 1):
            path = self.root / f"exercise{i}.mp4"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-f", "lavfi", "-i", f"color=c=0x333333:s=160x90:r=12:d=0.5",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)
            self.clips.append({"exercise": i, "role": role, "file": path.name})
        self.manifest = self.root / "recipe.json"
        self.save_manifest()

    def save_manifest(self):
        self.manifest.write_text(json.dumps({"schema_version": 1, "chart": 1, "clips": self.clips}), encoding="utf-8")

    def test_assembles_five_real_clips_with_traceable_evidence_and_no_audio(self):
        result = assemble(self.manifest, self.output, width=160, height=90, fps=12)
        self.assertEqual(result["purpose"], "EXPERIMENTAL_CHART1_REVIEW_ONLY_NOT_INSTRUCTIONAL_OR_OWNER_APPROVED")
        self.assertEqual(len(result["clips"]), 5)
        self.assertTrue(self.output.is_file())
        self.assertTrue(self.output.with_suffix(".evidence.json").is_file())
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
                                "-of", "csv=p=0", str(self.output)], capture_output=True, text=True, check=True)
        self.assertEqual(probe.stdout.strip(), "video")
        self.assertAlmostEqual(result["output_media"]["duration_seconds"], 2.5, delta=0.2)
        with self.assertRaisesRegex(AssemblyError, "already exists"):
            assemble(self.manifest, self.output, width=160, height=90)

    def test_missing_exercise_fails_before_writing(self):
        self.clips.pop()
        self.save_manifest()
        with self.assertRaisesRegex(AssemblyError, "five actual video"):
            preflight(self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_misordered_or_duplicate_media_is_rejected(self):
        self.clips[1]["role"] = "toe_touch"
        self.save_manifest()
        with self.assertRaisesRegex(AssemblyError, "Slot 2"):
            preflight(self.manifest, self.output)
        self.clips[1]["role"] = "partial_situp"
        self.clips[1]["file"] = self.clips[0]["file"]
        self.save_manifest()
        with self.assertRaisesRegex(AssemblyError, "distinct source"):
            preflight(self.manifest, self.output)

    def test_photo_masquerading_as_mp4_is_rejected(self):
        (self.root / "not_a_video.mp4").write_bytes(b"PNG fake")
        self.clips[2]["file"] = "not_a_video.mp4"
        self.save_manifest()
        with self.assertRaisesRegex(AssemblyError, "Unreadable source video"):
            preflight(self.manifest, self.output)


if __name__ == "__main__":
    unittest.main()
