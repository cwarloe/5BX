"""Regressions against silent Chart 1 scissor-booklet / color-role conflation.

These protect source wording and evidence boundaries, not actual video form.
"""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ScissorHistoricalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "data/5bx-charts.json").read_text(encoding="utf-8"))
        cls.exercise = cls.plan["charts"][0]["exercises"][4]

    def test_source_initial_anatomical_cross_and_shoulder_height(self):
        booklet = " ".join(self.exercise["notes"])
        self.assertIn("right leg and left arm extended forward", booklet)
        self.assertIn("left leg and right arm extended backward", booklet)
        self.assertIn("change position of arms and legs before landing", booklet)
        self.assertIn("arms shoulder high", booklet)

    def test_running_step_and_jump_dose_are_separate(self):
        self.assertIn("left foot touches floor", self.exercise["start"])
        self.assertIn("approximately 4 inches", self.exercise["start"])
        self.assertIn('Every 75 steps do 10 "scissor jumps"', self.exercise["movement"])
        self.assertEqual((self.exercise["jumpEvery"], self.exercise["jumpCount"]), (75, 10))
        self.assertEqual(self.plan["timing"]["secondsPerExercise"][4], 360)
        self.assertIn("not from the booklet", self.plan["$comment_jumpWindow"])

    def test_scissor_sources_do_not_claim_anatomical_side_authority(self):
        specs = ROOT / "photo_motion/specs"
        for name in ("chart1-scissor-jump.json", "chart1-scissor-jump-v7-prepared-pair.json"):
            with self.subTest(name=name):
                spec = json.loads((specs / name).read_text(encoding="utf-8"))
                self.assertIs(spec["track_provenance"]["anatomical_left_right_proven"], False)
                self.assertEqual([p["support"] for p in spec["phases"]],
                                 ["grounded", "airborne", "grounded", "airborne", "grounded"])
                self.assertEqual([p["id"] for p in spec["phases"]], ["A", "B", "C", "D", "E"])
                self.assertEqual(spec["duration_seconds"], 6.0)  # Pilot, not source cadence.


if __name__ == "__main__":
    unittest.main()
