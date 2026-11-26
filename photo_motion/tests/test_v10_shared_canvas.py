"""Synthetic, no-credit V10 reservation tests; fake replay isolates gate logic."""

import copy
import hashlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photo_motion import experiments, preflight_v10_shared_canvas as v10


class V10SourceGateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.paths = {}
        for key, (fmt, size, color) in {
            "A": ("PNG", (1280, 720), "red"),
            "C": ("PNG", (1280, 720), "blue"),
            "canvas": ("JPEG", (1344, 756), "gray"),
            "A*": ("PNG", (1344, 756), "orange"),
            "C*": ("PNG", (1344, 756), "cyan"),
        }.items():
            path = self.root / f"{key.replace('*', 'star')}.{fmt.lower()}"
            Image.new("RGB", size, color).save(path, format=fmt)
            self.paths[key] = path
        self.hashes = {key: hashlib.sha256(self.paths[key].read_bytes()).hexdigest()
                       for key in self.paths}
        patcher = patch.object(v10, "SOURCE_SHA256", {
            key: self.hashes[key] for key in ("A", "C", "canvas")})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.manifest = {
            "schema_version": 1, "tool": "photo_motion.shared_canvas",
            "transform": copy.deepcopy(v10.TRANSFORM),
            "source_images": {key: {"sha256": self.hashes[key]} for key in ("A", "C", "canvas")},
            "outputs": {key: {"sha256": self.hashes[key+"*"]} for key in ("A", "C")},
        }
        self.paths["manifest"] = self.root / "manifest.json"
        self.paths["manifest"].write_text(json.dumps(self.manifest))
        self.manifest_sha = hashlib.sha256(self.paths["manifest"].read_bytes()).hexdigest()
        for key in ("a_annotation", "c_annotation", "canvas_annotation"):
            path = self.root / f"{key}.json"
            path.write_text(json.dumps({"synthetic": True, "key": key}))
            self.paths[key] = path
        self.qa = {
            "schema_version": 1, "authority": "V10_SHARED_CANVAS_INDEPENDENT_QA",
            "manifest_sha256": self.manifest_sha,
            "source_sha256": {key: self.hashes[key] for key in ("A", "C", "canvas")},
            "output_sha256": {key: self.hashes[key+"*"] for key in ("A", "C")},
            "producer": "synthetic-compositor", "reviewer": "synthetic-independent-reviewer",
            "decision": "CANDIDATE_FOR_DIAGNOSTIC_ONLY",
            "checks": {name: {"verdict": "PASS", "evidence": "Synthetic detailed regression observation only"}
                       for name in v10.QA_CHECKS},
            "anatomical_left_right_proven": False,
            "exercise_form": "NOT_EVALUATED", "video_motion_and_release": "NOT_EVALUATED",
        }
        self.paths["qa"] = self.root / "qa.json"
        self.paths["qa"].write_text(json.dumps(self.qa))
        self.paths["prompt"] = self.root / "submitted.txt"
        self.paths["prompt"].write_text("One airborne exchange, no fade or audio", encoding="utf-8")
        self.specs = {}
        for role in ("A_TO_C", "C_TO_A"):
            path = self.root / f"spec-{role}.json"
            path.write_text(json.dumps(v10._expected_spec(role)))
            self.specs[role] = path

        # This stub writes the expected *full* replay artifacts. It deliberately
        # tests gate validation separately from the real compositor's tests.
        def fake_compose(a, c, canvas, out_dir, **kwargs):
            out_dir = Path(out_dir)
            for key, filename in (("A*", "A_shared_canvas.png"),
                                  ("C*", "C_shared_canvas.png"),
                                  ("manifest", "shared_canvas.manifest.json")):
                (out_dir / filename).write_bytes(self.paths[key].read_bytes())
            return self.manifest
        fake_module = types.ModuleType("photo_motion.shared_canvas")
        fake_module.compose = fake_compose
        p = patch.dict(sys.modules, {"photo_motion.shared_canvas": fake_module})
        p.start()
        self.addCleanup(p.stop)

    def request(self, role="A_TO_C"):
        first, last = ("A*", "C*") if role == "A_TO_C" else ("C*", "A*")
        return {
            "schema_version": 1, "attempt_key": f"synthetic-v10-{role}",
            "exercise_id": "chart1-scissor-jump", "spec_path": str(self.specs[role]),
            "submitted_prompt_file": str(self.paths["prompt"]),
            "input_assets": [
                {"role": "start-frame", "locator": "synthetic-start",
                 "local_path": str(self.paths[first]), "sha256": self.hashes[first]},
                {"role": "end-frame", "locator": "synthetic-end",
                 "local_path": str(self.paths[last]), "sha256": self.hashes[last]},
            ],
            "provider": "Google Flow", "model": "Omni 1.2 Flash",
            "settings": copy.deepcopy(v10.V10_SETTINGS), "estimated_credits": "9",
            "source_preflight": {"authority": v10.AUTHORITY,
                                 "original_a_png": str(self.paths["A"]),
                                 "original_c_png": str(self.paths["C"]),
                                 "canvas_jpeg": str(self.paths["canvas"]),
                                 "a_annotation": str(self.paths["a_annotation"]),
                                 "c_annotation": str(self.paths["c_annotation"]),
                                 "canvas_annotation": str(self.paths["canvas_annotation"]),
                                 "shared_manifest": str(self.paths["manifest"]),
                                 "derived_a_png": str(self.paths["A*"]),
                                 "derived_c_png": str(self.paths["C*"]),
                                 "independent_qa_report": str(self.paths["qa"]),
                                 "segment_role": role},
        }

    def test_both_directions_bound_to_original_derivative_and_qa_hashes(self):
        for role in ("A_TO_C", "C_TO_A"):
            with self.subTest(role=role):
                intent = experiments._validate_request(self.request(role))
                source = intent["source_preflight"]
                self.assertEqual(source["segment_role"], role)
                self.assertEqual(source["shared_canvas_manifest_sha256"], self.manifest_sha)
                self.assertEqual(source["deterministic_replay"], "EXACT_BYTE_REPLAY_PASS")
                self.assertFalse(source["anatomical_left_right_proven"])
                self.assertEqual(source["video_motion_form_and_release_approval"], "NOT_EVALUATED")

    def test_swapped_or_unverifiable_endpoints_fail(self):
        request = self.request()
        request["input_assets"].reverse()
        with self.assertRaisesRegex(ValueError, "ordered"):
            experiments._validate_request(request)
        request = self.request()
        del request["input_assets"][0]["local_path"]
        with self.assertRaisesRegex(ValueError, "locally rehashed"):
            experiments._validate_request(request)
        request = self.request()
        request["source_preflight"]["segment_role"] = "C_TO_A"
        with self.assertRaisesRegex(ValueError, "role"):
            experiments._validate_request(request)

    def test_changed_manifest_original_canvas_or_derivative_fails(self):
        for key in ("manifest", "A", "canvas", "A*"):
            with self.subTest(key=key):
                original = self.paths[key].read_bytes()
                self.paths[key].write_bytes(original + b"changed")
                try:
                    with self.assertRaises(ValueError):
                        experiments._validate_request(self.request())
                finally:
                    self.paths[key].write_bytes(original)

    def test_failed_or_unbound_independent_qa_holds(self):
        changes = (
            ("decision", "HOLD"), ("reviewer", "synthetic-compositor"),
            ("manifest_sha256", "f" * 64),
            ("anatomical_left_right_proven", True),
            ("exercise_form", "PASS"),
        )
        for name, bad in changes:
            with self.subTest(name=name):
                report = copy.deepcopy(self.qa)
                report[name] = bad
                self.paths["qa"].write_text(json.dumps(report))
                with self.assertRaisesRegex(ValueError, "independent|HOLD"):
                    experiments._validate_request(self.request())
        report = copy.deepcopy(self.qa)
        report["checks"]["seam_ghosting"]["verdict"] = "HOLD"
        self.paths["qa"].write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "check seam_ghosting"):
            experiments._validate_request(self.request())
        # A real earlier candidate missed the C forward hand in its claimed
        # subject bound. A separate annotation-coverage HOLD must block paid
        # video even if a composed image happens to look plausible.
        report = copy.deepcopy(self.qa)
        report["checks"]["annotation_coverage"]["verdict"] = "HOLD"
        self.paths["qa"].write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "check annotation_coverage"):
            experiments._validate_request(self.request())

    def test_model_cost_duration_seed_variants_and_hidden_modes_locked(self):
        for field, key, bad in (("request", "estimated_credits", "0"),
                                ("request", "model", "Omni 1.1 Flash"),
                                ("settings", "variants", 2),
                                ("settings", "duration_seconds", 6),
                                ("settings", "resolution", "1080p"),
                                ("settings", "seed", 17),
                                ("settings", "extra_outputs", 1)):
            with self.subTest(key=key):
                req = self.request()
                target = req["settings"] if field == "settings" else req
                target[key] = bad
                with self.assertRaisesRegex(ValueError, "observed"):
                    experiments._validate_request(req)

    def test_replay_disagreement_fails_before_reserve(self):
        fake = sys.modules["photo_motion.shared_canvas"]
        original = fake.compose

        def changed(*args, **kwargs):
            result = original(*args, **kwargs)
            path = Path(args[3]) / "C_shared_canvas.png"
            path.write_bytes(b"not replayed")
            return result

        with patch.object(fake, "compose", changed):
            with self.assertRaisesRegex(ValueError, "replay"):
                experiments._validate_request(self.request())

    def test_ledger_reserves_only_nine_for_single_qualified_segment(self):
        store = self.root / "ledger"
        experiments.initialize(store, provider="Google Flow", credit_limit=200,
                               opening_spent_credits=0)
        first = experiments.reserve(store, self.request())
        self.assertEqual(first["estimated_credits"], "9")
        self.assertEqual(first["release_status"], experiments.HOLD)
        self.assertEqual(experiments.snapshot(store)["pending_reserved_credits"], "9")
        experiments.settle(store, first["run_id"], actual_credits="9",
                           provider_generation_id="synthetic-video", outcome="FAILED")
        self.assertEqual(experiments.snapshot(store)["actual_credits"], "9")
        self.assertEqual(experiments.snapshot(store)["pending_reserved_credits"], "0")


if __name__ == "__main__":
    unittest.main()
