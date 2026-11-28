"""Physics and retiming math for gravity_retime.py (no video or rembg needed).

Run: python3 -m unittest discover -s tools/gravity_check/tests
"""

import importlib.util
import math
import sys
import types
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("gravity_retime", HERE / "gravity_retime.py")
gr = importlib.util.module_from_spec(spec)
sys.modules.setdefault("rembg", types.ModuleType("rembg"))   # not needed for these tests
spec.loader.exec_module(gr)

FPS = 24.0
PPM = 200.0          # pixels per metre


def synthetic_jump(g_true, rise_m, ground_frames=12):
    """Pelvis y (pixels, down is +) for one ballistic flight with ground frames either side."""
    T = 2 * math.sqrt(2 * rise_m / g_true)
    n_air = max(3, round(T * FPS))
    t = np.arange(n_air) / FPS
    v0 = g_true * T / 2
    rise = v0 * t - 0.5 * g_true * t ** 2           # metres above takeoff
    base = 300.0
    hip = np.concatenate([np.full(ground_frames, base), base - rise * PPM, np.full(ground_frames, base)])
    bot = np.concatenate([np.full(ground_frames, 376.0), 376.0 - 20 - rise * PPM, np.full(ground_frames, 376.0)])
    return hip, bot


class GravityMath(unittest.TestCase):
    def test_fit_recovers_earth_gravity(self):
        hip, bot = synthetic_jump(9.81, 0.10)
        segs, _ = gr.flights(bot, clearance_px=14, min_frames=3)
        res = gr.fit(hip, segs, FPS, PPM)
        self.assertEqual(len(res), 1)
        self.assertAlmostEqual(res[0]["g_apparent"], 9.81, delta=0.3)
        self.assertAlmostEqual(res[0]["speedup"], 1.0, delta=0.03)

    def test_floaty_jump_gets_the_right_speedup(self):
        # A "moon" jump at 0.94 m/s^2 needs sqrt(9.81/0.94) = 3.23x
        hip, bot = synthetic_jump(0.94, 0.15)
        segs, _ = gr.flights(bot, clearance_px=14, min_frames=3)
        res = gr.fit(hip, segs, FPS, PPM)
        self.assertAlmostEqual(res[0]["speedup"], math.sqrt(9.81 / 0.94), delta=0.1)

    def test_retimed_airtime_matches_the_formula(self):
        rise = 0.15
        hip, bot = synthetic_jump(0.94, rise)
        segs, _ = gr.flights(bot, clearance_px=14, min_frames=3)
        res = gr.fit(hip, segs, FPS, PPM)
        speed, t_out = gr.time_map(len(hip), FPS, res, ease_frames=0)
        i, j = res[0]["start_frame"], res[0]["end_frame"]
        airtime_out = t_out[j] - t_out[i] + 1 / (speed[j] * FPS)
        self.assertAlmostEqual(airtime_out, 2 * math.sqrt(2 * rise / 9.81), delta=1 / FPS)

    def test_ground_frames_keep_normal_speed(self):
        hip, bot = synthetic_jump(0.94, 0.15, ground_frames=20)
        segs, _ = gr.flights(bot, clearance_px=14, min_frames=3)
        res = gr.fit(hip, segs, FPS, PPM)
        speed, _ = gr.time_map(len(hip), FPS, res, ease_frames=2)
        self.assertTrue(np.all(speed[:15] == 1.0))
        self.assertTrue(np.all(speed[-15:] == 1.0))


if __name__ == "__main__":
    unittest.main()
