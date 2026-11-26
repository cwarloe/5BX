"""Failures from real photographic experiments become specification regressions."""

import copy
import unittest
from pathlib import Path

from photo_motion.contract import load_spec
from photo_motion.extended_contract import validate_extended
from photo_motion.__main__ import _check_spec
from photo_motion.__main__ import _prompt


ROOT = Path(__file__).resolve().parents[1] / "specs"


class ExtendedChartOneMovementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toe = load_spec(ROOT / "chart1-toe-touch.json")
        cls.sit = load_spec(ROOT / "chart1-partial-situp.json")
        cls.leg = load_spec(ROOT / "chart1-alternate-leg-raise.json")
        cls.running = load_spec(ROOT / "chart1-stationary-low-run.json")

    def test_all_new_specs_are_valid_plans_not_form_approvals(self):
        for spec in (self.toe, self.sit, self.leg, self.running):
            with self.subTest(spec=spec["id"]):
                self.assertEqual(validate_extended(spec), [])
                self.assertEqual(_check_spec(spec), [])
                self.assertEqual(spec["status"], "EXPERIMENTAL")

    def test_prompt_includes_exact_structured_support_and_tracked_running_limb_roles(self):
        prompt = _prompt(self.running)
        self.assertIn('"contacts":["orange_foot"]', prompt)
        self.assertIn('"contacts":["teal_foot"]', prompt)
        self.assertIn('"teal_leg":"low_lift"', prompt)
        self.assertIn('"foot_lift_class":"low_about_four_inches"', prompt)

    def test_chart1_toe_must_reach_between_feet_not_outside(self):
        bad = copy.deepcopy(self.toe)
        bad["phases"][1]["hand_target"] = "outside_left_shoe"
        self.assertIn("BETWEEN", " ".join(validate_extended(bad)))

    def test_toe_must_return_from_backbend(self):
        bad = copy.deepcopy(self.toe)
        bad["phases"][-1]["motion"] = "gentle_backbend"
        self.assertIn("motion phases", " ".join(validate_extended(bad)))

    def test_toe_shoes_cannot_slide(self):
        bad = copy.deepcopy(self.toe)
        bad["phases"][2]["feet_fixed"] = False
        self.assertIn("track points", " ".join(validate_extended(bad)))

    def test_partial_situp_is_not_full(self):
        bad = copy.deepcopy(self.sit)
        bad["phases"][2]["full_situp"] = True
        self.assertIn("full sit-up", " ".join(validate_extended(bad)))

    def test_partial_situp_head_and_shoulders_clear_floor(self):
        bad = copy.deepcopy(self.sit)
        bad["phases"][2]["shoulders"] = "down"
        self.assertIn("slightly_raised", " ".join(validate_extended(bad)))

    def test_partial_situp_heel_contact_cannot_move(self):
        bad = copy.deepcopy(self.sit)
        bad["phases"][1]["contacts"] = ["left_heel", "pelvis"]
        self.assertIn("support must stay planted", " ".join(validate_extended(bad)))

    def test_leg_raise_repeating_same_leg_is_rejected(self):
        bad = copy.deepcopy(self.leg)
        bad["phases"][3]["limbs"] = bad["phases"][1]["limbs"].copy()
        self.assertIn("SAME physical orange", " ".join(validate_extended(bad)))

    def test_leg_raise_requires_neutral_midpoint_and_straight_knee(self):
        bad = copy.deepcopy(self.leg)
        bad["phases"][2]["limbs"]["orange_leg"] = "raised"
        bad["phases"][3]["knees"] = "bent"
        errors = " ".join(validate_extended(bad))
        self.assertIn("neutral return", errors)
        self.assertIn("knees must stay straight", errors)

    def test_low_run_never_aliases_near_leg_to_screen_side(self):
        bad = copy.deepcopy(self.running)
        bad["phases"][3]["limbs"] = bad["phases"][2]["limbs"].copy()
        self.assertIn("physical leg", " ".join(validate_extended(bad)))

    def test_low_run_rejects_waist_high_knees(self):
        bad = copy.deepcopy(self.running)
        bad["phases"][1]["foot_lift_class"] = "waist_high"
        self.assertIn("not waist-high knees", " ".join(validate_extended(bad)))

    def test_low_run_end_must_match_start_limb_roles(self):
        bad = copy.deepcopy(self.running)
        bad["phases"][-1]["limbs"] = bad["phases"][1]["limbs"].copy()
        self.assertIn("first/last physical arm", " ".join(validate_extended(bad)))

    def test_extended_contract_keeps_locked_camera_and_no_auto_approval(self):
        bad = copy.deepcopy(self.sit)
        bad["camera"]["locked"] = False
        bad["status"] = "APPROVED"
        errors = " ".join(validate_extended(bad))
        self.assertIn("camera.locked", errors)
        self.assertIn("cannot assert approval", errors)

    def test_chart_and_exercise_number_cannot_relabel_an_unrelated_motion(self):
        for original, chart, exercise in (
            (self.toe, 6, 4),
            (self.sit, 1, 3),
            (self.leg, 2, 3),
            (self.running, 5, 2),
        ):
            with self.subTest(kind=original["movement_type"]):
                mislabeled = copy.deepcopy(original)
                mislabeled["chart"], mislabeled["exercise"] = chart, exercise
                self.assertIn("belongs to Chart 1 Exercise", " ".join(validate_extended(mislabeled)))


if __name__ == "__main__":
    unittest.main()
