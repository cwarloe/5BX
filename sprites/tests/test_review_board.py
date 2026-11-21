"""Review grid is derived from the canonical ledger and does not approve art."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import review_board


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class BoardTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        sprites = self.root / "sprites"
        self.data = {"charts": [{"id": 2, "exercises": [
            {"n": n, "name": f"Exercise {n}", "start": "standing", "movement": "move"}
            for n in range(1, 6)]}], "levelOrder": ["D-", "A+"]}
        write_json(self.root / "data/5bx-charts.json", self.data)
        names = ["toe", "sit", "back", "push", "run", "jump"]
        self.registry = {"charts": {"2": dict(zip(review_board.line.SLOTS, names))},
                         "strips": {n: {"file": n + ".png", "poses": 2, "cycle": [1, 2]} for n in names}}
        write_json(sprites / "config/strips.json", self.registry)
        write_json(sprites / "config/character.json", {"name": "boy"})
        self.entries = [{"id": f"asset-{n}", "strip": n, "file": f"sheets/{n}.png",
                         "verdict": "chosen", "grades": {}, "expert_reviewed": False,
                         "measured": {"sha": "badbadbadbad"}} for n in names]
        self.entries[4]["id"] = "chart1-run-shared"  # no chart-local assumption
        write_json(sprites / "library/index.json", {"entries": self.entries})
        write_json(sprites / "config/art-archive-index.json", {"direct_files": [
            {"path": f"sheets/{n}.png", "drive_id": "drive-" + n} for n in names]})

    def test_missing_art_is_linked_not_marked_checked_or_approved(self):
        items = review_board.review_items(self.root, 2)
        self.assertEqual(len(items), 6)
        self.assertEqual(items[4]["selected"]["id"], "chart1-run-shared")
        self.assertEqual(items[4]["drive_id"], "drive-run")
        self.assertTrue(all(i["technical"]["status"] == "NOT_RUN" for i in items))
        self.assertTrue(all(not i["human_review"] for i in items))
        html = review_board.render_html(2, items, self.data["levelOrder"])
        self.assertIn("Chart 2", html)
        self.assertIn("drive.google.com/file/d/drive-run/view", html)
        self.assertIn("Not restored locally", html)
        self.assertIn("D-, A+", html)

    def test_hash_mismatch_keeps_review_on_hold(self):
        image = self.root / "sprites/sheets/push.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b"a deliberately different source")
        items = review_board.review_items(self.root, 2)
        push = next(i for i in items if i["slot"] == "ex4")
        self.assertEqual(push["hash_state"], "MISMATCH")
        self.assertIn("Source differs from chosen version", push["blockers"])

    def test_hash_and_named_form_review_come_from_existing_library(self):
        image = self.root / "sprites/sheets/push.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b"chosen")
        self.entries[3]["measured"]["sha"] = hashlib.sha1(b"chosen").hexdigest()[:12]
        self.entries[3]["expert_reviewed"] = True
        self.entries[3]["graded_by"] = "Charles"
        self.entries[3]["grades"] = {"form": 5}
        write_json(self.root / "sprites/library/index.json", {"entries": self.entries})
        push = next(i for i in review_board.review_items(self.root, 2) if i["slot"] == "ex4")
        self.assertTrue(push["human_review"])
        self.assertEqual(push["hash_state"], "MATCH")

    def test_missing_selected_asset_is_not_silently_substituted(self):
        self.entries[2]["verdict"] = "candidate"
        write_json(self.root / "sprites/library/index.json", {"entries": self.entries})
        back = review_board.review_items(self.root, 2)[2]
        self.assertIsNone(back["selected"])
        self.assertIn("Expected one chosen image; found 0", back["blockers"])


if __name__ == "__main__":
    unittest.main()
