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

    def test_metrics_are_visible_without_inventing_a_first_pass_baseline(self):
        data = photo_traveler.with_metrics(
            photo_traveler.gallery_data(self.root, chart=1), self.root, chart=1)
        self.assertIsNone(data["metrics"]["measurements"]["first_pass_yield"]["value"])
        self.assertEqual(data["metrics"]["measurements"]["first_pass_yield"]["sample_size"], 0)
        rendered = photo_traveler.render_gallery(data, chart=1)
        self.assertIn('id="production-measurements"', rendered)
        self.assertIn("Not measured", rendered)
        self.assertIn("Recorded samples: 0", rendered)
        self.assertNotIn("100.0%", rendered)

    def test_old_gallery_remains_supported(self):
        # A missing chart record is never fabricated as a valid/approved image.
        with self.assertRaises(FileNotFoundError):
            photo_traveler.gallery_data(self.root, chart=2)
        # The original legacy implementation remains available through the CLI.
        self.assertIsNotNone(review_board.review_items)

    def test_latest_revision_supersedes_older_card_without_misclassifying_frames(self):
        folder = self.root / photo_traveler.PHOTO_DIR
        (folder / photo_traveler.INDEX).write_text("""# mobile index
## Latest test — 34K lifts the background elbow
- [34J vs 34K close mobile comparison](https://drive.google.com/file/d/comp34k/view) | [34K full-resolution four-frame card](https://drive.google.com/file/d/card34k/view). Review candidate, not approved; compare elbow heights.
## Latest test — 34J hides the far arm
- [34H vs 34J comparison](https://drive.google.com/file/d/comp34j/view) | [34J full-resolution four-frame card](https://drive.google.com/file/d/card34j/view). Review candidate only.
1. [Chart 1 overview](https://drive.google.com/file/d/c1/view).
2. [Chart 2 overview](https://drive.google.com/file/d/c2/view).
3. [Chart 3 overview](https://drive.google.com/file/d/c3/view).
4. [Chart 4 overview](https://drive.google.com/file/d/c4/view).
5. [Chart 5 overview](https://drive.google.com/file/d/c5/view).
6. [Chart 6 overview](https://drive.google.com/file/d/c6/view).
## What needs human eyes next
- **Scissor test 19:** [straight-arm card](https://drive.google.com/file/d/scissor19/view). Does the rear shoulder reach look appropriate?
- **Flow 20:** Watch alternating foot lifts, consistent outfit and loop seam.
""", encoding="utf-8")
        (folder / photo_traveler.INVENTORIES[4]).write_text("""# Chart 4
## Fast mobile review
- [34 — waist-high stationary run](https://drive.google.com/file/d/card34/view).
""", encoding="utf-8")
        (folder / photo_traveler.INVENTORIES[1]).write_text("""# Chart 1
## Direct mobile links
- [19 — scissor test](https://drive.google.com/file/d/scissor19/view).
- [20 — actual Flow video](https://flow.google.com/project/flow20).
""", encoding="utf-8")
        data = photo_traveler.gallery_data(self.root, chart=4)
        self.assertEqual(len(data["latest"]), 1)
        self.assertEqual(data["latest"][0]["revision"], "34K")
        self.assertEqual(data["latest"][0]["kind"], "contact card")
        self.assertEqual(data["latest"][0]["comparison"],
                         "https://drive.google.com/file/d/comp34k/view")
        self.assertEqual(data["high_res"], [])  # a full-res four-frame card is not a solo still
        self.assertEqual(len(data["review_queue"]), 1)
        self.assertEqual(data["review_queue"][0]["revision"], "34K")
        html = photo_traveler.render_gallery(data, chart=4)
        self.assertIn("Only these need human eyes", html)
        self.assertIn("card34k", html)
        self.assertNotIn("card34j", html)

        chart1 = photo_traveler.gallery_data(self.root, chart=1)
        self.assertEqual([x["revision"] for x in chart1["review_queue"]], ["19", "20"])
        self.assertEqual(chart1["review_queue"][1]["url"],
                         "https://flow.google.com/project/flow20")
        self.assertEqual(chart1["review_queue"][1]["kind"], "video")

    def test_thumbnail_urls_are_not_guessed_for_other_sites(self):
        self.assertIsNone(photo_traveler._image_url("https://flow.google.com/project/clip"))
        self.assertIsNone(photo_traveler._image_url("https://drive.google.com/file/d/invalid/edit"))
        self.assertEqual(photo_traveler._state("35 original REJECT"), "REJECT")
        self.assertEqual(photo_traveler._state("19 candidate"), "TEST ONLY")

    def test_flow_groups_variants_and_preserves_later_repair(self):
        folder = self.root / photo_traveler.PHOTO_DIR
        (folder / photo_traveler.INVENTORIES[3]).write_text("""## Mobile gallery
- [29C — old diagnostic](https://drive.google.com/file/d/p29c/view).
- [29E — form SAFETY HOLD](https://drive.google.com/file/d/p29e/view). Earlier assistant PASS revoked.
""", encoding="utf-8")
        (folder / photo_traveler.INVENTORIES[1]).write_text("""## Direct mobile links
- [17D — marker diagnostic](https://drive.google.com/file/d/p17d/view).
- [17 — cleaned leg raise candidate](https://drive.google.com/file/d/p17/view).
""", encoding="utf-8")
        chart3 = photo_traveler.gallery_data(self.root, chart=3)
        self.assertEqual([(r["work_id"], r["revision"], r["state"])
                          for r in chart3["flow"]], [("29", "29E", "HOLD")])
        chart1 = photo_traveler.gallery_data(self.root, chart=1)
        self.assertEqual([(r["work_id"], r["revision"])
                          for r in chart1["flow"]], [("17", "17")])

    def test_flow_status_counts_are_not_claimed_to_be_live_wip(self):
        standard = self.root / "sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md"
        standard.parent.mkdir(parents=True, exist_ok=True)
        standard.write_text("Keep **at most two release-validation exercises active** initially.",
                            encoding="utf-8")
        data = photo_traveler.gallery_data(self.root, chart=1)
        self.assertEqual(data["wip"]["limit"], 2)
        self.assertIsNone(data["wip"]["active"])
        html = photo_traveler.render_gallery(data, chart=1)
        self.assertIn("production-flow", html)
        self.assertIn("NOT active WIP", html)
        self.assertIn("unindexed drafts", html)
        self.assertIn("cannot be inferred", html)

    def test_more_than_three_human_requests_are_in_flow_not_inbox(self):
        folder = self.root / photo_traveler.PHOTO_DIR
        index = (folder / photo_traveler.INDEX).read_text(encoding="utf-8")
        index += """\n## What needs human eyes next
- **Test 15:** [toe touch](https://drive.google.com/file/d/p15/view). Is the reach right?
- **Test 16:** [sit-up](https://drive.google.com/file/d/p16/view). Is the lift too high?
- **Test 17:** [leg raise](https://drive.google.com/file/d/p17/view). Are the legs distinct?
- **Test 18:** [push-up](https://drive.google.com/file/d/p18/view). Are the elbows natural?
"""
        (folder / photo_traveler.INDEX).write_text(index, encoding="utf-8")
        (folder / photo_traveler.INVENTORIES[1]).write_text("""## Direct mobile links
- [15 — toe touch](https://drive.google.com/file/d/p15/view).
- [16 — sit-up](https://drive.google.com/file/d/p16/view).
- [17 — leg raise](https://drive.google.com/file/d/p17/view).
- [18 — push-up](https://drive.google.com/file/d/p18/view).
""", encoding="utf-8")
        data = photo_traveler.gallery_data(self.root, chart=1)
        self.assertEqual(len(data["review_queue"]), 3)
        self.assertEqual({r["work_id"] for r in data["flow"] if r["station"] == "Human review"},
                         {"15", "16", "17", "18"})


if __name__ == "__main__":
    unittest.main()
