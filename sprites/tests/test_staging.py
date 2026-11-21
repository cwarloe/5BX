"""The one-camera stage, render profiles and pinned loops (kit/staging.py). No image libraries needed."""
import json
import sys
import unittest
from pathlib import Path

SPRITES = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SPRITES / "kit"))
import staging  # noqa: E402

THEME = json.loads((SPRITES / "config" / "theme.json").read_text(encoding="utf-8"))
WIDE = THEME["formats"]["landscape"]


class StageTests(unittest.TestCase):
    def test_default_profile_is_1080p30_and_test_profile_is_720p24(self):
        F, fps = staging.apply_profile(THEME, WIDE, THEME["fps"], "default")
        self.assertEqual((F["W"], F["H"], fps), (1920, 1080, 30))
        F, fps = staging.apply_profile(THEME, WIDE, THEME["fps"], "test")
        self.assertEqual((F["W"], F["H"], fps), (1280, 720, 24))

    def test_stage_numbers_follow_the_frame(self):
        big = staging.stage_geom(THEME, WIDE)
        small = staging.stage_geom(THEME, staging.apply_profile(THEME, WIDE, 30, "test")[0])
        self.assertAlmostEqual(big["floor_y"], 975)
        self.assertAlmostEqual(small["floor_y"], 650)
        self.assertAlmostEqual(small["foot_x"], 640)
        self.assertAlmostEqual(small["standing_scale"], 0.936556, places=5)

    def test_lying_figures_are_scaled_up_by_the_multiplier(self):
        sg = staging.stage_geom(THEME, WIDE)
        stand, lying_s, _ = staging.stage_scale(sg, {}, 140, 600)
        lie, lying_l, _ = staging.stage_scale(sg, {}, 420, 110)
        self.assertFalse(lying_s)
        self.assertTrue(lying_l)
        self.assertAlmostEqual(lie / stand, THEME["stage"]["lying_scale_multiplier"], places=5)

    def test_posture_override_and_head_normalisation(self):
        sg = staging.stage_geom(THEME, WIDE)
        s, lying, _ = staging.stage_scale(sg, {"posture": "standing"}, 420, 110)
        self.assertFalse(lying)
        half, _, _ = staging.stage_scale(sg, {"head_px": THEME["stage"]["reference_head_px"] * 2}, 140, 300)
        self.assertAlmostEqual(half, sg["standing_scale"] / 2)

    def test_the_head_is_never_cropped(self):
        sg = staging.stage_geom(THEME, WIDE)
        s, _, notes = staging.stage_scale(sg, {}, 100, 2000)
        self.assertLessEqual(sg["floor_y"] - 2000 * s, sg["floor_y"])
        self.assertGreaterEqual(sg["floor_y"] - 2000 * s, sg["head_top_min"] - 1e-6)
        self.assertTrue(notes)

    def test_tall_format_has_no_stage(self):
        self.assertIsNone(staging.stage_geom(THEME, THEME["formats"]["portrait"]))


class LoopTests(unittest.TestCase):
    def test_pinned_loop_starts_and_ends_on_pose_one(self):
        frames = staging.pinned_loop([1, 2, 1, 3], 8.0, 1, 24)
        self.assertEqual(len(frames), 192)
        self.assertEqual(frames[0], 1)
        self.assertEqual(frames[-1], 1)
        self.assertEqual(set(frames), {1, 2, 3})

    def test_every_pose_gets_an_equal_hold(self):
        frames = staging.pinned_loop([1, 2, 3, 2], 4.0, 1, 24)
        self.assertEqual(frames.count(3), 24)

    def test_loop_length_lands_in_the_window(self):
        for cycle_s in (1.7, 3.3333, 6.0, 12.0, 30.0):
            n, cs = staging.choose_loop(cycle_s)
            self.assertTrue(6.0 <= n * cs <= 10.0, (cycle_s, n, cs))


if __name__ == "__main__":
    unittest.main()
