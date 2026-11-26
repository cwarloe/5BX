"""Output-first photo traveler is an honest, read-only view of existing QA notes."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import photo_traveler, review_board


class PhotoTravelerTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        folder = self.root / photo_traveler.PHOTO_DIR
        folder.mkdir(parents=True)
        (folder / photo_traveler.INDEX).write_text("""# mobile index
## Most recent round 2 refinements
- [**Chart 3 — elbow HOLD**](https://drive.google.com/file/d/abc_123/view): unsafe elbows.
1. [Chart 1 overview](https://drive.google.com/file/d/c1/view).
2. [Chart 2 overview](https://drive.google.com/file/d/c2/view).
3. [Chart 3 overview](https://drive.google.com/file/d/c3/view).
4. [Chart 4 overview](https://drive.google.com/file/d/c4/view).
5. [Chart 5 overview](https://drive.google.com/file/d/c5/view).
6. [Chart 6 overview](https://drive.google.com/file/d/c6/view).
## Full resolution references
- Chart 3 new 29H: [full-resolution frame](https://drive.google.com/file/d/photo29h/view) — identity HOLD.
""", encoding="utf-8")
        source = """# Chart 3
## Mobile gallery
- [29E — forehead-pike ON HOLD](https://drive.google.com/file/d/photo29e/view). User caught elbows.
- [29C — standalone diagnostic, ELBOW REVIEW REQUIRED](https://drive.google.com/file/d/photo29c/view). Not final.
## Exact prompts
- [29F — not a production output](https://drive.google.com/file/d/do_not_list/view)
"""
        (folder / photo_traveler.INVENTORIES[3]).write_text(source, encoding="utf-8")
        (folder / photo_traveler.INVENTORIES[1]).write_text("""# Chart 1
## Direct mobile links
- [15 — contact sheet](https://drive.google.com/file/d/card15/view), [15A — first high-resolution start](https://drive.google.com/file/d/full15a/view), [15B — preferred full-resolution start](https://drive.google.com/file/d/full15b/view).
""", encoding="utf-8")

    def test_only_current_review_outputs_are_listed(self):
        data = photo_traveler.gallery_data(self.root, chart=3)
        self.assertEqual(len(data["overviews"]), 1)
        self.assertEqual([x["test"] for x in data["items"]], ["29E", "29C"])
        self.assertEqual(data["items"][0]["state"], "HOLD")
        self.assertEqual(data["latest"][0]["state"], "HOLD")
        self.assertEqual([x["state"] for x in data["high_res"]], ["REVIEW ONLY", "HOLD"])
        self.assertEqual(data["high_res"][1]["title"], "29H — full-resolution frame")
        html = photo_traveler.render_gallery(data, chart=3)
        self.assertIn("thumbnail?id=photo29e", html)
        self.assertIn("Read prompts and QA record", html)
        self.assertNotIn("do_not_list", html)
        self.assertIn("No human-approved exercise forms", html)
        self.assertIn("Individual higher-resolution photo stills", html)
        self.assertIn("thumbnail?id=photo29h", html)
        self.assertIn("Open full-resolution still", html)

    def test_all_named_full_resolution_links_are_at_bottom_without_new_ledger(self):
        data = photo_traveler.gallery_data(self.root, chart=1)
        self.assertEqual(len(data["items"]), 1)  # contact card stays in the main gallery
        self.assertEqual([x["title"] for x in data["high_res"]], [
            "15A — first high-resolution start", "15B — preferred full-resolution start"])
        self.assertTrue(all(x["source"] == photo_traveler.INVENTORIES[1]
                            for x in data["high_res"]))
        html = photo_traveler.render_gallery(data, chart=1)
        self.assertLess(html.index('id="chart-1"'), html.index('id="high-resolution-stills"'))
        self.assertIn("Source / QA notes", html)
        self.assertNotIn("photo29h", html)  # chart filter also applies to high-res links

    def test_old_gallery_remains_supported(self):
        # A missing chart record is never fabricated as a valid/approved image.
        with self.assertRaises(FileNotFoundError):
            photo_traveler.gallery_data(self.root, chart=2)
        # The original legacy implementation remains available through the CLI.
        self.assertIsNotNone(review_board.review_items)

    def test_thumbnail_urls_are_not_guessed_for_other_sites(self):
        self.assertIsNone(photo_traveler._image_url("https://flow.google.com/project/clip"))
        self.assertIsNone(photo_traveler._image_url("https://drive.google.com/file/d/invalid/edit"))
        self.assertEqual(photo_traveler._state("35 original REJECT"), "REJECT")
        self.assertEqual(photo_traveler._state("19 candidate"), "TEST ONLY")


if __name__ == "__main__":
    unittest.main()
