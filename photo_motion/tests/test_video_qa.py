import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion.contract import load_spec
from photo_motion.video_qa import _phase_samples, inspect, probe, read_recipe


ROOT = Path(__file__).resolve().parents[1]


class TestVideoQA(unittest.TestCase):
    def test_terminal_phase_clamps_to_last_frame(self):
        spec = load_spec(ROOT / "specs/chart1-scissor-jump.json")
        samples = _phase_samples(spec, {"duration_seconds": 6.0, "fps": 24})
        self.assertEqual(samples[0][1], 0)
        self.assertAlmostEqual(samples[-1][1], 6 - 1 / 24)

    def test_recipe_captures_prompt_hash_without_claiming_determinism(self):
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            (tmp / "submitted.txt").write_text("Original prompt exactly as submitted", encoding="utf-8")
            (tmp / "run.json").write_text(json.dumps({
                "schema_version": 1, "provider": "Google Flow", "model": "Omni test",
                "generation_id": "test-1", "submitted_prompt_file": "submitted.txt",
                "input_images": [{"role": "start-frame", "locator": "provider://image/unavailable"}],
                "settings": {"seed": None, "duration_seconds": 6}
            }), encoding="utf-8")
            record = read_recipe(tmp / "run.json")
            self.assertEqual(len(record["exact_submitted_prompt_sha256"]), 64)
            self.assertTrue(record["warnings"])

    def test_recipe_rejects_modified_source_image(self):
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            (tmp / "submitted.txt").write_text("Actual prompt", encoding="utf-8")
            (tmp / "start.png").write_bytes(b"changed")
            (tmp / "run.json").write_text(json.dumps({
                "schema_version": 1, "provider": "Google Flow", "model": "Omni test",
                "generation_id": "test-1", "submitted_prompt_file": "submitted.txt",
                "input_images": [{"role": "start-frame", "locator": "start.png", "sha256": "0" * 64}],
                "settings": {"duration_seconds": 6}
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                read_recipe(tmp / "run.json")

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg binaries not installed")
    def test_synthetic_mp4_inspection_is_nonmutating_and_unapproved(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        spec_path = ROOT / "specs/chart1-kneeling-pushup.json"
        spec = load_spec(spec_path)
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            source = tmp / "synthetic.mp4"
            subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi",
                            "-i", "testsrc2=size=640x360:rate=24", "-t", "6", "-c:v", "mpeg4",
                            str(source)], check=True, capture_output=True)
            before = source.read_bytes()
            result = inspect(spec, spec_path, source, tmp / "qa")
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(result["form_and_release_approval"], "NOT_EVALUATED")
            self.assertEqual(len(result["frames"]), 4)
            self.assertEqual(len(result["source_video_sha256"]), 64)
            self.assertEqual(len(result["spec_sha256"]), 64)
            self.assertEqual(len(result["technical_warnings"]), 0)
            self.assertEqual(probe(source)["width"], 640)
            self.assertTrue((tmp / "qa/phase_contact_sheet.png").exists())
            self.assertTrue((tmp / "qa/inspection.json").exists())
            self.assertEqual(json.loads((tmp / "qa/inspection.json").read_text())["form_and_release_approval"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
