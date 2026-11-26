"""Quality learning checks never substitute for photo/video form approval."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import photo_defect_learning as learning


def example():
    return {
        "schema_version": 1,
        "defects": [{
            "id": "C1-E5-LIMB_ID-physical-exchange",
            "code": "LIMB_ID",
            "symptom": "Apparent same physical leg leads both endpoints",
            "first_seen_revision": "V1",
            "first_seen_evidence": "sprites/docs/photo_batches/example/QA.md",
            "risk": {"impact": "CRITICAL", "detection": "HUMAN_REVIEW",
                     "consequence": "Exercise movement would be demonstrated incorrectly",
                     "containment": "Hold the candidate; do not use it as source video"},
            "mechanism": {"confidence": "HYPOTHESIS",
                          "finding": "Screen-position wording loses anatomical ownership"},
            "corrections": [{"revision": "V2", "method": "PROMPT_ONLY",
                             "changed_variable": "Near/far depth phrase",
                             "outcome": "FAIL",
                             "evidence": "https://drive.google.com/file/d/example/view"}],
            "countermeasure": {"description": "Track named physical ankles in each phase",
                               "prevention_test": "Trace each colored ankle to the same hip",
                               "status": "PROPOSED"},
        }],
    }


def note(data):
    return "# Existing exercise QA\n\n<!-- 5bx-learning\n" + json.dumps(data, indent=2) + "\n-->\n"


class LearningTest(unittest.TestCase):
    def test_missing_annotation_is_backward_compatible(self):
        self.assertEqual(learning.validate_note("# Existing QA\n"), (0, []))

    def test_valid_proposed_countermeasure_is_not_form_approval(self):
        count, issues = learning.validate_note(note(example()))
        self.assertEqual(count, 1)
        self.assertEqual(issues, [])

    def test_malformed_and_multiple_comments_fail_closed(self):
        self.assertTrue(learning.validate_note("<!-- 5bx-learning\n{invalid\n-->")[1])
        self.assertTrue(learning.validate_note("<!-- 5bx-learning\n{}\n", "test")[1])
        self.assertTrue(learning.validate_note(note(example()) * 2)[1])

    def test_code_and_identity_cannot_silently_change(self):
        data = example()
        data["defects"][0]["code"] = "WRONG_LEG"
        data["defects"].append(deepcopy(data["defects"][0]))
        errors = learning.validate_note(note(data))[1]
        self.assertTrue(any("established 5BX defect code" in e for e in errors))
        self.assertTrue(any("duplicate defect identity" in e for e in errors))

    def test_two_unresolved_failed_corrections_require_escalation(self):
        data = example()
        data["defects"][0]["corrections"].append(
            {"revision": "V3", "method": "PROMPT_ONLY",
             "changed_variable": "Leg forward/back language", "outcome": "FAIL",
             "evidence": "https://drive.google.com/file/d/v3/view"})
        errors = learning.validate_note(note(data))[1]
        self.assertTrue(any("two failed corrections require" in e for e in errors))
        data["defects"][0]["escalation"] = {
            "reason": "Both prose retries failed",
            "alternative_method": "Use physically tagged ankle reference",
            "evidence": "sprites/docs/photo_batches/example/QA.md"}
        self.assertEqual(learning.validate_note(note(data))[1], [])
        data["defects"][0]["escalation"]["alternative_method"] = "PROMPT_ONLY"
        self.assertTrue(any("cannot be prompt-only retry" in e for e in
                            learning.validate_note(note(data))[1]))

    def test_different_defect_attempts_are_not_aggregated(self):
        data = example()
        second = deepcopy(data["defects"][0])
        second.update({"id": "C1-E5-HAND-wrist", "code": "HAND",
                       "symptom": "Wrong hand is visible", "corrections": []})
        data["defects"].append(second)
        self.assertEqual(learning.validate_note(note(data))[1], [])

    def test_confirmation_requires_independent_successful_verification(self):
        data = example()
        cm = data["defects"][0]["countermeasure"]
        cm["status"] = "CONFIRMED"
        cm["verification"] = {"result": "PASS",
                              "evidence": "sprites/docs/photo_batches/example/next-QA.md",
                              "independent_batch": "V2"}
        errors = learning.validate_note(note(data))[1]
        self.assertTrue(any("independent batch" in e for e in errors))
        cm["verification"]["independent_batch"] = "C2-exercise3-run1"
        self.assertEqual(learning.validate_note(note(data))[1], [])
        cm["verification"]["result"] = "FAIL"
        self.assertTrue(any("CONFIRMED requires a PASS" in e for e in
                            learning.validate_note(note(data))[1]))

    def test_evidenced_mechanism_needs_support(self):
        data = example()
        data["defects"][0]["mechanism"]["confidence"] = "EVIDENCED"
        self.assertTrue(any("mechanism.evidence" in e for e in
                            learning.validate_note(note(data))[1]))

    def test_cli_checks_in_place_notes_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note_dir = root / "sprites/docs/photo_batches/2026-11-26"
            note_dir.mkdir(parents=True)
            original = note(example())
            qa = note_dir / "EXISTING_QA.md"
            qa.write_text(original, encoding="utf-8")
            (note_dir / "OTHER.md").write_text("# No defect annotation", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = learning.main(["--repo-root", str(root), "--all"])
            self.assertEqual(result, 0)
            self.assertEqual(qa.read_text(encoding="utf-8"), original)
            summary = json.loads(stdout.getvalue())
            self.assertEqual(summary["notes_checked"], 2)
            self.assertEqual(summary["notes_with_learning"], 1)
            self.assertEqual(summary["defects"], 1)


if __name__ == "__main__":
    unittest.main()
