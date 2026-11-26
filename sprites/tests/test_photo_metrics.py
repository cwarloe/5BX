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

    def test_different_quality_gates_never_create_a_misleading_single_yield(self):
        self._notes("""# QA
<!-- 5bx-metric id=19A chart=1 exercise=5 stage=still gate=technical trial=1 quality=pass provider=Google_Flow model=Omni -->
<!-- 5bx-metric id=19B chart=1 exercise=5 stage=video gate=motion trial=1 quality=fail provider=Google_Flow model=Omni defect_code=LIMB_ID defect_id=C1-E5-switch -->
<!-- 5bx-metric id=19C chart=1 exercise=5 stage=video gate=motion trial=2 quality=pass provider=Google_Flow reviewer=independent-qa -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertIsNone(data["measurements"]["first_pass_yield"]["value"])
        self.assertEqual(data["gate_breakdown"]["still/technical"]["first_pass_yield"]["value"], 1)
        self.assertEqual(data["gate_breakdown"]["video/motion"]["first_pass_yield"]["value"], 0)
        self.assertEqual(data["provider_breakdown"]["Google_Flow"]["first_pass_yield_by_gate"]
                         ["video/motion"]["sample_size"], 1)

    def test_credit_units_do_not_mix_across_providers_and_dollars_stay_separate(self):
        self._notes("""# QA
<!-- 5bx-metric id=19A chart=1 exercise=5 stage=video trial=1 quality=fail credits=18 provider=Google_Flow model=Omni cost_usd=0 -->
<!-- 5bx-metric id=19B chart=1 exercise=5 stage=video trial=2 quality=pass credits=2 provider=Grok_Imagine cost_usd=0.50 manual_minutes=0 -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertIsNone(data["measurements"]["documented_attempt_credits"]["value"])
        self.assertEqual(data["measurements"]["documented_attempt_credits"]["sample_size"], 2)
        self.assertEqual(data["measurements"]["documented_attempt_cost_usd"]["value"], 0.5)
        self.assertEqual(data["provider_breakdown"]["Google_Flow"]["documented_credits"], 18)
        self.assertEqual(data["provider_breakdown"]["Grok_Imagine"]["documented_credits"], 2)
        self.assertEqual(data["measurements"]["documented_manual_minutes"]["value"], 0)
        self.assertEqual(data["instrumentation"]["with_cost_usd"], 2)

    def test_stable_defect_identity_counts_real_recurrence_not_generic_code(self):
        self._notes("""# QA
<!-- 5bx-metric id=19A chart=1 exercise=5 stage=video trial=1 quality=fail defect_code=LIMB_ID defect_id=C1-E5-switch -->
<!-- 5bx-metric id=19B chart=1 exercise=5 stage=video trial=2 quality=fail defect_code=LIMB_ID defect_id=C1-E5-switch -->
<!-- 5bx-metric id=19C chart=1 exercise=5 stage=video trial=3 quality=fail defect_code=LIMB_ID defect_id=C1-E5-depth -->
<!-- 5bx-metric id=19D chart=1 exercise=5 stage=video trial=4 quality=fail defect_code=FORM -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        defects = data["defect_breakdown"]
        self.assertEqual(defects["observed_attempts_by_code"]["LIMB_ID"], 3)
        self.assertEqual(defects["distinct_stable_defect_ids"], 2)
        self.assertEqual(defects["repeated_stable_defects"], 1)
        self.assertEqual(data["instrumentation"]["with_defect_id"], 3)

    def test_invalid_review_or_duplicate_annotation_key_is_not_evidence(self):
        self._notes("""# QA
<!-- 5bx-metric id=19A chart=1 exercise=5 stage=video gate=motion trial=1 quality=pass -->
<!-- 5bx-metric id=19B chart=1 exercise=5 stage=video trial=1 quality=fail provider=X provider=Google -->
<!-- 5bx-metric id=19C chart=1 exercise=5 stage=video trial=1 quality=fail defect_code=MADE_UP -->
<!-- 5bx-metric id=19D chart=1 exercise=6 stage=video trial=1 quality=fail -->
<!-- 5bx-metric id=19E chart=1 exercise=5 stage=video gate=motion trial=1 quality=pass reviewer=independent-qa credits=unknown -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertEqual(data["instrumentation"]["annotated_attempts"], 1)
        self.assertEqual(len(data["warnings"]), 4)
        self.assertEqual(data["gate_breakdown"]["video/motion"]["first_pass_yield"]["value"], 1)
        self.assertIsNone(data["measurements"]["documented_attempt_credits"]["value"])

    def test_nonfinite_large_cost_cannot_be_serialized_as_real_spend(self):
        huge_amount = "9" * 350
        self._notes(f"<!-- 5bx-metric id=19A chart=1 exercise=5 stage=video "
                    f"trial=1 quality=fail cost_usd={huge_amount} -->")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertEqual(data["instrumentation"]["annotated_attempts"], 0)
        self.assertEqual(len(data["warnings"]), 1)
        json.dumps(data, allow_nan=False)

    def test_unknown_optional_values_do_not_count_as_present_or_as_reviewers(self):
        self._notes("""# QA
<!-- 5bx-metric id=19A chart=1 exercise=5 stage=video gate=motion trial=1 quality=pass reviewer=unknown -->
<!-- 5bx-metric id=19B chart=1 exercise=5 stage=still trial=1 quality=fail provider=unknown model=unknown defect_code=unknown defect_id=unknown credits=unknown -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertEqual(data["instrumentation"]["annotated_attempts"], 1)
        self.assertEqual(data["instrumentation"]["with_provider"], 0)
        self.assertEqual(data["instrumentation"]["with_model"], 0)
        self.assertEqual(data["instrumentation"]["with_defect_id"], 0)
        self.assertEqual(data["defect_breakdown"]["distinct_stable_defect_ids"], 0)
        self.assertEqual(len(data["warnings"]), 1)

    def test_multiple_qa_gates_on_same_attempt_do_not_double_bill(self):
        self._notes("""# QA
<!-- 5bx-metric id=C1-E5-V8 chart=1 exercise=5 stage=video gate=technical trial=1 quality=pass provider=Google_Flow credits=18 cost_usd=0 -->
<!-- 5bx-metric id=C1-E5-V8 chart=1 exercise=5 stage=video gate=motion trial=1 quality=fail provider=Google_Flow credits=18 cost_usd=0 -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertEqual(data["instrumentation"]["annotated_attempts"], 2)
        self.assertEqual(data["instrumentation"]["with_cost"], 1)
        self.assertEqual(data["measurements"]["documented_attempt_credits"]["value"], 18)
        self.assertEqual(data["measurements"]["documented_attempt_cost_usd"]["value"], 0)
        self.assertEqual(len(data["warnings"]), 2)

    def test_conflicting_costs_for_same_attempt_are_excluded_not_arbitrated(self):
        self._notes("""# QA
<!-- 5bx-metric id=C1-E5-V8 chart=1 exercise=5 stage=video gate=technical trial=1 quality=pass provider=Google_Flow credits=18 -->
<!-- 5bx-metric id=C1-E5-V8 chart=1 exercise=5 stage=video gate=motion trial=1 quality=fail provider=Google_Flow credits=20 -->
""")
        data = photo_metrics.collect_metrics(self.root, chart=1)
        self.assertEqual(data["instrumentation"]["with_cost"], 0)
        self.assertIsNone(data["measurements"]["documented_attempt_credits"]["value"])
        self.assertTrue(any("conflicting credits" in warning for warning in data["warnings"]))


if __name__ == "__main__":
    unittest.main()
