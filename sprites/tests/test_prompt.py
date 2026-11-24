"""Future-avatar and successful-retake tests without calling any image model."""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kit import prompt


def fixture():
    boy = json.loads((ROOT / "config" / "character.json").read_text(encoding="utf-8"))
    specs = json.loads((ROOT / "prompts" / "strips.json").read_text(encoding="utf-8"))["strips"]
    return boy, specs


class PromptTest(unittest.TestCase):
    def test_unchanged_boy_and_grammatical_girl(self):
        boy, specs = fixture()
        spec = specs["back-extension-c2"]
        text = prompt.build(spec, boy)
        self.assertIn("his arms", text.lower())
        girl = dict(boy, noun="girl", description="a girl with short black hair and blue shoes",
                    pronouns={"he": "she", "him": "her", "his": "her", "himself": "herself", "boy": "girl"})
        for rendered in (prompt.build(spec, girl), prompt.remake(spec, girl, [("girl.png", "character"),
                                                                            ("booklet.png", "booklet")]),
                         prompt.retake(spec, girl)):
            self.assertIsNone(re.search(r"\b(he|his|him|himself|boy)\b", rendered, re.I))
            self.assertIn("her arms", rendered.lower())
            self.assertIn("girl", rendered.lower())
        self.assertEqual(prompt.avatar_words("the other hand", girl), "the other hand")
        self.assertEqual(prompt.avatar_words("HIS shoe", girl), "HER shoe")
        for key, movement in specs.items():
            with self.subTest(movement=key):
                self.assertIsNone(re.search(r"\b(he|his|him|himself|boy)\b", prompt.build(movement, girl), re.I))

    def test_batch_e_scissor_recipe_uses_the_successful_camera_and_shading(self):
        boy, specs = fixture()
        rendered = prompt.remake(specs["scissor-jumps-c1"], boy,
                                 [("boy.png", "character"), ("booklet.png", "booklet"),
                                  ("diagram.png", "schematic")])
        self.assertIn("LIGHT (near) leg forward", rendered)
        self.assertIn("DARK (far) leg forward", rendered)
        self.assertIn("identical camera angle", rendered.lower())
        self.assertNotIn("THREE-QUARTER FRONT", rendered)

    def test_batch_e_back_extension_has_distinct_lift_stages(self):
        boy, specs = fixture()
        rendered = prompt.remake(specs["back-extension-c2"], boy,
                                 [("boy.png", "character"), ("booklet.png", "booklet")])
        for cue in ("0 degrees", "about 15 degrees", "about 30 degrees", "thighs visibly CLEAR"):
            self.assertIn(cue, rendered)


    def test_near_trailing_depth_is_conditional_and_both_endpoints_distinct(self):
        boy, specs = fixture()

        scissors = prompt.remake(specs["scissor-jumps-c1"], boy,
                                [("boy.png", "character"), ("booklet.png", "booklet"),
                                 ("diagram.png", "schematic")])
        self.assertIn("DEPTH LOCK", scissors)
        self.assertIn("screen-LEFT", scissors)
        self.assertIn("near TRAILING thigh", scissors)
        self.assertIn("near leading thigh", scissors)
        self.assertIn("identical camera angle", scissors.lower())

        squat = prompt.build(specs["semi-squat-jumps-c4"], boy)
        self.assertIn("DEPTH LOCK", squat)
        self.assertIn("NEAR LIGHT trailing thigh", squat)
        self.assertIn("FAR DARK leading thigh", squat)

        low_run = prompt.build(specs["stationary-run-c1"], boy)
        high_run = prompt.build(specs["high-knee-run-c4"], boy)
        self.assertIn("DEPTH CONDITIONAL ONLY", low_run)
        self.assertIn("4-inch lift", low_run)
        self.assertIn("DEPTH:", high_run)
        self.assertIn("Maintain waist-high knee lift", high_run)

        # A blanket rule would corrupt lateral jumps and fixed-leg exercises.
        for key in ("astride-jumps-c2", "half-knee-bends-c3",
                    "semi-spread-eagle-jumps-c5", "jack-jumps-c6",
                    "knee-push-up-c1"):
            with self.subTest(exercise=key):
                self.assertNotIn("DEPTH LOCK", prompt.build(specs[key], boy))


if __name__ == "__main__":
    unittest.main()
