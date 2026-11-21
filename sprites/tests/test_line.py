"""Pure production-line checks; no image assets or nonstandard packages needed."""

import hashlib
import json
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

    def release(self, chart=None):
        return line.release_readiness(self.report(), self.registry, self.library,
                                      self.sheets, chart=chart)

    def prepare_approved_art(self):
        for entry in self.library["entries"]:
            data = (entry["strip"] + " approved image").encode("utf-8")
            (self.sheets / (entry["strip"] + ".png")).write_bytes(data)
            entry["measured"] = {"sha": hashlib.sha1(data).hexdigest()[:12]}
            entry["grades"] = {"form": 5}

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

    def test_missing_chart_backdrop_is_reported_without_blocking(self):
        theme = {"backdrop": {"style": "forest"},
                 "chart_looks": {"1": {"backdrop": {"style": "image", "image": "assets/backgrounds/gym.png"}}}}
        sprites = self.sheets / "sprites"
        self.assertEqual(line.missing_backdrop_images(theme, sprites, [1, 2]),
                         {1: "assets/backgrounds/gym.png"})
        image = sprites / "assets" / "backgrounds" / "gym.png"
        image.parent.mkdir(parents=True)
        image.write_bytes(b"existing art")
        self.assertEqual(line.missing_backdrop_images(theme, sprites, [1, 2]), {})

    def test_missing_global_backdrop_picture_is_checked_for_each_chart(self):
        theme = {"backdrop": {"style": "image", "image": "assets/backgrounds/default.png"},
                 "chart_looks": {"1": {"backdrop": {"style": "forest"}}}}
        self.assertEqual(line.missing_backdrop_images(theme, self.sheets, [1, 2]),
                         {2: "assets/backgrounds/default.png"})

    def test_restore_sources_limit_to_selected_slot_and_active_props(self):
        theme = {"backdrop": {"style": "forest"},
                 "chart_looks": {"1": {"backdrop": {"style": "image", "image": "assets/room.png"}}},
                 "hud": {"font": "assets/fonts/title.ttf"}}
        scene = {"props": [{"id": "bottle", "kind": "image", "enabled": True,
                            "slots": ["ex4"], "file": "assets/props/bottle.png"},
                           {"id": "unused", "kind": "image", "enabled": False,
                            "file": "assets/props/unused.png"}]}
        paths, issues = line.required_render_files(self.registry, theme, scene, 1, ["ex4"])
        self.assertEqual(issues, [])
        self.assertEqual(paths, {"sheets/ex4.png", "assets/room.png",
                                 "assets/fonts/title.ttf", "assets/props/bottle.png"})

    def test_archive_restore_plan_finds_exact_zip_and_unindexed_work(self):
        root = self.sheets / "repo"
        sprites = root / "sprites"
        (sprites / "config").mkdir(parents=True)
        (root / "data").mkdir(parents=True)
        theme = {"backdrop": {"style": "image", "image": "assets/gym.png"}, "hud": {}}
        archive_index = {"archives": [
            {"file_name": "source.zip", "drive_id": "source-id", "files": ["sheets/ex4.png"]},
            {"file_name": "background.zip", "drive_id": "background-id", "files": ["assets/gym.png"]},
        ]}
        for path, data in ((sprites / "config" / "strips.json", self.registry),
                           (sprites / "config" / "theme.json", theme),
                           (sprites / "config" / "scene.json", {"props": []}),
                           (sprites / "config" / "art-archive-index.json", archive_index),
                           (root / "data" / "5bx-charts.json", {"charts": [{"id": 1}]})):
            path.write_text(json.dumps(data))
        report = line.archive_restore_plan(root, 1, ["ex4"])
        self.assertEqual(report["issues"], [])
        self.assertEqual(report["unknown"], [])
        self.assertEqual(set(report["archives"]), {"source.zip", "background.zip"})
        self.assertEqual((report["required"], report["present"]), (2, 0))
        archive_index["direct_files"] = [{"path": "sheets/ex4.png", "drive_id": "direct-source-id"}]
        (sprites / "config" / "art-archive-index.json").write_text(json.dumps(archive_index))
        report = line.archive_restore_plan(root, 1, ["ex4"])
        self.assertEqual(report["direct"], archive_index["direct_files"])
        self.assertEqual(set(report["archives"]), {"background.zip"})
        (sprites / "sheets").mkdir()
        (sprites / "sheets" / "ex4.png").write_bytes(b"restored")
        self.assertEqual(set(line.archive_restore_plan(root, 1, ["ex4"])["archives"]),
                         {"background.zip"})
        self.registry["strips"]["ex4"]["file"] = "new-unarchived.png"
        (sprites / "config" / "strips.json").write_text(json.dumps(self.registry))
        self.assertEqual(line.archive_restore_plan(root, 1, ["ex4"])["unknown"],
                         ["sheets/new-unarchived.png"])

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

    def test_release_requires_restored_source_and_explicit_form_grade(self):
        blockers = self.release()[0]["blockers"]
        self.assertTrue(any("not restored" in b for b in blockers))
        self.assertTrue(any("passing form grade" in b for b in blockers))
        self.prepare_approved_art()
        self.assertEqual(self.release()[0]["blockers"], [])

    def test_release_rejects_stale_selected_sheet_even_if_chosen(self):
        self.prepare_approved_art()
        (self.sheets / "ex1.png").write_bytes(b"an older unapproved take")
        self.assertTrue(any("differs from chosen asset" in b for b in self.release()[0]["blockers"]))

    def test_release_holds_missing_mapping_and_missing_chosen(self):
        self.prepare_approved_art()
        del self.registry["charts"]["1"]["jump"]
        self.library["entries"][0]["verdict"] = "candidate"
        blockers = self.release()[0]["blockers"]
        self.assertTrue(any("jump: exercise not mapped" in b for b in blockers))
        self.assertTrue(any("expected one chosen asset" in b for b in blockers))

    def test_release_requires_positive_named_human_form_review(self):
        self.prepare_approved_art()
        self.library["entries"][0]["graded_by"] = ""
        self.library["entries"][1]["grades"]["form"] = 3
        blockers = self.release()[0]["blockers"]
        self.assertTrue(any("lacks a named human" in b for b in blockers))
        self.assertTrue(any("passing form grade" in b for b in blockers))

    def test_release_supports_chart_selection_and_unknown_chart(self):
        self.prepare_approved_art()
        self.assertEqual([c["chart"] for c in self.release(chart=1)], [1])
        self.assertTrue(self.release(chart=7)[0]["blockers"])


if __name__ == "__main__":
    unittest.main()
