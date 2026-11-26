import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import photo_motion.video_qa as video_module
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

    def test_recipe_rejects_untrusted_hash_and_warns_for_unverified_remote(self):
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            (tmp / "submitted.txt").write_text("Original prompt", encoding="utf-8")
            data = {"schema_version": 1, "provider": "Google Flow", "model": "Omni test",
                    "generation_id": "test", "submitted_prompt_file": "submitted.txt",
                    "input_images": [{"role": "start", "locator": "https://provider.invalid/asset", "sha256": "not-a-hash"}],
                    "settings": {"duration_seconds": 6}}
            (tmp / "run.json").write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "64-character"):
                read_recipe(tmp / "run.json")
            data["input_images"][0]["sha256"] = "f" * 64
            (tmp / "run.json").write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("not locally available", " ".join(read_recipe(tmp / "run.json")["warnings"]))

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

            with self.assertRaises(FileExistsError):
                inspect(spec, spec_path, source, tmp / "qa")
            # An old output directory with an attacker-placed link to the
            # ORIGINAL MP4 must be refused without mutating the source.
            hostile = tmp / "hostile"
            hostile.mkdir()
            (hostile / "frame_01_A.png").symlink_to(source)
            with self.assertRaises(FileExistsError):
                inspect(spec, spec_path, source, hostile)
            self.assertEqual(source.read_bytes(), before)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg binaries not installed")
    def test_source_swapped_during_frame_extraction_cannot_produce_a_mixed_take_report(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        spec_path = ROOT / "specs/chart1-kneeling-pushup.json"
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            source, other = tmp / "red.mp4", tmp / "blue.mp4"
            for path, color in ((source, "red"), (other, "blue")):
                subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi",
                                "-i", f"color=c={color}:s=640x360:r=24:d=6", "-c:v", "mpeg4",
                                str(path)], check=True, capture_output=True)
            real_extract = video_module._extract
            extracted = 0

            def swap_after_first_frame(video, at, output):
                nonlocal extracted
                real_extract(video, at, output)
                extracted += 1
                if extracted == 1:
                    shutil.copyfile(other, source)

            with patch.object(video_module, "_extract", side_effect=swap_after_first_frame):
                with self.assertRaisesRegex(RuntimeError, "source video changed"):
                    inspect(load_spec(spec_path), spec_path, source, tmp / "mixed-qa")
            self.assertFalse((tmp / "mixed-qa/inspection.json").exists())


if __name__ == "__main__":
    unittest.main()
