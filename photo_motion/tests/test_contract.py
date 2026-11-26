import copy
import math
import unittest
from pathlib import Path

from photo_motion.__main__ import _prompt
from photo_motion.contract import load_spec, validate
from photo_motion.extended_contract import validate_extended


ROOT = Path(__file__).resolve().parents[1]


class TestMotionContract(unittest.TestCase):
    def setUp(self):
        self.scissor = load_spec(ROOT / "specs" / "chart1-scissor-jump.json")
        self.pushup = load_spec(ROOT / "specs" / "chart1-kneeling-pushup.json")

    def test_known_specs_validate(self):
        self.assertEqual(validate(self.scissor), [])
        self.assertEqual(validate(self.pushup), [])

    def test_audio_policy_rejects_unknown_enforcement_values(self):
        low_run = load_spec(ROOT / "specs" / "chart1-stationary-low-run.json")
        self.assertEqual(low_run["audio_policy"], "forbid")
        self.assertEqual(validate_extended(low_run), [])
        low_run["audio_policy"] = "silence-maybe"
        self.assertIn("audio_policy must be", " ".join(validate_extended(low_run)))

    def test_core_motion_cannot_claim_unrelated_chart_or_exercise(self):
        for base, chart, exercise in (
            (self.scissor, 1, 4),
            (self.pushup, 2, 4),
        ):
            with self.subTest(kind=base["movement_type"]):
                bad = copy.deepcopy(base)
                bad["chart"], bad["exercise"] = chart, exercise
                self.assertIn("belongs to Chart 1 Exercise", " ".join(validate(bad)))

    def test_scissor_cannot_teleport_from_opposite_landing_to_start(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"].pop(3)
        self.assertIn("two exchanges, no teleport", " ".join(validate(bad)))

    def test_same_leg_forward_in_both_landings_is_rejected(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"][2]["limbs"] = copy.deepcopy(bad["phases"][0]["limbs"])
        self.assertIn("grounded leads", " ".join(validate(bad)))

    def test_same_color_arm_pump_is_rejected(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"][1]["limbs"]["orange_arm"] = "forward"
        self.assertIn("same-color leg", " ".join(validate(bad)))

    def test_verified_source_marker_roles_must_match_actual_first_phase(self):
        bad = copy.deepcopy(self.scissor)
        bad["track_provenance"]["source_marker_start_state"]["orange_leg"] = "forward"
        self.assertIn("scissor source marker start-state", " ".join(validate(bad)))
        bad = copy.deepcopy(self.scissor)
        del bad["track_provenance"]["source_marker_start_state"]
        self.assertIn("scissor source marker start-state", " ".join(validate(bad)))

    def test_bent_running_arms_are_rejected(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"][2]["arm_form"] = "bent_running"
        self.assertIn("extended shoulder-high arms", " ".join(validate(bad)))

    def test_airborne_shoe_cannot_be_planted(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"][1]["contacts"] = ["orange_foot"]
        self.assertIn("airborne phase", " ".join(validate(bad)))

    def test_invalid_timestamps_rejected(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"][3]["time_seconds"] = 1.0
        self.assertIn("increase and not exceed duration", " ".join(validate(bad)))

    def test_nonfinite_timing_rejected(self):
        bad = copy.deepcopy(self.scissor)
        bad["fps"] = math.inf
        self.assertIn("finite and positive", " ".join(validate(bad)))
        bad = copy.deepcopy(self.scissor)
        bad["phases"][1]["time_seconds"] = math.nan
        self.assertIn("time_seconds must be finite", " ".join(validate(bad)))

    def test_unlocked_camera_rejected(self):
        bad = copy.deepcopy(self.scissor)
        bad["camera"]["locked"] = False
        self.assertIn("camera.locked must be true", " ".join(validate(bad)))

    def test_camera_must_have_description_for_prompt(self):
        bad = copy.deepcopy(self.scissor)
        bad["camera"].pop("description")
        self.assertIn("camera.description", " ".join(validate(bad)))

    def test_malformed_support_is_rejected_without_exception(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"][0]["support"] = {"grounded": True}
        self.assertIn("support must be grounded", " ".join(validate(bad)))

    def test_uncertain_scissor_limb_directions_are_not_accepted(self):
        bad = copy.deepcopy(self.scissor)
        bad["phases"][1]["limbs"] = {
            "orange_leg": "transition", "teal_leg": "neutral",
            "orange_arm": "neutral", "teal_arm": "transition"
        }
        self.assertIn("explicit FORWARD/BACK", " ".join(validate(bad)))

    def test_no_self_approval_in_contract(self):
        bad = copy.deepcopy(self.pushup)
        bad["status"] = "APPROVED"
        self.assertIn("cannot assert approval", " ".join(validate(bad)))

    def test_pushup_requires_both_palms_and_knees(self):
        bad = copy.deepcopy(self.pushup)
        bad["phases"][1]["contacts"] = ["left_palm", "right_palm", "left_knee"]
        self.assertIn("both palms and knees", " ".join(validate(bad)))

    def test_chart1_pushup_requires_booklet_chest_floor_touch(self):
        bad = copy.deepcopy(self.pushup)
        bad["phases"][2]["chest_position"] = "hover_above_floor"
        self.assertIn("original booklet requires gentle chest-to-floor contact", " ".join(validate(bad)))
        self.assertIn('"chest_position":"touch_floor"', _prompt(self.pushup))
        bad = copy.deepcopy(self.pushup)
        bad["phases"][2]["elbows"] = "extended"
        self.assertIn("bottom requires bent elbows", " ".join(validate(bad)))

    def test_pushup_must_return_to_start(self):
        bad = copy.deepcopy(self.pushup)
        bad["phases"][-1]["elbows"] = "bent"
        self.assertIn("start and finish", " ".join(validate(bad)))

    def test_prompt_generation_deterministic_and_explicit(self):
        self.assertEqual(_prompt(self.scissor), _prompt(self.scissor))
        self.assertIn("SECOND distinct airborne exchange", _prompt(self.scissor))
        self.assertIn("No voice, captions or music", _prompt(self.scissor))
        self.assertIn('"support":"airborne"', _prompt(self.scissor))
        self.assertIn('"contacts":[]', _prompt(self.scissor))
        self.assertIn('"arm_form":"straight_shoulder_high"', _prompt(self.scissor))
        self.assertIn('"orange_leg":"back"', _prompt(self.scissor))
        self.assertIn("Resolve any conflict", _prompt(self.scissor))
        self.assertIn("ORIGINAL SOURCE MARKER AUTHORITY", _prompt(self.scissor))
        self.assertIn("760x504 V6 panel", _prompt(self.scissor))


if __name__ == "__main__":
    unittest.main()
