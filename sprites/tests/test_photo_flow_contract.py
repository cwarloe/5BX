"""Adversarial, source-backed contracts for the photographic flow view.

The flow is a projection of the existing photographic QA documents, not a new
source of approval or a promise that one numbered output equals one exercise.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import photo_traveler


class FlowContracts(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.folder = self.root / photo_traveler.PHOTO_DIR
        self.folder.mkdir(parents=True)

    def write(self, index, chart_records):
        (self.folder / photo_traveler.INDEX).write_text(index, encoding="utf-8")
        for chart, contents in chart_records.items():
            (self.folder / photo_traveler.INVENTORIES[chart]).write_text(
                contents, encoding="utf-8"
            )

    def index(self, other=""):
        return (
            "# Mobile review\n"
            "1. [Chart 1 overview](https://drive.google.com/file/d/overview1/view).\n"
            "2. [Chart 2 overview](https://drive.google.com/file/d/overview2/view).\n"
            + other
        )

    @staticmethod
    def row(data, test_id):
        matches = [entry for entry in data["flow"] if entry["work_id"] == test_id]
        assert len(matches) == 1, f"Expected one flow row for {test_id}: {matches!r}"
        return matches[0]

    def test_optimistic_assistant_pass_does_not_create_human_approval(self):
        self.write(
            self.index(),
            {1: """## Direct mobile links
- [15 — excellent contact sheet](https://drive.google.com/file/d/p15/view). Assistant QA PASS and strong provisional, still needs Charles's form approval and video validation.
"""},
        )
        data = photo_traveler.gallery_data(self.root, chart=1)
        row = self.row(data, "15")
        self.assertNotEqual(row["state"], "APPROVED")
        self.assertNotEqual(row["station"], "Approved")
        self.assertIn(row["station"], {
            "Still / form QA", "Human review", "Video QC", "Hold / rework", "Unclassified"
        })
        self.assertEqual(row["source"], photo_traveler.INVENTORIES[1])
        self.assertEqual(row["url"], "https://drive.google.com/file/d/p15/view")
        html = photo_traveler.render_gallery(data, chart=1)
        self.assertIn("production", html.lower())
        self.assertIn("p15/view", html)
        self.assertNotIn('class="tag approved"', html)

    def test_explicit_hold_vetoes_positive_words_in_same_card(self):
        self.write(
            self.index(),
            {1: """## Direct mobile links
- [16 — candidate strongly positive but SAFETY HOLD](https://drive.google.com/file/d/p16/view). Assistant-level geometry PASS; elbow hyperextension makes it unsafe to animate.
"""},
        )
        row = self.row(photo_traveler.gallery_data(self.root, chart=1), "16")
        self.assertEqual(row["station"], "Hold / rework")
        self.assertEqual(row["state"], "HOLD")
        self.assertTrue(row["blocker"])

    def test_explicit_human_question_does_not_approve_form(self):
        self.write(
            self.index("""
## What needs human eyes next
- **Scissor test 19:** [clean scissor contact card](https://drive.google.com/file/d/p19/view). Does the rear shoulder position look historically correct?
"""),
            {1: """## Direct mobile links
- [19 — scissor candidate](https://drive.google.com/file/d/p19/view). Four-limb tracking appears consistent; historical form still unapproved.
"""},
        )
        row = self.row(photo_traveler.gallery_data(self.root, chart=1), "19")
        self.assertEqual(row["station"], "Human review")
        self.assertEqual(row["state"], "NEEDS EYES")
        self.assertNotEqual(row["state"], "APPROVED")
        self.assertTrue(row["next_action"])

    def test_real_video_without_frame_qa_is_video_qc_not_released(self):
        self.write(
            self.index("""
## What needs human eyes next
- **Flow 20:** Watch whether the alternating foot lifts are real; the loop seam and raw frames are still unverified.
"""),
            {1: """## Direct mobile links
- [20 — actual six-second Flow video](https://flow.google.com/project/clip20). First-frame conditional; complete motion, identity and loop cannot be independently verified.
"""},
        )
        row = self.row(photo_traveler.gallery_data(self.root, chart=1), "20")
        self.assertEqual(row["station"], "Video QC")
        self.assertNotEqual(row["state"], "APPROVED")
        self.assertIn("flow.google.com", row["url"])

    def test_chart_filter_excludes_other_chart_work_items(self):
        self.write(
            self.index(),
            {
                1: """## Direct mobile links
- [15 — toe touch candidate](https://drive.google.com/file/d/p15/view).
""",
                2: """## Mobile-first review
- [21 — back extension candidate](https://drive.google.com/file/d/p21/view).
""",
            },
        )
        chart_one = photo_traveler.gallery_data(self.root, chart=1)
        chart_two = photo_traveler.gallery_data(self.root, chart=2)
        self.assertEqual({x["chart"] for x in chart_one["flow"]}, {1})
        self.assertEqual({x["chart"] for x in chart_two["flow"]}, {2})
        self.assertEqual({x["work_id"] for x in chart_one["flow"]}, {"15"})
        self.assertEqual({x["work_id"] for x in chart_two["flow"]}, {"21"})
        self.assertNotIn("p21/view", photo_traveler.render_gallery(chart_one, chart=1))

    def test_flow_state_is_not_truncated_by_three_item_review_inbox(self):
        # The gallery intentionally limits the owner-facing exception *inbox*
        # to three questions. The production state for all four work families
        # must still be honest, even if one question is not featured above.
        self.write(
            self.index("""
## What needs human eyes next
- **Test 15:** [toe-touch candidate](https://drive.google.com/file/d/p15/view). Is the movement safe?
- **Test 16:** [sit-up candidate](https://drive.google.com/file/d/p16/view). Is the trunk range correct?
- **Test 17:** [leg-raise candidate](https://drive.google.com/file/d/p17/view). Does the near leg truly alternate?
- **Test 18:** [push-up candidate](https://drive.google.com/file/d/p18/view). Are shoulder positions natural?
"""),
            {1: """## Direct mobile links
- [15 — toe touch](https://drive.google.com/file/d/p15/view).
- [16 — sit-up](https://drive.google.com/file/d/p16/view).
- [17 — leg raise](https://drive.google.com/file/d/p17/view).
- [18 — push-up](https://drive.google.com/file/d/p18/view).
"""},
        )
        data = photo_traveler.gallery_data(self.root, chart=1)
        self.assertLessEqual(len(data["review_queue"]), 3)
        self.assertEqual({x["work_id"] for x in data["flow"] if x["station"] == "Human review"},
                         {"15", "16", "17", "18"})

    def test_latest_revision_wins_without_historical_reject_leakage(self):
        self.write(
            self.index("""
## Latest test — 18C repaired the old elbow
- [18C full-resolution four-frame card](https://drive.google.com/file/d/new18c/view). Review candidate, not approved; corrected hand support still needs human inspection.
## Latest test — 18B rejected predecessor
- [18B REJECT card](https://drive.google.com/file/d/old18b/view). Human rejected the old elbow.
"""),
            {1: """## Direct mobile links
- [18 — push-up candidate](https://drive.google.com/file/d/original18/view). Older conditional test.
"""},
        )
        data = photo_traveler.gallery_data(self.root, chart=1)
        row = self.row(data, "18")
        self.assertEqual(row["revision"], "18C")
        self.assertEqual(row["url"], "https://drive.google.com/file/d/new18c/view")
        self.assertNotEqual(row["state"], "APPROVED")
        self.assertNotEqual(row["state"], "REJECT")  # That verdict belongs to 18B.

    def test_flow_does_not_promote_unlisted_numbers_in_narrative(self):
        self.write(
            self.index(),
            {1: """## Direct mobile links
- [19 — scissor card](https://drive.google.com/file/d/p19/view). Changed after 22 attempts in 2026; prior 17A arm issue cited as history.
## Narrative only
- 18 historical source: [18 earlier file](https://drive.google.com/file/d/not_for_review/view).
"""},
        )
        work = {x["work_id"] for x in photo_traveler.gallery_data(self.root, chart=1)["flow"]}
        self.assertEqual(work, {"19"})

    def test_html_escapes_untrusted_record_text_and_url_attributes(self):
        self.write(
            self.index(),
            {1: """## Direct mobile links
- [15 — <script>alert('x')</script> image](https://drive.google.com/file/d/p15/view?tag=%22%20onmouseover=%22alert). Note <img src=x onerror=alert(1)>.
"""},
        )
        data = photo_traveler.gallery_data(self.root, chart=1)
        html = photo_traveler.render_gallery(data, chart=1)
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertNotIn('onmouseover="alert"', html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img", html)


if __name__ == "__main__":
    unittest.main()
