"""Synthetic human observations; no user photo/video included in Git."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from photo_motion import scissor_phase_qa as phase


SPEC = Path(__file__).resolve().parents[1] / "specs" / "chart1-scissor-jump.json"


class ScissorPhaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.video = self.root / "synthetic.mp4"
        self.video.write_bytes(b"SYNTHETIC-NOT-A-VIDEO")
        self.photo = self.root / "exact-start-photo.png"
        self.photo.write_bytes(b"SYNTHETIC-NOT-A-PHOTO")
        self.hashes = [hashlib.sha256(f"RGB24-frame-{i}".encode()).hexdigest() for i in range(144)]
        self.metadata = {"width": 1280, "height": 720, "fps": 24.0, "duration_seconds": 6.0}
        self.video_sha = phase.file_sha256(self.video)
        self.snapshot = patch.object(phase, "_video_snapshot", return_value=(
            self.video.resolve(), self.video_sha, self.metadata, self.hashes))
        self.snapshot.start()
        self.addCleanup(self.snapshot.stop)
        self.doc = phase.make_template(self.video, SPEC, self.photo)
        self.doc["forward_screen_direction"] = "RIGHT"
        self.doc["review"] = {"method": "HUMAN_VISUAL", "reviewer": "independent-manual-qa"}
        for i, row in enumerate(self.doc["frames"]):
            # Two independent airborne intervals with a visually grounded C
            # between. Both exchanges interpolate physical marker positions,
            # rather than instantaneously reassign screen-side labels.
            progress = ((i - 29) / 10 if 30 <= i <= 38 else 1 if 39 <= i <= 89 else
                        1 - (i - 89) / 11 if 90 <= i <= 99 else 0 if i <= 29 or i >= 100 else 1)
            progress = max(0, min(1, progress))
            orange_leg_x = .35 + .30 * progress
            teal_leg_x = .65 - .30 * progress
            orange_arm_x = .65 - .30 * progress
            teal_arm_x = .35 + .30 * progress
            coords = {"orange_ankle": [orange_leg_x, .85], "teal_ankle": [teal_leg_x, .85],
                      "orange_wrist": [orange_arm_x, .40], "teal_wrist": [teal_arm_x, .40]}
            row["marker_identity"] = "STABLE"
            row["shoe_contact"] = {shoe: "AIRBORNE" if 30 <= i <= 38 or 90 <= i <= 99 else "PLANTED"
                                   for shoe in phase.CONTACTS}
            row["landmarks"] = {name: {"visibility": "VISIBLE", "point": coords[name]}
                                for name in phase.LANDMARKS}

    def analyze(self, doc=None):
        path = self.root / "observations.json"
        path.write_text(json.dumps(doc if doc is not None else self.doc), encoding="utf-8")
        return phase.analyze(self.video, path)

    def failure_reasons(self, result):
        return {entry["reason"] for entry in result["failures"]}

    def test_template_does_not_imply_observation_or_pass(self):
        template = phase.make_template(self.video, SPEC, self.photo)
        self.assertEqual(template["review"]["method"], "UNREVIEWED")
        self.assertEqual(template["frames"][0]["marker_identity"], "UNKNOWN")
        self.assertEqual(phase.analyze(self.video, self._write(template))["phase_verdict"], "NOT_EVALUATED")

    def _write(self, data):
        path = self.root / "unreviewed.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_two_physical_exchanges_pass_only_as_manually_attested(self):
        result = self.analyze()
        self.assertEqual(result["phase_verdict"], "PASS_MANUALLY_ATTESTED")
        self.assertEqual([r["duration_frames"] for r in result["airborne_runs"]], [9, 10])
        self.assertIn(60, result["opposite_landing_candidate_frames"])
        self.assertEqual(result["exercise_form_identity_loop_and_release_approval"], "NOT_EVALUATED")

    def test_hops_without_opposite_pose_fail(self):
        for row in self.doc["frames"]:
            for name in phase.LANDMARKS:
                row["landmarks"][name]["point"][0] = (.35 if name in ("orange_ankle", "teal_wrist") else .65)
        result = self.analyze()
        self.assertEqual(result["phase_verdict"], "FAIL")
        self.assertIn("NO_OPPOSITE_GROUNDED_C_WITHIN_WINDOW", self.failure_reasons(result))

    def test_no_first_flight_fails_even_with_opposite_stance(self):
        for i in range(30, 39):
            self.doc["frames"][i]["shoe_contact"] = {shoe: "PLANTED" for shoe in phase.CONTACTS}
        result = self.analyze()
        self.assertEqual(result["phase_verdict"], "FAIL")
        self.assertIn("MISSING_B_TWO_FRAME_AIRBORNE_EVENT", self.failure_reasons(result))

    def test_no_second_flight_fails(self):
        for i in range(90, 100):
            self.doc["frames"][i]["shoe_contact"] = {shoe: "PLANTED" for shoe in phase.CONTACTS}
        result = self.analyze()
        self.assertEqual(result["phase_verdict"], "FAIL")
        self.assertIn("MISSING_D_TWO_FRAME_AIRBORNE_EVENT", self.failure_reasons(result))

    def test_third_airborne_event_fails(self):
        for i in range(70, 74):
            self.doc["frames"][i]["shoe_contact"] = {shoe: "AIRBORNE" for shoe in phase.CONTACTS}
        result = self.analyze()
        self.assertEqual(result["phase_verdict"], "FAIL")
        self.assertIn("MORE_THAN_TWO_DISTINCT_AIRBORNE_EVENTS", self.failure_reasons(result))

    def test_marker_migration_fails_immediately(self):
        self.doc["frames"][49]["marker_identity"] = "MIGRATED"
        self.assertIn("PHYSICAL_MARKER_MIGRATION", self.failure_reasons(self.analyze()))

    def test_unknown_marker_cannot_pass(self):
        self.doc["frames"][49]["marker_identity"] = "UNKNOWN"
        self.assertEqual(self.analyze()["phase_verdict"], "NOT_EVALUATED")

    def test_occluded_shoe_cannot_pass(self):
        self.doc["frames"][49]["shoe_contact"]["orange_shoe"] = "OCCLUDED"
        self.assertEqual(self.analyze()["phase_verdict"], "NOT_EVALUATED")

    def test_missing_frame_cannot_pass(self):
        self.doc["frames"].pop(5)
        self.assertEqual(self.analyze()["phase_verdict"], "NOT_EVALUATED")

    def test_no_human_reviewer_cannot_pass(self):
        self.doc["review"]["method"] = "UNREVIEWED"
        self.assertEqual(self.analyze()["phase_verdict"], "NOT_EVALUATED")

    def test_unknown_forward_orientation_cannot_pass(self):
        self.doc["forward_screen_direction"] = "UNKNOWN"
        self.assertEqual(self.analyze()["phase_verdict"], "NOT_EVALUATED")

    def test_wrong_end_posture_fails(self):
        row = self.doc["frames"][-1]
        row["landmarks"]["orange_ankle"]["point"][0] = .85
        self.assertIn("E_WRONG_PHYSICAL_LIMB_ORDER", self.failure_reasons(self.analyze()))

    def test_start_end_far_apart_fails_even_if_order_matches(self):
        row = self.doc["frames"][-1]
        row["landmarks"]["orange_ankle"]["point"][1] = .50
        self.assertIn("A_E_MARKER_POSITION_MISMATCH", self.failure_reasons(self.analyze()))

    def test_unphysical_one_frame_teleport_fails(self):
        self.doc["frames"][49]["landmarks"]["orange_wrist"]["point"][1] = .90
        self.assertIn("SUDDEN_MARKER_TELEPORT", self.failure_reasons(self.analyze()))

    def test_changed_rgb24_hash_is_hard_error(self):
        self.doc["frames"][49]["rgb24_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "RGB24 hash changed"):
            self.analyze()

    def test_changed_video_hash_is_hard_error(self):
        self.doc["source_video_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "MP4 hash"):
            self.analyze()

    def test_changed_reference_is_hard_error(self):
        self.photo.write_bytes(b"DIFFERENT-PHOTO")
        with self.assertRaisesRegex(ValueError, "photographic reference hash mismatch"):
            self.analyze()

    def test_invalid_coordinates_rejected(self):
        self.doc["frames"][49]["landmarks"]["teal_wrist"]["point"] = [float("nan"), .5]
        with self.assertRaisesRegex(ValueError, "finite normalized"):
            self.analyze()

    def test_duplicate_frame_rejected(self):
        self.doc["frames"].append(copy.deepcopy(self.doc["frames"][49]))
        with self.assertRaisesRegex(ValueError, "duplicate or out-of-range"):
            self.analyze()

    def test_modified_contract_hash_is_hard_error(self):
        self.doc["contract"]["sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "contract hash mismatch"):
            self.analyze()


if __name__ == "__main__":
    unittest.main()
