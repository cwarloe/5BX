"""Synthetic V6 pre-credit gates; never call Flow or touch private media."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photo_motion import contract, experiments, panel_prep, preflight_v6


SPEC = Path(__file__).resolve().parents[1] / "specs" / "chart1-scissor-jump.json"


class V6PreflightTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="synthetic-v6-preflight-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / "synthetic-v6-source.png"
        self.prepared = self.root / "prepared.png"
        self.spec = self.root / "spec.json"
        self.prompt = self.root / "submitted.txt"
        self.ledger = self.root / "private-ledger"
        self.prompt.write_text("One photographic scissor cycle with two distinct airborne flights.", encoding="utf-8")
        # A tiny header/body resemblance is intentionally NOT necessary here:
        # these are exact-byte/transform tests, never human form verification.
        Image.new("RGB", (1536, 1024), (50, 90, 160)).save(self.source)
        self.source_sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        for mod, name in ((contract, "V6_TAGGED_CARD_SHA256"),
                          (preflight_v6, "V6_TAGGED_CARD_SHA256")):
            mocked = patch.object(mod, name, self.source_sha)
            mocked.start()
            self.addCleanup(mocked.stop)
        spec = contract.load_spec(SPEC)
        spec["track_provenance"]["source_card_sha256"] = self.source_sha
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        panel_prep.prepare(self.source, self.prepared,
                           expected_source_sha256=self.source_sha,
                           expected_source_size=(1536, 1024),
                           export_size=(1280, 720))
        self.manifest = self.prepared.with_suffix(".manifest.json")

    def request(self):
        return {
            "schema_version": 1, "attempt_key": "scissor-v6-one", "exercise_id": "chart1-scissor-jump",
            "spec_path": str(self.spec), "submitted_prompt_file": str(self.prompt),
            "input_assets": [{"role": "start-frame", "locator": "private://test/v6-prepared",
                              "local_path": str(self.prepared)}],
            "provider": "Google Flow", "model": "synthetic-Omni-Flash",
            "settings": {"duration_seconds": 6, "aspect_ratio": "16:9", "seed": None},
            "estimated_credits": "18",
            "source_preflight": {"original_card": str(self.source), "prepared_png": str(self.prepared),
                                 "manifest": str(self.manifest)},
        }

    def test_true_bytes_spec_transform_and_manifest_replay(self):
        result = preflight_v6.verify(self.spec, self.source, self.prepared)
        self.assertEqual(result["preflight_result"], "VERIFIED_INPUT_BYTES_ONLY")
        self.assertEqual(result["prepared_png_sha256"], hashlib.sha256(self.prepared.read_bytes()).hexdigest())
        self.assertEqual(result["source_crop_half_open"], [4, 4, 764, 508])
        self.assertFalse(result["anatomical_left_right_proven"])
        self.assertEqual(result["exercise_motion_and_release_approval"], "NOT_EVALUATED")

    def test_original_source_substitution_is_rejected(self):
        Image.new("RGB", (1536, 1024), "red").save(self.source)
        with self.assertRaisesRegex(preflight_v6.PreflightError, "original V6 card SHA-256"):
            preflight_v6.verify(self.spec, self.source, self.prepared)

    def test_prepared_image_substitution_and_manifest_forgery_are_rejected(self):
        Image.new("RGB", (1280, 720), "green").save(self.prepared)
        with self.assertRaisesRegex(preflight_v6.PreflightError, "output_sha256|prepared PNG bytes"):
            preflight_v6.verify(self.spec, self.source, self.prepared)
        # Even a fake manifest digest cannot make a wrong pixel transform pass.
        doc = json.loads(self.manifest.read_text())
        doc["output_sha256"] = hashlib.sha256(self.prepared.read_bytes()).hexdigest()
        self.manifest.write_text(json.dumps(doc))
        with self.assertRaisesRegex(preflight_v6.PreflightError, "prepared PNG bytes"):
            preflight_v6.verify(self.spec, self.source, self.prepared)

    def test_mutated_manifest_crop_or_claim_is_rejected(self):
        doc = json.loads(self.manifest.read_text())
        doc["crop_bounds_half_open"] = [100, 100, 500, 500]
        self.manifest.write_text(json.dumps(doc))
        with self.assertRaisesRegex(preflight_v6.PreflightError, "crop_bounds_half_open"):
            preflight_v6.verify(self.spec, self.source, self.prepared)
        spec = contract.load_spec(self.spec)
        spec["track_provenance"]["anatomical_left_right_proven"] = True
        self.spec.write_text(json.dumps(spec))
        with self.assertRaisesRegex(preflight_v6.PreflightError, "anatomical left/right"):
            preflight_v6.verify(self.spec, self.source, self.prepared)

    def test_paid_run_reservation_requires_exact_local_start_frame_binding(self):
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="200")
        req = self.request()
        without = copy.deepcopy(req)
        without.pop("source_preflight")
        with self.assertRaisesRegex(experiments.ExperimentError, "requires source_preflight"):
            experiments.reserve(self.ledger, without)
        wrong = copy.deepcopy(req)
        wrong["input_assets"][0]["role"] = "unverified-identity"
        with self.assertRaisesRegex(experiments.ExperimentError, "prepared start-frame"):
            experiments.reserve(self.ledger, wrong)
        wrong = copy.deepcopy(req)
        wrong["settings"]["aspect_ratio"] = "4:3"
        with self.assertRaisesRegex(experiments.ExperimentError, "16:9"):
            experiments.reserve(self.ledger, wrong)
        self.assertEqual(experiments.snapshot(self.ledger)["attempts"], 0)
        accepted = experiments.reserve(self.ledger, req)
        self.assertEqual(accepted["release_status"], experiments.HOLD)
        self.assertEqual(accepted["request"]["source_preflight"]["prepared_png_sha256"],
                         hashlib.sha256(self.prepared.read_bytes()).hexdigest())
        self.assertEqual(experiments.snapshot(self.ledger)["pending_reserved_credits"], "18")


if __name__ == "__main__":
    unittest.main()
