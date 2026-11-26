import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion.contact_qa import evaluate_annotations, render_overlay, _validate


def example(width=640, height=360):
    return {
        "schema_version": 1,
        "source_video_sha256": None,
        "frame_size": [width, height],
        "annotation_method": "manual",
        "fixed_contacts": ["near_palm", "near_knee"],
        "samples": [
            {"time_seconds": 0.0, "landmarks": {"near_palm": {"x": 300, "y": 245}, "near_knee": {"x": 100, "y": 240}}},
            {"time_seconds": 0.8, "landmarks": {"near_palm": {"x": 302, "y": 246}, "near_knee": {"x": 101, "y": 240}}},
            {"time_seconds": 1.6, "landmarks": {"near_palm": {"x": 301, "y": 245}, "near_knee": {"x": 102, "y": 241}}}
        ]
    }


class ContractTests(unittest.TestCase):
    def test_offline_stable_data_is_not_video_verified(self):
        result = evaluate_annotations(example())
        self.assertEqual(result["technical_contact_screen"], "NOT_EVALUATED")
        self.assertEqual([p["screen_status"] for p in result["per_landmark"]], ["PASS", "PASS"])
        self.assertEqual(result["exercise_form_approval"], "NOT_EVALUATED")

    def test_offline_true_drift_still_exposes_warning(self):
        doc = example()
        doc["samples"][2]["landmarks"]["near_knee"]["x"] += 40
        result = evaluate_annotations(doc)
        self.assertEqual(result["per_landmark"][1]["screen_status"], "WARN")
        self.assertGreater(result["per_landmark"][1]["max_drift_px"], 30)
        self.assertEqual(result["technical_contact_screen"], "NOT_EVALUATED")

    def test_missing_occluded_contact_is_not_pass(self):
        doc = example()
        doc["samples"][1]["landmarks"]["near_knee"] = None
        result = evaluate_annotations(doc)
        self.assertEqual(result["per_landmark"][1]["screen_status"], "NOT_EVALUATED")

    def test_missing_first_contact_fails_even_with_three_later_samples(self):
        doc = example()
        doc["samples"].append({"time_seconds": 1.9, "landmarks": {"near_palm": {"x": 300, "y": 245}, "near_knee": {"x": 100, "y": 240}}})
        doc["samples"][0]["landmarks"]["near_knee"] = None
        result = evaluate_annotations(doc)
        self.assertEqual(result["per_landmark"][1]["screen_status"], "NOT_EVALUATED")
        self.assertIn("First and final", result["per_landmark"][1]["reason"])

    def test_low_confidence_detector_cannot_pass(self):
        doc = example()
        doc["annotation_method"] = "model"
        for frame in doc["samples"]:
            frame["landmarks"]["near_palm"]["confidence"] = 0.2
            frame["landmarks"]["near_knee"]["confidence"] = 0.95
        result = evaluate_annotations(doc)
        self.assertEqual(result["per_landmark"][0]["screen_status"], "NOT_EVALUATED")
        self.assertEqual(result["per_landmark"][1]["screen_status"], "PASS")

    def test_missing_model_confidence_cannot_pass(self):
        doc = example()
        doc["annotation_method"] = "model"
        result = evaluate_annotations(doc)
        self.assertEqual(result["technical_contact_screen"], "NOT_EVALUATED")
        self.assertTrue(result["per_landmark"][0]["skipped"])

    def test_outside_native_frame_rejected(self):
        doc = example()
        doc["samples"][1]["landmarks"]["near_palm"]["x"] = 641
        with self.assertRaisesRegex(ValueError, "outside native video"):
            _validate(doc)

    def test_duplicate_time_rejected(self):
        doc = example()
        doc["samples"][2]["time_seconds"] = 0.8
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            _validate(doc)

    def test_nonnumeric_nan_rejected(self):
        doc = example()
        doc["samples"][1]["landmarks"]["near_palm"]["y"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite number"):
            _validate(doc)

    def test_undeclared_contact_rejected(self):
        doc = example()
        doc["samples"][0]["landmarks"]["another_shoe"] = {"x": 10, "y": 10}
        with self.assertRaisesRegex(ValueError, "undeclared"):
            _validate(doc)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe not installed")
class VideoVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.temp.name)
        cls.video = cls.folder / "source.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=s=640x360:r=24",
                        "-t", "2", "-c:v", "mpeg4", str(cls.video)], check=True, capture_output=True)
        cls.sha = hashlib.sha256(cls.video.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def sample(self):
        doc = example()
        doc["source_video_sha256"] = self.sha
        return doc

    def test_matching_real_source_and_stable_points_can_screen_pass(self):
        result = evaluate_annotations(self.sample(), video_path=self.video)
        self.assertEqual(result["technical_contact_screen"], "PASS")
        self.assertTrue(result["video"]["matched_annotation_sha256"])
        self.assertEqual(result["exercise_form_approval"], "NOT_EVALUATED")

    def test_matching_source_and_large_drift_warns(self):
        doc = self.sample()
        doc["samples"][2]["landmarks"]["near_knee"]["x"] += 40
        result = evaluate_annotations(doc, video_path=self.video)
        self.assertEqual(result["technical_contact_screen"], "WARN")

    def test_source_hash_mismatch_never_reuses_annotations(self):
        doc = self.sample()
        doc["source_video_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 does not match"):
            evaluate_annotations(doc, video_path=self.video)

    def test_without_pinned_hash_does_not_get_pass(self):
        result = evaluate_annotations(example(), video_path=self.video)
        self.assertEqual(result["technical_contact_screen"], "NOT_EVALUATED")
        self.assertIn("was not pinned", " ".join(result["warnings"]))

    def test_video_native_size_mismatch_rejected(self):
        doc = self.sample()
        doc["frame_size"] = [1280, 720]
        with self.assertRaisesRegex(ValueError, "dimensions do not match"):
            evaluate_annotations(doc, video_path=self.video)

    def test_overlay_matches_original_frame_and_does_not_change_video(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow absent")
        doc = self.sample()
        before = self.sha
        paths = render_overlay(doc, self.video, self.folder / "overlay-output")
        self.assertEqual(len(paths), 3)
        with Image.open(paths[0]) as im:
            self.assertEqual(im.size, (640, 360))
        self.assertEqual(hashlib.sha256(self.video.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
