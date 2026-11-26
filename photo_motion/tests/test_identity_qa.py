import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

import photo_motion.identity_qa as identity_qa
from photo_motion.identity_qa import inspect_manifest, main, validate_box


class TestIdentityQA(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Entire images are synthetic. The viewer knows which patch is a shirt;
        # the tool must never pretend to discover identity or physical limbs.
        Image.new("RGB", (120, 120), (80, 160, 200)).save(self.root / "master.png")
        Image.new("RGB", (120, 120), (96, 192, 240)).save(self.root / "brighter.png")
        Image.new("RGB", (120, 120), (180, 70, 60)).save(self.root / "different.png")

    def write_manifest(self, patches=None, samples=None):
        data = {
            "schema_version": 1,
            "reference": {
                "image": "master.png",
                "subject_box": [0.1, 0.1, 0.9, 0.9],
                "regions": patches if patches is not None else {
                    "shirt": [0.2, 0.2, 0.6, 0.6],
                    "face": [0.1, 0.1, 0.2, 0.2]
                }
            },
            "samples": samples if samples is not None else [{
                "image": "brighter.png", "time_seconds": 1.5,
                "subject_box": [0.2, 0.2, 0.8, 0.8],
                "regions": {"shirt": [0.2, 0.2, 0.6, 0.6]}
            }]
        }
        path = self.root / "annotations.json"
        path.write_text(json.dumps(data))
        return path

    def test_brightness_change_separate_from_chroma_and_identification(self):
        result = inspect_manifest(self.write_manifest())
        assert result["identity_verdict"] == "NOT_EVALUATED"
        shirt = result["samples"][0]["regions"]["shirt"]
        self.assertEqual(shirt["status"], "COMPARISON_ONLY")
        self.assertAlmostEqual(shirt["relative_to_master"]["chromaticity_distance"], 0, places=5)
        self.assertAlmostEqual(shirt["relative_to_master"]["luminance_ratio_to_reference"], 1.2, places=3)
        self.assertEqual(result["samples"][0]["regions"]["face"]["status"], "NOT_EVALUATED")
        self.assertAlmostEqual(result["samples"][0]["subject_box_area_ratio_to_master"], 0.5625, places=3)
        self.assertEqual(len(result["master_sha256"]), 64)
        self.assertEqual(len(result["samples"][0]["image_sha256"]), 64)

    def test_mismatched_colors_raise_metrics_not_false_identity_verdict(self):
        path = self.write_manifest(samples=[{
            "image": "different.png", "time_seconds": 2,
            "regions": {"shirt": [0.2, 0.2, 0.6, 0.6], "face": [0.1, 0.1, 0.2, 0.2]}
        }])
        result = inspect_manifest(path)
        self.assertGreater(result["samples"][0]["regions"]["shirt"]["relative_to_master"]["chromaticity_distance"], .3)
        self.assertEqual(result["identity_verdict"], "NOT_EVALUATED")
        self.assertIsNone(result["samples"][0]["subject_box_area_ratio_to_master"])

    def test_invalid_boxes_rejected(self):
        bad = ([.7, .2, .1, .9], [-.1, .1, .2, .2], [0, 0, float("nan"), 1], [0, 0, 1])
        for box in bad:
            with self.subTest(box=box), self.assertRaises(ValueError):
                validate_box(box, "test")

    def test_tiny_patch_rejected(self):
        with self.assertRaisesRegex(ValueError, "under 6 pixels"):
            inspect_manifest(self.write_manifest(patches={"hair": [.1, .1, .11, .11]}))

    def test_missing_frame_detected(self):
        path = self.write_manifest(samples=[{"image": "does-not-exist.png", "time_seconds": 2.0, "regions": {"shirt": [.2, .2, .6, .6]}}])
        with self.assertRaises(FileNotFoundError):
            inspect_manifest(path)

    def test_missing_sample_time_is_not_reproducible(self):
        path = self.write_manifest(samples=[{"image": "brighter.png", "regions": {"shirt": [.2, .2, .6, .6]}}])
        with self.assertRaisesRegex(ValueError, "time_seconds"):
            inspect_manifest(path)

    def test_cli_writes_read_only_analysis_and_does_not_modify_source(self):
        path = self.write_manifest()
        before = path.read_bytes()
        result_path = self.root / "results" / "identity.json"
        self.assertEqual(main([str(path), "--out", str(result_path)]), 0)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(json.loads(result_path.read_text())["identity_verdict"], "NOT_EVALUATED")

    def test_cli_never_overwrites_source_manifest(self):
        path = self.write_manifest()
        self.assertEqual(main([str(path), "--out", str(path)]), 2)

    def test_cli_refuses_existing_report_without_explicit_replacement(self):
        path = self.write_manifest()
        report = self.root / "identity.json"
        report.write_text("important previous QA")
        self.assertEqual(main([str(path), "--out", str(report)]), 2)
        self.assertEqual(report.read_text(), "important previous QA")

    def test_master_mutated_during_patch_analysis_is_rejected(self):
        path = self.write_manifest()
        original = identity_qa.patch_stats
        def mutate_master_during_stats(image, box, name):
            result = original(image, box, name)
            if name == "reference.shirt":
                # The decoder inspected the *original* red master, while its
                # path is replaced before the report is created.
                Image.new("RGB", (120, 120), (30, 30, 250)).save(self.root / "master.png")
            return result
        with mock.patch.object(identity_qa, "patch_stats", side_effect=mutate_master_during_stats):
            with self.assertRaisesRegex(ValueError, "master image changed during analysis"):
                inspect_manifest(path)

    def test_sample_mutated_during_patch_analysis_is_rejected(self):
        path = self.write_manifest()
        original = identity_qa.patch_stats
        def mutate_sample_during_stats(image, box, name):
            result = original(image, box, name)
            if name == "samples[0].shirt":
                Image.new("RGB", (120, 120), (50, 70, 90)).save(self.root / "brighter.png")
            return result
        with mock.patch.object(identity_qa, "patch_stats", side_effect=mutate_sample_during_stats):
            with self.assertRaisesRegex(ValueError, "sample image 0 changed during analysis"):
                inspect_manifest(path)

    def test_earlier_frame_mutated_while_later_frame_is_analyzed(self):
        path = self.write_manifest(samples=[
            {"image": "brighter.png", "time_seconds": 1.5, "regions": {"shirt": [.2, .2, .6, .6]}},
            {"image": "different.png", "time_seconds": 3.0, "regions": {"shirt": [.2, .2, .6, .6]}}
        ])
        original = identity_qa.patch_stats
        def mutate_earlier_frame(image, box, name):
            result = original(image, box, name)
            if name == "samples[1].shirt":
                Image.new("RGB", (120, 120), (1, 2, 3)).save(self.root / "brighter.png")
            return result
        with mock.patch.object(identity_qa, "patch_stats", side_effect=mutate_earlier_frame):
            with self.assertRaisesRegex(ValueError, "sample image 0 changed during analysis"):
                inspect_manifest(path)

    def test_manifest_mutated_after_parsing_is_rejected(self):
        path = self.write_manifest()
        original = identity_qa.patch_stats
        def mutate_manifest(image, box, name):
            result = original(image, box, name)
            if name == "reference.shirt":
                path.write_text('{"schema_version": 1, "forged": true}', encoding="utf-8")
            return result
        with mock.patch.object(identity_qa, "patch_stats", side_effect=mutate_manifest):
            with self.assertRaisesRegex(ValueError, "annotation manifest changed during analysis"):
                inspect_manifest(path)


if __name__ == "__main__":
    unittest.main()
