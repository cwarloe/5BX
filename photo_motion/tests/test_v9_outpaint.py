"""Only synthetic PNGs and a disposable ledger; no private photos or Flow calls."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photo_motion import experiments, preflight_v9_outpaint as v9


class V9OutpaintTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.sources = {}
        self.shas = {}
        for role, color in (("A", "red"), ("C", "blue")):
            path = self.root / f"source-{role}.png"
            Image.new("RGB", (16, 9), color).save(path)
            self.sources[role] = path
            self.shas[role] = hashlib.sha256(path.read_bytes()).hexdigest()
        for name, replacement in (("SOURCE_SHA256", self.shas),
                                  ("V7_PREPARED_SIZE", (16, 9))):
            p = patch.object(v9, name, replacement)
            p.start()
            self.addCleanup(p.stop)
        self.spec = self.root / "v9.json"
        self.spec.write_text(json.dumps(v9._expected_spec()))
        self.prompt = self.root / "exact-submitted-prompt.txt"
        self.prompt.write_bytes(b"Keep the same boy and full-body framing; extend background.\r\n")

    def request(self, pose="A"):
        source = self.sources[pose]
        return {
            "schema_version": 1,
            "attempt_key": f"synthetic-V9-{pose}-001",
            "exercise_id": "chart1-scissor-jump",
            "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [{"role": "source-photo", "locator": f"synthetic://{pose}",
                              "local_path": str(source), "sha256": self.shas[pose]}],
            "provider": "Google Flow", "model": "Nano Banana 2.1",
            "settings": copy.deepcopy(v9.IMAGE_EDIT_SETTINGS),
            "estimated_credits": "0",
            "source_preflight": {"authority": v9.AUTHORITY,
                                 "source_png": str(source), "source_pose": pose},
        }

    def test_each_original_png_role_accepted_for_free_still_observation(self):
        for pose in ("A", "C"):
            with self.subTest(pose=pose):
                data = experiments._validate_request(self.request(pose))
                self.assertEqual(data["estimated_credits"], "0")
                self.assertEqual(data["source_preflight"]["source_pose"], pose)
                self.assertEqual(data["source_preflight"]["source_png_sha256"], self.shas[pose])
                self.assertFalse(data["source_preflight"]["parent_crop_replay_verified"])
                self.assertEqual(data["source_preflight"]["paid_video_source_authority"], "NOT_GRANTED")
                self.assertEqual(data["input_assets"][0]["verification"], "rehashed_from_local_bytes")

    def test_wrong_or_derivative_source_rejected(self):
        swapped = self.request("A")
        swapped["source_preflight"]["source_png"] = str(self.sources["C"])
        with self.assertRaisesRegex(ValueError, "source|SHA"):
            experiments._validate_request(swapped)

        jpeg = self.root / "outpaint.jpg"
        Image.new("RGB", (20, 12), "green").save(jpeg)
        substituted = self.request("A")
        substituted["source_preflight"]["source_png"] = str(jpeg)
        substituted["input_assets"][0].update(local_path=str(jpeg),
                                                sha256=hashlib.sha256(jpeg.read_bytes()).hexdigest())
        with self.assertRaisesRegex(ValueError, "SHA"):
            experiments._validate_request(substituted)

        remote = self.request("A")
        del remote["input_assets"][0]["local_path"]
        with self.assertRaisesRegex(ValueError, "locally rehashed"):
            experiments._validate_request(remote)

    def test_exactly_one_image_and_no_unknown_settings(self):
        tests = [
            ("requested_outputs", 2), ("thinking_level", "Low"),
            ("aspect_ratio", "16:9"), ("generation_mode", "Frames to Video"),
        ]
        for name, value in tests:
            with self.subTest(name=name):
                req = self.request()
                req["settings"][name] = value
                with self.assertRaisesRegex(ValueError, "exact observed"):
                    experiments._validate_request(req)
        req = self.request()
        req["settings"]["seed"] = 1
        with self.assertRaisesRegex(ValueError, "exact observed"):
            experiments._validate_request(req)
        req = self.request()
        req["input_assets"].append(copy.deepcopy(req["input_assets"][0]))
        with self.assertRaisesRegex(ValueError, "exactly one"):
            experiments._validate_request(req)

    def test_quote_provider_spec_and_authority_fail_closed(self):
        for change in ("cost", "model", "provider", "scope", "spec", "extra_source_field"):
            with self.subTest(change=change):
                req = self.request()
                if change == "cost":
                    req["estimated_credits"] = "1"
                elif change == "model":
                    req["model"] = "Nano Banana 2"
                elif change == "provider":
                    req["provider"] = "Another Service"
                elif change == "scope":
                    req["exercise_id"] = "chart1-kneeling-pushup"
                elif change == "spec":
                    damaged = json.loads(self.spec.read_text())
                    damaged["status"] = "APPROVED"
                    bad_spec = self.root / "bad.json"
                    bad_spec.write_text(json.dumps(damaged))
                    req["spec_path"] = str(bad_spec)
                else:
                    req["source_preflight"]["unquoted_image"] = "other"
                with self.assertRaises(ValueError):
                    experiments._validate_request(req)

    def test_free_attempt_is_immutable_ledger_intent_with_zero_actual_charge(self):
        store = self.root / "private-ledger"
        experiments.initialize(store, provider="Google Flow", credit_limit="200",
                               opening_spent_credits="0")
        request = self.request()
        result = experiments.reserve(store, request)
        self.assertEqual(result["estimated_credits"], "0")
        self.assertEqual(result["release_status"], experiments.HOLD)
        self.assertEqual(result["request"]["submitted_prompt_sha256"],
                         hashlib.sha256(self.prompt.read_bytes()).hexdigest())
        self.assertEqual(experiments.reserve(store, request)["run_id"], result["run_id"])
        with self.assertRaisesRegex(ValueError, "attempt_key already"):
            changed = self.request("C")
            changed["attempt_key"] = request["attempt_key"]
            experiments.reserve(store, changed)
        image = self.root / "synthetic-derived-output.jpg"
        Image.new("RGB", (20, 12), "yellow").save(image)
        artifact = experiments.record_artifact(store, result["run_id"], artifact_path=image,
                                               role="raw-generated-still", locator="synthetic://output")
        self.assertEqual(artifact["proof"]["sha256"], hashlib.sha256(image.read_bytes()).hexdigest())
        experiments.settle(store, result["run_id"], actual_credits="0",
                           provider_generation_id="synthetic-editor-001", outcome="COMPLETED")
        state = experiments.snapshot(store)
        self.assertEqual(state["actual_credits"], "0")
        self.assertEqual(state["pending_reserved_credits"], "0")
        self.assertEqual(state["available_credits"], "200")

    def test_v7_positive_quote_gate_remains_untouched(self):
        req = self.request()
        req["source_preflight"]["authority"] = "V7_DIRECT_PREPARED_PAIR"
        with self.assertRaisesRegex(ValueError, "positive provider-quoted"):
            experiments._validate_request(req)


if __name__ == "__main__":
    unittest.main()
