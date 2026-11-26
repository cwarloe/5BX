"""Synthetic-only V11 candidate checks. No user media, Flow, or credits."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photo_motion import apex_candidate_qa as apex


class ApexCandidateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.image = self.root / "b.jpg"
        Image.new("RGB", apex.SIZE, "blue").save(self.image)
        self.sha = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.v10_paths = {k: "synthetic-" + k for k in apex.V10_KEYS}
        source = patch.object(apex, "verify_v10_pair", return_value={
            "start_sha256": apex.A_STAR_SHA256,
            "end_sha256": apex.C_STAR_SHA256,
            "shared_canvas_manifest_sha256": apex.V10_MANIFEST_SHA256,
            "independent_source_qa_report_sha256": apex.V10_QA_SHA256,
        })
        source.start()
        self.addCleanup(source.stop)
        self.qa = {
            "schema_version": 1, "authority": apex.AUTHORITY,
            "a_star_sha256": apex.A_STAR_SHA256,
            "c_star_sha256": apex.C_STAR_SHA256,
            "v10_manifest_sha256": apex.V10_MANIFEST_SHA256,
            "v10_qa_sha256": apex.V10_QA_SHA256,
            "b_sha256": self.sha, "b_format": "JPEG", "image_size": list(apex.SIZE),
            "producer": "synthetic-producer", "reviewer": "synthetic-independent-reviewer",
            "decision": "CANDIDATE_FOR_DIAGNOSTIC_ONLY",
            "checks": {key: {"verdict": "PASS", "evidence": "Synthetic independent test description only"}
                       for key in apex.CHECKS},
            "measurements": {
                "forward_screen_direction": "RIGHT",
                "reference_a_markers": {
                    "orange_ankle": [450, 550], "teal_ankle": [600, 550],
                    "orange_wrist": [650, 240], "teal_wrist": [450, 240]},
                "candidate_b_markers": {
                    "orange_ankle": [650, 510], "teal_ankle": [450, 510],
                    "orange_wrist": [450, 230], "teal_wrist": [650, 230]},
                "reference_a_ground": {"ground_y": 700,
                                       "orange_sole_y": 700, "teal_sole_y": 698},
                "candidate_b_shoe_bottoms": {"orange_sole_y": 640, "teal_sole_y": 645},
                "candidate_b_shoulders": {"orange_y": 230, "teal_y": 232},
            },
            "anatomical_left_right_proven": False,
            "video_form_release": "NOT_EVALUATED",
        }
        self.report = self.root / "qa.json"
        self.save()

    def save(self):
        self.report.write_text(json.dumps(self.qa), encoding="utf-8")

    def check(self):
        return apex.check_candidate(self.v10_paths, self.image, self.report)

    def test_synthetic_airborne_candidate_only_never_authorizes_paid(self):
        result = self.check()
        self.assertEqual(result["observed_geometry"]["minimum_both_shoe_clearance_px"], 55)
        self.assertEqual(result["paid_video_precredit_authority"], "NOT_GRANTED")
        self.assertEqual(result["historical_anatomical_left_right"], "UNKNOWN")
        self.assertEqual(result["motion_video_release_approval"], "NOT_EVALUATED")

    def test_grounded_b1_style_source_rejected_even_if_qa_says_pass(self):
        self.qa["measurements"]["candidate_b_shoe_bottoms"] = {
            "orange_sole_y": 697, "teal_sole_y": 694}
        self.save()
        with self.assertRaisesRegex(ValueError, "grounded|clearance"):
            self.check()

    def test_24_pixel_clearance_rejected(self):
        self.qa["measurements"]["candidate_b_shoe_bottoms"]["orange_sole_y"] = 676
        self.save()
        with self.assertRaisesRegex(ValueError, "clearance"):
            self.check()

    def test_marker_missing_or_not_reversed(self):
        for change in ("missing", "ankle", "wrist"):
            with self.subTest(change=change):
                old = copy.deepcopy(self.qa)
                markers = self.qa["measurements"]["candidate_b_markers"]
                if change == "missing":
                    del markers["orange_wrist"]
                elif change == "ankle":
                    markers["orange_ankle"][0] = 410
                else:
                    markers["teal_wrist"][0] = 400
                self.save()
                with self.assertRaisesRegex(ValueError, "marker|reversed"):
                    self.check()
                self.qa = old

    def test_arm_and_ground_reference_invalid(self):
        self.qa["measurements"]["candidate_b_shoulders"]["orange_y"] = 350
        self.save()
        with self.assertRaisesRegex(ValueError, "shoulder-high"):
            self.check()
        self.qa["measurements"]["candidate_b_shoulders"]["orange_y"] = 230
        self.qa["measurements"]["reference_a_ground"]["ground_y"] = 660
        self.save()
        with self.assertRaisesRegex(ValueError, "ground"):
            self.check()

    def test_stale_sha_and_non_raw_file_fail(self):
        self.qa["b_sha256"] = "f" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "bound"):
            self.check()
        self.qa["b_sha256"] = self.sha
        self.save()
        self.image.write_bytes(b"JPEG corruption")
        with self.assertRaises(ValueError):
            self.check()

    def test_independent_review_and_unknown_form_cannot_be_bypassed(self):
        for field, value in (("decision", "HOLD"),
                             ("reviewer", "synthetic-producer"),
                             ("anatomical_left_right_proven", True),
                             ("video_form_release", "APPROVED")):
            with self.subTest(field=field):
                old = copy.deepcopy(self.qa)
                self.qa[field] = value
                self.save()
                with self.assertRaises(ValueError):
                    self.check()
                self.qa = old
        self.qa["checks"]["background_stability"]["verdict"] = "HOLD"
        self.save()
        with self.assertRaisesRegex(ValueError, "background_stability"):
            self.check()

    def test_v10_source_must_be_exact_replay_authority(self):
        with patch.object(apex, "verify_v10_pair", return_value={
                "start_sha256": "0" * 64, "end_sha256": apex.C_STAR_SHA256,
                "shared_canvas_manifest_sha256": apex.V10_MANIFEST_SHA256,
                "independent_source_qa_report_sha256": apex.V10_QA_SHA256}):
            with self.assertRaisesRegex(ValueError, "V10 source authority"):
                self.check()
        bad_paths = dict(self.v10_paths)
        del bad_paths["canvas_jpeg"]
        with self.assertRaisesRegex(ValueError, "exact V10"):
            apex.check_candidate(bad_paths, self.image, self.report)


if __name__ == "__main__":
    unittest.main()
