import copy
import unittest
from pathlib import Path

from photo_motion.__main__ import _prompt
from photo_motion.contract import load_spec, validate


ROOT = Path(__file__).resolve().parents[1]


class TestMotionContract(unittest.TestCase):
    def setUp(self):
        self.scissor = load_spec(ROOT / "specs" / "chart1-scissor-jump.json")
        self.pushup = load_spec(ROOT / "specs" / "chart1-kneeling-pushup.json")

    def test_known_specs_validate(self):
        self.assertEqual(validate(self.scissor), [])
        self.assertEqual(validate(self.pushup), [])

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
        self.assertIn("time_seconds must increase", " ".join(validate(bad)))

    def test_unlocked_camera_rejected(self):
        bad = copy.deepcopy(self.scissor)
        bad["camera"]["locked"] = False
        self.assertIn("camera.locked must be true", " ".join(validate(bad)))

    def test_no_self_approval_in_contract(self):
        bad = copy.deepcopy(self.pushup)
        bad["status"] = "APPROVED"
        self.assertIn("cannot assert approval", " ".join(validate(bad)))

    def test_pushup_requires_both_palms_and_knees(self):
        bad = copy.deepcopy(self.pushup)
        bad["phases"][1]["contacts"] = ["left_palm", "right_palm", "left_knee"]
        self.assertIn("both palms and knees", " ".join(validate(bad)))

    def test_pushup_must_return_to_start(self):
        bad = copy.deepcopy(self.pushup)
        bad["phases"][-1]["elbows"] = "bent"
        self.assertIn("start and finish", " ".join(validate(bad)))

    def test_prompt_generation_deterministic_and_explicit(self):
        self.assertEqual(_prompt(self.scissor), _prompt(self.scissor))
        self.assertIn("SECOND distinct airborne exchange", _prompt(self.scissor))
        self.assertIn("No voice, captions or music", _prompt(self.scissor))


if __name__ == "__main__":
    unittest.main()
