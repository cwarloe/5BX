"""Synthetic-only two-still V6 pre-credit provenance gates; no Flow calls."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photo_motion import contract, experiments, panel_prep, preflight_v6


SPEC = Path(__file__).resolve().parents[1] / "specs" / "chart1-scissor-jump.json"


class DualV6IngredientTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="synthetic-v6-dual-precredit-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "synthetic-original-v6.png"
        self.a = self.root / "start-A.png"
        self.c = self.root / "opposite-C.png"
        self.spec = self.root / "spec.json"
        self.prompt = self.root / "proposed-flow-input.txt"
        self.ledger = self.root / "private-ledger"
        # Distinct photographic-looking source regions, never real media.
        image = Image.new("RGB", (1536, 1024), (50, 80, 150))
        image.paste(Image.new("RGB", (760, 504), (150, 80, 30)), (4, 516))
        image.save(self.source)
        self.source_sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        for target, name in ((contract, "V6_TAGGED_CARD_SHA256"),
                             (preflight_v6, "V6_TAGGED_CARD_SHA256"),
                             (panel_prep, "VERIFIED_V6_SOURCE_SHA256")):
            fake = patch.object(target, name, self.source_sha)
            fake.start()
            self.addCleanup(fake.stop)
        spec = contract.load_spec(SPEC)
        spec["track_provenance"]["source_card_sha256"] = self.source_sha
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        self.prompt.write_text("Two continuous scissor flights, opposite grounded C, recover A.", encoding="utf-8")
        panel_prep.prepare(self.source, self.a, panel="A", expected_source_sha256=self.source_sha,
                           expected_source_size=(1536, 1024), export_size=(1280, 720))
        panel_prep.prepare(self.source, self.c, panel="C", expected_source_sha256=self.source_sha,
                           expected_source_size=(1536, 1024), export_size=(1280, 720))
        self.a_manifest = self.a.with_suffix(".manifest.json")
        self.c_manifest = self.c.with_suffix(".manifest.json")
        self.assertNotEqual(self.a.read_bytes(), self.c.read_bytes())

    def request(self):
        return {
            "schema_version": 1, "attempt_key": "V6-two-ingredients-attempt-001",
            "exercise_id": "chart1-scissor-jump",
            "spec_path": str(self.spec), "submitted_prompt_file": str(self.prompt),
            "provider": "Google Flow", "model": "synthetic-Omni-Flash",
            "estimated_credits": "18",
            "settings": {"duration_seconds": 6, "aspect_ratio": "16:9", "output_count": 1, "seed": None},
            "input_assets": [
                {"role": "start-frame", "locator": "private://v6/A", "local_path": str(self.a)},
                {"role": "opposite-pose-reference", "locator": "private://v6/C", "local_path": str(self.c)},
            ],
            "source_preflight": {
                "original_card": str(self.source), "prepared_png": str(self.a), "manifest": str(self.a_manifest),
                "opposite_pose_reference": {"prepared_png": str(self.c), "manifest": str(self.c_manifest)},
            },
        }

    def verify_rejected(self, request, fragment):
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="200", opening_spent_credits="0")
        with self.assertRaisesRegex(experiments.ExperimentError, fragment):
            experiments.reserve(self.ledger, request)
        self.assertEqual(experiments.snapshot(self.ledger)["attempts"], 0)

    def test_both_panels_from_one_verified_source_and_distinct_exact_bytes(self):
        a = preflight_v6.verify(self.spec, self.source, self.a, self.a_manifest)
        c = preflight_v6.verify(self.spec, self.source, self.c, self.c_manifest, panel="C")
        joint = preflight_v6.verify_pair(self.spec, self.source, self.a, self.a_manifest,
                                          self.c, self.c_manifest)
        self.assertEqual(a["source_crop_half_open"], [4, 4, 764, 508])
        self.assertEqual(c["source_crop_half_open"], [4, 516, 764, 1020])
        self.assertEqual(c["source_panel"], "C")
        self.assertEqual(joint["source_panel"], "A")
        self.assertEqual(c["source_marker_opposite_state"], {"orange_leg": "forward", "teal_leg": "back",
                                                             "orange_arm": "back", "teal_arm": "forward"})
        self.assertEqual(joint["opposite_pose_reference"], c)
        self.assertEqual(a["original_v6_card_sha256"], c["original_v6_card_sha256"])
        self.assertNotEqual(a["prepared_png_sha256"], c["prepared_png_sha256"])
        self.assertEqual(c["exercise_motion_and_release_approval"], "NOT_EVALUATED")

    def test_one_ingredient_legacy_is_still_allowed_without_new_receipt_fields(self):
        req = self.request()
        req["input_assets"].pop()
        req["source_preflight"].pop("opposite_pose_reference")
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="200", opening_spent_credits="0")
        run = experiments.reserve(self.ledger, req)
        self.assertEqual(run["request"]["source_preflight"],
                         preflight_v6.verify(self.spec, self.source, self.a, self.a_manifest))
        self.assertEqual(len(run["request"]["input_assets"]), 1)
        self.assertEqual(experiments.snapshot(self.ledger)["pending_reserved_credits"], "18")

    def test_legacy_A_manifest_without_explicit_panel_fields_remains_accepted(self):
        doc = json.loads(self.a_manifest.read_text())
        doc.pop("source_panel", None)
        doc.pop("crop_matches_verified_panel_bounds", None)
        self.a_manifest.write_text(json.dumps(doc), encoding="utf-8")
        run = preflight_v6.verify(self.spec, self.source, self.a, self.a_manifest)
        self.assertNotIn("source_panel", run)
        self.assertEqual(run["source_crop_half_open"], [4, 4, 764, 508])
        # The NEW dual path also permits historical A manifest, but C must
        # still carry its explicit panel identity and verified crop.
        pair = preflight_v6.verify_pair(self.spec, self.source, self.a, self.a_manifest,
                                        self.c, self.c_manifest)
        self.assertEqual(pair["source_panel"], "A")
        self.assertEqual(pair["opposite_pose_reference"]["source_panel"], "C")

    def test_exact_dual_recipe_can_reserve_once_without_duplication_or_approval(self):
        req = self.request()
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="200", opening_spent_credits="0")
        first = experiments.reserve(self.ledger, req)
        self.assertEqual(first, experiments.reserve(self.ledger, req))
        self.assertEqual(first["release_status"], experiments.HOLD)
        self.assertEqual(len(first["request"]["input_assets"]), 2)
        self.assertEqual([a["role"] for a in first["request"]["input_assets"]],
                         ["start-frame", "opposite-pose-reference"])
        self.assertEqual(first["request"]["input_assets"][1]["verification"], "rehashed_from_local_bytes")
        receipt_c = first["request"]["source_preflight"]["opposite_pose_reference"]
        self.assertEqual(receipt_c["preparation_manifest_sha256"], hashlib.sha256(self.c_manifest.read_bytes()).hexdigest())
        self.assertEqual(receipt_c["prepared_png_sha256"], hashlib.sha256(self.c.read_bytes()).hexdigest())
        self.assertEqual(experiments.snapshot(self.ledger)["attempts"], 1)
        self.assertEqual(experiments.snapshot(self.ledger)["pending_reserved_credits"], "18")

    def test_reject_wrong_or_extra_asset_role_and_order(self):
        req = self.request()
        req["input_assets"][1]["role"] = "identity-master"
        self.verify_rejected(req, "ordered verified start-frame A")
        req = self.request()
        req["input_assets"].reverse()
        self.verify_rejected(req, "ordered verified start-frame A")
        req = self.request()
        req["input_assets"].append({"role": "third-photo", "locator": "private://other", "local_path": str(self.c)})
        self.verify_rejected(req, "ordered verified start-frame A")

    def test_reject_extra_image_without_C_preflight_and_missing_second_image(self):
        req = self.request()
        req["source_preflight"].pop("opposite_pose_reference")
        self.verify_rejected(req, "ordered verified start-frame A")
        req = self.request()
        req["input_assets"].pop()
        self.verify_rejected(req, "ordered verified start-frame A")

    def test_reject_declared_only_remote_second_asset(self):
        req = self.request()
        req["input_assets"][1].pop("local_path")
        req["input_assets"][1]["sha256"] = hashlib.sha256(self.c.read_bytes()).hexdigest()
        self.verify_rejected(req, "ordered verified start-frame A")

    def test_reject_corrupted_C_png_and_crop_manifest(self):
        req = self.request()
        Image.new("RGB", (1280, 720), "green").save(self.c)
        self.verify_rejected(req, "manifest output_sha256|prepared PNG bytes")

    def test_reject_tampered_C_crop_and_panel_identity(self):
        req = self.request()
        for key, fake in (("crop_bounds_half_open", [4, 4, 764, 508]),
                          ("source_panel", "A"),
                          ("crop_matches_verified_panel_bounds", False),
                          ("expected_source_sha256", "a" * 64),
                          ("source_hash_matches_expected", False)):
            with self.subTest(key=key):
                original = json.loads(self.c_manifest.read_text())
                edited = dict(original)
                edited[key] = fake
                self.c_manifest.write_text(json.dumps(edited), encoding="utf-8")
                try:
                    self.verify_rejected(req, "preparation manifest")
                finally:
                    self.c_manifest.write_text(json.dumps(original), encoding="utf-8")

    def test_missing_C_explicit_panel_tag_fails(self):
        doc = json.loads(self.c_manifest.read_text())
        doc.pop("source_panel")
        self.c_manifest.write_text(json.dumps(doc), encoding="utf-8")
        self.verify_rejected(self.request(), "source_panel")

    def test_reject_missing_C_manifest_and_invalid_nested_schema(self):
        req = self.request()
        req["source_preflight"]["opposite_pose_reference"] = None
        self.verify_rejected(req, "must contain exactly")
        req = self.request()
        req["source_preflight"]["opposite_pose_reference"]["original_card"] = str(self.source)
        self.verify_rejected(req, "must contain exactly")
        req = self.request()
        req["source_preflight"]["opposite_pose_reference"]["manifest"] = str(self.root / "does-not-exist.json")
        self.verify_rejected(req, "preflight failed")

    def test_reject_C_claim_from_arbitrary_original_card(self):
        req = self.request()
        stranger = self.root / "unrelated.png"
        Image.new("RGB", (1536, 1024), "purple").save(stranger)
        panel_prep.prepare(stranger, self.root / "unrelated-C.png", panel="C",
                           expected_source_sha256=hashlib.sha256(stranger.read_bytes()).hexdigest(),
                           expected_source_size=(1536, 1024), export_size=(1280, 720))
        req["source_preflight"]["opposite_pose_reference"] = {
            "prepared_png": str(self.root / "unrelated-C.png"),
            "manifest": str(self.root / "unrelated-C.manifest.json")}
        req["input_assets"][1]["local_path"] = str(self.root / "unrelated-C.png")
        self.verify_rejected(req, "preflight failed")

    def test_reject_C_masquerading_as_A_or_duplicate_A(self):
        req = self.request()
        req["source_preflight"]["opposite_pose_reference"] = {
            "prepared_png": str(self.a), "manifest": str(self.a_manifest)}
        req["input_assets"][1]["local_path"] = str(self.a)
        self.verify_rejected(req, "preflight failed")


if __name__ == "__main__":
    unittest.main()
