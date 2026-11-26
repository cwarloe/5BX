"""Only synthetic data: no private media or real-person image in Git."""

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from photo_motion import arm_trajectory_qa as arm


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class ArmTrajectoryQATests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-arm-qa-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.video = root / "synthetic.mp4"
        self.manifest = root / "manual-annotations.json"
        subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
            "color=c=blue:s=160x96:r=4:d=1", "-frames:v", "4", "-pix_fmt", "yuv420p",
            "-y", str(self.video),
        ], check=True, capture_output=True)
        self.template = arm.make_template(self.video)
        self.assertEqual(self.template["frame_count"], 4)

    def complete(self):
        payload = copy.deepcopy(self.template)
        payload["review"] = {"method": "HUMAN_VISUAL", "reviewer": "synthetic-reviewer"}
        geometry = {
            "orange": {"shoulder": [40, 40], "elbow": [60, 40], "wrist": [80, 40]},
            "teal": {"shoulder": [120, 40], "elbow": [100, 40], "wrist": [80, 40]},
        }
        for row in payload["frames"]:
            for color, joints in geometry.items():
                for joint, point in joints.items():
                    row["arms"][color][joint] = {"visibility": "VISIBLE", "point": point.copy()}
        return payload

    def analyze(self, payload):
        self.manifest.write_text(json.dumps(payload), encoding="utf-8")
        return arm.analyze(self.video, self.manifest)

    def test_unreviewed_template_fails_closed(self):
        outcome = self.analyze(self.template)
        self.assertEqual(outcome["trajectory_verdict"], "NOT_EVALUATED")
        self.assertEqual(outcome["arm_height"]["evaluable_frames"], 0)

    def test_fully_attested_geometry_is_only_a_diagnostic_pass(self):
        outcome = self.analyze(self.complete())
        self.assertEqual(outcome["trajectory_verdict"], "PASS_MANUALLY_ATTESTED_GEOMETRY_ONLY")
        self.assertEqual(outcome["arm_height"]["evaluable_frames"], 4)
        self.assertEqual(outcome["elbow_extension"]["evaluable_frames"], 4)
        self.assertEqual(outcome["anatomical_left_right_physical_marker_identity_exercise_form_and_release"],
                         "NOT_EVALUATED")

    def test_dropped_wrist_fails_even_with_correct_endpoint_frames(self):
        payload = self.complete()
        for index in (1, 2):
            payload["frames"][index]["arms"]["orange"]["wrist"]["point"][1] = 65
        result = self.analyze(payload)
        self.assertEqual(result["arm_height"]["verdict"], "FAIL_OBSERVED_GEOMETRY")
        self.assertEqual(result["arm_height"]["observed_bad_frames"], 2)
        self.assertEqual(result["trajectory_verdict"], "FAIL_OBSERVED_GEOMETRY")

    def test_one_observed_violation_cannot_be_hidden_by_many_good_frames(self):
        payload = self.complete()
        payload["frames"][2]["arms"]["orange"]["wrist"]["point"][1] = 65
        result = self.analyze(payload)
        self.assertEqual(result["arm_height"]["observed_bad_frames"], 1)
        self.assertEqual(result["arm_height"]["verdict"], "FAIL_OBSERVED_GEOMETRY")

    def test_bent_elbow_fails_separately_from_wrist_height(self):
        payload = self.complete()
        payload["frames"][2]["arms"]["orange"]["elbow"]["point"] = [80, 30]
        result = self.analyze(payload)
        self.assertEqual(result["arm_height"]["verdict"], "PASS_MANUALLY_ATTESTED_GEOMETRY_ONLY")
        self.assertEqual(result["elbow_extension"]["verdict"], "FAIL_OBSERVED_GEOMETRY")
        self.assertEqual(result["trajectory_verdict"], "FAIL_OBSERVED_GEOMETRY")

    def test_occlusion_never_counts_as_compliant(self):
        payload = self.complete()
        payload["frames"][2]["arms"]["teal"]["wrist"] = {"visibility": "OCCLUDED", "point": None}
        result = self.analyze(payload)
        self.assertEqual(result["trajectory_verdict"], "NOT_EVALUATED")
        self.assertEqual(result["arm_height"]["evaluable_frames"], 3)

    def test_missing_elbows_cannot_certify_straightness(self):
        payload = self.complete()
        for row in payload["frames"]:
            for color in arm.ARM_COLORS:
                row["arms"][color]["elbow"] = {"visibility": "UNKNOWN", "point": None}
        result = self.analyze(payload)
        self.assertEqual(result["arm_height"]["verdict"], "PASS_MANUALLY_ATTESTED_GEOMETRY_ONLY")
        self.assertEqual(result["elbow_extension"]["verdict"], "NOT_EVALUATED")
        self.assertEqual(result["trajectory_verdict"], "NOT_EVALUATED")

    def test_unreviewed_numeric_annotations_do_not_pass(self):
        payload = self.complete()
        payload["review"] = {"method": "MODEL_PREDICTED", "reviewer": "model"}
        self.assertEqual(self.analyze(payload)["trajectory_verdict"], "NOT_EVALUATED")

    def test_observed_failure_overrides_missing_other_frames(self):
        payload = self.complete()
        payload["frames"][1]["arms"]["orange"]["wrist"]["point"][1] = 70
        payload["frames"].pop(3)
        self.assertEqual(self.analyze(payload)["trajectory_verdict"], "FAIL_OBSERVED_GEOMETRY")

    def test_video_and_decoded_frame_rebinding_fails_closed(self):
        payload = self.complete()
        payload["source_video_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "video SHA mismatch"):
            self.analyze(payload)
        payload = self.complete()
        payload["frames"][0]["rgb24_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "RGB24 hash mismatch"):
            self.analyze(payload)

    def test_duplicate_frame_and_bad_coordinate_rejected(self):
        payload = self.complete()
        payload["frames"].append(copy.deepcopy(payload["frames"][0]))
        with self.assertRaisesRegex(ValueError, "duplicated"):
            self.analyze(payload)
        payload = self.complete()
        payload["frames"][1]["arms"]["orange"]["wrist"]["point"] = [170, 40]
        with self.assertRaisesRegex(ValueError, "outside decoded frame"):
            self.analyze(payload)
        payload = self.complete()
        payload["frames"][1]["arms"]["orange"]["wrist"]["point"] = [True, 40]
        with self.assertRaisesRegex(ValueError, "outside decoded frame"):
            self.analyze(payload)

    def test_nonvisible_point_or_zero_length_joint_rejected(self):
        payload = self.complete()
        payload["frames"][2]["arms"]["teal"]["elbow"] = {
            "visibility": "OCCLUDED", "point": [50, 40]}
        with self.assertRaisesRegex(ValueError, "non-visible point must be null"):
            self.analyze(payload)
        payload = self.complete()
        payload["frames"][2]["arms"]["teal"]["elbow"]["point"] = [120, 40]
        with self.assertRaisesRegex(ValueError, "zero-length segment"):
            self.analyze(payload)

    def test_cli_never_overwrites_existing_annotation_or_video(self):
        payload = self.complete()
        self.manifest.write_text(json.dumps(payload), encoding="utf-8")
        original = self.manifest.read_bytes()
        self.assertEqual(arm.main([str(self.video), "--annotations", str(self.manifest),
                                   "--report", str(self.manifest)]), 2)
        self.assertEqual(self.manifest.read_bytes(), original)
        self.assertEqual(arm.main([str(self.video), "--template", str(self.video)]), 2)


if __name__ == "__main__":
    unittest.main()
