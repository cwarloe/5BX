"""Timeline rules for render_level.py. Run: python3 -m unittest discover -s video/tests"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from level_plan import ClipInfo, ex5_plan, load_data, plan_level  # noqa: E402

DATA = load_data()
ORDER = ["toe", "situp", "legraise", "kneepushup", "run", "scissor"]
CLIPS = {
    "toe": ClipInfo("toe", 111, 1), "situp": ClipInfo("situp", 206, 1),
    "legraise": ClipInfo("legraise", 180, 1), "kneepushup": ClipInfo("kneepushup", 137, 1),
    "run": ClipInfo("run", 91, 3.5), "scissor": ClipInfo("scissor", 28, 2),
}


def work(segs, ex):
    return sum(s.seconds for s in segs if s.exercise == ex and s.kind != "card")


class LevelPlan(unittest.TestCase):
    def test_every_level_fills_exactly_the_booklet_time(self):
        alloc = DATA["timing"]["secondsPerExercise"]
        for chart in (1, 2, 3):
            for lv in DATA["levelOrder"]:
                segs = plan_level(DATA, chart, lv, CLIPS, ORDER)
                for ex in range(1, 6):
                    with self.subTest(chart=chart, level=lv, ex=ex):
                        self.assertAlmostEqual(work(segs, ex), alloc[ex - 1], places=3)

    def test_counts_reach_the_chart_numbers(self):
        for lv in DATA["levelOrder"]:
            segs = plan_level(DATA, 1, lv, CLIPS, ORDER)
            reps = DATA["charts"][0]["levels"][lv]["reps"]
            steps = DATA["charts"][0]["levels"][lv]["steps"]
            for ex in range(1, 5):
                done = sum(s.reps for s in segs if s.exercise == ex and s.kind == "reps")
                self.assertEqual(done, reps[ex - 1], (lv, ex))
            self.assertEqual(sum(s.reps for s in segs if s.kind == "run"), steps, lv)

    def test_jump_sets_follow_the_app_rule(self):
        # A set after every full 75-step block except the one that finishes the target.
        for lv in DATA["levelOrder"]:
            p = ex5_plan(DATA, 1, lv)
            segs = plan_level(DATA, 1, lv, CLIPS, ORDER)
            sets = sum(1 for s in segs if s.kind == "jumps")
            self.assertEqual(sets, max(0, math.ceil(p["target"] / 75) - 1), lv)
            self.assertTrue(all(s.reps == 10 for s in segs if s.kind == "jumps"))

    def test_never_slow_motion(self):
        for lv in DATA["levelOrder"]:
            for s in plan_level(DATA, 1, lv, CLIPS, ORDER):
                if s.kind in ("reps", "run", "jumps"):
                    self.assertGreaterEqual(s.speed, 1.0 - 1e-9, (lv, s))

    def test_slow_source_is_reported(self):
        segs = plan_level(DATA, 1, "A+", CLIPS, ORDER)
        notes = [n for s in segs for n in s.notes]
        self.assertTrue(any("too slow" in n for n in notes))

    def test_front_pacing_puts_reps_first(self):
        segs = plan_level(DATA, 1, "D-", CLIPS, ORDER, pacing="front")
        toe = [s.kind for s in segs if s.exercise == 1 and s.kind != "card"]
        self.assertEqual(toe, ["reps", "done"])


if __name__ == "__main__":
    unittest.main()
