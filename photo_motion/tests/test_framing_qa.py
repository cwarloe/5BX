"""Synthetic MP4 regression tests for fail-closed photographic framing QA."""

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from photo_motion import framing_qa


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe required")
class FramingQATests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.video = root / "synthetic.mp4"
        self.identity = root / "synthetic-master.bin"
        self.identity.write_bytes(b"synthetic-only-master-not-real-person")
        subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
            "color=c=green:s=160x96:r=4:d=1", "-frames:v", "4", "-pix_fmt", "yuv420p",
            "-y", str(self.video)
        ], check=True, capture_output=True)
        self.template = framing_qa.make_template(self.video, identity_source=self.identity)
        self.assertEqual(self.template["frame_count"], 4)
        self.manifest = root / "annotations.json"

    def _valid(self):
        data = copy.deepcopy(self.template)
        data["review"] = {"method": "HUMAN_VISUAL", "reviewer": "synthetic-qa-test"}
        boxes = {"head": [0.40, 0.08, 0.58, 0.27],
                 "left_shoe": [0.20, 0.75, 0.37, 0.93],
                 "right_shoe": [0.63, 0.75, 0.80, 0.93]}
        for frame in data["frames"]:
            for name, box in boxes.items():
                frame["landmarks"][name] = {"visibility": "VISIBLE", "box": box.copy()}
        return data

    def _run(self, data):
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        return framing_qa.analyze(self.video, self.manifest)

    def test_all_frames_manually_annotated_and_identity_master_verified(self):
        report = self._run(self._valid())
        self.assertEqual(report["framing_verdict"], "PASS_MANUALLY_ATTESTED")
        self.assertEqual(report["fully_visible_frame_count"], 4)
        self.assertEqual(report["annotated_frame_count"], 4)
        self.assertEqual(report["exercise_form_person_identity_and_release_approval"], "NOT_EVALUATED")

    def test_head_cropped_fails_even_if_background_identical(self):
        data = self._valid()
        data["frames"][2]["landmarks"]["head"] = {"visibility": "PARTIAL", "box": None}
        report = self._run(data)
        self.assertEqual(report["framing_verdict"], "FAIL")
        self.assertIn({"frame": 2, "landmark": "head", "reason": "PARTIAL"}, report["failures"])

    def test_visible_head_too_close_to_top_fails(self):
        data = self._valid()
        data["frames"][1]["landmarks"]["head"]["box"][1] = 0.005
        report = self._run(data)
        self.assertEqual(report["framing_verdict"], "FAIL")
        self.assertIn({"frame": 1, "landmark": "head", "reason": "HEAD_TOP_CLEARANCE"}, report["failures"])

    def test_foot_bottom_and_horizontal_clipping_fail(self):
        data = self._valid()
        data["frames"][0]["landmarks"]["left_shoe"]["box"][3] = 0.995
        data["frames"][1]["landmarks"]["right_shoe"]["box"][2] = 0.997
        report = self._run(data)
        reasons = {row["reason"] for row in report["failures"]}
        self.assertEqual(report["framing_verdict"], "FAIL")
        self.assertIn("SHOE_BOTTOM_CLEARANCE", reasons)
        self.assertIn("HORIZONTAL_EDGE_CLEARANCE", reasons)

    def test_partial_coverage_and_occluded_foot_not_evaluated(self):
        data = self._valid()
        data["frames"].pop(1)
        data["frames"][0]["landmarks"]["right_shoe"] = {"visibility": "OCCLUDED", "box": None}
        report = self._run(data)
        self.assertEqual(report["framing_verdict"], "NOT_EVALUATED")
        self.assertEqual(report["annotated_frame_count"], 3)
        reasons = {r["reason"] for r in report["not_evaluated"]}
        self.assertIn("MISSING_FRAME_ANNOTATIONS", reasons)
        self.assertIn("OCCLUDED", reasons)

    def test_unknown_identity_or_reviewer_does_not_pass(self):
        data = self._valid()
        data["identity_source"] = None
        data["review"]["method"] = "MODEL_PREDICTED"
        report = self._run(data)
        self.assertEqual(report["framing_verdict"], "NOT_EVALUATED")
        reasons = {r["reason"] for r in report["not_evaluated"]}
        self.assertIn("IDENTITY_SOURCE_UNVERIFIED", reasons)
        self.assertIn("HUMAN_REVIEW_ATTESTATION_MISSING", reasons)

    def test_observed_failure_overrides_missing_coverage(self):
        data = self._valid()
        data["frames"].pop(1)
        data["frames"][0]["landmarks"]["left_shoe"]["visibility"] = "OUT_OF_FRAME"
        data["frames"][0]["landmarks"]["left_shoe"]["box"] = None
        self.assertEqual(self._run(data)["framing_verdict"], "FAIL")

    def test_stale_video_and_frame_hashes_are_rejected(self):
        data = self._valid()
        data["source_video_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "video SHA"):
            self._run(data)
        data = self._valid()
        data["frames"][3]["rgb24_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "RGB24 hash mismatch"):
            self._run(data)

    def test_stale_identity_master_rejected(self):
        data = self._valid()
        self.identity.write_bytes(b"master-overwritten-after-template")
        with self.assertRaisesRegex(ValueError, "identity-source master SHA"):
            self._run(data)

    def test_duplicate_frames_and_malformed_annotations_rejected(self):
        data = self._valid()
        data["frames"].append(copy.deepcopy(data["frames"][0]))
        with self.assertRaisesRegex(ValueError, "duplicated"):
            self._run(data)
        data = self._valid()
        data["frames"][0]["landmarks"]["head"]["box"] = [0.5, 0.5, 0.4, 0.9]
        with self.assertRaisesRegex(ValueError, "positive size"):
            self._run(data)

    def test_unreviewed_template_is_never_a_pass(self):
        report = self._run(self.template)
        self.assertEqual(report["framing_verdict"], "NOT_EVALUATED")
        self.assertEqual(report["fully_visible_frame_count"], 0)

    def test_cannot_weaken_minimum_clearance_to_manufacture_pass(self):
        data = self._valid()
        data["minimum_clearance"]["head_top"] = 0.005
        with self.assertRaisesRegex(ValueError, "do not weaken the baseline"):
            self._run(data)

    def test_video_mutation_during_decode_invalidates_snapshot(self):
        original_decode = framing_qa._stream_frame_hashes

        def mutate_after_decode(*args):
            hashes = original_decode(*args)
            self.video.write_bytes(b"replaced video after bytes were decoded")
            return hashes

        with patch.object(framing_qa, "_stream_frame_hashes", side_effect=mutate_after_decode):
            with self.assertRaisesRegex(RuntimeError, "source MP4 changed"):
                framing_qa.make_template(self.video, identity_source=self.identity)

    def test_cli_refuses_to_overwrite_pinned_identity_source(self):
        data = self._valid()
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        original_master = self.identity.read_bytes()
        with patch("sys.stderr"):
            result = framing_qa.main([str(self.video), "--annotations", str(self.manifest),
                                      "--report", str(self.identity)])
        self.assertEqual(result, 2)
        self.assertEqual(self.identity.read_bytes(), original_master)


if __name__ == "__main__":
    unittest.main()
