"""Synthetic, unpaid tests for the production generation preflight."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from photo_motion import generation_preflight


SOURCE_SPEC = Path(__file__).resolve().parents[1] / "specs" / "chart1-toe-touch.json"


class GenerationPreflightTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fivebx-preflight-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.spec = self.root / "photo_motion" / "specs" / SOURCE_SPEC.name
        self.spec.parent.mkdir(parents=True)
        self.spec.write_bytes(SOURCE_SPEC.read_bytes())
        policy = self.root / "sprites/docs/PHOTOREALISTIC_AVATAR_DIRECTION_2026-11-25.md"
        policy.parent.mkdir(parents=True)
        policy.write_text("Photographic identity master is canonical.", encoding="utf-8")
        self.prompt = self.root / "private" / "submitted.txt"
        self.prompt.parent.mkdir(parents=True)
        self.prompt.write_text("Locked photo camera; natural toe touch; return to start.", encoding="utf-8")
        self.image = self.root / "private" / "start.png"
        Image.new("RGB", (1280, 720), "#334466").save(self.image)
        self.request = {
            "schema_version": 1,
            "attempt_key": "chart1-toe-touch-001",
            "exercise_id": "chart1-toe-touch",
            "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [{"role": "start-frame", "locator": "private://toe/start",
                              "local_path": str(self.image),
                              "sha256": hashlib.sha256(self.image.read_bytes()).hexdigest()}],
            "provider": "Google Flow",
            "model": "test-model",
            "settings": {"duration_seconds": 6, "aspect_ratio": "16:9", "seed": None},
            "estimated_credits": "5",
        }

    def evaluate(self, request=None, **kwargs):
        return generation_preflight.evaluate(request or self.request, repo_root=self.root,
                                             available_credits=kwargs.pop("available_credits", "10"),
                                             **kwargs)

    def test_pass_is_input_only_and_never_a_reservation_or_approval(self):
        result = self.evaluate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["motion_contract"], self.spec.relative_to(self.root).as_posix())
        self.assertEqual(result["submitted_prompt_sha256"], hashlib.sha256(self.prompt.read_bytes()).hexdigest())
        self.assertEqual(result["input_assets"][0]["verification"], "rehashed_from_local_bytes")
        self.assertEqual(result["generation_authorization"], "NOT_GRANTED_BY_PREFLIGHT")
        self.assertEqual(result["form_and_release_approval"], "NOT_EVALUATED")
        self.assertTrue(any("unregistered" in warning.lower() for warning in result["warnings"]))

    def test_bad_contract_and_mismatched_exercise_are_blocked(self):
        changed = copy.deepcopy(self.request)
        changed["exercise_id"] = "chart1-scissor-jump"
        result = self.evaluate(changed)
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("exercise_id does not match", " ".join(result["errors"]))

        spec = json.loads(self.spec.read_text())
        spec["phases"][-1]["pose_key"] = "different"
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        self.assertIn("loop is not closed", " ".join(self.evaluate()["errors"]))

    def test_settings_duration_and_aspect_ratio_cannot_drift(self):
        changed = copy.deepcopy(self.request)
        changed["settings"]["duration_seconds"] = 8
        self.assertIn("duration_seconds", " ".join(self.evaluate(changed)["errors"]))
        changed = copy.deepcopy(self.request)
        changed["settings"]["aspect_ratio"] = "9:16"
        self.assertIn("aspect_ratio", " ".join(self.evaluate(changed)["errors"]))

    def test_identity_policy_cannot_silently_revert_to_cartoon(self):
        spec = json.loads(self.spec.read_text())
        spec["identity_reference"] = "old cyan red cartoon sprite"
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        self.assertIn("photographic avatar", " ".join(self.evaluate()["errors"]))

    def test_contract_outside_repository_is_rejected(self):
        changed = copy.deepcopy(self.request)
        outside = self.root / "private" / "arbitrary-spec.json"
        outside.write_bytes(self.spec.read_bytes())
        changed["spec_path"] = str(outside)
        self.assertIn("photo_motion/specs", " ".join(self.evaluate(changed)["errors"]))

    def test_explicit_contract_hold_blocks_generation(self):
        spec = json.loads(self.spec.read_text())
        spec["status"] = "HOLD"
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        self.assertIn("on HOLD", " ".join(self.evaluate()["errors"]))

    def test_audio_policy_reports_missing_prevention_and_blocks_contradiction(self):
        spec = json.loads(self.spec.read_text())
        spec["audio_policy"] = "forbid"
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        self.assertEqual(self.evaluate()["status"], "PASS")
        self.assertIn("audio", " ".join(self.evaluate()["warnings"]))
        changed = copy.deepcopy(self.request)
        changed["settings"]["generate_audio"] = True
        self.assertIn("audio_policy", " ".join(self.evaluate(changed)["errors"]))

    def test_source_aspect_ratio_and_hash_mismatch_are_detected(self):
        Image.new("RGB", (720, 1280), "#334466").save(self.image)
        changed = copy.deepcopy(self.request)
        changed["input_assets"][0].pop("sha256")
        self.assertIn("aspect ratio", " ".join(self.evaluate(changed)["errors"]))
        self.assertIn("SHA mismatch", " ".join(self.evaluate()["errors"]))

    def test_missing_or_insufficient_budget_is_hold(self):
        self.assertIn("available_credits", " ".join(self.evaluate(available_credits=None)["errors"]))
        self.assertIn("insufficient", " ".join(self.evaluate(available_credits="4")["errors"]))

    def test_remote_only_and_corrupt_images_are_blocked(self):
        changed = copy.deepcopy(self.request)
        changed["input_assets"][0].pop("local_path")
        self.assertIn("local", " ".join(self.evaluate(changed)["errors"]))
        self.image.write_bytes(b"pretend PNG")
        changed = copy.deepcopy(self.request)
        changed["input_assets"][0].pop("sha256")
        self.assertIn("image", " ".join(self.evaluate(changed)["errors"]))

    def test_wip_full_does_not_start_third_exercise(self):
        qa = self.root / "sprites" / "docs" / "photo_batches" / "2026-11-26"
        qa.mkdir(parents=True)
        for exercise in (3, 4):
            obj = {"schema_version": 1, "chart": 1, "exercise": exercise,
                   "revision": f"active-{exercise}", "status": "PRODUCING", "agent": "test"}
            (qa / f"active-{exercise}.md").write_text("<!-- 5bx-production\n" + json.dumps(obj) + "\n-->\n")
        self.assertIn("WIP", " ".join(self.evaluate()["errors"]))

    def test_broken_queue_blocks_new_generation(self):
        qa = self.root / "sprites" / "docs" / "photo_batches" / "2026-11-26"
        qa.mkdir(parents=True)
        (qa / "broken.md").write_text("<!-- 5bx-production\n{invalid\n-->\n")
        self.assertIn("queue", " ".join(self.evaluate()["errors"]))


if __name__ == "__main__":
    unittest.main()
