"""Fail-closed tests for agent-complete versus owner-accepted video handoff."""

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import photo_traveler, photo_workflow


H = "a" * 64
I = "b" * 64
URL = "https://drive.google.com/file/d/test-video-one/view"


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.batch = self.root / "sprites/docs/photo_batches/2026-11-26"
        self.batch.mkdir(parents=True)
        self.spec = self.root / "photo_motion/specs/chart1-scissor.json"
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text(json.dumps({"chart": 1, "exercise": 5, "name": "Scissors"}))
        self.inspection = self.root / "photo_motion/diagnostics/scan.md"
        self.inspection.parent.mkdir(parents=True)
        self.inspection.write_text("Inspection results; owner form approval not inferred.")
        (self.batch / "MOBILE_REVIEW_INDEX.md").write_text("Scissor video: " + URL)

    def record(self, data, name="scissor-qa.md"):
        path = self.batch / name
        path.write_text("# QA evidence\n\n<!-- 5bx-production\n" +
                        json.dumps(data, indent=2) + "\n-->\n", encoding="utf-8")

    def ready(self):
        checks = {k: {"verdict": "PASS", "evidence": "QA note confirms observed motion"}
                  for k in photo_workflow.GATES}
        checks["form"]["reviewer"] = "independent-form-agent"
        checks["motion"]["reviewer"] = "independent-motion-agent"
        return {"schema_version": 1, "chart": 1, "exercise": 5,
                "revision": "scissor-v2", "status": "READY_FOR_REVIEW", "agent": "producer-agent",
                "contract": "photo_motion/specs/chart1-scissor.json",
                "video": {"url": URL, "sha256": H, "media_type": "video/mp4"},
                "inspection": {"video_sha256": H, "report_sha256": I,
                               "evidence": "photo_motion/diagnostics/scan.md"},
                "checks": checks,
                "review": {"summary": "One complete motion cycle inspected",
                           "recommendation": "Approve only if the leg ownership looks natural",
                           "question": "Do you accept this exact video for use?"},
                "owner_decision": None}

    def test_empty_record_does_not_fake_idle_work_or_ready_video(self):
        result = photo_workflow.collect(self.root)
        self.assertEqual(result["ready_for_review"], [])
        self.assertEqual(result["active_wip"]["declared"], 0)
        self.assertFalse(result["active_wip"]["complete"])
        self.assertEqual(len(result["unregistered_specs"]), 1)

    def test_ready_video_is_owner_queue_not_active_wip_or_done(self):
        self.record(self.ready())
        result = photo_workflow.collect(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["active_wip"]["declared"], 0)
        self.assertEqual(len(result["ready_for_review"]), 1)
        self.assertEqual(result["done"], [])
        self.assertEqual(result["ready_for_review"][0]["video_sha256"], H)
        html = photo_traveler._production_queue({"production": result}, chart=1)
        self.assertIn("Play exact video", html)
        self.assertIn("READY FOR REVIEW · NOT APPROVED", html)

    def test_owner_question_is_escaped_in_viewer(self):
        item = self.ready()
        item["review"]["question"] = "<script>alert('false approval')</script>"
        self.record(item)
        html = photo_traveler._production_queue(
            {"production": photo_workflow.collect(self.root)}, chart=1)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_unverified_or_unindexed_video_never_reaches_owner_queue(self):
        item = self.ready()
        item["checks"]["loop"] = {"verdict": "UNKNOWN", "evidence": "unclear seam"}
        self.record(item)
        result = photo_workflow.collect(self.root)
        self.assertFalse(result["ready_for_review"])
        self.assertTrue(any("loop gate" in x for x in result["errors"]))
        (self.batch / "MOBILE_REVIEW_INDEX.md").write_text("No output link yet")
        result = photo_workflow.collect(self.root)
        self.assertTrue(any("not registered" in x for x in result["errors"]))

    def test_no_fake_owner_done_from_agent_pass(self):
        item = self.ready()
        item["status"] = "DONE"
        self.record(item)
        result = photo_workflow.collect(self.root)
        self.assertEqual(result["done"], [])
        self.assertTrue(any("owner decision" in x for x in result["errors"]))

    def test_exact_owner_video_hash_is_required_for_done(self):
        item = self.ready()
        item["status"] = "DONE"
        item["owner_decision"] = {"reviewer": "cwarloe", "decision": "ACCEPT",
                                  "decided_at": "2026-11-26T12:00:00Z",
                                  "evidence_url": "https://github.com/cwarloe/5BX/issues/42#issuecomment-1",
                                  "video_sha256": "c" * 64}
        self.record(item)
        result = photo_workflow.collect(self.root)
        self.assertFalse(result["done"])
        self.assertTrue(any("exact video hash" in x for x in result["errors"]))
        item["owner_decision"]["video_sha256"] = H
        self.record(item)
        result = photo_workflow.collect(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["done"]), 1)

    def test_blocked_escalation_only_if_owner_needed(self):
        item = {"schema_version": 1, "chart": 1, "exercise": 5,
                "revision": "scissor-v0", "status": "BLOCKED", "agent": "producer",
                "blocker": {"reason": "Reference disagreement", "question": "Which range?",
                            "recommendation": "Use physical source", "owner_needed": False}}
        self.record(item)
        result = photo_workflow.collect(self.root)
        self.assertEqual(len(result["owner_blockers"]), 0)
        self.assertEqual(result["active_wip"]["declared"], 1)
        item["blocker"]["owner_needed"] = True
        self.record(item)
        self.assertEqual(len(photo_workflow.collect(self.root)["owner_blockers"]), 1)

    def test_more_than_two_active_exercises_fails_closed(self):
        self.record({"schema_version": 1, "chart": 1, "exercise": 5,
                     "revision": "a", "status": "PRODUCING", "agent": "one"})
        for exercise in (3, 4):
            self.record({"schema_version": 1, "chart": 1, "exercise": exercise,
                         "revision": "a", "status": "QA", "agent": "two"}, f"qa-{exercise}.md")
        result = photo_workflow.collect(self.root)
        self.assertEqual(result["active_wip"]["declared"], 3)
        self.assertIn("WIP exceeded", " ".join(result["errors"]))

    def test_duplicate_revision_handoffs_error(self):
        item = self.ready()
        self.record(item)
        self.record(deepcopy(item), "duplicate.md")
        result = photo_workflow.collect(self.root)
        self.assertTrue(any("duplicate chart/exercise" in x for x in result["errors"]))
        self.assertEqual(len(result["ready_for_review"]), 0)

    def test_malformed_markers_are_not_silently_ignored(self):
        (self.batch / "bad.md").write_text(
            '<!-- 5bx-production\n{"status": "READY_FOR_REVIEW",}\n-->\n', encoding="utf-8")
        self.assertTrue(any("invalid production marker" in x for x in
                            photo_workflow.collect(self.root)["errors"]))


if __name__ == "__main__":
    unittest.main()
