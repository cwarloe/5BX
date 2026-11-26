"""Metrics report only what the canonical photographic QA actually records."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "sprites"))
from kit import photo_metrics, photo_traveler


class PhotoMetricsTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.folder = self.root / photo_traveler.PHOTO_DIR
        self.folder.mkdir(parents=True)
        overview = "\n".join(
            f"{n}. [Chart {n} overview](https://drive.google.com/file/d/c{n}/view)."
            for n in range(1, 7))
        (self.folder / photo_traveler.INDEX).write_text(
            f"# Photographic pilot\n{overview}\n", encoding="utf-8")
        for n, name in photo_traveler.INVENTORIES.items():
            start = photo_traveler.ID_RANGES[n][0]
            (self.folder / name).write_text(
                f"# Chart {n}\n## Direct mobile links\n"
                f"- [{start} — test candidate](https://drive.google.com/file/d/image{start}/view)\n",
                encoding="utf-8")

    def _notes(self, content):
        target = self.folder / "round_test" / "QA.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def test_missing_measurements_remain_null_not_fabricated_from_dates_or_titles(self):
        (self.folder / "REVIEW_INVENTORY.md").write_text(
            "# Chart 1\n## Direct mobile links\n"
            "- [15 — REVIEW PASS](https://drive.google.com/file/d/good15/view)\n"
            "| **20** | Flow run | VIDEO GENERATED / CONDITIONAL | "
            "6 s Omni Flash, 720p, 18 credits, full video unverified |\n",
            encoding="utf-8")
        self._notes("Dated 2026-11-26; second generation looks good. PASS is assistant technical only.")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertEqual(data["instrumentation"]["annotated_attempts"], 0)
        self.assertIsNone(data["measurements"]["first_pass_yield"]["value"])
        self.assertIsNone(data["measurements"]["cycle_time_hours"]["value"])
        self.assertIsNone(data["measurements"]["credits_per_approved_video"]["value"])
        self.assertEqual(data["other_known_cost_observations"][0]["credits"], 18)
        self.assertEqual(len(data["other_known_cost_observations"]), 1)
        self.assertEqual(photo_metrics.collect_metrics(self.root, chart=2)
                         ["other_known_cost_observations"], [])
        self.assertIn("not every generated file", data["scope"]["coverage"])

    def test_only_explicit_records_support_sampled_numbers(self):
        self._notes("""# QA
<!-- 5bx-metric id=15A chart=1 exercise=1 stage=still trial=1 quality=pass credits=3 manual_minutes=1 start=2026-11-26T15:00:00Z end=2026-11-26T15:02:00Z -->
<!-- 5bx-metric id=19A chart=1 exercise=5 stage=still trial=1 quality=fail credits=5 manual_minutes=2 start=2026-11-26T15:00:00+00:00 end=2026-11-26T15:04:00Z -->
<!-- 5bx-metric id=19B chart=1 exercise=5 stage=still trial=2 quality=pass credits=6 manual_minutes=3 -->
<!-- 5bx-metric id=21A chart=2 exercise=1 stage=still trial=1 quality=fail credits=9 -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertEqual(data["instrumentation"]["annotated_attempts"], 3)
        self.assertEqual(data["measurements"]["first_pass_yield"]["value"], 0.5)
        self.assertEqual(data["measurements"]["first_pass_yield"]["sample_size"], 2)
        self.assertEqual(data["measurements"]["repeat_attempt_share"]["value"], 0.3333)
        self.assertAlmostEqual(data["measurements"]["cycle_time_hours"]["value"], 0.05)
        self.assertEqual(data["stage_cycle_times"]["still"]["sample_size"], 2)
        self.assertIsNone(data["stage_cycle_times"]["video"]["value"])
        self.assertEqual(data["measurements"]["documented_attempt_credits"]["value"], 14)
        self.assertEqual(data["measurements"]["documented_manual_minutes"]["value"], 6)
        self.assertEqual(photo_metrics.collect_metrics(self.root, chart=2)
                         ["measurements"]["first_pass_yield"]["value"], 0.0)
        self.assertIsNone(data["measurements"]["credits_per_approved_video"]["value"])

    def test_invalid_annotations_are_skipped_with_warnings(self):
        self._notes("""# QA
<!-- 5bx-metric id=29A chart=3 exercise=4 stage=still trial=1 quality=pass start=2026-11-26 end=2026-11-27 -->
<!-- 5bx-metric id=29B chart=3 exercise=4 stage=still trial=2 quality=pass credits=-6 -->
<!-- 5bx-metric id=29C chart=3 exercise=4 stage=still trial=3 quality=pass manual_minutes=4 start=2026-11-27T10:00:00Z end=2026-11-26T10:00:00Z -->
<!-- 5bx-metric id=29D chart=3 exercise=4 stage=still trial=4 quality=hold -->
<!-- 5bx-metric id=29D chart=3 exercise=4 stage=still trial=4 quality=hold -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=3)
        self.assertEqual(data["instrumentation"]["annotated_attempts"], 1)
        self.assertIsNone(data["measurements"]["first_pass_yield"]["value"])
        self.assertEqual(len(data["warnings"]), 4)
        self.assertIn("duplicate", data["warnings"][-1])

    def test_ambiguous_first_attempt_numbers_cannot_inflate_first_pass_yield(self):
        self._notes("""# QA
<!-- 5bx-metric id=19A chart=1 exercise=5 stage=still trial=1 quality=fail -->
<!-- 5bx-metric id=19B chart=1 exercise=5 stage=still trial=1 quality=pass -->
<!-- 5bx-metric id=19C chart=1 exercise=5 stage=still trial=2 quality=pass -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertIsNone(data["measurements"]["first_pass_yield"]["value"])
        self.assertEqual(data["measurements"]["repeat_attempt_share"]["sample_size"], 1)
        self.assertTrue(any("ambiguous attempt" in warning for warning in data["warnings"]))

    def test_cli_writes_only_the_requested_json_with_nulls(self):
        target = self.root / "output" / "qa-metrics.json"
        subprocess.run([sys.executable, str(REPO_ROOT / "sprites/kit/photo_metrics.py"),
                        "--repo-root", str(self.root), "--chart", "2", "--out", str(target)],
                       check=True, capture_output=True, text=True)
        content = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(content["scope"]["charts"], [2])
        self.assertEqual(content["indexed_outputs"]["numbered_review_entries"], 1)
        self.assertIsNone(content["measurements"]["first_pass_yield"]["value"])
        self.assertEqual(list((self.root / "output").iterdir()), [target])


if __name__ == "__main__":
    unittest.main()
