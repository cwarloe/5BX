"""Fast checks for tools/video_finish (synthetic frames; no video files, no model download).

  python3 -m unittest discover -s tools/video_finish/tests
"""
import os, sys, unittest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import video_finish as vf

CFG = vf.load_config()


def moving_dot(n, period, h=36, w=64, phase=0.0, amp=20, second_motion=False):
    """A dot circling with the given period; optionally a second dot that moves only in the second half of each cycle."""
    G = np.full((n, h, w), 230, np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    for i in range(n):
        t = 2 * np.pi * (i / period + phase)
        cy, cx = h / 2 + 8 * np.sin(t), w / 2 + amp * np.cos(t)
        G[i][(yy - cy) ** 2 + (xx - cx) ** 2 < 16] = 40
        if second_motion:
            c2 = (i % (2 * period)) >= period          # "the other leg": present every other cycle
            if c2: G[i][(yy - 6) ** 2 + (xx - 8) ** 2 < 9] = 40
    return G


class Loops(unittest.TestCase):
    def test_finds_one_period(self):
        G = moving_dot(120, period=40)
        a, b, joint = vf.find_loop(G, fps=24, min_cycle_s=1.0)
        self.assertEqual((b - a) % 40, 0, f"cycle {b - a} is not a whole number of periods")
        self.assertLess(joint, CFG["loop"]["joint_smooth_below"])

    def test_alternating_needs_both_sides(self):
        # A movement that differs on alternate cycles (left leg, right leg). A long enough minimum length makes the loop
        # contain both; the default could pick a single cycle, which is the leg-raise mistake recorded in config.json.
        G = moving_dot(240, period=40, second_motion=True)
        a, b, _ = vf.find_loop(G, fps=24, min_cycle_s=80 / 24)
        self.assertEqual((b - a) % 80, 0, f"cycle {b - a} does not contain both alternating halves")

    def test_loop_order(self):
        self.assertEqual(vf.loop_order(4, "cut"), [0, 1, 2, 3])
        self.assertEqual(vf.loop_order(4, "pingpong"), [0, 1, 2, 3, 2, 1])   # no repeated end frames, so no stutter

    def test_verdicts(self):
        self.assertEqual(vf.joint_verdict(0.9, CFG), "smooth")
        self.assertEqual(vf.joint_verdict(2.0, CFG), "slight hitch")
        self.assertEqual(vf.joint_verdict(3.5, CFG), "visible jump")


class Placement(unittest.TestCase):
    def test_standing_matches_reference_height_and_contact_line(self):
        clip = {"body_kind": "standing", "body_length_px": 600}
        s, ox, oy, sw, sh = vf.placement(CFG, clip, 1280, 720, (600, 50, 700, 650))
        H = CFG["canvas"]["height"]
        self.assertAlmostEqual(600 * s, CFG["proportion"]["standing_height_frac"] * H, places=6)
        self.assertAlmostEqual(oy + 650 * s, CFG["proportion"]["contact_line_frac"] * H, delta=1)
        self.assertAlmostEqual(ox + 650 * s, CFG["proportion"]["center_x_frac"] * CFG["canvas"]["width"], delta=1)

    def test_lying_uses_lying_length(self):
        clip = {"body_kind": "lying", "body_length_px": 1000}
        s, *_ = vf.placement(CFG, clip, 1280, 720, (100, 300, 1100, 400))
        self.assertAlmostEqual(1000 * s, CFG["proportion"]["lying_length_frac"] * CFG["canvas"]["height"], places=6)

    def test_never_bigger_than_reference(self):
        self.assertLessEqual(CFG["proportion"]["standing_height_frac"], CFG["proportion"]["max_standing_height_frac"])

    def test_cut_line_when_source_edge_lands_inside_canvas(self):
        m = np.zeros((100, 100), bool); m[0:60, 40:60] = True           # person touches the top of the source frame
        self.assertEqual(vf.cut_lines(m, ox=10, oy=50, sw=100, sh=100, cw=1280, ch=720), ["top"])
        self.assertEqual(vf.cut_lines(m, ox=10, oy=-5, sw=100, sh=100, cw=1280, ch=720), [])   # edge above the canvas: fine


class Config(unittest.TestCase):
    def test_every_clip_is_complete(self):
        for k, c in CFG["clips"].items():
            for key in ("title", "drive_id", "body_length_px", "body_kind", "loop"):
                self.assertIn(key, c, f"{k} missing {key}")
            self.assertIn(c["body_kind"], ("standing", "lying"))
            self.assertIn(c["loop"]["mode"], ("cut", "pingpong"))
            self.assertLess(c["loop"]["start"], c["loop"]["end"])
            if "usable_until_frame" in c: self.assertLessEqual(c["loop"]["end"], c["usable_until_frame"])

    def test_plate_exists(self):
        self.assertTrue(os.path.exists(os.path.join(vf.HERE, CFG["plate"]["file"])))


if __name__ == "__main__":
    unittest.main()
