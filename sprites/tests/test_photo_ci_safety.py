"""Protect the CI quality gate from quietly losing photographic coverage.

These tests check wiring, not the safety or correctness of generated media.
The actual video must still pass independent form and motion review.
"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


class PhotographicQualityWorkflowTest(unittest.TestCase):
    def workflow(self, name):
        return (WORKFLOWS / name).read_text(encoding="utf-8")

    def test_photo_motion_changes_trigger_both_independent_quality_views(self):
        for filename in ("photographic-motion-ci.yml", "photo-traveler.yml"):
            with self.subTest(filename=filename):
                source = self.workflow(filename)
                # New producer adapters, canaries and motion regression cases
                # must not bypass the CI gate merely because they are new paths.
                self.assertIn("'photo_motion/**'", source)
                self.assertIn("'sprites/kit/photo_*.py'", source)
                self.assertIn("'sprites/tests/test_photo_*.py'", source)
                self.assertIn("'sprites/docs/PHOTOGRAPHIC_PRODUCTION_STANDARD_WORK.md'", source)
                self.assertIn("'AGENTS.md'", source)

    def test_handoffs_fail_closed_and_keep_auditable_artifacts(self):
        for filename in ("photographic-motion-ci.yml", "photo-traveler.yml"):
            with self.subTest(filename=filename):
                source = self.workflow(filename)
                self.assertIn("photo_workflow.py --repo-root . --check", source)
                self.assertIn("photo_defect_learning.py --repo-root . --all", source)
                self.assertIn("if: always()", source)
                self.assertIn("artifacts/owner-review-queue.json", source)
                self.assertIn("contents: read", source)
                self.assertIn("cancel-in-progress: true", source)

    def test_contracts_and_real_video_regressions_stay_in_ci(self):
        source = self.workflow("photographic-motion-ci.yml")
        self.assertIn("python3 -m photo_motion validate photo_motion/specs/*.json", source)
        self.assertIn("python3 -m unittest discover -s photo_motion/tests -v", source)
        self.assertIn("Cross-check photographic traveler and handoff contracts", source)
        traveler = self.workflow("photo-traveler.yml")
        self.assertIn("python3 -m unittest discover -s sprites/tests -p 'test_photo_*.py' -v", traveler)
        self.assertIn("artifacts/production-metrics.json", traveler)


if __name__ == "__main__":
    unittest.main()
