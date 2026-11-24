"""Pose-fix helpers (kit/posefix.py): unmix keying, far-limb shading, joint rotation, loop seam."""
import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kit"))
import posefix  # noqa: E402

BG = (221, 5, 196)   # the textured pink-magenta a generated video came back with


class PoseFixTests(unittest.TestCase):
    def test_unmix_removes_background_and_recovers_edge_colour(self):
        a = np.zeros((200, 200, 3), float) + BG
        a[80:120, 80:120] = (255, 255, 255)
        a[80:120, 120] = 0.8 * np.array(BG) + 0.2 * 255     # an edge pixel 20 percent covered by the figure
        out = np.asarray(posefix.key_unmix(Image.fromarray(a.astype(np.uint8))))
        self.assertEqual(out[10, 10, 3], 0)
        self.assertEqual(out[100, 100, 3], 255)
        edge = out[100, 120]
        self.assertGreater(edge[3], 0)
        self.assertGreater(int(edge[1]), int(0.8 * BG[1] + 0.2 * 255) + 40)   # unmixing pulls the edge toward white, away from pink

    def test_darken_is_eighteen_percent_and_keeps_hue(self):
        a = np.full((4, 4, 4), 200, np.uint8); a[..., 0] = 250
        m = np.zeros((4, 4), bool); m[0, 0] = True
        d = posefix.darken(a, m)
        self.assertEqual(tuple(d[0, 0, :3]), (205, 164, 164))
        self.assertEqual(tuple(d[1, 1, :3]), (250, 200, 200))

    def test_rotate_about_keeps_the_pivot_still(self):
        a = np.zeros((101, 101, 4), np.uint8); a[49:52, 49:52] = (255, 0, 0, 255); a[49:52, 88:91] = (0, 255, 0, 255)
        r = np.asarray(posefix.rotate_about(Image.fromarray(a), (50.5, 50.5), 90))   # pixel 50's centre
        self.assertGreater(r[50, 50, 3], 100)
        self.assertGreater(r[10, 50, 1], 50)                 # the point to the right went up (counter-clockwise)

    def test_loop_seam_flags_a_jump(self):
        fr = [Image.fromarray(np.full((8, 8), 10 * i, np.uint8)) for i in range(10)]
        seam, step = posefix.loop_seam(fr, 1)
        self.assertGreater(seam, 5 * step)


if __name__ == "__main__":
    unittest.main()
