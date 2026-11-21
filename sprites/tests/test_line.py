"""Pure production-line checks; no image assets or nonstandard packages needed."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import line


def sample():
    plan = {"charts": [{"id": 1}]}
    registry = {
        "strips": {slot: {"poses": 3, "file": slot + ".png", "cycle": [1, 2, 3]} for slot in line.SLOTS},
        "charts": {"1": {slot: slot for slot in line.SLOTS}},
    }
    prompts = {"strips": {slot: {"poses": ["start", "middle", "end"]} for slot in line.SLOTS}}
    library = {"entries": [{"id": slot + "-01", "strip": slot, "verdict": "chosen",
                            "expert_reviewed": True, "graded_by": "Charles"} for slot in line.SLOTS]}
    return plan, registry, prompts, library


class ProductionLineTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.sheets = Path(self.temp.name)
        self.plan, self.registry, self.prompts, self.library = sample()

    def report(self):
        return line.analyze(self.plan, self.registry, self.prompts, self.library, self.sheets)

    def test_valid_registry_needs_no_art_to_pass_structure(self):
        report = self.report()
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["charts"][0]["chosen"], 6)
        self.assertEqual(report["charts"][0]["needs_review"], [])
        self.assertEqual(len(report["charts"][0]["absent_art"]), 6)

    def test_missing_work_is_warning_not_error(self):
        del self.registry["charts"]["1"]["jump"]
        report = self.report()
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["charts"][0]["missing"], ["jump"])

    def test_unknown_registered_strip_blocks_check(self):
        self.registry["charts"]["1"]["jump"] = "not-a-strip"
        self.assertTrue(any("unknown strip" in x for x in self.report()["errors"]))

    def test_bad_cycle_blocks_check(self):
        self.registry["strips"]["jump"]["cycle"] = [1, 4]
        self.assertTrue(any("invalid cycle pose" in x for x in self.report()["errors"]))

    def test_mirrored_pose_needs_declaration(self):
        self.registry["strips"]["jump"]["cycle"] = [1, "2m", 3]
        self.assertTrue(any("not declared" in x for x in self.report()["errors"]))
        self.registry["strips"]["jump"]["mirror"] = [2]
        self.assertEqual(self.report()["errors"], [])

    def test_extra_returned_pose_is_flagged_without_blocking(self):
        self.registry["strips"]["jump"]["poses"] = 4
        report = self.report()
        self.assertEqual(report["errors"], [])
        self.assertTrue(any("prompt describes 3 poses" in w for w in report["warnings"]))

    def test_ai_grading_does_not_count_as_human_form_review(self):
        entry = self.library["entries"][0]
        entry.update(expert_reviewed=False, graded_by="claude")
        report = self.report()
        self.assertIn(entry["strip"], report["charts"][0]["needs_review"])
        entry["form_reviewed_by"] = "Charles"
        self.assertNotIn(entry["strip"], self.report()["charts"][0]["needs_review"])

    def test_duplicate_asset_identifiers_are_errors(self):
        self.library["entries"][1]["id"] = self.library["entries"][0]["id"]
        self.assertTrue(any("duplicate library asset ID" in e for e in self.report()["errors"]))


if __name__ == "__main__":
    unittest.main()
